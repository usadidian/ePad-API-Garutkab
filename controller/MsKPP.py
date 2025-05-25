from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.tblUser import tblUser

class MsKPP(db.Model, SerializerMixin):
    __tablename__ = 'MsKPP'
    KPPID = db.Column(db.Integer, primary_key=True)
    Parent = db.Column(db.Integer, nullable=False)
    KPPNo= db.Column(db.String, nullable=False)
    KPP = db.Column(db.String, nullable=False)
    KabKota = db.Column(db.String, nullable=False)
    KPPKota = db.Column(db.String, nullable=False)


    class ListAll2(Resource):
        def get(self,  *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('Parent', type=str)
            select_query = db.session.execute(
                f"SELECT KPP + ' - ' + (case when KabKota='' then Kota else KabKota end) AS KPPID, KPPNo AS KPP "
                f"FROM MsKPP k LEFT JOIN MsKota o ON k.KPPKota = o.KotaID WHERE KPPNo <> '' ORDER BY KPPNo")
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
            select_query = MsKPP.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsKPP.KPPID.ilike(search),
                        MsKPP.KPPNo.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsKPP, args['sort']).desc()
                else:
                    sort = getattr(MsKPP, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsKPP.KPPID)

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
            parser.add_argument('KPPID', type=str)
            parser.add_argument('Parent', type=str)
            parser.add_argument('KPPNo', type=str)
            parser.add_argument('KPP', type=str)
            parser.add_argument('KabKota', type=str)
            parser.add_argument('KPPKota', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            select_query = db.session.execute(
                f"SELECT CAST(MAX(CAST(KPPID AS int) + 1) AS varchar(10)) AS NextID FROM MsKPP")
            result2 = select_query.first()[0]
            kelurahanid = result2

            add_record = MsKPP(
                KPPID=kelurahanid,
                Parent=args['Parent'],
                KPPNo=args['KPPNo'],
                KPP=args['KPP'],
                KabKota=args['KabKota'],
                KPPKota=args['KPPKota'],

            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsKPP.query.filter_by(KPPID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('KPPID', type=str)
            parser.add_argument('Parent', type=str)
            parser.add_argument('KPPNo', type=str)
            parser.add_argument('KPP', type=str)
            parser.add_argument('KabKota', type=str)
            parser.add_argument('KPPKota', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = MsKPP.query.filter_by(KPPID=id).first()
                if select_query:
                    select_query.KPPID = args['KPPID']
                    select_query.Parent = args['Parent']
                    select_query.KPPNo = args['KPPNo']
                    select_query.KPP = args['KPP']
                    select_query.KabKota = args['KabKota']
                    select_query.KPPKota = args['KPPKota']
                    db.session.commit()
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsKPP.query.filter_by(KPPID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})