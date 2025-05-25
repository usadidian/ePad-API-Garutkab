from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.tblUser import tblUser


class MsGrupUsaha(db.Model, SerializerMixin):
    __tablename__ = 'MsGrupUsaha'
    GrupUsahaID = db.Column(db.String, primary_key=True)
    GrupUsaha = db.Column(db.String, nullable=False)
    Keterangan= db.Column(db.String, nullable=False)

    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT GrupUsahaID, GrupUsaha FROM MsGrupUsaha ORDER BY GrupUsahaID ")
            result=[]
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
            parser.add_argument('search', type=str)

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            print(UserId)
            select_query = MsGrupUsaha.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsGrupUsaha.GrupUsaha.ilike(search),
                        MsGrupUsaha.Keterangan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsGrupUsaha, args['sort']).desc()
                else:
                    sort = getattr(MsGrupUsaha, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsGrupUsaha.GrupUsahaID)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('GrupUsahaID', type=str)
            parser.add_argument('GrupUsaha', type=str)
            parser.add_argument('Keterangan', type=str)

            uid = kwargs['claim']["UID"]
            print(uid)

            args = parser.parse_args()
            select_query = db.session.execute(
                f"DECLARE @NoUrut INT,@GrupUsahaID CHAR(2)"
                f"SET @NoUrut=ISNULL((SELECT DISTINCT MAX(CAST(mgu.GrupUsahaID AS INT)+1)  FROM MsGrupUsaha AS mgu),0)"
                f"SET @GrupUsahaID = (select SUBSTRING('00' + CAST(@NoUrut as varchar), LEN(@NoUrut)+1 , 2))"
                f"SELECT @GrupUsahaID AS GrupUsahaID")
            result3 = select_query.first()[0]
            grupusahaid = result3

            result = []
            for row in result:
                result.append(row)

            add_record = MsGrupUsaha(
                GrupUsahaID=grupusahaid,
                GrupUsaha=args['GrupUsaha'],
                Keterangan=args['Keterangan'],
            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsGrupUsaha.query.filter_by(GrupUsahaID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('GrupUsahaID', type=str)
            parser.add_argument('GrupUsaha', type=str)
            parser.add_argument('Keterangan', type=str)

            uid = kwargs['claim']["UID"]
            print(uid)

            args = parser.parse_args()
            try:
                select_query = MsGrupUsaha.query.filter_by(GrupUsahaID=id).first()
                if select_query:
                    select_query.GrupUsaha = args['GrupUsahaID']
                    select_query.GrupUsaha = args['GrupUsaha']
                    select_query.Keterangan = args['Keterangan']
                    db.session.commit()
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsGrupUsaha.query.filter_by(GrupUsahaID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})
