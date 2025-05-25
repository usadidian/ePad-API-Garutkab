import json
import os
import re

import cloudinary.uploader
import requests
from flask import request, make_response, jsonify
from flask_restful import Resource, abort

from config.api_message import success_create, failed_create, success_delete, failed_delete
from config.config import sightengine_api_secret, sightengine_api_user, appFrontWebLogo, appName, appFrontWebUrl
from config.database import db
from config.helper import logger
from controller.MsWPData import MsWPData
from controller.articles.articles import Articles
from controller.notifications.fcm_session import sendNotificationNative
from controller.tblUser import tblUser

folder_cloudinary = "articles"


class TaskUploadArticleImg(Resource):
    def post(self, *args, **kwargs):
        data_par = json.loads(request.data.decode())
        folder_name = data_par['folder_name']
        id = data_par['id']
        filenames_str = data_par['filenames']
        userid = data_par['userid']
        # ///user for updated
        select_query = Articles.query.filter_by(id=id).first()
        try:
            # ///user for notif
            data_user = tblUser.query.filter_by(UserId=userid).first()
            notification_data = {
                "notification": {
                    "title": appName,
                    "body": f"Gambar Artikel {select_query.title} sedang di unggah",
                    "priority": "high",
                    "icon": appFrontWebLogo,
                    "click_action": f"{appFrontWebUrl()}#/admin",
                },
                "data": {
                    "type": "avatar_upload_start",
                    "page": "articles",
                    "id": select_query.id
                }
            }
            sendNotificationNative(data_user.DeviceId, notification_data)
            filenames = filenames_str.split(',')
            # CHECK NUDITY
            logger.info('CHECK NUDITY OF IMAGES TO sightengine START')
            images = set()
            if not os.path.exists(f'./static/uploads/article_temp'):
                os.makedirs(f'./static/uploads/article_temp')
            folder_temp = f'./static/uploads/article_temp'
            for row in filenames:
                file = open(f'{folder_temp}/{row}', 'rb')
                images.add(('media[]', file))
            par_sightengine = {
                'models': 'nudity,wad,offensive,text-content,gore',
                'api_user': sightengine_api_user,
                'api_secret': sightengine_api_secret
            }
            check_image_nudity = requests.post('https://api.sightengine.com/1.0/check.json', files=images,
                                               data=par_sightengine)
            check_image_nudity_output = json.loads(check_image_nudity.text)
            if check_image_nudity_output['status'] == 'success':
                if len(filenames) > 1:
                    for row in check_image_nudity_output['data']:
                        if row['nudity']['safe'] < 0.50:
                            return abort(make_response(
                                jsonify({'status_code': 51, 'message': 'Foto mengandung unsur pornografi!',
                                         'data': {}
                                         }), 500))
                else:
                    if check_image_nudity_output['nudity']['safe'] < 0.50:
                        notification_data = {
                            "notification": {
                                "title": appName,
                                "body": f"Gambar Artikel {select_query.title} gagal di unggah karena mengandung unsur pornografi atau kekerasan",
                                "priority": "high",
                                "icon": appFrontWebLogo,
                                "click_action": f"{appFrontWebUrl()}#/admin",
                            },
                            "data": {
                                "type": "avatar_upload_failed",
                                "page": "articles",
                                "id": select_query.id
                            }
                        }
                        sendNotificationNative(data_user.DeviceId, notification_data)
                        return abort(make_response(
                            jsonify({'status_code': 51, 'message': 'Foto mengandung unsur pornografi!',
                                     'data': {}
                                     }), 500))

            # //close image connection
            for row in images:
                # print(row[1])
                row[1].close()

            logger.info('CHECK NUDITY OF IMAGES TO sightengine FINISH')
            # /////////////////////////
            origin = request.headers.get('Origin')
            origin = origin.replace('http://', '').replace('https://', '') + '/' if origin else ''
            for row in filenames:
                # DO UPLOAD
                filename = row.split('.')[0]
                upload_result = cloudinary.uploader.upload(f'{folder_name}/{row}',
                                                           public_id=f"Articles/{origin}article_{str(id)}")
                if upload_result['public_id']:
                    index = filename.split('_')[-1]

                    if select_query:
                        select_query.img = upload_result['secure_url']
                        db.session.commit()
                        # //delete image
                        os.remove(f'{folder_name}/{row}')
            # unit_data.isUploading = False
            # db.session.commit()
            notification_data = {
                "notification": {
                    "title": appName,
                    "body": f"Gambar Artikel {select_query.title} berhasil di unggah",
                    "priority": "high",
                    "icon": upload_result['secure_url'],
                    "click_action": f"{appFrontWebUrl()}#/admin",
                },
                "data": {
                    "type": "avatar_upload_finish",
                    "img": upload_result['secure_url'],
                    "page": "articles",
                    "id": select_query.id
                }
            }
            sendNotificationNative(data_user.DeviceId, notification_data)
            return success_create({})
        except Exception as e:
            notification_data = {
                "notification": {
                    "title": appName,
                    "body": f"Gambar Artikel {select_query.title} gagal di unggah",
                    "priority": "high",
                    "icon": appFrontWebLogo,
                    "click_action": f"{appFrontWebUrl()}#/admin",
                },
                "data": {
                    "type": "avatar_upload_failed",
                    "page": "articles",
                    "id": select_query.id
                }
            }
            sendNotificationNative(data_user.DeviceId, notification_data)
            db.session.rollback()
            logger.error(e)
            return failed_create({})


class TaskDeleteArticleImg(Resource):
    def post(self, *args, **kwargs):
        data_par = json.loads(request.data.decode())
        path = data_par['path']

        try:
            folder = path.split('/')[-1]
            get_public_id = folder.rsplit('.', 1)[0]
            origin = request.headers.get('Origin')
            origin = origin.replace('http://', '').replace('https://', '') + '/' if origin else ''
            delete_img = cloudinary.uploader.destroy('Articles/'+origin+get_public_id)
            return success_delete({})
        except Exception as e:
            db.session.rollback()
            logger.error(e)
            return failed_delete({})