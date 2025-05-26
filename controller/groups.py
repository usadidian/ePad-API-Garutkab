import sys
from datetime import datetime

from flask_restful import Resource, reqparse

from config.api_message import success_read, failed_reads, success_create, failed_create, failed_delete, success_delete, \
    success_update, failed_update, success_reads
from config.database import db
from controller.tblGroupUser import tblGroupUser
from controller.tblUser import tblUser

sys.setrecursionlimit(1500)




class ListAll2(Resource):
    def get(self, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT DISTINCT * FROM tblGroupUser AS tgu WHERE tgu.IsAdmin=1 OR tgu.IsWP=1 OR tgu.IsPendaftaran=1 "
            f"OR tgu.IsPendataan=1 OR tgu.IsPenetapan=1 OR tgu.IsPembayaran=1 OR tgu.IsPenyetoran=1 OR tgu.IsExecutive=1 "
            f"OR tgu.IsExecutive=1 "
            f"ORDER BY tgu.GroupId")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)

class ListAll(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        try:
            # select_data = tblGroupUser.query.order_by(tblGroupUser.DateUpd.desc()).all()
            select_data = tblGroupUser.query.order_by(tblGroupUser.DateUpd.desc()).limit(100).all()
            result = []
            for row in select_data:
                result.append(row.to_dict())
            return success_read(result)
        except Exception as e:
            print(e)
            return failed_reads({})

#
    def post(self, *args, **kwargs):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('nama_group', type=str, required=True, help="Harus diisi")
            parser.add_argument('code_group', type=str, required=True, help="Harus diisi")
            parser.add_argument('description', type=str)
            parser.add_argument('level_group', type=str)
            parser.add_argument('IsAdmin', type=str)
            parser.add_argument('IsPendaftaran', type=str)
            parser.add_argument('IsPendataan', type=str)
            parser.add_argument('IsPenetapan', type=str)
            parser.add_argument('IsPembayaran', type=str)
            parser.add_argument('IsPenyetoran', type=str)
            parser.add_argument('IsIntegrasi', type=str)
            parser.add_argument('IsWP', type=str)
            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            add_record = tblGroupUser(
                nama_group=args['nama_group'],
                description=args['description'],
                level_group=args['level_group'],
                IsAdmin=args['IsAdmin'],
                IsPendaftaran=args['IsPendaftaran'],
                IsPendataan=args['IsPendataan'],
                IsPenetapan=args['IsPenetapan'],
                IsPembayaran=args['IsPembayaran'],
                IsPenyetoran=args['IsPenyetoran'],
                IsIntegrasi=args['IsIntegrasi'],
                IsWP=args['IsWP'],
                code_group=args['code_group'],
                UserUpd=uid or "",
                DateUpd=datetime.now()
            )
            db.session.add(add_record)
            db.session.commit()
            return success_create({"id": add_record.GroupId})
        except Exception as e:
            print(e)
            return failed_create({})


class ListById(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege], 'delete': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('nama_group', type=str)
            parser.add_argument('code_group', type=str)
            parser.add_argument('description', type=str)
            parser.add_argument('level_group', type=str)
            parser.add_argument('IsAdmin', type=str)
            parser.add_argument('IsWP', type=str)
            args = parser.parse_args()
            if args:
                select_query = tblGroupUser.query.filter_by(GroupId=id).first()
                if args['nama_group']:
                    select_query.nama_group = args['nama_group']
                if args['code_group']:
                    select_query.code_group = args['code_group']
                if args['description']:
                    select_query.description = args['description']
                if args['level_group']:
                    select_query.level_group = args['level_group']
                if args['IsAdmin']:
                    select_query.IsAdmin = args['IsAdmin']
                if args['IsAdmin']:
                    select_query.IsAdmin = args['IsAdmin']
                if args['IsPendaftaran']:
                    select_query.IsAdmin = args['IsPendaftaran']
                if args['IsPendataan']:
                    select_query.IsAdmin = args['IsPendataan']
                if args['IsPenetapan']:
                    select_query.IsAdmin = args['IsPenetapan']
                if args['IsPembayaran']:
                    select_query.IsAdmin = args['IsPembayaran']
                if args['IsPenyetoran']:
                    select_query.IsAdmin = args['IsPenyetoran']
                if args['IsIntegrasi']:
                    select_query.IsAdmin = args['IsIntegrasi']
                if args['IsWP']:
                    select_query.IsWP = args['IsWP']
                db.session.commit()
            return success_update({})
        except Exception as e:
            print(e)
            return failed_update({})


    def delete(self, id, *args, **kwargs):
        try:
            check_header = tblGroupUser.query.filter_by(GroupId=id)
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