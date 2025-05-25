from datetime import datetime, timedelta

import jwt
from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import desc
from sqlalchemy.sql.elements import or_, and_

from config.api_message import success_reads, success_update, failed_reads, failed_read, success_read, success_create, \
    failed_create, failed_update
from config.config import jwt_secretkey, appName, appFrontWebUrl
from config.database import db
from config.helper import toDict, checkIsEmail, logger
from controller.notifications.fcm_session import sendNotificationNative
from controller.notifications.notifications import Notifications
from controller.tblGroupUser import tblGroupUser
from controller.tblUser import tblUser


def getUserValid(refresh_db=True, userData=None,  includeWp=False):
    ListDevice = []
    if not userData.UserId:
        return ListDevice
    try:
        Users = tblUser.query
        # if not includeWp:
        #     Users = Users.join(tblGroupUser).filter(tblGroupUser.IsWP == None)
        Users = Users.filter(tblUser.UserId != userData.UserId).order_by(desc(tblUser.last_request)).all()
        for row in Users:
            # print(row.Email)
            if row.last_request:
                online_state = False
                notification = Notifications.query.filter_by(id_notificationsType=3)
                notification = notification.filter(
                    or_((and_(Notifications.UserId == userData.UserId, Notifications.created_by == row.Email)),
                        (and_(Notifications.UserId == row.UserId, Notifications.created_by == userData.Email)))
                )

                unreadCount = notification.filter_by(readDate=None).filter(
                    Notifications.created_by != userData.Email).count()
                notificationData = notification.order_by(desc(Notifications.created_date)).first()
                lastMessage = notificationData.description if notificationData else ""
                lastMessageAt = notificationData.created_date if notificationData else datetime(1900, 1, 1)
                # print(row.last_request)

                if row.APIKey:
                    online_state = row.last_request > (
                                datetime.now() - timedelta(minutes=1)) if row.last_request else False
                    try:
                        jwt.decode(row.APIKey, jwt_secretkey, algorithms=['HS256'])
                    except Exception as ex:
                        if refresh_db:
                            row.APIKey = None
                            row.DeviceId = None
                            db.session.flush()
                        print(ex)

                # print(lastMessageAt)
                data_public = {
                    'id': row.Email or row.UserId,
                    'unreadCount': unreadCount,
                    'email': row.Email,
                    'name': row.nama_user,
                    'group': row.Group.nama_group,
                    'avatar': row.Avatar,
                    'onlineState': online_state,
                    'lastView': row.last_request if row.last_request else datetime(1900, 1, 1),
                    'lastMessage': lastMessage,
                    'lastMessageAt': lastMessageAt
                }
                ListDevice.append(data_public)
        ListDevice = sorted(ListDevice, key=lambda d: (d['lastMessageAt'], d['lastView']), reverse=True, )
        if refresh_db:
            db.session.commit()
    except Exception as e:
        print(e)
    return ListDevice


def getConversationByEmail(fromUserData, toEmail):
    toUser = tblUser.query.filter_by(Email=toEmail).first()
    ListConversation = []
    ListNotification = []
    select = db.session.query(Notifications, tblUser.nama_user, tblUser.Avatar, tblUser.Email) \
        .join(tblUser) \
        .filter(Notifications.id_notificationsType == 3) \
        .filter(
        or_((and_(Notifications.UserId == fromUserData.UserId, Notifications.created_by == toEmail)),
            (and_(Notifications.UserId == toUser.UserId, Notifications.created_by == fromUserData.Email)))
    ).order_by(Notifications.created_date).all()

    emailList = []

    for row in select:
        emailList.append(row.Email)
        readAt = row.Notifications.readDate
        # print(not readAt, readAt)
        if not readAt and row.Notifications.created_by.rstrip() == toEmail.rstrip():
            readAt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row.Notifications.readDate = datetime.now()
            db.session.flush()

            dataNotification = {
                'chatId': row.Notifications.id,
                'readAt': readAt,
            }
            ListNotification.append(dataNotification)
        # print(fromUserData.Email)
        # print(row.Email)
        # print(row.Notifications.description)
        if fromUserData.Email != row.Email:
            data = {
                'name': fromUserData.nama_user,
                'avatar': fromUserData.Avatar,
                'email': fromUserData.Email,
                'chatId': row.Notifications.id,
                'description': row.Notifications.description,
                'createdAt': row.Notifications.created_date,
                'deliveryAt': row.Notifications.last_updated_date,
                'readAt': readAt,
                'isMine': True
            }
        else:
            data = {
                'name': toUser.nama_user,
                'avatar': toUser.Avatar,
                'email': toUser.Email,
                'chatId': row.Notifications.id,
                'description': row.Notifications.description,
                'createdAt': row.Notifications.created_date,
                'deliveryAt': row.Notifications.last_updated_date,
                'readAt': readAt,
                'isMine': False
            }

        ListConversation.append(data)

    if fromUserData.Email in emailList or toEmail in emailList:
        db.session.commit()
        # sendReadToFromEmail = toUser
        if len(ListNotification) > 0 and toUser.DeviceId:
            notification_data = {
                "notification": {},
                "data": {
                    'type': 'chat_read',
                    'messages': ListNotification
                }
            }
            sendNotificationNative(toUser.DeviceId, notification_data)
        return ListConversation
    else:
        return []


def setReadMessage(chatId, readDate):
    try:
        select = Notifications.query.filter_by(id=chatId).first()
        select.readDate = readDate
        db.session.commit()
        return True
    except Exception as e:
        return False


class UserOnlineStatus(Resource):
    method_decorators = {'get': [tblUser.auth_apikey]}

    def get(self, *args, **kwargs):
        # parser = reqparse.RequestParser()
        # args = parser.parse_args()

        user_info = kwargs['user_info']
        if user_info.Group.IsWP:
            return failed_reads({})

        ListDevice = getUserValid(userData=user_info)
        return success_reads(ListDevice)


class UserChatById(Resource):
    method_decorators = {'get': [tblUser.auth_apikey], 'post': [tblUser.auth_apikey]}

    def get(self, email, *args, **kwargs):
        # parser = reqparse.RequestParser()
        # args = parser.parse_args()

        user_info = kwargs['user_info']
        if user_info.Group.IsWP:
            return failed_read({})
        # print(user_info.UserId)
        ListConversation = getConversationByEmail(fromUserData=user_info, toEmail=email)
        return success_read(ListConversation)

    def post(self, email, *args, **kwargs):
        try:
            user_info = kwargs['user_info']
            if not checkIsEmail(email):
                return failed_create({})
            if user_info.Group.IsWP:
                return failed_create({})

            if not (user_to := tblUser.query.filter_by(Email=email).first()):
                return failed_create({})

            parser = reqparse.RequestParser()
            parser.add_argument('message', type=str)
            args = parser.parse_args()
            message = args['message']

            addNewMessage = Notifications(
                UserId=user_to.UserId,
                id_notificationsType=3,
                title='-',
                description=args['message'],
                created_date=datetime.now(),
                created_by=user_info.Email
            )
            db.session.add(addNewMessage)
            db.session.commit()
            result = {
                'avatar': user_info.Avatar,
                'chatId': addNewMessage.id,
                'createdAt': addNewMessage.created_date.strftime("%Y-%m-%d %H:%M:%S"),
                'deliveryAt': None,
                'description': message,
                'email': user_info.Email,
                'isMine': True,
                'name': user_info.nama_user,
                'readAt': None
            }
            response_message = success_create(result)
            result_notif = result
            result_notif['type'] = 'chat'
            result_notif['isMine'] = False
            notification_data = {
                "notification": {
                    "title": user_info.nama_user if user_info.nama_user else user_info.Email,
                    "body": f"{args['message']}",
                    "icon": user_info.Avatar,
                    "click_action": f"{appFrontWebUrl()}#/admin",
                },
                "data": result_notif
            }
            notificationResponse = sendNotificationNative(user_to.DeviceId, notification_data)
            # print(notificationResponse.status_code == 200)
            # SET DELIVERY DATE
            if notificationResponse.status_code == 200:
                addNewMessage.last_updated_date = datetime.now()
                addNewMessage.last_updated_by = 'system'
                db.session.commit()
            return response_message
        except Exception as e:
            print(e)
            return failed_create({})


class SetReadChat(Resource):
    method_decorators = {'post': [tblUser.auth_apikey]}

    def post(self, id, *args, **kwargs):
        user_info = kwargs['user_info']
        parser = reqparse.RequestParser()
        parser.add_argument('readAt', type=str, required=True)
        args = parser.parse_args()

        if not (select := Notifications.query.filter_by(id=id).first()):
            return failed_update({})

        setRead = setReadMessage(id, args['readAt'])
        if not setRead:
            return failed_update({})

        messageFrom = tblUser.query.filter_by(Email=select.created_by).first()
        if messageFrom.DeviceId:
            notification_data = {
                "notification": {},
                "data": {
                    'type': 'chat_read',
                    'messages': [{'chatId': id, 'readAt': args['readAt']}]
                }
            }
            sendNotificationNative(messageFrom.DeviceId, notification_data)
        return success_update({'chatId': id, 'readAt': args['readAt']})


class UserRefreshStatus(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, *args, **kwargs):
        # parser = reqparse.RequestParser()
        # args = parser.parse_args()
        user_info = kwargs['user_info']
        getUserValid(refresh_db=True, userData=user_info)
        # print(ListDevice)
        return success_update({})