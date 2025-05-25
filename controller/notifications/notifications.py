from pathlib import Path

import yagmail
from flask_restful import Resource
from sqlalchemy import desc
from sqlalchemy_serializer import SerializerMixin
from config.helper import *
from config.api_message import success_reads, failed_reads, success_read, failed_read
from config.database import db
from controller.tblUser import tblUser


class NotificationsType(db.Model, SerializerMixin):
    serialize_rules = ('-id',)
    __tablename__ = 'notificationsType'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)


class Notifications(db.Model, SerializerMixin):
    serialize_rules = ('-created_by', '-last_updated_by', '-last_updated_date', '-UserId', '-id_notificationsType', '-readDate', )
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, db.ForeignKey('tblUser.UserId'), nullable=False)
    id_notificationsType = db.Column(db.Integer, db.ForeignKey('notificationsType.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    created_date = db.Column(db.TIMESTAMP, nullable=True, default=datetime.now())
    readDate = db.Column(db.TIMESTAMP, nullable=True)
    last_updated_date = db.Column(db.TIMESTAMP, nullable=True)
    created_by = db.Column(db.String, nullable=True)
    last_updated_by = db.Column(db.String, nullable=True)
    notificationsType = db.relationship('NotificationsType')
    attributes = db.Column(db.String, nullable=True)


class NotifList(Resource):
    method_decorators = {'get': [tblUser.auth_apikey]}

    def get(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('detail', type=str)
        try:
            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            if args['detail'] == "true":
                result = []

                # filter except chats
                listAll = Notifications.query.filter_by(
                    UserId=UserId,
                ).filter(Notifications.id_notificationsType != 3).order_by(desc(Notifications.created_date)).limit(10)
                for row in listAll:
                    row.readDate = datetime.now()
                    result.append(row.to_dict())

                # set read
                Notifications.query.filter_by(
                    UserId=UserId, readDate=None
                ).filter(Notifications.id_notificationsType != 3).update({Notifications.readDate: datetime.now()})
                db.session.commit()

                return success_reads(result)
            else:
                notifData = Notifications.query.filter_by(
                    UserId=UserId, readDate=None
                ).filter(Notifications.id_notificationsType != 3)
                chatData = Notifications.query.filter_by(
                    UserId=UserId, readDate=None
                ).filter(Notifications.id_notificationsType == 3)
                countNotif = notifData.count()
                countChat = chatData.count()
                return success_read({'count': countNotif, 'chat': countChat})
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return failed_reads({})