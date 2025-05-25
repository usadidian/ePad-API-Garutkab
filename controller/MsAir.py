from datetime import datetime

from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads, failed_reads
from config.database import db
from controller.tblUser import tblUser


class MsAir(db.Model, SerializerMixin):
    __tablename__ = 'MsAir'
    AirID = db.Column(db.Integer, primary_key=True)
    VolAwal = db.Column(db.Integer, nullable=False)
    VolAkhir = db.Column(db.Integer, nullable=False)
    VolMax = db.Column( db.Integer, nullable=False )



    # class VolAwal(Resource):
    #     method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}
    #
    #     def get(self, *args, **kwargs):
    #
    #         # PARSING PARAMETER DARI REQUEST
    #         parser = reqparse.RequestParser()
    #         parser.add_argument('page', type=int)
    #         parser.add_argument('length', type=int)
    #         parser.add_argument('sort', type=str)
    #         parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
    #         parser.add_argument('search', type=str)
    #
    #         args = parser.parse_args()
    #         UserId = kwargs['claim']["UserId"]
    #         print(UserId)
    #         select_query = db.session.query(MsAir.AirID.label('AirID'),
    #                                         MsAir.VolAwal.label('VolAwal'),
    #                                         MsAir.VolAkhir.label('VolAkhir'))
    #
    #         # SEARCH
    #         if args['search'] and args['search'] != 'null':
    #             search = '%{0}%'.format(args['search'])
    #             select_query = select_query.filter(
    #                 or_(MsAir.AirID.ilike(search),
    #                     MsAir.VolAwal.ilike(search),
    #                     MsAir.VolAkhir.ilike( search ),
    #                     MsAir.VolMax.ilike(search))
    #             )
    #
    #         # SORT
    #         if args['sort']:
    #             if args['sort_dir'] == "desc":
    #                 sort = getattr(MsAir, args['sort']).desc()
    #             else:
    #                 sort = getattr(MsAir, args['sort']).asc()
    #             select_query = select_query.order_by(sort)
    #         else:
    #             select_query = select_query.order_by(MsAir.AirID)
    #
    #         # PAGINATION
    #         page = args['page'] if args['page'] else 1
    #         length = args['length'] if args['length'] else 5
    #         lengthLimit = length if length < 101 else 100
    #         query_execute = select_query.paginate(page, lengthLimit)
    #
    #         result = []
    #         for row in query_execute.items:
    #             d = {}
    #             for key in row.keys():
    #                 d[key] = getattr( row, key )
    #             result.append( d )
    #         return success_reads_pagination( query_execute, result )

    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            try:
                select_query = db.session.execute(
                    f"SELECT JenisAirID + KawasanID + convert(varchar,AirID) AS Kode,AirID,"
                    f"right('000'+convert(varchar,AirID),3) + ' - ' + VolAwal + ', ' + Kecamatan AS Nama FROM MsAir j "
                    f"LEFT JOIN MsKecamatan c ON j.VolAkhir = c.VolAkhir ORDER BY VolAwal ")
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
            parser.add_argument( 'VolAkhir', type=str )

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            print(UserId)

            select_query = db.session.query(MsAir.AirID, MsAir.VolAwal, MsAir.VolAkhir,
                                            MsAir.VolMax)

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsAir.AirID.ilike(search),
                        MsAir.VolAwal.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsAir, args['sort']).desc()
                else:
                    sort = getattr(MsAir, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsAir.VolAwal)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads_pagination( query_execute, result )

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('VolAwal', type=str)
            parser.add_argument('VolAkhir', type=str)
            parser.add_argument( 'VolMax', type=str )

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()

            result = []
            for row in result:
                result.append(row)

            select_query = db.session.execute(
                f"SELECT CAST(MAX(CAST(AirID AS int) + 1) AS varchar(10)) AS NextID FROM MsAir")
            result2 = select_query.first()[0]
            AirID = result2

            add_record = MsAir(
                AirID=AirID,
                VolAwal=args['VolAwal'],
                VolAkhir=args['VolAkhir'],
                VolMax=args['VolMax'],

            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsAir.query.filter_by(AirID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            # parser.add_argument( 'AirID', type=str )
            parser.add_argument('VolAwal', type=str)
            parser.add_argument('VolAkhir', type=str)
            parser.add_argument('VolMax', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = MsAir.query.filter_by(AirID=id).first()
                if select_query:
                    if args['VolAwal']:
                        select_query.VolAwal = args['VolAwal']
                    if args['VolAkhir']:
                        select_query.KawasanID = args['VolAkhir']
                    if args['VolMax']:
                        select_query.JenisAirID = args['VolMax']
                    db.session.commit()
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsAir.query.filter_by(AirID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})
