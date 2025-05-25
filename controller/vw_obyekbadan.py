from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.tblUser import tblUser


class vw_obyekbadan(db.Model, SerializerMixin):
    __tablename__ = 'vw_obyekbadan'

    WPID = db.Column(db.Integer, primary_key=True)
    WapuID = db.Column(db.Integer, nullable=False)
    ObyekBadanNo = db.Column(db.String, nullable=False)
    NamaBadan = db.Column(db.String, nullable=False)
    OPDID = db.Column(db.Integer, primary_key=True)
    NamaOPD = db.Column(db.String)
    KecamatanOPD = db.Column(db.Integer)
    KelurahanOPD = db.Column(db.Integer)
    AlamatOPD = db.Column(db.String)
    RWOPD = db.Column(db.Integer)
    RTOPD = db.Column(db.Integer)
    NoTelpOPD = db.Column(db.String)
    WajibPungut = db.Column(db.String, nullable=False)
    GrupUsahaID= db.Column(db.String, nullable=False)
    KlasifikasiID = db.Column(db.String, nullable=False)
    LokasiID = db.Column(db.String, nullable=False)
    NamaLokasi = db.Column(db.String, nullable=False)
    AlamatBadan = db.Column(db.String, nullable=False)
    Kota = db.Column(db.String, nullable=False)
    Kecamatan = db.Column(db.Integer, nullable=False)
    Kelurahan = db.Column(db.Integer, nullable=False)
    RWBadan = db.Column(db.Integer, nullable=True)
    RTBadan = db.Column(db.Integer, nullable=True)
    NoTelpBadan = db.Column(db.String, nullable=False)
    NoFaxBadan = db.Column(db.String, nullable=False)
    TglPendataan = db.Column(db.DateTime)
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

    TglPendaftaran = db.Column(db.DateTime, nullable=False)
    TglPengesahan = db.Column(db.DateTime, nullable=False)
    NoPengesahan = db.Column(db.String, nullable=False)
    TglPenghapusan = db.Column(db.DateTime, nullable=True)
    TglHapus = db.Column(db.DateTime, nullable=True)
    TglHapusOPD = db.Column(db.DateTime, nullable=True)
    PetugasPendaftar = db.Column(db.String, nullable=False)
    Insidentil = db.Column(db.String, nullable=False)
    # UserUpd = db.Column(db.String, nullable=False)
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

    OPDID = db.Column(db.Integer, nullable=False)
    NamaJenisPendapatan = db.Column(db.String, nullable=False)
    # TglDaftar = db.Column(db.TIMESTAMP, nullable=True)
    # TglSah = db.Column(db.TIMESTAMP, nullable=True)
    TglData = db.Column(db.TIMESTAMP, nullable=True)
    # TglHapus = db.Column(db.TIMESTAMP, nullable=True)
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
    ParentID = db.Column(db.String, nullable=True)

    avatar = db.Column(db.String, nullable=True)
    latlng = db.Column(db.String, nullable=True)
    NIK = db.Column(db.String, nullable=True)
    NIB = db.Column(db.String, nullable=True)
    NOP = db.Column(db.String, nullable=True)
    TglNOP = db.Column(db.String, nullable=False)
    klas = db.Column( db.String, nullable=True )
    wajib_pungut = db.relationship("MsWapu", foreign_keys=[WapuID], primaryjoin="vw_obyekbadan.WapuID == MsWapu.WapuID",
                                   lazy='joined')
    Nama_Badan = db.relationship("MsWPData", foreign_keys=[WPID], primaryjoin="vw_obyekbadan.WPID == MsWPData.WPID",
                                   lazy='joined')
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
            select_query = vw_obyekbadan.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_obyekbadan.ObyekBadanNo.ilike(search),
                        vw_obyekbadan.NamaBadan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_obyekbadan, args['sort']).desc()
                else:
                    sort = getattr(vw_obyekbadan, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_obyekbadan.WPID)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)


    class ListByKecUsaha(Resource):
        # method_decorators = {'get': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):
            try:
                parser = reqparse.RequestParser()
                parser.add_argument('UsahaBadan', type=str)
                args = parser.parse_args()
                query = vw_obyekbadan.query.filter_by(
                    UsahaBadan=args['UsahaBadan']
                ).all()
                result = []
                for row in query:
                    result.append({
                        "Kode": row.WPID,
                        "Nama":  f"{row.ObyekBadanNo} - {row.NamaBadan} {' (Non Aktif)' if row.TglHapus else ''}"
                    })
                return success_read(result)
            except Exception as e:
                print(e)
                return failed_read({})