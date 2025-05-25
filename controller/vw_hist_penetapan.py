from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination
from config.database import db
from controller.tblUser import tblUser

class vw_hist_penetapan(db.Model, SerializerMixin):
    __tablename__ = 'vw_hist_penetapan'
    HistoryID = db.Column(db.Integer, primary_key=True)
    OPDID = db.Column(db.Integer, nullable=False)
    OBN = db.Column(db.String, nullable=True)
    ObyekBadanNo = db.Column(db.String, nullable=True)
    NamaBadan = db.Column(db.String, nullable=True)
    NamaPemilik = db.Column(db.String, nullable=True)
    AlamatPemilik = db.Column(db.String, nullable=True)
    AlamatBadan = db.Column(db.String, nullable=True)
    Kota = db.Column(db.String, nullable=True)
    Kecamatan = db.Column(db.String, nullable=True)
    Kelurahan = db.Column(db.String, nullable=True)

    UsahaBadan = db.Column(db.String, nullable=True)
    MasaAwal = db.Column(db.TIMESTAMP, nullable=False)
    MasaAkhir = db.Column(db.TIMESTAMP, nullable=False)
    UrutTgl = db.Column(db.Integer, nullable=False)

    Jenis = db.Column(db.String, nullable=True)
    JenisPendapatanID = db.Column(db.String, nullable=True)
    NamaJenisPendapatan = db.Column(db.String, nullable=True)
    StatusBayar = db.Column(db.String, nullable=True)
    NoKohir = db.Column(db.String, nullable=False)
    TglPenetapan = db.Column(db.TIMESTAMP, nullable=False)
    TglJatuhTempo = db.Column(db.TIMESTAMP, nullable=False)
    Pajak = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    IsPaid = db.Column(db.String, nullable=False)
    JmlBayar = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    JmlKurangBayar = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    Denda = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    Kenaikan = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    KodeRekening = db.Column(db.String, nullable=True)
    OmzetBase = db.Column(db.String, nullable=True)
    FlagJenisPendapatan = db.Column(db.String, nullable=True)
    Insidentil = db.Column(db.String, nullable=False)
    NIsPaid = db.Column(db.String, nullable=True)
    JatuhTempo = db.Column(db.String, nullable=False)
    HarusBayar = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    TglBayar = db.Column(db.TIMESTAMP, nullable=True)
    OmzetID = db.Column(db.String, nullable=True)
    TglHapus = db.Column(db.TIMESTAMP, nullable=True)
    KohirID = db.Column(db.String, nullable=False)
    Teguran = db.Column(db.Integer, nullable=False)
    TglKurangBayar = db.Column(db.TIMESTAMP, nullable=True)
    MasaPen = db.Column(db.String, nullable=False)
    LokID = db.Column(db.String, nullable=False)

    JOA = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    WPID = db.Column(db.Integer, nullable=False)
    SKPOwner = db.Column(db.String, nullable=False)
    UPTID = db.Column(db.String, nullable=False)
    UPT = db.Column(db.String, nullable=False)
    SelfAssesment = db.Column(db.String, nullable=False)
    StatusBayar = db.Column(db.String, nullable=True)
    DateUpd = db.Column(db.TIMESTAMP, nullable=True)
    UserUpdHist = db.Column(db.String, nullable=False)
    DateUpdHist = db.Column(db.TIMESTAMP, nullable=False)

    NoSKHapus = db.Column( db.String, nullable=False )
    TglSKHapus = db.Column( db.TIMESTAMP, nullable=False )
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
            select_query = vw_hist_penetapan.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_hist_penetapan.KohirID.ilike(search),
                        vw_hist_penetapan.TglPenetapan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_hist_penetapan, args['sort']).desc()
                else:
                    sort = getattr(vw_hist_penetapan, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_hist_penetapan.KohirID)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)