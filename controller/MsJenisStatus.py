from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy.sql.elements import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination, success_reads, failed_reads
from config.database import db
from controller.tblUser import tblUser


class MsJenisStatus(db.Model, SerializerMixin):
    __tablename__ = 'MsJenisStatus'
    KodeStatus = db.Column(db.String, primary_key=True)
    LabelStatus = db.Column(db.String, nullable=False)
    Uraian = db.Column(db.String, nullable=False)


    class ListAll2(Resource):
        def get(self,  *args, **kwargs):
            try:
                select_query = db.session.execute(
                    f"SELECT KodeStatus, LabelStatus FROM MsJenisStatus WHERE KodeStatus in('70','73','76','77') "
                    f"ORDER BY KodeStatus  ")
                result=[]
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr(row, key)
                    result.append(d)
                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_reads()

    class ListAll3(Resource):
        def get(self, *args, **kwargs):
            try:
                select_query = db.session.execute(
                    f"SELECT KodeStatus, LabelStatus FROM MsJenisStatus WHERE KodeStatus in('01','02') "
                    f"ORDER BY KodeStatus  ")
                result = []
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr(row, key)
                    result.append(d)
                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_reads()

    class ListAll4(Resource):
        def get(self, *args, **kwargs):
            try:
                select_query = db.session.execute(
                    f"SELECT KodeStatus, LabelStatus FROM MsJenisStatus WHERE KodeStatus in('03','04','05') "
                    f"ORDER BY KodeStatus  ")
                result = []
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr(row, key)
                    result.append(d)
                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_reads()

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
            select_query = MsJenisStatus.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsJenisStatus.KodeStatus.ilike(search),
                        MsJenisStatus.LabelStatus.ilike(search),
                        MsJenisStatus.Uraian.ilike(search),)
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsJenisStatus, args['sort']).desc()
                else:
                    sort = getattr(MsJenisStatus, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsJenisStatus.KodeStatus)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)

    # class ListAll(Resource):
    #     #method_decorators = [users.auth_apikey_privilege]
    #     def get(self):
    #         # select_query = MsJenisStatus.query.all()
    #         select_query = MsJenisStatus.query.order_by(MsJenisStatus.KodeStatus).paginate(1, 10)
    #         # result = [row.to_dict() for row in select_query]
    #         # return jsonify({'status_code': 1, 'message': 'OK', 'data': result})
    #         result = []
    #         for row in select_query.items:
    #             result.append(row.to_dict())
    #         return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

