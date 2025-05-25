import json
import mimetypes
import os
import re

import cloudinary.uploader
import requests
from flask import request, make_response, jsonify
from flask_restful import Resource, abort
from werkzeug.utils import secure_filename

from config.api_message import success_create, failed_create, success_delete, failed_delete
from config.config import sightengine_api_secret, sightengine_api_user, appFrontWebLogo, appName, appFrontWebUrl
from config.database import db
from config.helper import logger, allowed_file
from controller.PelaporanByOmzet import PelaporanByOmzet

from controller.notifications.fcm_session import sendNotificationNative
from controller.tblUser import tblUser

folder_cloudinary = "items"

ALLOWED_EXTENSIONS = {'.pdf', '.jpeg', '.jpg', '.png'}

# Fungsi untuk memvalidasi ekstensi file
def is_allowed_file(filename):
    file_extension = os.path.splitext(filename)[1].lower()
    return file_extension in ALLOWED_EXTENSIONS

class TaskUploadDocLapor(Resource):
    def post(self, *args, **kwargs):
        data_par = json.loads(request.data.decode())
        folder_name = data_par['folder_name']
        filenames_str = data_par['filenames']
        userid = data_par['userid']
        id = data_par['doc_lapor']
        origin = request.headers.get('Origin', '').replace('http://', '').replace('https://', '') + '/'
        # cloudinary_folder = f"DocLapor/{origin}doc_lapor_{str(id)}"
        cloudinary_folder = f"DocLapor/epad35/doc_lapor_{str(id)}"

        # Pilih folder Cloudinary berdasarkan `self_upload`
        if data_par['self_upload']:
            select_query = PelaporanByOmzet.query.filter_by(PelaporanID=id).first()
            cloudinary_folder = f"DocLapor/epad35/doc_lapor_{str(id)}_self_uploaded"
        else:
            select_query = PelaporanByOmzet.query.filter_by(PelaporanID=id).first()

        try:
            data_user = tblUser.query.filter_by(UserId=userid).first()
            filenames = filenames_str.split(',')

            for row in filenames:
                # Periksa ekstensi file
                if not os.path.splitext(row)[1]:
                    raise ValueError(f"File {row} tidak memiliki ekstensi.")
                if not is_allowed_file(row):
                    raise ValueError(f"File {row} memiliki ekstensi yang tidak didukung. "
                                     f"Hanya {', '.join(ALLOWED_EXTENSIONS)} yang diperbolehkan.")

                # Tentukan resource_type untuk Cloudinary
                file_extension = os.path.splitext(row)[1].lower()
                resource_type = "image" if file_extension in {'.jpeg', '.jpg', '.png'} else "raw"

                # Tambahkan ekstensi pada public_id
                filename_with_extension = f"{cloudinary_folder}{file_extension}"

                # Proses unggahan
                upload_result = cloudinary.uploader.upload(
                    f'{folder_name}/{row}',
                    public_id=filename_with_extension,
                    resource_type=resource_type
                )

                # Simpan URL ke database
                if select_query:
                    select_query.DocLapor = upload_result['secure_url']
                    db.session.commit()
                    logger.info(f"File berhasil diunggah dan disimpan: {upload_result['secure_url']}")

                # Hapus file lokal setelah diunggah
                os.remove(f'{folder_name}/{row}')
                logger.info(f"File lokal dihapus: {row}")

            # Kirim notifikasi sukses
            notification_data = {
                "notification": {
                    "title": appName,
                    "body": f"File untuk {select_query.NamaBadan} berhasil diunggah.",
                    "priority": "high",
                    "icon": appFrontWebLogo,
                    "click_action": f"{appFrontWebUrl()}#/admin/pelaporan",
                },
                "data": {
                    "type": "doc_lapor_upload_finish",
                    "page": "pelaporan",
                    "doc_lapor": upload_result['secure_url'],
                    "id": select_query.PelaporanID
                }
            }
            sendNotificationNative(data_user.DeviceId, notification_data)

            return success_create({})

        except Exception as e:
            # Kirim notifikasi jika gagal
            notification_data = {
                "notification": {
                    "title": appName,
                    "body": f"Pengunggahan file gagal untuk {select_query.NamaBadan}.",
                    "priority": "high",
                    "icon": appFrontWebLogo,
                    "click_action": f"{appFrontWebUrl()}#/admin/pelaporan",
                },
                "data": {
                    "type": "doc_lapor_upload_failed",
                    "page": "pelaporan",
                    "id": select_query.PelaporanID
                }
            }
            sendNotificationNative(data_user.DeviceId, notification_data)
            db.session.rollback()
            logger.error(e)
            return failed_create({"error": str(e)})

class TaskDeleteDocLapor(Resource):
    def post(self, *args, **kwargs):
        data_par = json.loads(request.data.decode())
        path = data_par['path']

        try:
            folder = path.split('/')[-1]
            get_public_id = folder.rsplit('.', 1)[0]
            origin = request.headers.get('Origin')
            origin = origin.replace('http://', '').replace('https://', '') + '/' if origin else ''
            delete_doc = cloudinary.uploader.destroy('DocLapor/' + origin + get_public_id)
            return success_delete({})
        except Exception as e:
            db.session.rollback()
            logger.error(e)
            return failed_delete({})