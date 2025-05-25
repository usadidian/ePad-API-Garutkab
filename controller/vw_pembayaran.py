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


class vw_pembayaran(db.Model, SerializerMixin):
    __tablename__ = 'vw_pembayaran'
    PenetapanID = db.Column( db.Integer, primary_key=True )
    OPDID = db.Column(db.Integer, nullable=False)
    OBN = db.Column( db.String, nullable=True )
    ObyekBadanNo = db.Column( db.String, nullable=True )
    UsahaBadan = db.Column( db.String, nullable=True )
    NamaBadan = db.Column( db.String, nullable=True )
    TglJatuhTempo = db.Column( db.TIMESTAMP, nullable=False )
    StatusBayar = db.Column( db.String, nullable=False )
    NoKohir = db.Column( db.String, nullable=False )
    KohirID = db.Column( db.String, nullable=False )
    STS = db.Column( db.String, nullable=True )
    KodeBayar = db.Column( db.String, nullable=True )
    Dinas = db.Column( db.String, nullable=True )
    NTPD = db.Column(db.String, nullable=True)
    SKPOwner = db.Column(db.String, nullable=True)
    TglNTPD = db.Column(db.TIMESTAMP, nullable=False)
    NamaPemilik = db.Column( db.String, nullable=True )
    AlamatPemilik = db.Column( db.String, nullable=True )
    AlamatBadan = db.Column( db.String, nullable=True )
    MasaAwal = db.Column( db.TIMESTAMP, nullable=False )
    MasaAkhir = db.Column( db.TIMESTAMP, nullable=False )
    TglPenetapan = db.Column( db.TIMESTAMP, nullable=False )
    Pajak = db.Column( db.Numeric( precision=8, asdecimal=False, decimal_return_scale=None ), nullable=True )
    JmlBayar = db.Column( db.Numeric( precision=8, asdecimal=False, decimal_return_scale=None ), nullable=True )
    JmlBayarOpsen = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    JmlKurangBayar = db.Column( db.Numeric( precision=8, asdecimal=False, decimal_return_scale=None ), nullable=True )
    Denda = db.Column( db.Numeric( precision=8, asdecimal=False, decimal_return_scale=None ), nullable=True )
    Kenaikan = db.Column( db.Numeric( precision=8, asdecimal=False, decimal_return_scale=None ), nullable=True )
    JenisPendapatanID = db.Column(db.String, nullable=True)
    NamaJenisPendapatan = db.Column(db.String, nullable=True)
    SetoranHistID = db.Column( db.Integer, nullable=True )
    NoSSPD = db.Column( db.String, nullable=False )
    StatusBayar = db.Column(db.String, nullable=True)
    TglBayar = db.Column( db.TIMESTAMP, nullable=True )
    KodeRekening = db.Column(db.String, nullable=True)
    Insidentil = db.Column( db.String, nullable=False )
    SelfAssesment = db.Column( db.String, nullable=False )
    OmzetBase = db.Column(db.String, nullable=False)
    UPTID = db.Column( db.String, nullable=True )
    UPT = db.Column( db.String, nullable=True )
    DateUpd = db.Column( db.TIMESTAMP, nullable=True )
    KodeStatus = db.Column( db.String, nullable=True )
    LabelStatus = db.Column( db.String, nullable=True )
    IsPaid = db.Column( db.String, nullable=True )
    JatuhTempo = db.Column( db.String, nullable=True )
    avatar = db.Column(db.String, nullable=True)

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
            select_query = vw_pembayaran.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_pembayaran.KohirID.ilike(search),
                        vw_pembayaran.TglPenetapan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_pembayaran, args['sort']).desc()
                else:
                    sort = getattr(vw_pembayaran, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_pembayaran.KohirID)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)