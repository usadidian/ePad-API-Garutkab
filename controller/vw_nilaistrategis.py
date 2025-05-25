from datetime import datetime

from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination, success_read, failed_read, success_update, failed_update, \
    success_delete, failed_delete
from config.database import db
from controller.MsPegawai import MsPegawai
from controller.tblUser import tblUser


class vw_nilaistrategis(db.Model, SerializerMixin):
    __tablename__ = 'vw_nilaistrategis'
    StrategisID = db.Column( db.Integer, primary_key=True )
    NamaStrategis = db.Column( db.String, nullable=False )
    Wilayah = db.Column( db.String, nullable=False )
    Persentase = db.Column( db.String, nullable=False )
    DetailID = db.Column( db.Integer, primary_key=True )
    NamaStrategisDtl = db.Column( db.String, nullable=False )
    Nilai = db.Column( db.Numeric( 12, 2 ), nullable=False )
    TipeLokasiID = db.Column( db.String, primary_key=True )
    TipeKelas = db.Column( db.String, primary_key=True )
    NamaKelas = db.Column( db.String, nullable=False )


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
            select_query = vw_nilaistrategis.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_nilaistrategis.KohirID.ilike(search),
                        vw_nilaistrategis.TglPenetapan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_nilaistrategis, args['sort']).desc()
                else:
                    sort = getattr(vw_nilaistrategis, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_nilaistrategis.KohirID)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)