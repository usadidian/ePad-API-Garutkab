import hashlib
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import unquote

from flasgger import swag_from
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt
import yagmail
from flask import jsonify, make_response, request
from flask_restful import Resource, abort, reqparse
from multiprocessing.context import Process

from sqlalchemy.sql.elements import or_

from config.api_message import failed_update, apikey_expired, failed_authentication
from config.config import jwt_secretkey, jwt_token_exp_min, appName, appFrontWebLogo, appFrontWebUrl, jwt_otp_exp_min, \
    appFrontWebUrlWp, oauth2_clientid, appFrontWebUrlExecutive
from config.database import db
from config.helper import logger, checkIsEmail, generateOTP, encrypt_token, decrypt_token, checkIsUserId, checkIsPhone
from controller.notifications.email_session import emailSendOtp, emailSendOtpMobile, emailSendOtpForgotPwd
from controller.notifications.fcm_session import sendNotificationNative
from controller.notifications.notifications import Notifications
from controller.task.task_bridge import GoToTaskNotificationSendToAll
from controller.tblGroupUser import tblGroupUser
from controller.tblUPTOpsen import tblUPTOpsen
from controller.tblUser import tblUser


class UserLogin(Resource):
    @swag_from({
        'tags': ['Authentication'],
        'summary': 'User Login',
        'description': 'Melakukan login dan mendapatkan API key untuk akses endpoint lainnya.',
        'consumes': ['multipart/form-data'],
        'parameters': [
            {
                'name': 'userid',
                'in': 'formData',
                'type': 'string',
                'required': True,
                'example': 'epad'
            },
            {
                'name': 'password',
                'in': 'formData',
                'type': 'string',
                'required': True,
                'example': '12345678!aBx'
            }
        ],
        'responses': {
            200: {
                'description': 'Login berhasil',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'status_code': {'type': 'integer', 'example': 1},
                                'message': {'type': 'string', 'example': 'OK'},
                                'data': {
                                    'type': 'object',
                                    'properties': {
                                        'userid': {'type': 'string', 'example': 'epad'},
                                        'nama_user': {'type': 'string', 'example': 'epad'},
                                        'APIkey': {'type': 'string', 'example': 'eyJ0eXAiOiJKV1QiLCJ...'}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            401: {
                'description': 'Login gagal (username/password salah)'
            }
        }
    })
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('phone', type=str)
        parser.add_argument('userid', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str, required=True, help="password cannot be blank!")
        parser.add_argument('deviceid', type=str)
        args = parser.parse_args()
        logger.info(f"========================= LOGIN : TRIED by {args['email']} from domain {request.base_url}")

        user_check = tblUser.query \
            .filter_by(password=hashlib.md5(args['password'].encode()).hexdigest())
        if args['email']:
            if not checkIsEmail(args['email']):
                return abort(make_response(jsonify({
                    'status_code': 212,
                    'message': 'Login gagal, mohon periksa userid dan password',
                    'data': {}
                }), 500))
            user_check = user_check.filter_by(Email=args['email'])
        if args['userid']:
            if not checkIsUserId(args['userid']):
                return abort(make_response(jsonify({
                    'status_code': 213,
                    'message': 'Login gagal, mohon periksa userid dan password',
                    'data': {}
                }), 500))
            user_check = user_check.filter_by(UID=args['userid'])
        if args['phone']:
            if not checkIsPhone( args['phone'] ):
                return abort( make_response( jsonify( {
                'status_code': 214,
                'message': 'Login gagal, mohon periksa userid dan password',
                'data': {}
            } ), 500 ) )
            user_check = user_check.filter_by(Phone=args['phone'])

        user_check = user_check.first()
        if user_check:
            query = db.session.query(tblUPTOpsen.KotaPropID).filter(
                tblUPTOpsen.UPTID == user_check.WapuID
            ).first()
            kotaprop_id = str(query[0]) if query else None

            payloads = {
                'exp': datetime.now() + jwt_token_exp_min,
                'UserId': user_check.UserId,
                'UID': user_check.UID,
                'WapuID': user_check.WapuID,
                'GroupId': user_check.GroupId,
                'code_group': user_check.code_group,
                'PegawaiID': user_check.PegawaiID,
                'IsAdmin': user_check.Group.IsAdmin,
                'IsPendaftaran': user_check.Group.IsPendaftaran,
                'IsPendataan': user_check.Group.IsPendataan,
                'IsPenetapan': user_check.Group.IsPenetapan,
                'IsPembayaran': user_check.Group.IsPembayaran,
                'IsPenyetoran': user_check.Group.IsPenyetoran,
                'IsIntegrasi': user_check.Group.IsIntegrasi,
                'IsWP': user_check.Group.IsWP,
                'KotaPropID': kotaprop_id or ''
            }
            apikey = jwt.encode(payloads, jwt_secretkey, algorithm='HS256')
            apikeystr = apikey.decode("UTF-8")
            user_check.APIKey = apikeystr
            if args['deviceid']:
                user_check.DeviceId = args['deviceid']
            db.session.commit()
            logger.info(
                f"========================= LOGIN : SUCCESSED by {args['email']} from domain {request.base_url}")

            response_data = {
                # 'Phone': user_check.Phone,
                # 'Avatar': user_check.Avatar,
                # 'email': user_check.Email,
                'userid': user_check.UID,
                'nama_user': user_check.nama_user,
                # 'wapuid': user_check.WapuID or None,
                # 'kotapropid': kotaprop_id or '',
                'APIkey': apikeystr,
            }

            # if WP do login here
            if user_check.Group.IsWP == 1 and request.origin + "/" != appFrontWebUrlWp:
                response_data['url_wp'] = f'{appFrontWebUrlWp}'
                return abort(make_response(jsonify({
                    'status_code': 217,
                    'message': f'Anda adalah seorang Wajib Pajak, silahkan melakukan login di web WP : {appFrontWebUrlWp} atau silahkan login melalui mobile app WP ',
                    'data': response_data
                }), 500))

            # if Executive do login here
            if user_check.Group.IsExecutive == 1 and request.origin + "/" != appFrontWebUrlExecutive:
                response_data['url'] = f'{appFrontWebUrlExecutive}?access='
                return abort(make_response(jsonify({
                    'status_code': 217,
                    'message': f'Anda adalah seorang Eksekutif Epad, silahkan melakukan login di web Eksekutif : {appFrontWebUrlExecutive}.',
                    'data': response_data
                }), 500))

            return jsonify({'status_code': 1, 'message': 'OK', 'data': response_data})
        else:
            logger.error(
                f"========================= LOGIN : FAILED by {args['email']} from domain {request.base_url}")
            return abort(make_response(jsonify({
                'status_code': 212,
                'message': 'Login gagal, mohon periksa userid dan password',
                'data': {}
            }), 500))
        # except Exception as e:
        #     # db.session.rollback()
        #     logger.error(e)
        #     logger.error(f"========================= LOGIN : FAILED by {args['email']} from domain {request.base_url}")
        #     return abort(make_response(jsonify({
        #         'status_code': 212,
        #         'message': 'Login gagal, mohon periksa email dan password',
        #         'data': {}
        #     }), 500))


class UpdateDevice(Resource):
    method_decorators = {'post': [tblUser.auth_apikey]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('device', type=str, required=True, help="device not defined!")
        args = parser.parse_args()
        try:
            # logger.info(args['device'])
            new_device = args['device']
            data_user = kwargs['user_info']
            old_device = data_user.DeviceId
            # logger.info(new_device)
            if old_device:
                # logger.info('OLD DEVICE ADA')
                if old_device != new_device:
                    notifBody = "Akun anda telah digunakan pada perangkat lain, mohon untuk login kembali."
                    notification_data = {
                        "notification": {
                            "title": appName,
                            "body": notifBody,
                            "priority": "high",
                            "icon": appFrontWebLogo,
                            "click_action": f"{appFrontWebUrl()}#/login",
                        },
                        "data": {
                            "type": "session_exp"
                        }
                    }
                    # sendNotificationToSingleDevice(old_device, notification_data)
                    sendNotif = sendNotificationNative(old_device, notification_data)
                    # if sendNotif.status_code == 200:
                    #     add_notif = Notifications(
                    #         UserId=data_user.UserId,
                    #         id_notificationsType=1,
                    #         title="Sesi Berakhir",
                    #         description=notifBody,
                    #         created_by="system"
                    #     )
                    #     db.session.add(add_notif)
                    #     db.session.commit()

            data_user.DeviceId = new_device
            db.session.commit()

            # email_admin_dev = "amry.maftuh85@gmail.com"
            # if data_user.Email != email_admin_dev:
            #     dataAdmin = tblUser.query.filter_by(Email=email_admin_dev).first()
            #     data_to_notif_all = {
            #         "body": {
            #             "notification": {
            #                 "title": appName,
            #                 "body": f"{data_user.nama_user} sedang aktif di epad ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}).",
            #                 "priority": "high",
            #                 "icon": appFrontWebLogo,
            #                 "click_action": f"{appFrontWebUrl()}",
            #             },
            #             "name": data_user.nama_user,
            #             "avatar": data_user.Avatar,
            #             "date_joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            #             "device": dataAdmin.DeviceId,
            #         },
            #         "headers": {
            #             "kjtbdg": 'kjtbdgyess'
            #         }
            #     }
            #     thread = Process(target=GoToTaskNotificationSendToAll, args=(data_to_notif_all,))
            #     thread.daemon = True
            #     thread.start()

            return jsonify({'status_code': 1, 'message': 'DEVICE UPDATED SUCCESS!'})
        except Exception as e:
            logger.error(e)
            return failed_update({})


class CheckSession(Resource):
    method_decorators = {'post': [tblUser.auth_apikey]}

    def post(self, *args, **kwargs):
        try:
            apikey_request_enc = request.headers.get('APIKey')
            APIKEY_decode = jwt.decode(apikey_request_enc, jwt_secretkey, algorithms=['HS256'])
            usersId = APIKEY_decode["UserId"]
        except jwt.ExpiredSignatureError as a:
            print(a)
            return apikey_expired()
        except Exception as e:
            print(e)
            return failed_authentication()

        # CEK APIKEY KE TABEL USER
        cek_apikey_to_table = tblUser.query.filter_by(UserId=usersId, APIKey=apikey_request_enc).first()
        if cek_apikey_to_table:
            return jsonify({'status_code': 1, 'message': 'SESSION OK', 'data': {
                'Phone': cek_apikey_to_table.Phone,
                'Avatar': cek_apikey_to_table.Avatar,
                'email': cek_apikey_to_table.Email,
                'nama_user': cek_apikey_to_table.nama_user,
                'wapuid': cek_apikey_to_table.WapuID,
                'APIkey': apikey_request_enc
            }})
        else:
            return abort(make_response(jsonify({
                'status_code': 8001,
                'message': 'SESSION FAILED',
            }), 401))

# ===========================================


class UserLoginWPO(Resource):
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('phone', type=str)
        parser.add_argument('userid', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str, required=True, help="password cannot be blank!")
        parser.add_argument('deviceid', type=str)
        args = parser.parse_args()
        logger.info(f"========================= LOGIN-WPO : TRIED by {args['email']} from domain {request.base_url}")

        if args['email']:
            if not checkIsEmail(args['email']):
                return abort(make_response(jsonify({
                    'status_code': 212,
                    'message': 'Login gagal, mohon periksa userid dan password',
                    'data': {}
                }), 500))
            user_check = tblUser.query.filter(
                tblUser.pwd == hashlib.md5(args['password'].encode()).hexdigest(),
            )
            user_check = user_check.filter(tblUser.Email == args['email'])
        if args['userid']:
            user_check = user_check.filter(tblUser.UID == args['userid'])
        if args['phone']:
            user_check = user_check.filter(tblUser.Phone == args['phone'])

        user_check = user_check.first()
        if user_check:
            # if user_check.Group.IsWP != 1:
            #     return abort(make_response(jsonify({
            #         'status_code': 212,
            #         'message': 'Login gagal, anda adalah petugas pajak',
            #         'data': {}
            #     }), 500))

            payloads = {
                'exp': datetime.now() + jwt_token_exp_min,
                'UserId': user_check.UserId,
                'UID': user_check.UID,
                # 'WPID': user_check.WPID,
                # 'ObyekBadanNo': user_check.ObyekBadanNo,
                'GroupId': user_check.GroupId,
                'code_group': user_check.code_group,
                'IsWP': user_check.Group.IsWP,
            }
            apikey = jwt.encode(payloads, jwt_secretkey, algorithm='HS256')
            apikeystr = apikey.decode("UTF-8")
            # update_apikey = tblUser.query.filter_by(UserId=user_check.UserId, APIKey=user_check.APIKey).first()
            # update_apikey.APIKey = apikeystr
            user_check.APIKey = apikeystr
            if args['deviceid']:
                user_check.DeviceId = args['deviceid']
            db.session.commit()
            logger.info(
                f"========================= LOGIN-WPO : SUCCESSED by {args['email']} from domain {request.base_url}")
            return jsonify({'status_code': 1, 'message': 'OK', 'data': {
                'Phone': user_check.Phone,
                'Avatar': user_check.Avatar or "",
                'Email': user_check.Email,
                'nama_user': user_check.nama_user,
                'wapuid': user_check.WapuID,
                'APIkey': apikeystr,
                # 'wpdata': {
                #     'WPID': user_check.WPID,
                #     'ObyekBadanNo': user_check.ObyekBadanNo,
                #     'NamaPemilik': user_check.NamaPemilik,
                #     'NamaBadan': user_check.NamaBadan,
                #     'AlamatBadan': user_check.AlamatBadan,
                #     'nama_user': user_check.nama_user
                # }
            }})
        else:
            logger.error(
                f"========================= LOGIN-WPO : FAILED by {args['email']} from domain {request.base_url}")
            return abort(make_response(jsonify({
                'status_code': 212,
                'message': 'Login gagal, mohon periksa userid dan password',
                'data': {}
            }), 500))
        # except Exception as e:
        #     # db.session.rollback()
        #     logger.error(e)
        #     logger.error(f"========================= LOGIN-WPO : FAILED by {args['email']} from domain {request.base_url}")
        #     return abort(make_response(jsonify({
        #         'status_code': 212,
        #         'message': 'Login gagal, mohon periksa email dan password',
        #         'data': {}
        #     }), 500))


class RegisterWPO(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help="email cannot be blank!")
        parser.add_argument('password', type=str, required=True, help="password cannot be blank!")
        # parser.add_argument('password2', type=str, required=True, help="password cannot be blank!")
        parser.add_argument('phone', type=str)
        parser.add_argument('device', type=str)
        args = parser.parse_args()
        logger.info(f"========================= PRE-REGISTER : TRIED by {args['email']} from domain {request.base_url}")

        if not checkIsEmail(args['email']):
            return abort(make_response(jsonify({
                'status_code': 212,
                'message': 'pendaftaran gagal, mohon isi email dengan benar',
                'data': {}
            }), 500))

        # if args['password'] != args['password2']:
        #     return abort(make_response(jsonify({
        #         'status_code': 213,
        #         'message': 'Pendafataran Gagal. Password tidak sesuai.'
        #     }), 500))

        user_check = tblUser.query.filter(or_(tblUser.Email == args['email'])).first()
        if user_check:
            return abort(make_response(jsonify({
                'status_code': 213,
                'message': 'Pendafataran Gagal. Email atau Nomor Ponsel sudah terdaftar, silahkan melakukan login'
            }), 500))
        genOTP = generateOTP(4)
        payloads = {
            'hash': hashlib.md5(args['password'].encode()).hexdigest(),
            'exp': datetime.now() + jwt_otp_exp_min,
            'email': args['email'],
            'phone': args['phone'],
            'device': args['device'],
            'code': genOTP
        }
        apikey = jwt.encode(payloads, jwt_secretkey, algorithm='HS256')
        apikeystr = apikey.decode("UTF-8")
        apikeystr_secure = encrypt_token(apikeystr)
        emailSendOtpMobile(args['email'], genOTP)
        logger.info(
            f"========================= PRE-REGISTER SEND OTP WPO TO {args['email']} from domain {request.base_url}")
        return jsonify({'status_code': 1, 'message': 'OK', 'data': {
            'APIkey': apikeystr_secure,
        }})


class UserLoginByGoogleWP(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', type=str)
        parser.add_argument('id_token', type=str)
        parser.add_argument('deviceid', type=str)
        args = parser.parse_args()

        #CHECK TO GOOGLE
        google_user = None
        try:
            # print(args['access_token'])
            # print(args['id_token'])
            idinfo = id_token.verify_oauth2_token(args['id_token'], requests.Request(), oauth2_clientid)
            # print(idinfo)
            userid = idinfo['sub']
            logger.info(f"========================= LOGIN-WPO-BY-GOOGLE: TRIED by {idinfo['email']}")
            google_user = idinfo
        except ValueError:
            logger.error(f"========================= LOGIN-WPO-BY-GOOGLE: FAILED AUTHENTICATION WITH GOOGLE")
            return abort(make_response(jsonify({
                'status_code': 212,
                'message': 'Login by google failed',
                'data': {}
            }), 500))

        # CHECK TO DB
        user_check = tblUser.query.filter_by(Email=google_user['email']).first()
        if user_check:
            # if user_check.Group.IsWP != 1:
            #     logger.error(f"========================= LOGIN-WPO-BY-GOOGLE: NOT MEMBER OF WP!")
            #     return abort(make_response(jsonify({
            #         'status_code': 212,
            #         'message': 'Login gagal, anda adalah petugas pajak',
            #         'data': {}
            #     }), 500))

            # Update field
            if not user_check.nama_user:
                user_check.nama_user = google_user['name']
            if not user_check.Avatar:
                user_check.Avatar = google_user['picture']

            payloads = {
                'exp': datetime.now() + jwt_token_exp_min,
                'UserId': user_check.UserId,
                'UID': user_check.UID,
                'GroupId': user_check.GroupId,
                'code_group': user_check.code_group,
                'IsWP': user_check.Group.IsWP,
            }
            apikey = jwt.encode(payloads, jwt_secretkey, algorithm='HS256')
            apikeystr = apikey.decode("UTF-8")
            user_check.APIKey = apikeystr
            if args['deviceid']:
                user_check.DeviceId = args['deviceid']
            db.session.commit()
            logger.info(
                f"========================= LOGIN-WPO-BY-GOOGLE : SUCCESSED by {google_user['email']}")
            return jsonify({'status_code': 1, 'message': 'OK', 'data': {
                'Phone': user_check.Phone,
                'Avatar': user_check.Avatar or "",
                'Email': user_check.Email,
                'nama_user': user_check.nama_user,
                'APIkey': apikeystr,
            }})
        else:
            # return abort(make_response(jsonify({
            #     'status_code': 212,
            #     'message': 'Lanjut Daftar?',
            #     'data': {}
            # }), 500))
            # AUTO REGISTER NEW USER
            result = insertNewUserWP(google_user)
            logger.info(
                f"========================= REGISTER-WPO-BY-GOOGLE SUCCESS by {google_user['email']}")
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})


def insertNewUserWP(data):
    groupId = tblGroupUser.query.filter_by(IsWP=1).first()
    nama_user = data['name'] if 'name' in data else data["email"]
    uid = data["email"].split("@")[0]
    pwd = data["hash"] if 'hash' in data else 'generated_by_google'
    avatar = data['picture'] if 'picture' in data else None
    addNewUser = tblUser(
        code_group=groupId.code_group,
        GroupId=groupId.GroupId,
        UserUpd=uid,
        DateUpd=datetime.now(),
        UID=uid,
        nama_user=nama_user,
        pwd=pwd,
        flag_active='1',
        date_exp='2024-01-01 00:00:00.000',
        user_level='60',
        Email=data["email"],
        Phone=data["phone"] if 'phone' in data else None,
        DeviceId=data["device"] if 'device' in data else None,
        Avatar=avatar
    )
    db.session.add(addNewUser)
    db.session.commit()

    # NOTIF TO ADMINS GROUP
    list_admin = tblUser.query.join(tblGroupUser).filter(tblGroupUser.IsAdmin == 1).all()
    for row in list_admin:
        if row.DeviceId:
            notifBody = f'Registrasi User Baru ({data["email"]}) Sukses'
            notification_data = {
                "notification": {
                    "title": appName,
                    "body": notifBody,
                    "priority": "high",
                    "icon": appFrontWebLogo,
                    "click_action": f"{appFrontWebUrl()}#/admin/users",
                },
                "data": {
                    "type": "new_reg_wp",
                    "page": "users"
                }
            }
            sendNotif = sendNotificationNative(row.DeviceId, notification_data)
            if sendNotif.status_code == 200:
                add_notif = Notifications(
                    UserId=row.UserId,
                    id_notificationsType=1,
                    title="Registrasi User Baru",
                    description=notifBody,
                    created_by="system"
                )
                db.session.add(add_notif)
                db.session.commit()

    if not addNewUser.UserId:
        logger.error('insert new user to db failed')
        return abort(make_response(jsonify({
            'status_code': 212,
            'message': 'Terjadi Kesalahan!',
            'data': {}
        }), 500))

    apikeyResponse = {
        'exp': datetime.now() + jwt_token_exp_min,
        'UserId': addNewUser.UserId,
        'UID': addNewUser.UID,
        'WPID': '',
        'ObyekBadanNo': '',
        'GroupId': addNewUser.GroupId,
        'code_group': addNewUser.code_group,
        'IsWP': addNewUser.Group.IsWP,
    }
    apikey = jwt.encode(apikeyResponse, jwt_secretkey, algorithm='HS256')
    apikeystr = apikey.decode("UTF-8")
    addNewUser.APIKey = apikeystr
    db.session.commit()
    return {
                'Phone': addNewUser.Phone,
                'Email': addNewUser.Email,
                'nama_user': addNewUser.nama_user,
                'Avatar': addNewUser.Avatar or "",
                'APIkey': apikeystr
            }


class AuthOtpWPO(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('otp', type=str, required=True, help="otp cannot be blank!")
        args = parser.parse_args()
        logger.info(f"========================= REGISTER-OTP : TRIED from domain {request.base_url}")
        try:
            apikey_request_enc = request.headers.get('APIKey')
            if apikey_request_enc is None:
                logger.error(f'APIKEY GAK ADA... (APIKEY GAK ADA DI HEADER REQUEST)')
                return abort(make_response(jsonify({
                    'status_code': 212,
                    'message': 'Terjadi Kesalahan!',
                    'data': {}
                }), 500))

            apikey_request_jwt = decrypt_token(apikey_request_enc)
            APIKEY_decode = jwt.decode(apikey_request_jwt, jwt_secretkey, algorithms=['HS256'])
            otp = APIKEY_decode["code"]
            if args['otp'] != otp:
                logger.error('OTP tidak valid!')
                return abort(make_response(jsonify({
                    'status_code': 212,
                    'message': 'OTP tidak valid!',
                    'data': {}
                }), 500))

            # groupId = tblGroupUser.query.filter_by(IsWP=1).first()
            # addNewUser = tblUser(
            #     code_group=groupId.code_group,
            #     GroupId=groupId.GroupId,
            #     UserUpd=APIKEY_decode["email"].split("@")[0],
            #     DateUpd=datetime.now(),
            #     UID=APIKEY_decode["email"].split("@")[0],
            #     nama_user=APIKEY_decode["email"],
            #     password=APIKEY_decode["hash"],
            #     flag_active='1',
            #     date_exp='2024-01-01 00:00:00.000',
            #     user_level='60',
            #     Email=APIKEY_decode["email"],
            #     Phone=APIKEY_decode["phone"] or "",
            #     DeviceId=APIKEY_decode["device"] or "",
            # )
            # db.session.add(addNewUser)
            # db.session.commit()
            #
            # # NOTIF TO ADMINS GROUP
            # list_admin = tblUser.query.join(tblGroupUser).filter(tblGroupUser.IsAdmin == 1).all()
            # for row in list_admin:
            #     if row.DeviceId:
            #         notifBody = f'Registrasi User Baru ({APIKEY_decode["email"]}) Sukses'
            #         notification_data = {
            #             "notification": {
            #                 "title": appName,
            #                 "body": notifBody,
            #                 "priority": "high",
            #                 "icon": appFrontWebLogo,
            #                 "click_action": f"{appFrontWebUrl()}#/admin/users",
            #             },
            #             "data": {
            #                 "type": "new_reg_wp",
            #                 "page": "users"
            #             }
            #         }
            #         sendNotif = sendNotificationNative(row.DeviceId, notification_data)
            #         if sendNotif.status_code == 200:
            #             add_notif = Notifications(
            #                 UserId=row.UserId,
            #                 id_notificationsType=1,
            #                 title="Registrasi User Baru",
            #                 description=notifBody,
            #                 created_by="system"
            #             )
            #             db.session.add(add_notif)
            #             db.session.commit()
            #
            # if not addNewUser.UserId:
            #     logger.error('insert new user to db failed')
            #     return abort(make_response(jsonify({
            #         'status_code': 212,
            #         'message': 'Terjadi Kesalahan!',
            #         'data': {}
            #     }), 500))
            # apikeyResponse = {
            #     'exp': datetime.now() + jwt_token_exp_min,
            #     'UserId': addNewUser.UserId,
            #     'UID': addNewUser.UID,
            #     'WPID': '',
            #     'ObyekBadanNo': '',
            #     'GroupId': addNewUser.GroupId,
            #     'code_group': addNewUser.code_group,
            # }
            # apikey = jwt.encode(apikeyResponse, jwt_secretkey, algorithm='HS256')
            # apikeystr = apikey.decode("UTF-8")
            # addNewUser.APIKey = apikeystr
            # db.session.commit()

            result = insertNewUserWP(APIKEY_decode)
            logger.info(
                f"========================= REGISTER-OTP SUCCESS from domain {request.base_url}")
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})
        except jwt.ExpiredSignatureError as a:
            logger.error(a)
            return apikey_expired()
        except Exception as e:
            logger.error(e)
            return failed_authentication()


class UserLogout(Resource):
    method_decorators = {'post': [tblUser.auth_apikey]}

    def post(self, *args, **kwargs):
        email = kwargs['user_info'].Email
        try:
            logger.info(f"========================= LOGOUT : TRIED by {email} from domain {request.base_url}")
            kwargs['user_info'].APIKey = None
            db.session.commit()
            logger.info(
                f"========================= LOGOUT : SUCCESSED by {email} from domain {request.base_url}")
            return jsonify({'status_code': 1, 'message': 'OK', 'data': {}})
        except Exception as e:
            db.session.rollback()
            logger.error(e)
            logger.error(f"========================= LOGOUT : FAILED by {email} from domain {request.base_url}")
            return abort(make_response(jsonify({
                'status_code': 212,
                'message': 'Logout Gagal',
                'data': {}
            }), 500))


class ChangePassword(Resource):
    method_decorators = {'post': [tblUser.auth_apikey]}

    def post(self, *args, **kwargs):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('old-pwd', type=str, required=True, help="old-pwd not defined!")
            parser.add_argument('new-pwd', type=str, required=True, help="new-pwd not defined!")
            args = parser.parse_args()
            # logger.info(args['device'])
            oldPwd = args['old-pwd']
            newPwd = args['new-pwd']
            data_user = kwargs['user_info']
            apikey_request_enc = request.headers.get('APIKey')
            user_check = tblUser.query.filter_by(
                pwd=hashlib.md5(oldPwd.encode()).hexdigest(),
                Email=data_user.Email,
                APIKey=apikey_request_enc
            ).first()
        except Exception as e:
            logger.error(e)
            return failed_update({})

        if not user_check:
            return failed_update({})

        user_check.pwd = hashlib.md5(newPwd.encode()).hexdigest()
        db.session.commit()
        return jsonify({'status_code': 1, 'message': 'Password Changed!'})


class ForgotCheckEmail(Resource):
    def post(self, *args, **kwargs):
        from flask import Response
        if not request.headers.get('Origin'):
            return Response(
                "Bad Request",
                status=400,
            )
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('email', type=str, required=True)
            args = parser.parse_args()
            email = args['email']
            user_check = tblUser.query.filter_by(
                Email=email
            ).first()
        except Exception as e:
            logger.error(e)
            return failed_update({})

        if not user_check:
            return failed_update({})

        Origin = request.headers.get('Origin')
        genOTP = generateOTP(6)
        now = datetime.now()
        id = str(uuid.uuid4())
        payloads = {
            'exp': now + timedelta(minutes=5),
            'origin': Origin,
            'email': email,
            'code': genOTP,
            'id': id
        }
        reset_token = jwt.encode(payloads, jwt_secretkey, algorithm='HS256')
        reset_token_str = reset_token.decode("UTF-8")
        reset_token_str_secure = encrypt_token(reset_token_str)
        dataToCompose = {
            'email': email,
            'code': genOTP,
            'origin': Origin,
            'datetime': now.strftime("%d %B %Y") + ' Jam ' + now.strftime("%H:%M:%S")
        }
        emailSendOtpForgotPwd(dataToCompose)
        # generateLink = f'{Origin}/reset-pwd?key={reset_token_str_secure}'
        return jsonify({'status_code': 1, 'message': 'Link Send to Email!', 'data': {
            'token': reset_token_str_secure, 'id': id
        }})


class ForgotCheckOtp(Resource):
    def post(self, *args, **kwargs):
        from flask import Response
        Origin = request.headers.get('Origin')
        if not Origin:
            return Response(
                "Bad Request",
                status=400,
            )
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('otp', type=int, required=True)
            parser.add_argument('token', type=str, required=True)
            args = parser.parse_args()
            otp = args['otp']
            token = args['token']

            apikey_request_enc = token
            if apikey_request_enc is None:
                logger.error(f'VALID OTP FORGOT PWD TOKEN GAK ADA...')
                return abort(make_response(jsonify({
                    'message': 'Terjadi Kesalahan!'
                }), 500))

            apikey_request_jwt = decrypt_token(apikey_request_enc)
            APIKEY_decode = jwt.decode(apikey_request_jwt, jwt_secretkey, algorithms=['HS256'])

            if APIKEY_decode['origin'] != Origin:
                logger.error('origin FORGOT PWD tidak valid!')
                return abort(make_response(jsonify({
                    'message': 'Terjadi Kesalahan!'
                }), 500))

            if otp != int(APIKEY_decode["code"]):
                logger.error('OTP FORGOT PWD tidak valid!')
                return abort(make_response(jsonify({
                    'message': 'OTP tidak valid!'
                }), 500))

            email = APIKEY_decode["email"]
            user_check = tblUser.query.filter_by(
                Email=email
            ).first()
            if not user_check:
                return abort(make_response(jsonify({
                    'message': 'Terjadi Kesalahan!'
                }), 500))

            now = datetime.now()
            id = str(uuid.uuid4())
            tokenNew = {
                'exp': now + timedelta(minutes=5),
                'origin': Origin,
                'email': email,
                'id': id
            }
            reset_token = jwt.encode(tokenNew, jwt_secretkey, algorithm='HS256')
            reset_token_str = reset_token.decode("UTF-8")
            reset_token_str_secure = encrypt_token(reset_token_str)
            return jsonify({'status_code': 1, 'message': 'OTP Valid!', 'data': {
                'token': reset_token_str_secure, 'id': id
            }})

        except jwt.ExpiredSignatureError as a:
            print(a)
            return apikey_expired()

        except Exception as e:
            logger.error(e)
            return failed_update({})


class ResetPwd(Resource):
    def post(self, *args, **kwargs):
        from flask import Response
        Origin = request.headers.get('Origin')
        if not Origin:
            return Response(
                "Bad Request",
                status=400,
            )
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('new_pwd', type=str, required=True)
            parser.add_argument('id', type=str, required=True)
            args = parser.parse_args()
            pwd = args['new_pwd']
            id_token = args['id']

            apikey_request_enc = request.headers.get('token')
            if apikey_request_enc is None:
                logger.error(f'RESET PWD TOKEN GAK ADA...')
                return abort(make_response(jsonify({
                    'message': 'Terjadi Kesalahan!'
                }), 500))

            apikey_request_jwt = decrypt_token(apikey_request_enc)
            APIKEY_decode = jwt.decode(apikey_request_jwt, jwt_secretkey, algorithms=['HS256'])

            if APIKEY_decode['origin'] != Origin:
                logger.error('origin RESET PWD tidak valid!')
                return abort(make_response(jsonify({
                    'message': 'Terjadi Kesalahan!'
                }), 500))

            if id_token != APIKEY_decode["id"]:
                logger.error('ID RESET PWD tidak valid!')
                return abort(make_response(jsonify({
                    'message': 'Terjadi Kesalahan!'
                }), 500))

            if len(pwd) < 6:
                logger.error('ID RESET PWD tidak valid!')
                return abort(make_response(jsonify({
                    'message': 'Minimum length of password is 6 character!'
                }), 500))

            email = APIKEY_decode["email"]
            user_check = tblUser.query.filter_by(
                Email=email
            ).first()
            if not user_check:
                return abort(make_response(jsonify({
                    'message': 'Terjadi Kesalahan!'
                }), 500))

            user_check.pwd = hashlib.md5(pwd.encode()).hexdigest()
            db.session.commit()

            return jsonify({'status_code': 1, 'message': 'Password Changed!'})

        except jwt.ExpiredSignatureError as a:
            print(a)
            return apikey_expired()

        except Exception as e:
            logger.error(e)
            return failed_update({})


class ForgotCheckOtpResetPwd(Resource):
    def post(self, *args, **kwargs):
        from flask import Response
        Origin = request.headers.get('Origin')
        if not Origin:
            return Response(
                "Bad Request",
                status=400,
            )
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('otp', type=int, required=True)
            parser.add_argument('new_pwd', type=str, required=True)
            parser.add_argument('id', type=str, required=True)
            parser.add_argument('email', type=str, required=True)
            args = parser.parse_args()
            otp = args['otp']
            pwd = args['new_pwd']
            email = args['email']
            id_token = args['id']
            token = request.headers.get('token')
            if token is None:
                logger.error(f'VALID OTP FORGOT PWD TOKEN GAK ADA...')
                return abort(make_response(jsonify({
                    'message': 'Terjadi Kesalahan!'
                }), 500))

            apikey_request_jwt = decrypt_token(token)
            APIKEY_decode = jwt.decode(apikey_request_jwt, jwt_secretkey, algorithms=['HS256'])

            if APIKEY_decode['origin'] != Origin:
                logger.error('origin FORGOT PWD tidak valid!')
                return abort(make_response(jsonify({
                    'message': 'Terjadi Kesalahan!'
                }), 500))

            if otp != int(APIKEY_decode["code"]):
                logger.error('OTP FORGOT PWD tidak valid!')
                return abort(make_response(jsonify({
                    'message': 'OTP tidak valid!'
                }), 500))

            if id_token != APIKEY_decode["id"]:
                logger.error('ID RESET PWD tidak valid!')
                return abort(make_response(jsonify({
                    'message': 'Terjadi Kesalahan!'
                }), 500))

            if email != APIKEY_decode["email"]:
                logger.error('EMAIL RESET PWD tidak valid!')
                return abort(make_response(jsonify({
                    'message': 'Terjadi Kesalahan!'
                }), 500))

            if len(pwd) < 6:
                logger.error('ID RESET PWD tidak valid!')
                return abort(make_response(jsonify({
                    'message': 'Minimum length of password is 6 character!'
                }), 500))

            email_args = APIKEY_decode["email"]
            user_check = tblUser.query.filter_by(
                Email=email_args
            ).first()
            if not user_check:
                return abort(make_response(jsonify({
                    'message': 'Terjadi Kesalahan!'
                }), 500))

            user_check.pwd = hashlib.md5(pwd.encode()).hexdigest()
            db.session.commit()

            return jsonify({'status_code': 1, 'message': 'Password Changed!'})

            # now = datetime.now()
            # id = str(uuid.uuid4())
            # tokenNew = {
            #     'exp': now + timedelta(minutes=5),
            #     'origin': Origin,
            #     'email': email,
            #     'id': id
            # }
            # reset_token = jwt.encode(tokenNew, jwt_secretkey, algorithm='HS256')
            # reset_token_str = reset_token.decode("UTF-8")
            # reset_token_str_secure = encrypt_token(reset_token_str)
            # return jsonify({'status_code': 1, 'message': 'OTP Valid!', 'data': {
            #     'token': reset_token_str_secure, 'id': id
            # }})

        except jwt.ExpiredSignatureError as a:
            print(a)
            return apikey_expired()

        except Exception as e:
            logger.error(e)
            return failed_update({})