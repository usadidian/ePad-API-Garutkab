from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.tblUser import tblUser


class MsJenisPungut(db.Model, SerializerMixin):
    __tablename__ = 'MsJenisPungut'
    JenisPungutID = db.Column(db.Integer, primary_key=True)
    Kode = db.Column(db.String, nullable=False)
    JenisPungut = db.Column(db.String, nullable=False)
    Keterangan = db.Column(db.String, nullable=False)
    KdLevel = db.Column(db.Integer, nullable=False)

    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT JenisPungutID,Kode, JenisPungut, Keterangan, KdLevel FROM MsJenisPungut ORDER BY JenisPungutID ")
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
            select_query = MsJenisPungut.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsJenisPungut.JenisPungut.ilike(search),
                        MsJenisPungut.JenisPungut.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsJenisPungut, args['sort']).desc()
                else:
                    sort = getattr(MsJenisPungut, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsJenisPungut.JenisPungutID)

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
            parser.add_argument('Kode', type=str)
            parser.add_argument('JenisPungut', type=str)
            parser.add_argument('Keterangan', type=str)

            uid = kwargs['claim']["UID"]
            print(uid)

            args = parser.parse_args()
            select_query = db.session.execute("""
                SELECT RIGHT('00' + CAST(
                    ISNULL(
                        (SELECT MAX(CAST(REPLACE(Kode,'.','') AS INT)) + 1 FROM MsJenisPungut), 
                        1
                    ) AS VARCHAR
                ), 2) AS Kode
            """)
            kode = select_query.first()[0]

            result = []
            for row in result:
                result.append(row)

            add_record = MsJenisPungut(
                Kode=kode,
                JenisPungut=args['JenisPungut'] if args['JenisPungut'] else '',
                Keterangan=args['Keterangan'] if args['Keterangan'] else '',
            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsJenisPungut.query.filter_by(JenisPungutID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('Kode', type=str)
            parser.add_argument('JenisPungut', type=str)
            parser.add_argument('Keterangan', type=str)

            uid = kwargs['claim']["UID"]
            print(uid)

            select_query = db.session.execute(
                f"DECLARE @CURENTKODE VARCHAR(2), @KODE VARCHAR(2) "
                f"SET @CURENTKODE = (SELECT CAST(ISNULL((SELECT DISTINCT MAX(CAST(mjp.Kode AS INT)+1) FROM MsJenisPungut AS mjp),0) AS VARCHAR(2))) "
                f"SET @KODE = ISNULL((CASE WHEN LEN(@CURENTKODE)=1 THEN '0'+LTRIM(RTRIM(@CURENTKODE)) WHEN LEN(@CURENTKODE)=2 THEN LTRIM(RTRIM(@CURENTKODE))END),'01') "
                f"SELECT @KODE AS KODE")
            kode = select_query.first()[0]

            args = parser.parse_args()
            try:
                select_query = MsJenisPungut.query.filter_by(JenisPungutID=id).first()
                if select_query:
                    if args['Kode']: select_query.Kode = args['Kode']
                    if args['JenisPungut']: select_query.JenisPungut = args['JenisPungut']
                    if args['Keterangan']: select_query.Keterangan = args['Keterangan']
                    db.session.commit()
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsJenisPungut.query.filter_by(JenisPungutID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})
