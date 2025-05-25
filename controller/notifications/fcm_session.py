import json

import requests
from cloudinary import logger
from flask import request, jsonify, make_response
from flask_restful import Resource, reqparse, abort
from pyfcm import FCMNotification

from config.config import api_key_fcm
# from config.helper import logger
# from controller.tblUser import tblUser

push_service = FCMNotification(api_key=api_key_fcm)


def sendNotificationNative(deviceId, notification_data):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + api_key_fcm,
        }

        body = {
            'notification': notification_data['notification'],
            'to': deviceId,
            'priority': 'high',
        }
        if notification_data['data']:
            body['data'] = notification_data['data']
        response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
        # if response.status_code == 200:
        logger.info('Notifikasi FCM berhasil dikirim')
        return response
    except Exception as e:
        logger.error(e)
        logger.error('Notifikasi FCM gagal dikirim')
        return None


def sendNotificationAdmin(notification_data, deviceId):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + api_key_fcm,
        }
        body = {
            'notification': notification_data['notification'],
            'priority': 'high',
        }
        if deviceId:
            body["to"] = deviceId
        if notification_data['data']:
            body['data'] = notification_data['data']
        response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
        # print(response)
        if response.status_code == 200:
            logger.info('Notifikasi FCM berhasil dikirim')
            return True
        else:
            logger.error('Notifikasi FCM gagal dikirim')
            return False
    except Exception as e:
        logger.error(e)
        logger.error('Notifikasi FCM gagal dikirim')
        return False


def sendNotificationToSingleDevice(deviceId, notification_data):
    registration_id = deviceId
    message_title = notification_data['notification']['title']
    message_body = notification_data['notification']['body']
    data_message = notification_data['data']
    if data_message:
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                   message_body=message_body, data_message=data_message)
    else:
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                   message_body=message_body)
    if result and result['success'] == 1:
        logger.info('Notifikasi FCM berhasil dikirim')
    else:
        logger.error('Notifikasi FCM gagal dikirim')


class NotifToAdmin(Resource):
    def post(self):
        if request.headers['kjtbdg'] == 'kjtbdgyess':
            try:
                args = json.loads(request.data)
                notification_data = {
                    "data": {
                        "type": "online_stat",
                        "name": args['name'],
                        "date_joined": args['date_joined'],
                        "avatar": args['avatar'],
                    },
                    "notification": args['notification']
                }
                deviceId = args['device']
                if sendNotificationAdmin(notification_data, deviceId):
                    return jsonify({'status_code': 1, 'message': 'OK', 'data': 'user online status to all sent'})
                else:
                    return abort(make_response(jsonify({
                        'status_code': 1002,
                        'message': 'user online status to all failed to sent'
                    }), 500))
            except Exception as e:
                print(e)
                return abort(make_response(jsonify({
                    'status_code': 1002,
                    'message': 'user online status to all failed to sent'
                }), 500))
        else:
            return abort(make_response(jsonify({
                'status_code': 1002,
                'message': 'user online status to all failed to sent'
            }), 500))


class NotifToAdmins(Resource):
    def post(self):
        if request.headers['kjtbdg'] == 'kjtbdgyess':
            try:
                args = json.loads(request.data)
                notification_data = {
                    "data": {
                        "type": "new_object_wpo"
                    },
                    "notification": args['body']['notification']
                }
                deviceId = args['body']['device']
                if sendNotificationAdmin(notification_data, deviceId):
                    return jsonify({'status_code': 1, 'message': 'OK', 'data': 'user online status to all sent'})
                else:
                    return abort(make_response(jsonify({
                        'status_code': 1002,
                        'message': 'user online status to all failed to sent'
                    }), 500))
            except Exception as e:
                print(e)
                return abort(make_response(jsonify({
                    'status_code': 1002,
                    'message': 'user online status to all failed to sent'
                }), 500))
        else:
            return abort(make_response(jsonify({
                'status_code': 1002,
                'message': 'user online status to all failed to sent'
            }), 500))