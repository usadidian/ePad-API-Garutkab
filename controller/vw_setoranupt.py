from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination
from config.database import db
from controller.tblUser import tblUser


class vw_setoranupt(db.Model, SerializerMixin):
    __tablename__ = 'vw_setoranupt'
    HeaderID = db.Column(db.Integer, primary_key=True)
    UPTID = db.Column(db.String, nullable=False)
    UPT = db.Column(db.String, nullable=False)
    SetoranDari = db.Column(db.String, nullable=True)
    SetoranDariUPT = db.Column(db.String, nullable=True)
    KodaSatker = db.Column(db.String, nullable=True)
    ParentID = db.Column(db.String, nullable=True)
    NoSTS = db.Column(db.String, nullable=False)
    STSKe = db.Column(db.Integer, nullable=False)
    TglSetoran = db.Column(db.TIMESTAMP, nullable=False)
    Keterangan = db.Column(db.String, nullable=False)
    StatusBayar = db.Column(db.String, nullable=True)
    KodeSB = db.Column(db.String, nullable=True)
    Status = db.Column(db.String, nullable=False)
    UPTStatus = db.Column(db.String, nullable=False)
    BendaharaID = db.Column(db.String, nullable=False)
    KodeStatus = db.Column(db.String,  nullable=False)
    JmlSetoran = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    Status = db.Column(db.String, nullable=False)
    NTB = db.Column(db.String, nullable=True)
    NTPD = db.Column(db.String, nullable=True)
    TglNTPD = db.Column(db.TIMESTAMP, nullable=True)


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
            select_query = vw_setoranupt.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_setoranupt.NoSTS.ilike(search),
                        vw_setoranupt.Keterangan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_setoranupt, args['sort']).desc()
                else:
                    sort = getattr(vw_setoranupt, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_setoranupt.HeaderID)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)
