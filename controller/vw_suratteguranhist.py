from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_delete, failed_delete, success_reads_pagination
from config.database import db
from controller.tblUser import tblUser


class vw_suratteguranhist(db.Model, SerializerMixin):
    __tablename__ = 'vw_suratteguranhist'
    SuratID = db.Column(db.Integer, primary_key=True)
    NoUrut = db.Column(db.Integer, nullable=False)
    NoSurat = db.Column(db.String, nullable=False)
    TglSurat = db.Column(db.TIMESTAMP, nullable=False)
    Status = db.Column(db.String, nullable=False)
    OBN = db.Column(db.String, nullable=True)
    ObyekBadanNo = db.Column(db.String, nullable=True)
    NamaBadan = db.Column(db.String, nullable=True)
    NamaPemilik = db.Column(db.String, nullable=True)
    AlamatBadan = db.Column(db.String, nullable=True)
    AlamatPemilik = db.Column(db.String, nullable=True)
    Kota = db.Column(db.String, nullable=False)
    Kecamatan = db.Column(db.Integer, nullable=False)
    Kelurahan = db.Column(db.Integer, nullable=False)
    KohirID = db.Column(db.String, nullable=False)
    MasaAwal = db.Column(db.TIMESTAMP, nullable=False)
    MasaAkhir = db.Column(db.TIMESTAMP, nullable=False)
    TglPenetapan = db.Column( db.TIMESTAMP, nullable=False )
    JatuhTempo = db.Column(db.String, nullable=True)
    TglJatuhTempo = db.Column(db.TIMESTAMP, nullable=False)
    JmlTeguran = db.Column(db.Integer, nullable=True)
    UPTID = db.Column(db.String, nullable=True)
    UPT = db.Column(db.String, nullable=True)
    JenisPendapatanID = db.Column(db.String, nullable=True)
    NamaJenisPendapatan = db.Column(db.String, nullable=True)
    SelfAssessment = db.Column( db.String, nullable=True )
    Insidentil = db.Column( db.String, nullable=True )
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)
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
            select_query = vw_suratteguranhist.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_suratteguranhist.KohirID.ilike(search),
                        vw_suratteguranhist.TglPenetapan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_suratteguranhist, args['sort']).desc()
                else:
                    sort = getattr(vw_suratteguranhist, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_suratteguranhist.TglSurat.desc())

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)

