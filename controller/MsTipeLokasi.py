from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.tblUser import tblUser



class MsTipeLokasi(db.Model, SerializerMixin):
    __tablename__ = 'MsTipeLokasi'

    TipeLokasiID = db.Column(db.String, primary_key=True)
    TipeKelas = db.Column(db.String, primary_key=True)
    NamaKelas = db.Column(db.String, nullable=False)
    Keterangan = db.Column(db.String, nullable=False)


    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT TipeLokasiID, TipeKelas, NamaKelas, Keterangan, Keterangan+'. '+NamaKelas AS JenisReklame "
                f"FROM MsTipeLokasi ORDER BY TipeLokasiID")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll3(Resource):
        def get(self, tipelokasiid, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT DISTINCT Keterangan + "
                f"'0'+CAST(CAST(ISNULL(RIGHT(MAX(mtlh.NomorTitik),2),'01') AS INT)+1 AS CHAR(2))  AS NomorTitik "
                f"FROM MsTipeLokasi tl LEFT JOIN MsTitikLokasiHdr AS mtlh ON mtlh.TipeLokasiID = tl.TipeLokasiID "
                f"where tl.TipeLokasiID={tipelokasiid} GROUP BY tl.Keterangan")
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
            select_query = MsTipeLokasi.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsTipeLokasi.TipeKelas.ilike(search),
                        MsTipeLokasi.NamaKelas.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsTipeLokasi, args['sort']).desc()
                else:
                    sort = getattr(MsTipeLokasi, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsTipeLokasi.TipeLokasiID)

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
            # parser.add_argument('TipeLokasiID', type=str)
            parser.add_argument('TipeKelas', type=str)
            parser.add_argument('NamaKelas', type=str)
            parser.add_argument('Keterangan', type=str)

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            add_record = MsTipeLokasi(
                TipeKelas=args['TipeKelas'],
                NamaKelas=args['NamaKelas'],
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
                select_query = MsTipeLokasi.query.filter_by(TipeLokasiID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            # parser.add_argument('TipeLokasiID', type=str)
            parser.add_argument('TipeKelas', type=str)
            parser.add_argument('NamaKelas', type=str)
            parser.add_argument('Keterangan', type=str)

            args = parser.parse_args()
            try:
                select_query = MsTipeLokasi.query.filter_by(TipeLokasiID=id).first()
                if select_query:
                    # select_query.TipeLokasiID = args['TipeLokasiID']
                    select_query.TipeKelas = args['TipeKelas']
                    select_query.NamaKelas = args['NamaKelas']
                    select_query.Keterangan = args['Keterangan']

                    db.session.commit()
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsTipeLokasi.query.filter_by(TipeLokasiID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})

