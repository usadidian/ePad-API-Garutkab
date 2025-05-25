from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination
from config.database import db
from controller.tblUser import tblUser


class msobyekbadan(db.Model, SerializerMixin):
    __tablename__ = 'msobyekbadan'
    WPID = db.Column(db.String, primary_key=True)
    OPDID = db.Column(db.Integer, nullable=False)
    ObyekBadanNo = db.Column(db.String, nullable=False)
    NamaBadan = db.Column(db.String, nullable=False)
    GrupUsahaID= db.Column(db.String, nullable=False)
    KlasifikasiID = db.Column(db.String, nullable=False)
    LokasiID = db.Column(db.String, nullable=False)
    SelfAssesment = db.Column(db.String, nullable=False)
    AlamatBadan = db.Column(db.String, nullable=False)
    KotaBadan = db.Column(db.String, nullable=False)
    KecamatanBadan = db.Column(db.Integer, nullable=False)
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
    RWPemilik = db.Column(db.Integer, nullable=True)
    RTPemilik = db.Column(db.Integer, nullable=True)
    NoTelpPemilik = db.Column(db.String, nullable=False)
    NoFaxPemilik = db.Column(db.String, nullable=False)

    TglPendaftaran = db.Column(db.DateTime, nullable=False)
    TglPengesahan = db.Column(db.DateTime, nullable=False)
    NoPengesahan = db.Column(db.String, nullable=False)
    TglPenghapusan = db.Column(db.DateTime, nullable=True)
    PetugasPendaftar = db.Column(db.String, nullable=False)
    Insidentil = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.String, nullable=False)

    NamaPengelola = db.Column(db.String, nullable=True)
    AlamatPengelola = db.Column(db.String, nullable=True)
    KotaPengelola = db.Column(db.String, nullable=True)
    KecamatanPengelola = db.Column(db.Integer, nullable=True)
    KelurahanPengelola = db.Column(db.Integer, nullable=True)
    RWPengelola = db.Column(db.Integer, nullable=True)
    RTPengelola = db.Column(db.Integer, nullable=True)
    NoTelpPengelola = db.Column(db.String, nullable=True)
    NoFaxPengelola = db.Column(db.String, nullable=True)

    NPWPPemilik = db.Column(db.String, nullable=True)
    NPWPPengelola = db.Column(db.String, nullable=True)
    NPWPUsaha = db.Column(db.String, nullable=True)
    UsahaBadan = db.Column(db.String, nullable=True)


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
            select_query = msobyekbadan.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(msobyekbadan.ObyekBadanNo.ilike(search),
                        msobyekbadan.NamaBadan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(msobyekbadan, args['sort']).desc()
                else:
                    sort = getattr(msobyekbadan, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(msobyekbadan.WPID)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)