import hashlib
import os
from datetime import datetime
from multiprocessing import Process

from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy import or_

from config.api_message import success_reads_pagination, failed_reads, success_update, failed_update, failed_create, \
    success_create, success_delete, failed_delete, success_read, failed_read
from config.database import db
from config.helper import logger
from controller.tblGroupUser import tblGroupUser
from controller.tblUser import tblUser


class ListAll(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
            parser.add_argument('search', type=str)
            parser.add_argument('code_group', type=str)
            args = parser.parse_args()

            select_query = db.session.query(tblUser, tblGroupUser)

            select_query = select_query.join(tblGroupUser, tblGroupUser.GroupId == tblUser.GroupId) \
                # .join(tblUser.pegawai)

            if args['code_group']:
                select_query = select_query.filter(
                    tblGroupUser.code_group == args['code_group']
                )
            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(
                        tblUser.nama_user.ilike(search),
                        # tblUser.pegawai.Nama.ilike(search),
                        tblGroupUser.nama_group.ilike(search),
                        tblUser.Email.ilike(search),
                        tblUser.Phone.ilike(search),
                    )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    if args['sort'] == "nama_group":
                        sort = getattr(tblGroupUser, args['sort']).desc()
                    else:
                        sort = getattr(tblUser, args['sort']).desc()
                else:
                    if args['sort'] == "nama_group":
                        sort = getattr(tblGroupUser, args['sort']).asc()
                    else:
                        sort = getattr(tblUser, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(tblUser.DateUpd.desc())

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)
            result = []
            for row in query_execute.items:
                # print(toDict(row.tblUser))
                newObj = {
                    "userid": row.tblUser.UID,
                    "name": row.tblUser.nama_user or "",
                    "email": row.tblUser.Email or "",
                    "phone": row.tblUser.Phone or "",
                    "avatar": row.tblUser.Avatar or "",
                    "group_name": row.tblGroupUser.nama_group,
                    "code_group": row.tblGroupUser.code_group,
                    "GroupId": row.tblUser.GroupId,
                    "pegawai_nama": row.tblUser.pegawai.Nama if row.tblUser.pegawai else "",
                    "pegawai_nip": row.tblUser.pegawai.NIP if row.tblUser.pegawai else "",
                    "namabadan": row.tblUser.wapu.NamaBadan if row.tblUser.wapu else "",
                    "wapuid": row.tblUser.wapu.WapuID if row.tblUser.wapu else ""
                }
                result.append(newObj)
            return success_reads_pagination(query_execute, result)
        except Exception as e:
            print(e)
            return failed_reads({})

    def post(self, *args, **kwargs):
        try:

            parser = reqparse.RequestParser()
            parser.add_argument('userid', type=str, required=True, help="Harus diisi")
            parser.add_argument('name', type=str, required=True, help="Harus diisi")
            parser.add_argument('password', type=str, required=True, help="Harus diisi")
            parser.add_argument('email', type=str, required=True, help="Harus diisi")
            parser.add_argument('phone', type=str)
            parser.add_argument('GroupId', type=str, required=True, help="Harus diisi")
            parser.add_argument('wapuid', type=str)
            parser.add_argument('code_group', type=str, help="Harus diisi")
            parser.add_argument('pegawaiid', type=str)
            args = parser.parse_args()

            print("Received JSON payload:", request.json)

            pwd = hashlib.md5(args['password'].encode()).hexdigest()
            print(pwd)
            uid = kwargs['claim']["UID"]
            select_query = tblGroupUser.query.filter_by(GroupId=args['GroupId']).first()
            add_record = tblUser(
                UID=args['userid'] if args['userid'] else '',
                nama_user=args['name'] if args['name'] else '',
                password=pwd,
                Email=args['email'] if args['email'] else '',
                Phone=args['phone'] if args['phone'] else '',
                GroupId=args['GroupId'] if args['GroupId'] else None,
                WapuID=args['wapuid'] if args['wapuid'] else 1,
                code_group=args['code_group'] if args['code_group'] else '',
                PegawaiID=args['pegawaiid'] if args['pegawaiid'] else None,
                flag_active="1",
                date_exp='2028-01-31 15:55:44.483',
                user_level="60",
                UserUpd=uid or "",
                DateUpd=datetime.now()
            )
            db.session.add(add_record)
            db.session.commit()

            if add_record.UID:
                # ////INCLUDE IMG
                files_img = request.files
                if files_img:
                    if not os.path.exists(f'./static/uploads/avatar_temp'):
                        os.makedirs(f'./static/uploads/avatar_temp')
                    folder_temp = f'./static/uploads/avatar_temp'

                    # add item img and upload
                    filenames = []

                    for img_row in files_img.items():
                        img_row_ok = img_row[1]
                        if img_row_ok.filename == '':
                            logger.info('file image dengan nama avatar wajib disertakan')
                        if img_row_ok:
                            new_filename = f"{add_record.UserId}.png"
                            img_row_ok.save(os.path.join(folder_temp, new_filename))
                            filenames.append(new_filename)
                    filenames_str = ','.join([str(elem) for elem in filenames])
                    logger.info(filenames_str)
                    if filenames_str != '':
                        thread = Process(target=GoToTaskUploadAvatar,
                                         args=(folder_temp, filenames_str, add_record.UID, kwargs['claim']["UserId"], request.origin))
                        thread.daemon = True
                        thread.start()

            return success_create({})
        except Exception as e:
            print(e)
            return failed_create({})


class ListById(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege], 'delete': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('nama_user', type=str)
            parser.add_argument('email', type=str)
            parser.add_argument('phone', type=str)
            parser.add_argument('code_group', type=str)
            parser.add_argument('GroupId', type=int)
            parser.add_argument('pegawai_id', type=int)
            parser.add_argument('WapuID', type=int)
            args = parser.parse_args()
            if args:
                select_query = tblUser.query.filter_by(UID=id).first()
                if args['nama_user']:
                    select_query.nama_user = args['nama_user']
                if args['email']:
                    select_query.Email = args['email']
                if args['phone']:
                    select_query.Phone = args['phone']
                if args['code_group']:
                    select_query.code_group = args['code_group']
                if args['WapuID']:
                    select_query.WapuID = args['WapuID']
                if args['GroupId']:
                    select_query.GroupId = args['GroupId']
                if args['pegawai_id']:
                    select_query.PegawaiID = args['pegawai_id']

                # ////INCLUDE IMG
                files_img = request.files
                if files_img:
                    if not os.path.exists(f'./static/uploads/avatar_temp'):
                        os.makedirs(f'./static/uploads/avatar_temp')
                    folder_temp = f'./static/uploads/avatar_temp'

                    # add item img and upload
                    filenames = []

                    for img_row in files_img.items():
                        img_row_ok = img_row[1]
                        if img_row_ok.filename == '':
                            logger.info('file image dengan nama avatar wajib disertakan')
                        if img_row_ok:
                            new_filename = f"{id}.png"
                            img_row_ok.save(os.path.join(folder_temp, new_filename))
                            filenames.append(new_filename)
                    filenames_str = ','.join([str(elem) for elem in filenames])
                    logger.info(filenames_str)
                    if filenames_str != '':
                        thread = Process(target=GoToTaskUploadAvatar,
                                         args=(folder_temp, filenames_str, id,
                                               kwargs['claim']['UserId'], request.origin))
                        thread.daemon = True
                        thread.start()

                db.session.commit()
            return success_update({})
        except Exception as e:
            print(e)
            return failed_update({})

    def delete(self, id, *args, **kwargs):
        try:
            check_header = tblUser.query.filter_by(UID=id)
            check = check_header.first()
            if check:
                thread = Process(target=GoToTaskDeleteAvatar(check.Avatar, request.origin))
                thread.daemon = True
                thread.start()
            check_header.delete()
            db.session.commit()
            if check_header:
                return success_delete({})
            else:
                db.session.rollback()
                return failed_delete({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_delete({})


class MyProfile(Resource):
    method_decorators = {'get': [tblUser.auth_apikey], 'put': [tblUser.auth_apikey]}

    def get(self, *args, **kwargs):
        try:
            id = kwargs['claim']["UID"]
            row = tblUser.query.filter_by(UID=id).first()
            result = {
                'nama_user': row.nama_user,
                'email': row.Email,
                'Phone': row.Phone,
                'Avatar': row.Avatar,
                'pegawai_nama': row.pegawai.Nama if row.pegawai else "",
                'namabadan': row.wapu.NamaBadan if row.wapu else "",
                'group': row.Group.nama_group
            }
            return success_read(result)
        except Exception as e:
            print(e)
            return failed_read({})


    def put(self, *args, **kwargs):
        try:
            id = kwargs['claim']["UID"]
            parser = reqparse.RequestParser()
            parser.add_argument('nama_user', type=str)
            parser.add_argument('phone', type=str)
            args = parser.parse_args()
            if args or request.files:
                select_query = tblUser.query.filter_by(UID=id).first()
                if args['nama_user']:
                    select_query.nama_user = args['nama_user']
                if args['phone']:
                    select_query.Phone = args['phone']
                # ////INCLUDE IMG
                files_img = request.files
                if files_img:
                    if not os.path.exists(f'./static/uploads/avatar_temp'):
                        os.makedirs(f'./static/uploads/avatar_temp')
                    folder_temp = f'./static/uploads/avatar_temp'

                    # add item img and upload
                    filenames = []

                    for img_row in files_img.items():
                        img_row_ok = img_row[1]
                        if img_row_ok.filename == '':
                            logger.info('file image dengan nama avatar wajib disertakan')
                        if img_row_ok:
                            new_filename = f"{id}.png"
                            img_row_ok.save(os.path.join(folder_temp, new_filename))
                            filenames.append(new_filename)
                    filenames_str = ','.join([str(elem) for elem in filenames])
                    logger.info(filenames_str)
                    if filenames_str != '':
                        thread = Process(target=GoToTaskUploadAvatar,
                                         args=(folder_temp, filenames_str, id,
                                               kwargs['claim']['UserId'], request.origin))
                        thread.daemon = True
                        thread.start()
                db.session.commit()
                return success_update({})
            else:
                return failed_update({})
        except Exception as e:
            print(e)
            return failed_update({})


def users():
    return None