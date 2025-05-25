from datetime import datetime
from functools import wraps
from urllib.parse import urlparse
import jwt
from flask import request
from sqlalchemy_serializer import SerializerMixin
from config.api_message import apikey_required, apikey_not_match, endpoint_restricted, apikey_expired, \
    failed_authentication
from config.config import jwt_secretkey
from config.database import db
from config.helper import logger
from controller.tblAkses import tblAkses
from controller.tblGroupUser import tblGroupUser
from controller.tblMenu import tblMenu
from controller.tblMenuDet import tblMenuDet
from controller.tblRole import tblRole
from controller.tblUrl import tblUrl


class tblUser(db.Model, SerializerMixin):
    serialize_rules = ('-created_by',
                       '-last_updated_by',
                       '-groupsId',
                       '-usersPwd',
                       '-usersApiKey',
                       '-usersDeviceId',
                       '-unitsId',)

    __tablename__ = 'tblUser'
    # __abstract__ = True
    UserId = db.Column(db.Integer, primary_key=True)
    UID = db.Column(db.String, nullable=False)
    # WapuID = db.Column(db.Integer, primary_key=True)
    code_group = db.Column(db.String, nullable=False)
    # PegawaiID = db.Column(db.String, nullable=True)
    nama_user = db.Column(db.String, nullable=True)
    password = db.Column(db.String, nullable=False)
    pwd = db.Column( db.String, nullable=False )
    flag_active = db.Column(db.String, nullable=False)
    date_exp = db.Column(db.String, nullable=False)
    user_level = db.Column(db.Integer, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)
    # GroupId = db.Column(db.String, nullable=True)
    APIKey = db.Column(db.Integer, nullable=True)
    DeviceId = db.Column(db.String, nullable=True)
    Email = db.Column(db.Integer, nullable=False)
    Phone = db.Column(db.String, nullable=True)
    Avatar = db.Column(db.String, nullable=True)

    last_request = db.Column(db.TIMESTAMP, nullable=True)

    GroupId = db.Column(db.Integer, db.ForeignKey('tblGroupUser.GroupId'), nullable=False)
    PegawaiID = db.Column(db.String, db.ForeignKey('MsPegawai.PegawaiID'), nullable=False)
    WapuID = db.Column(db.Integer, db.ForeignKey('MsWapu.WapuID'), nullable=False)

    wapu = db.relationship('MsWapu', foreign_keys=WapuID)
    pegawai = db.relationship('MsPegawai', foreign_keys=PegawaiID )
    Group = db.relationship('tblGroupUser')


    def auth_apikey(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            apikey_request_enc = request.headers.get('APIKey')
            if apikey_request_enc is None:
                print(f'APIKEY GAK ADA... (APIKEY GAK ADA DI HEADER REQUEST)')
                return apikey_required()
            try:
                APIKEY_decode = jwt.decode(apikey_request_enc, jwt_secretkey, algorithms=['HS256'])
                usersId = APIKEY_decode["UserId"]

                # CEK APIKEY KE TABEL USER
                cek_apikey_to_table = tblUser.query.filter_by(UserId=usersId, APIKey=apikey_request_enc).first()
                if cek_apikey_to_table is None:
                    return apikey_not_match()
                else:
                    kwargs['claim'] = APIKEY_decode
                    kwargs['user_info'] = cek_apikey_to_table
                    cek_apikey_to_table.last_request = datetime.now()
                    db.session.commit()
                    return func(*args, **kwargs)
            except jwt.ExpiredSignatureError as a:
                print(a)
                return apikey_expired()
            except Exception as e:
                print(e)
                return failed_authentication()
            # return func(*args, **kwargs)

        wrapper.__doc__ = func.__doc__
        wrapper.__name__ = func.__name__
        return wrapper

    def auth_apikey_privilege(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            apikey_request_enc = request.headers.get('APIKey')
            if apikey_request_enc:
                # apikey_request = decrypt_token(apikey_request_enc)
                # print(apikey_request)
                # if (apikey_request is None):
                #     print(f'APIKEY GAK ADA... (APIKEY GAK ADA DI HEADER REQUEST)')
                #     apikey_required()
                # else:
                # print(apikey_request)
                # print(request.base_url)
                # print(request.method)

                try:
                    APIKEY_decode = jwt.decode(apikey_request_enc, jwt_secretkey, algorithms=['HS256'])
                    usersId = APIKEY_decode["UserId"]
                    groupsId = APIKEY_decode["GroupId"]
                    checkadmin = tblGroupUser.query.filter_by(GroupId = groupsId).first()
                    print(usersId)
                    print(groupsId)
                    print(checkadmin)
                    # CEK APIKEY KE TABEL USER
                    cek_apikey_to_table = tblUser.query.filter_by(UserId=usersId, APIKey=apikey_request_enc).first()
                except jwt.ExpiredSignatureError as a:
                    print(a)
                    return apikey_expired()
                except Exception as e:
                    print(e)
                    return failed_authentication()

                if cek_apikey_to_table is None:
                    return apikey_not_match()
                else:
                    method = request.method
                    endpoint = urlparse(request.base_url).path
                    last_segment = endpoint[:endpoint.rfind('/')]
                    if last_segment:
                        endpoint = endpoint[:endpoint.rfind('/')] + '/'

                    endpoints_data = tblUrl.query.filter_by(Url=endpoint).first()
                    if endpoints_data:
                        if checkadmin.IsAdmin == 1:
                            print(checkadmin.IsAdmin)
                            check_privilege = tblRole.query.filter_by(GroupId=groupsId,
                                                                      UrlId=endpoints_data.UrlId)
                            if method == "GET":
                                check_privilege = check_privilege.filter_by(Get=True).first()
                            elif method == "POST":
                                check_privilege = check_privilege.filter_by(Post=True).first()
                            elif method == "PUT":
                                check_privilege = check_privilege.filter_by(Put=True).first()
                            else:
                                check_privilege = check_privilege.filter_by(Del=True).first()

                            if check_privilege:
                                # print(apikey_request)
                                # print(func(*args))
                                kwargs['claim'] = APIKEY_decode
                                kwargs['user_info'] = cek_apikey_to_table
                                cek_apikey_to_table.last_request = datetime.now()
                                db.session.commit()
                                logger.info(f'status: 200 | from-domain: {request.origin} | endpoint: {request.url} | method: {method} | user: {cek_apikey_to_table.Email}')
                                return func(*args, **kwargs)
                                # return apikey_request
                            else:
                                print(
                                    f'groupsId {groupsId} tidak diizinkan akses ke endpoint {endpoint} dengan method {method}!')

                                return endpoint_restricted()

                        else:
                            # Ambil semua menu yang cocok
                            check_menu_list = tblMenuDet.query.filter_by(UrlId=endpoints_data.UrlId).all()

                            # Inisialisasi variabel hasil
                            check_privileges = []

                            # Iterasi setiap menu
                            for menu in check_menu_list:
                                privileges = tblAkses.query.filter_by(GroupId=groupsId, MenuId=menu.MenuId,
                                                                      Get=True).all()
                                check_privileges.extend(privileges)

                            # Tampilkan hasil
                            if check_privileges:
                                print(f"Privileges ditemukan: {check_privileges}")
                            else:
                                print("Tidak ada privileges dengan Get=True.")

                            # Filter privilege berdasarkan method
                            check_privilege = None  # Inisialisasi
                            if method == "GET":
                                check_privilege = next((priv for priv in check_privileges if priv.Get), None)
                            elif method == "POST":
                                check_privilege = next((priv for priv in check_privileges if priv.Post), None)
                            elif method == "PUT":
                                check_privilege = next((priv for priv in check_privileges if priv.Put), None)
                            else:
                                check_privilege = next((priv for priv in check_privileges if priv.Del), None)

                            # Proses hasil
                            if check_privilege:
                                kwargs['claim'] = APIKEY_decode
                                kwargs['user_info'] = cek_apikey_to_table
                                cek_apikey_to_table.last_request = datetime.now()
                                db.session.commit()
                                logger.info(
                                    f'status: 200 | from-domain: {request.origin} | endpoint: {request.url} | method: {method} | user: {cek_apikey_to_table.Email}'
                                )
                                return func(*args, **kwargs)
                            else:
                                print(
                                    f'groupsId {groupsId} tidak diizinkan akses ke endpoint {endpoint} dengan method {method}!'
                                )
                                return endpoint_restricted()

                    else:
                        print(f'endpoints {endpoint} belum terdaftar di db!')
                        return endpoint_restricted()

            else:
                return apikey_required()
            # return func(*args, **kwargs)

        wrapper.__doc__ = func.__doc__
        wrapper.__name__ = func.__name__
        return wrapper