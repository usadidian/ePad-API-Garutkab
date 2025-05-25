from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination
from config.database import db
from controller.tblUser import tblUser


class vw_obyekbadanwpo(db.Model, SerializerMixin):
    __tablename__ = 'vw_obyekbadanwpo'
    WPID = db.Column(db.Integer, primary_key=True)
    NamaBadan = db.Column(db.String, nullable=False)
    GrupUsahaID= db.Column(db.String, nullable=False)
    KlasifikasiID = db.Column(db.String, nullable=False)
    LokasiID = db.Column(db.String, nullable=False)
    NamaLokasi = db.Column(db.String, nullable=False)
    AlamatBadan = db.Column(db.String, nullable=False)
    KotaBadan = db.Column(db.String, nullable=False)
    Kecamatan = db.Column(db.String, nullable=False)
    KecamatanBadan = db.Column(db.Integer, nullable=False)
    Kelurahan = db.Column(db.String, nullable=False)
    KelurahanBadan = db.Column(db.Integer, nullable=False)
    RWBadan = db.Column(db.Integer, nullable=True)
    RTBadan = db.Column(db.Integer, nullable=True)
    NoTelpBadan = db.Column(db.String, nullable=False)
    NoFaxBadan = db.Column(db.String, nullable=False)

    NamaPemilik = db.Column(db.String, nullable=False)
    JabatanPemilik = db.Column(db.String, nullable=False)
    AlamatPemilik = db.Column(db.String, nullable=False)
    KotaPemilik = db.Column(db.String, nullable=False)
    KecamatanPemilik = db.Column(db.Integer, nullable=False)
    KelurahanPemilik = db.Column(db.Integer, nullable=False)
    # RWPemilik = db.Column(db.Integer, nullable=True)
    # RTPemilik = db.Column(db.Integer, nullable=True)
    NoTelpPemilik = db.Column(db.String, nullable=False)
    NoFaxPemilik = db.Column(db.String, nullable=False)
    Insidentil = db.Column(db.String, nullable=False)
    # UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.String, nullable=False)
    OPDID = db.Column(db.Integer, nullable=False)
    NamaJenisPendapatan = db.Column(db.String, nullable=False)
    SelfAssesment = db.Column(db.String, nullable=True)
    MasaPendapatan = db.Column(db.String, nullable=True)
    OBN = db.Column(db.String, nullable=True)
    vw_al_usaha = db.Column(db.String, nullable=True)
    vw_al_pemilik = db.Column(db.String, nullable=True)
    vw_kel_badan = db.Column(db.String, nullable=False)
    KecamatanID = db.Column(db.Integer, nullable=True)
    FaxKecamatan  = db.Column(db.String, nullable=False)
    KelurahanID = db.Column(db.Integer, nullable=True)
    JenisPendapatanID = db.Column(db.String, nullable=True)
    KodeRekening = db.Column(db.String, nullable=True)
    UsahaBadan = db.Column(db.String, nullable=True)
    avatar = db.Column(db.String, nullable=True)
    latlng = db.Column(db.String, nullable=True)
    NIK = db.Column(db.String, nullable=True)
    UserUpd = db.Column(db.String, nullable=True)

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
            select_query = vw_obyekbadanwpo.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_obyekbadanwpo.NamaPemilik.ilike(search),
                        vw_obyekbadanwpo.NamaBadan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_obyekbadanwpo, args['sort']).desc()
                else:
                    sort = getattr(vw_obyekbadanwpo, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_obyekbadanwpo.WPID)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)