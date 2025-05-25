from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from config.helper import toDict
from controller.MsRT import MsRT
from controller.tblUser import tblUser



class MsRW(db.Model, SerializerMixin):
    __tablename__ = 'MsRW'
    RWID = db.Column(db.Integer, primary_key=True)
    RW = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.String, nullable=False)

    KecamatanID = db.Column(db.Integer, db.ForeignKey('MsKecamatan.KecamatanID'), nullable=False)
    KelurahanID = db.Column(db.Integer, db.ForeignKey('MsKelurahan.KelurahanID'), nullable=False)

    # class ListAll2(Resource):
    #     def get(self, kelurahanid, *args, **kwargs):
    #         parser = reqparse.RequestParser()
    #         parser.add_argument('KecamatanID', type=str)
    #         parser.add_argument('KelurahanID', type=str)
    #         select_query = db.session.execute(
    #             f"SELECT RWID, 'RW.' + RW AS RW FROM MsRW WHERE KelurahanID='{kelurahanid}' ORDER BY RW")
    #         result = []
    #         for row in select_query:
    #             d = {}
    #             for key in row.keys():
    #                 d[key] = getattr(row, key)
    #             result.append(d)
    #         return success_reads(result)

    class ListAll2(Resource):
        def get(self, kelurahanid, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('KecamatanID', type=str)
            # select_query = db.session.execute(
            #     f"SELECT RWID, 'RW.' + RW AS RW FROM MsRW WHERE KelurahanID='{kelurahanid}' ORDER BY RW")
            select_query = MsRW.query.filter_by(KelurahanID=kelurahanid).all()
            result = []
            for row in select_query:
                rt = MsRT.query.filter_by(RWID=row.RWID).all()
                new_row = {
                    'label': row.RW, 'value': row.RWID,
                    'items':  [{'label': f"RT : {row_rt.RT} (RW : {row.RW})", 'value': {"RWID": row.RWID, 'RTID': row_rt.RTID}} for row_rt in rt] if rt else [],
                    'RTID': [row_rt.RTID for row_rt in rt] if rt else [],
                    "RWID": row.RWID,
                    "RW": row.RW
                }
                # for key in row.keys():
                #     d[key] = getattr(row, key)
                result.append(new_row)
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
            select_query = MsRW.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsRW.RWID.ilike(search),
                        MsRW.RW.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsRW, args['sort']).desc()
                else:
                    sort = getattr(MsRW, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsRW.RWID)

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
            parser.add_argument('RWID', type=str)
            parser.add_argument('KelurahanID', type=str)
            parser.add_argument('KecamatanID', type=str)
            parser.add_argument('RW', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            add_record = MsRW(
                # RWID=rwid,
                KelurahanID=args['KelurahanID'],
                KecamatanID=args['KecamatanID'],
                RW=args['RW'],
                UserUpd=uid,
                DateUpd=datetime.now(),

            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsRW.query.filter_by(RWID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('KelurahanID', type=str)
            parser.add_argument('KecamatanID', type=str)
            parser.add_argument('RWID', type=str)
            parser.add_argument('RW', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = MsRW.query.filter_by(RWID=id).first()
                if select_query:
                    select_query.RWID = args['RWID']
                    select_query.KelurahanID = args['KelurahanID']
                    select_query.KecamatanID = args['KecamatanID']
                    select_query.RW = args['RW']
                    select_query.UserUpd = uid
                    select_query.DateUpd = datetime.now()
                    db.session.commit()
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsRW.query.filter_by(RWID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})