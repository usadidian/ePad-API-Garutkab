from asyncio.windows_events import NULL
from datetime import datetime

import sqlalchemy
from flask import jsonify, request
from flask_restful import Resource, reqparse
from sqlalchemy import text, engine, or_, null, desc, func, literal, distinct, join
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_create, failed_create, success_delete, failed_delete, \
    success_update, success_reads_pagination, failed_reads, success_reads
from config.database import db
from config.helper import toDict
from controller.GeneralParameter import GeneralParameter
from controller.MsGrupUsaha import MsGrupUsaha
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsKecamatan import MsKecamatan
from controller.MsKelurahan import MsKelurahan
from controller.MsKlasifikasiUsaha import MsKlasifikasiUsaha
from controller.MsKota import MsKota
from controller.MsLokasiKhusus import MsLokasiKhusus
from controller.MsPegawai import MsPegawai
from controller.tblUser import tblUser
from controller.vw_obyekbadan import vw_obyekbadan
from sqlalchemy import func, distinct, and_, not_



class MsWPData(db.Model, SerializerMixin):
    # serialize_only = ('WPID',)
    # __bind_key__ = 'db_a'
    __tablename__ = 'MsWPData'
    __table_args__ = {"extend_existing": True}
    # query = db.session.query(
    #     GeneralParameter.ParamNumValue ).filter( GeneralParameter.ParamID == 'varian_epad' )
    # varian = query.first()[0]
    # if varian == 1:

    WPID = db.Column(db.Integer, primary_key=True)
    ObyekBadanNo = db.Column(db.String, nullable=False)
    NamaBadan = db.Column(db.String, nullable=False)
    GrupUsahaID = db.Column(db.String, nullable=True)
    KlasifikasiID = db.Column(db.String, nullable=True)
    LokasiID = db.Column(db.String, nullable=True)
    AlamatBadan = db.Column(db.String, nullable=False)
    KotaBadan = db.Column(db.String, nullable=False)
    KecamatanBadan = db.Column(db.Integer, nullable=False)
    KelurahanBadan = db.Column(db.Integer, nullable=True)
    RWBadan = db.Column(db.Integer, nullable=True)
    RTBadan = db.Column(db.Integer, nullable=True)
    NoTelpBadan = db.Column(db.String, nullable=True)
    NoFaxBadan = db.Column(db.String, nullable=True)

    NamaPemilik = db.Column(db.String, nullable=True)
    JabatanPemilik = db.Column(db.String, nullable=True)
    AlamatPemilik = db.Column(db.String, nullable=True)
    KotaPemilik = db.Column(db.String, nullable=True)
    KecamatanPemilik = db.Column(db.Integer, nullable=True)
    KelurahanPemilik = db.Column(db.Integer, nullable=True)
    RWPemilik = db.Column(db.Integer, nullable=True)
    RTPemilik = db.Column(db.Integer, nullable=True)
    NoTelpPemilik = db.Column(db.String, nullable=True)
    NoFaxPemilik = db.Column(db.String, nullable=True)

    TglPendaftaran = db.Column(db.TIMESTAMP, nullable=False)
    TglPengesahan = db.Column(db.TIMESTAMP, nullable=False)
    NoPengesahan = db.Column(db.String, nullable=False)
    TglPenghapusan = db.Column(db.TIMESTAMP, nullable=True, default=None)
    PetugasPendaftar = db.Column(db.String, nullable=False)
    Insidentil = db.Column(db.String, nullable=True)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)
    avatar = db.Column( db.String, nullable=True )
    latlng = db.Column( db.String, nullable=True )
    NIK = db.Column( db.String, nullable=True )
    NIB = db.Column(db.String, nullable=True)
    # doc = db.Column( db.String, nullable=True )

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
    klas = db.Column(db.String, nullable=True)

    Koordinat = ''
    JalanID = ''

    WapuID = db.Column(db.Integer, db.ForeignKey('MsWapu.WapuID'), nullable=False)

    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            # Ambil parameter dari query string
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int, required=True, help="Page number is required")
            parser.add_argument('rows', type=int, required=True, help="Number of rows is required")
            parser.add_argument('search', type=str)
            args = parser.parse_args()

            page = args['page']
            rows = args['rows']

            # Hitung offset
            offset = (page - 1) * rows

            # Query data dengan pagination dan ORDER BY
            results = (
                MsWPData.query
                .filter(MsWPData.TglPenghapusan == None)
                .order_by(MsWPData.WPID)
                .limit(rows)
                .offset(offset)
                .all()
            )

            # Menghitung total records
            total_records = MsWPData.query.filter(MsWPData.TglPenghapusan == None).count()

            # Mengubah hasil query menjadi format yang sesuai
            result = [
                {
                    'WPID': row.WPID,
                    'ObyekBadanNo': row.ObyekBadanNo,
                    'NamaBadan': row.NamaBadan  # Cukup ambil nama saja
                }
                for row in results
            ]
            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                results = (
                    MsWPData.query
                    .filter(MsWPData.TglPenghapusan == None)
                    .filter(
                        or_(
                            MsWPData.NamaBadan.ilike(search),
                            MsWPData.ObyekBadanNo.ilike(search),
                        )
                    )
                    .order_by(MsWPData.WPID)
                    .limit(rows)
                    .offset(offset)
                    .all()
                )

            # Mengubah hasil query menjadi format yang sesuai
            result = [
                {
                    'WPID': row.WPID,
                    'ObyekBadanNo': row.ObyekBadanNo,
                    'NamaBadan': row.NamaBadan  # Cukup ambil nama saja
                }
                for row in results
            ]

            # Kembalikan data dan total records
            return {
                'data': result,
                'totalRecords': total_records,
                'status_code': 1,
                'message': 'OK'
            }

    class ListAll21(Resource):
        def get(self, *args, **kwargs):
            # Ambil parameter dari query string
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int, required=True, help="Page number is required")
            parser.add_argument('rows', type=int, required=True, help="Number of rows is required")
            parser.add_argument('search', type=str)
            args = parser.parse_args()

            page = args['page']
            rows = args['rows']

            # Hitung offset
            offset = (page - 1) * rows

            query = (
                db.session.query(
                    func.left(vw_obyekbadan.ObyekBadanNo + ' - ' + vw_obyekbadan.NamaBadan, 50).label('nama'),
                    vw_obyekbadan.WPID.label('kode'),
                    vw_obyekbadan.NamaBadan
                )
                .select_from(vw_obyekbadan)  # Explicitly setting the FROM clause
                .outerjoin(
                    MsWPData,
                    and_(
                        MsWPData.ObyekBadanNo == vw_obyekbadan.ObyekBadanNo,
                        MsWPData.WPID != vw_obyekbadan.WPID
                    )  # Explicitly specifying the ON clause for the join
                )
                .filter(
                    vw_obyekbadan.TglHapus == None,
                    vw_obyekbadan.Insidentil == 'N',
                    vw_obyekbadan.TglData != None,
                    not_(
                        vw_obyekbadan.WPID.in_(
                            db.session.query(tblUser.UID).filter(tblUser.code_group == 'WP')
                        )
                    ),
                    not_(
                        vw_obyekbadan.ObyekBadanNo.in_(
                            db.session.query(distinct(MsWPData.ObyekBadanNo))
                            .filter(MsWPData.Insidentil == 'N')
                            .correlate(None)
                        )
                    )
                )
                .order_by(vw_obyekbadan.NamaBadan)
            )

            # Eksekusi query
            results = query.limit(rows).offset(offset).all()

            # Mengubah hasil query menjadi format yang sesuai
            result = [
                {
                    'WPID': row.kode,
                    'ObyekBadanNo': row.nama,
                    'NamaBadan': row.NamaBadan
                }
                for row in results
            ]

            # Tambahkan filter pencarian jika search query ada
            if args['search'] and args['search'] != 'null':
                search = f"%{args['search']}%"
                query = query.filter(
                    or_(
                        vw_obyekbadan.NamaBadan.ilike(search),
                        vw_obyekbadan.ObyekBadanNo.ilike(search),
                    )
                )

            # Menghitung total records sebelum pagination
            total_records = query.count()

            # Pagination dengan limit dan offset
            results = (
                query
                .order_by(vw_obyekbadan.NamaBadan)
                .limit(rows)
                .offset(offset)
                .all()
            )

            # Mengubah hasil query menjadi format yang sesuai
            result = [
                {
                    'WPID': row.kode,
                    'ObyekBadanNo': row.nama,
                    'NamaBadan': row.NamaBadan  # Cukup ambil nama saja
                }
                for row in results
            ]

            # Kembalikan data dan total records
            return {
                'data': result,
                'totalRecords': total_records,
                'status_code': 1,
                'message': 'OK'
            }

    # class ListAll2(Resource):
    #     def get(self, *args, **kwargs):
    #         # select_query = db.session.execute(
    #         #     f"EXEC SP_DATA_WP")
    #         # result = []
    #         # for row in select_query:
    #         #     d = {}
    #         #     for key in row.keys():
    #         #         d[key] = getattr(row, key)
    #         #     result.append(d)
    #         # return success_reads(result)
    #
    #         results = MsWPData.query.filter(MsWPData.TglPenghapusan == None).all()
    #
    #         # Mengubah hasil query menjadi format yang sesuai
    #         result = []
    #         for row in results:
    #             d = {
    #                 'WPID': row.WPID,
    #                 'ObyekBadanNo': row.ObyekBadanNo,
    #                 'NamaBadan': f"{row.NamaBadan}"
    #             }
    #             result.append(d)
    #
    #         return success_reads(result)
    # class ListAll2(Resource):
    #
    #     def get(self, *args, **kwargs):
    #         page = request.args.get('page', 1, type=int)
    #         per_page = request.args.get('per_page', 20, type=int)  # Default 20 items per halaman
    #
    #         # Melakukan query dengan pagination
    #         pagination = MsWPData.query.filter(MsWPData.TglPenghapusan == None).paginate(page=page, per_page=per_page,
    #                                                                                      error_out=False)
    #
    #         # Mengubah hasil query menjadi format yang sesuai
    #         result = []
    #         for row in pagination.items:  # Akses data yang sesuai page
    #             d = {
    #                 'WPID': row.WPID,
    #                 'ObyekBadanNo': row.ObyekBadanNo,
    #                 'NamaBadan': f"{row.ObyekBadanNo}  {row.NamaBadan}"
    #             }
    #             result.append(d)
    #
    #         # Mengembalikan hasil pagination beserta metadata
    #         return success_reads({
    #             'total': pagination.total,
    #             'pages': pagination.pages,
    #             'current_page': pagination.page,
    #             'per_page': pagination.per_page,
    #             'has_next': pagination.has_next,
    #             'has_prev': pagination.has_prev,
    #             'data': result
    #         })

    class ListAll3(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, wpid, *args, **kwargs):

            select_query = db.session.query(vw_obyekbadan, MsJenisPendapatan.ParentID, MsGrupUsaha.GrupUsaha,vw_obyekbadan.WapuID,vw_obyekbadan.WajibPungut,
                                            MsKlasifikasiUsaha.JenisUsaha, MsKlasifikasiUsaha.KlasUsaha, MsKlasifikasiUsaha.IdKlasifikasi, MsKlasifikasiUsaha.KlasifikasiID,
                                            MsLokasiKhusus.Lokasi, MsPegawai.Nama, vw_obyekbadan.klas
                                            ) \
                .outerjoin(MsJenisPendapatan, vw_obyekbadan.UsahaBadan == MsJenisPendapatan.JenisPendapatanID) \
                .outerjoin(MsGrupUsaha, MsGrupUsaha.GrupUsahaID == vw_obyekbadan.GrupUsahaID) \
                .outerjoin(MsKlasifikasiUsaha, MsKlasifikasiUsaha.IdKlasifikasi == vw_obyekbadan.KlasifikasiID) \
                .outerjoin(MsLokasiKhusus, MsLokasiKhusus.LokasiID == vw_obyekbadan.LokasiID) \
                .outerjoin(MsPegawai, MsPegawai.PegawaiID == vw_obyekbadan.PetugasPendaftar) \
                    .filter(vw_obyekbadan.WPID == wpid) \
                .first()
            if select_query:
                data = toDict(select_query.vw_obyekbadan)
                data.update({'ParentID': select_query.ParentID})
                data.update({'Insidentil': False if select_query.vw_obyekbadan.Insidentil == 'N' else True})
                data.update({'klas': False if select_query.vw_obyekbadan.klas == '2' else True})
                data.update({
                    'optionGrupUsaha': {
                        'GrupUsaha': select_query.GrupUsaha,
                        'GrupUsahaID': select_query.vw_obyekbadan.GrupUsahaID
                    }
                })
                data.update({
                    'optionKlasifikasiUsaha': {
                        'IdKlasifikasi': select_query.IdKlasifikasi or "",
                        'JenisUsaha': f"{select_query.JenisUsaha  or ''}",
                        'KlasUsaha': f"{select_query.KlasUsaha  or ''}",
                        'KlasifikasiID': select_query.KlasifikasiID  or ""
                    }
                })
                data.update({
                    'optionKlasifikasiKhusus': {
                        'Lokasi': select_query.Lokasi,
                        'LokasiID': select_query.vw_obyekbadan.KlasifikasiID
                    }
                })
                data.update({
                    'optionPetugas': {
                        'Petugas': select_query.Nama,
                        'PetugasID': select_query.vw_obyekbadan.PetugasPendaftar
                    }
                })

                data.update({
                    'optionWapu': {
                        'WajibPungut': select_query.WajibPungut,
                        'WapuID': select_query.vw_obyekbadan.WapuID
                    }
                })

                cities = db.session.query(
                    MsKota, MsKecamatan, MsKelurahan
                ).join(MsKecamatan, MsKecamatan.KotaID == MsKota.KotaID) \
                    .join(MsKelurahan, MsKelurahan.KecamatanID == MsKecamatan.KecamatanID)
                if select_query.vw_obyekbadan.Kelurahan:
                    cityBadan = cities.filter(
                        MsKelurahan.KelurahanID == select_query.vw_obyekbadan.KelurahanID).first()
                    data.update({
                        'optionCitiesBadan': {
                            'name': cityBadan.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                    + ', Kec.' + cityBadan.MsKecamatan.Kecamatan
                                    + ', Kel.' + cityBadan.MsKelurahan.Kelurahan
                                    + ' - ' + cityBadan.MsKelurahan.KodePos,
                        }
                    })
                if select_query.vw_obyekbadan.KelurahanPemilik:
                    cityOwner = cities.filter(
                        MsKelurahan.KelurahanID == select_query.vw_obyekbadan.KelurahanPemilik).first()
                    data.update({
                        'optionCitiesPemilik': {
                            'name': cityOwner.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                    + ', Kec.' + cityOwner.MsKecamatan.Kecamatan
                                    + ', Kel.' + cityOwner.MsKelurahan.Kelurahan
                                    + ' - ' + cityOwner.MsKelurahan.KodePos,
                        }
                    })

                # query = db.session.query(
                #     GeneralParameter.ParamNumValue ).filter( GeneralParameter.ParamID == 'varian_epad' )
                # varian = query.first()[0]
                # if varian == 1:
                if select_query.vw_obyekbadan.KelurahanPengelola:
                    cityManager = cities.filter(
                        MsKelurahan.KelurahanID == select_query.vw_obyekbadan.KelurahanPengelola).first()
                    data.update({
                        'optionCitiesPengelola': {
                            'name': cityManager.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                    + ', Kec.' + cityManager.MsKecamatan.Kecamatan
                                    + ', Kel.' + cityManager.MsKelurahan.Kelurahan
                                    + ' - ' + cityManager.MsKelurahan.KodePos,
                        }
                    })
                return success_reads(data)
            else:
                return success_reads({})

    class ProfileWp(Resource):
        method_decorators = {'get': [tblUser.auth_apikey]}

        def get(self, npwpd, *args, **kwargs):
            try:
                select_query = MsWPData.query.filter_by(ObyekBadanNo=npwpd).first()
                return success_reads(toDict(select_query))
            except Exception as e:
                print(e)
                return failed_reads({})



    class ListAll(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
            parser.add_argument('search', type=str)
            parser.add_argument('search_jenis', type=str)
            # parser.add_argument( 'kategori', type=str, choices=('true', 'false'), help='diisi dengan true atau false' )
            parser.add_argument('nonwp', type=str, choices=('true', 'false'), help='diisi dengan true atau false')
            parser.add_argument('klas', type=str, choices=('true', 'false'), help='diisi dengan true atau false')
            args = parser.parse_args()
            result = []
            try:
                select_query = db.session.query(MsWPData.WPID,
                                                MsWPData.ObyekBadanNo,
                                                MsWPData.NamaBadan,
                                                MsWPData.NamaPemilik,

                                                func.ltrim(
                                                    func.rtrim(
                                                        MsWPData.AlamatPemilik +
                                                        func.coalesce(literal(' ') + MsKelurahan.Kelurahan, '') +
                                                        func.coalesce(literal(' ') + MsKelurahan.KodePos, '') +
                                                        func.coalesce(literal(' ') + MsKecamatan.Kecamatan,
                                                                      literal(' - ') + MsKota.Kota)
                                                    )
                                                ).label('vw_al_usaha'),

                                                MsWPData.TglPengesahan,
                                                MsWPData.Insidentil,MsWPData.klas,
                                                MsWPData.TglPendaftaran,
                                                func.coalesce(MsWPData.avatar, '').label('avatar'),
                                                func.coalesce(MsWPData.latlng, '').label('latlng')
                                                ) \
                .join(MsKota, MsWPData.KotaBadan == MsKota.KotaID)\
                .join(MsKecamatan, MsWPData.KecamatanBadan == MsKecamatan.KecamatanID)\
                .join(MsKelurahan, MsWPData.KelurahanBadan == MsKelurahan.KelurahanID)\
                    .filter(
                    MsWPData.TglPenghapusan == None
                ).distinct(MsWPData.WPID)


                # SEARCH_JENIS
                # if args['search_jenis']:
                #     select_query = select_query.filter(
                #         vw_obyekbadan.JenisPendapatanID == args['search_jenis']
                #     )

                # # kategori
                # if args['kategori'] or args['kategori'] == "true":
                #     select_query = select_query.filter( vw_obyekbadan.SelfAssesment == 'Y' )
                # # else:
                # #     select_query = select_query.filter( vw_obyekbadan.SelfAssesment == 'N' )

                # nonwp
                if args['nonwp'] or args['nonwp'] == "true":
                    select_query = select_query.filter(MsWPData.Insidentil == 'Y')
                else:
                    select_query = select_query.filter(MsWPData.Insidentil == 'N')

                if args['klas'] or args['klas'] == "true":
                    select_query = select_query.filter(MsWPData.klas == '1')
                else:
                    select_query = select_query.filter(MsWPData.klas == '2')



                # SEARCH
                if args['search'] and args['search'] != 'null':
                    search = '%{0}%'.format(args['search'])
                    select_query = select_query.filter(
                        or_(MsWPData.NamaBadan.ilike(search),
                            MsWPData.NamaPemilik.ilike(search),
                            MsWPData.ObyekBadanNo.ilike(search),
                            # vw_obyekbadan.NamaJenisPendapatan.ilike(search)
                            ),
                    )

                # SORT
                if args['sort']:
                    if args['sort_dir'] == "desc":
                        sort = getattr(MsWPData, args['sort']).desc()
                    else:
                        sort = getattr(MsWPData, args['sort']).asc()
                    select_query = select_query.order_by(sort)
                else:
                    select_query = select_query.order_by(MsWPData.DateUpd.desc())

                # PAGINATION
                page = args['page'] if args['page'] else 1
                length = args['length'] if args['length'] else 10
                lengthLimit = length if length < 101 else 100
                query_execute = select_query.paginate(page, lengthLimit)

                # print(query_execute.items)
                for row in query_execute.items:
                    d = {}
                    for key in row.keys():
                        # print(key,  getattr(row, key))
                        d[key] = getattr(row, key)
                    # d['badge'] = 'Baru' if row.TglData == None else ''
                    result.append(d)
                return success_reads_pagination(query_execute, result)
            except Exception as e:
                print(e)
                return failed_reads(result)

    # class MsWPData(Resource):
        def post(self, *args, **kwargs):
            query = db.session.query(
                GeneralParameter.ParamNumValue ).filter( GeneralParameter.ParamID == 'varian_epad' )
            varian = query.first()[0]
            if varian == 1:
                parser = reqparse.RequestParser()
                parser.add_argument('ObyekBadanNo', type=str)
                parser.add_argument('NamaBadan', type=str)
                parser.add_argument('GrupUsahaID', type=str)
                parser.add_argument('KlasifikasiID', type=str)
                parser.add_argument('LokasiID', type=str)
                parser.add_argument('AlamatBadan', type=str)
                parser.add_argument('KotaBadan', type=str)
                parser.add_argument('KecamatanBadan', type=str)
                parser.add_argument('KelurahanBadan', type=str)
                parser.add_argument('RWBadan', type=str)
                parser.add_argument('RTBadan', type=str)
                parser.add_argument('NoTelpBadan', type=str)
                parser.add_argument('NoFaxBadan', type=str)
                parser.add_argument('NamaPemilik', type=str)
                parser.add_argument('JabatanPemilik', type=str)
                parser.add_argument('AlamatPemilik', type=str)
                parser.add_argument('KotaPemilik', type=str)
                parser.add_argument('KecamatanPemilik', type=str)
                parser.add_argument('KelurahanPemilik', type=str)
                parser.add_argument('RWPemilik', type=str)
                parser.add_argument('RTPemilik', type=str)
                parser.add_argument('NoTelpPemilik', type=str)
                parser.add_argument('NoFaxPemilik', type=str)
                parser.add_argument('TglPendaftaran', type=str)
                parser.add_argument('TglPengesahan', type=str)
                parser.add_argument('NoPengesahan', type=str)
                parser.add_argument('TglPenghapusan', type=str)
                parser.add_argument('PetugasPendaftar', type=str)
                parser.add_argument('Insidentil', type=str)
                parser.add_argument('UserUpd', type=str)
                parser.add_argument('DateUpd', type=str)
                parser.add_argument('NamaPengelola', type=str)
                parser.add_argument('AlamatPengelola', type=str)
                parser.add_argument('KotaPengelola', type=str)
                parser.add_argument('KecamatanPengelola', type=str)
                parser.add_argument('KelurahanPengelola', type=str)
                parser.add_argument('RWPengelola', type=str)
                parser.add_argument('RTPengelola', type=str)
                parser.add_argument('NoTelpPengelola', type=str)
                parser.add_argument('NoFaxPengelola', type=str)
                parser.add_argument('NPWPPemilik', type=str)
                parser.add_argument('NPWPPengelola', type=str)
                parser.add_argument('NPWPUsaha', type=str)
            else:
                parser = reqparse.RequestParser()
                parser.add_argument( 'ObyekBadanNo', type=str )
                parser.add_argument( 'NamaBadan', type=str )
                parser.add_argument( 'GrupUsahaID', type=str )
                parser.add_argument( 'KlasifikasiID', type=str )
                parser.add_argument( 'LokasiID', type=str )
                parser.add_argument( 'AlamatBadan', type=str )
                parser.add_argument( 'KotaBadan', type=str )
                parser.add_argument( 'KecamatanBadan', type=str )
                parser.add_argument( 'KelurahanBadan', type=str )
                parser.add_argument( 'RWBadan', type=str )
                parser.add_argument( 'RTBadan', type=str )
                parser.add_argument( 'NoTelpBadan', type=str )
                parser.add_argument( 'NoFaxBadan', type=str )
                parser.add_argument( 'NamaPemilik', type=str )
                parser.add_argument( 'JabatanPemilik', type=str )
                parser.add_argument( 'AlamatPemilik', type=str )
                parser.add_argument( 'KotaPemilik', type=str )
                parser.add_argument( 'KecamatanPemilik', type=str )
                parser.add_argument( 'KelurahanPemilik', type=str )
                parser.add_argument( 'RWPemilik', type=str )
                parser.add_argument( 'RTPemilik', type=str )
                parser.add_argument( 'NoTelpPemilik', type=str )
                parser.add_argument( 'NoFaxPemilik', type=str )
                parser.add_argument( 'TglPendaftaran', type=str )
                parser.add_argument( 'TglPengesahan', type=str )
                parser.add_argument( 'NoPengesahan', type=str )
                parser.add_argument( 'TglPenghapusan', type=str )
                parser.add_argument( 'PetugasPendaftar', type=str )
                parser.add_argument( 'Insidentil', type=str )
                parser.add_argument( 'UserUpd', type=str )
                parser.add_argument( 'DateUpd', type=str )

            uid = kwargs['claim']["UID"]
            print(uid)

            args = parser.parse_args()
            result = db.session.execute(
                f"exec [SP_NPWPD] '{args['KecamatanBadan']}','{args['KelurahanBadan']}','{args['TglPengesahan']}'")

            result2 = []
            for row in result:
                result2.append(row)
                # print(row[0], row[1])
                # print(row['ObyekBadanNo'])
            ObyekBadanNo = result2[0][0]
            NoPengesahan = result2[0][1]

            query = db.session.query(
                GeneralParameter.ParamNumValue ).filter( GeneralParameter.ParamID == 'varian_epad' )
            varian = query.first()[0]
            if varian == 1:
                add_record = MsWPData(
                    # WPID=args['WPID'],

                    NamaBadan=args['NamaBadan'],
                    GrupUsahaID=args['GrupUsahaID'],
                    KlasifikasiID=args['KlasifikasiID'],
                    LokasiID=args['LokasiID'],
                    AlamatBadan=args['AlamatBadan'],
                    KotaBadan=args['KotaBadan'],
                    KecamatanBadan=args['KecamatanBadan'],
                    KelurahanBadan=args['KelurahanBadan'],
                    RWBadan=args['RWBadan'],
                    RTBadan=args['RTBadan'],
                    NoTelpBadan=args['NoTelpBadan'],
                    NoFaxBadan=args['NoFaxBadan'],
                    NamaPemilik=args['NamaPemilik'],
                    JabatanPemilik=args['JabatanPemilik'],
                    AlamatPemilik=args['AlamatPemilik'],
                    KotaPemilik=args['KotaPemilik'],
                    KecamatanPemilik=args['KecamatanPemilik'],
                    KelurahanPemilik=args['KelurahanPemilik'],
                    RWPemilik=args['RWPemilik'],
                    RTPemilik=args['RTPemilik'],
                    NoTelpPemilik=args['NoTelpPemilik'],
                    NoFaxPemilik=args['NoFaxPemilik'],
                    TglPendaftaran=args['TglPendaftaran'],
                    TglPengesahan=args['TglPengesahan'],
                    NoPengesahan=NoPengesahan,
                    TglPenghapusan=sqlalchemy.sql.null(),
                    PetugasPendaftar=args['PetugasPendaftar'],
                    Insidentil=args['Insidentil'],
                    UserUpd=uid,
                    DateUpd=datetime.now(),
                    NamaPengelola=args['NamaPengelola'],
                    AlamatPengelola=args['AlamatPengelola'],
                    KotaPengelola=args['KotaPengelola'],
                    KecamatanPengelola=args['KecamatanPengelola'],
                    KelurahanPengelola=args['KelurahanPengelola'],
                    RWPengelola=args['RWPengelola'],
                    RTPengelola=args['RTPengelola'],
                    NoTelpPengelola=args['NoTelpPengelola'],
                    NoFaxPengelola=args['NoFaxPengelola'],
                    NPWPPemilik=args['NPWPPemilik'],
                    NPWPPengelola=args['NPWPPengelola'],
                    NPWPUsaha=args['NPWPUsaha'],
                    ObyekBadanNo=ObyekBadanNo
                )
            else:
                add_record = MsWPData(
                    # WPID=args['WPID'],

                    NamaBadan=args['NamaBadan'],
                    GrupUsahaID=args['GrupUsahaID'],
                    KlasifikasiID=args['KlasifikasiID'],
                    LokasiID=args['LokasiID'],
                    AlamatBadan=args['AlamatBadan'],
                    KotaBadan=args['KotaBadan'],
                    KecamatanBadan=args['KecamatanBadan'],
                    KelurahanBadan=args['KelurahanBadan'],
                    RWBadan=args['RWBadan'],
                    RTBadan=args['RTBadan'],
                    NoTelpBadan=args['NoTelpBadan'],
                    NoFaxBadan=args['NoFaxBadan'],
                    NamaPemilik=args['NamaPemilik'],
                    JabatanPemilik=args['JabatanPemilik'],
                    AlamatPemilik=args['AlamatPemilik'],
                    KotaPemilik=args['KotaPemilik'],
                    KecamatanPemilik=args['KecamatanPemilik'],
                    KelurahanPemilik=args['KelurahanPemilik'],
                    RWPemilik=args['RWPemilik'],
                    RTPemilik=args['RTPemilik'],
                    NoTelpPemilik=args['NoTelpPemilik'],
                    NoFaxPemilik=args['NoFaxPemilik'],
                    TglPendaftaran=args['TglPendaftaran'],
                    TglPengesahan=args['TglPengesahan'],
                    NoPengesahan=NoPengesahan,
                    TglPenghapusan=sqlalchemy.sql.null(),
                    PetugasPendaftar=args['PetugasPendaftar'],
                    Insidentil=args['Insidentil'],
                    UserUpd=uid,
                    DateUpd=datetime.now(),
                    ObyekBadanNo=ObyekBadanNo
                )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsWPData.query.filter_by(WPID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('ObyekBadanNo', type=str)
            parser.add_argument('NamaBadan', type=str)
            parser.add_argument('GrupUsahaID', type=str)
            parser.add_argument('KlasifikasiID', type=str)
            parser.add_argument('LokasiID', type=str)
            parser.add_argument('AlamatBadan', type=str)
            parser.add_argument('KotaBadan', type=str)
            parser.add_argument('KecamatanBadan', type=str)
            parser.add_argument('KelurahanBadan', type=str)
            parser.add_argument('RWBadan', type=str)
            parser.add_argument('RTBadan', type=str)
            parser.add_argument('NoTelpBadan', type=str)
            parser.add_argument('NoFaxBadan', type=str)
            parser.add_argument('NamaPemilik', type=str)
            parser.add_argument('JabatanPemilik', type=str)
            parser.add_argument('AlamatPemilik', type=str)
            parser.add_argument('KotaPemilik', type=str)
            parser.add_argument('KecamatanPemilik', type=str)
            parser.add_argument('KelurahanPemilik', type=str)
            parser.add_argument('RWPemilik', type=str)
            parser.add_argument('RTPemilik', type=str)
            parser.add_argument('NoTelpPemilik', type=str)
            parser.add_argument('NoFaxPemilik', type=str)
            parser.add_argument('TglPendaftaran', type=str)
            parser.add_argument('TglPengesahan', type=str)
            parser.add_argument('NoPengesahan', type=str)
            parser.add_argument('TglPenghapusan', type=str)
            parser.add_argument('PetugasPendaftar', type=str)
            parser.add_argument('Insidentil', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)
            parser.add_argument('NamaPengelola', type=str)
            parser.add_argument('AlamatPengelola', type=str)
            parser.add_argument('KotaPengelola', type=str)
            parser.add_argument('KecamatanPengelola', type=str)
            parser.add_argument('KelurahanPengelola', type=str)
            parser.add_argument('RWPengelola', type=str)
            parser.add_argument('RTPengelola', type=str)
            parser.add_argument('NoTelpPengelola', type=str)
            parser.add_argument('NoFaxPengelola', type=str)
            parser.add_argument('NPWPPemilik', type=str)
            parser.add_argument('NPWPPengelola', type=str)
            parser.add_argument('NPWPUsaha', type=str)

            uid = kwargs['claim']["UID"]
            print(uid)

            args = parser.parse_args()
            try:
                select_query = MsWPData.query.filter_by(WPID=id).first()
                if select_query:
                    if args['NamaBadan']:
                        select_query.NamaBadan = f"{args['NamaBadan']}"
                    if args['GrupUsahaID']:
                        select_query.GrupUsahaID = args['GrupUsahaID']
                    if args['KlasifikasiID']:
                        select_query.KlasifikasiID = args['KlasifikasiID']
                    if args['LokasiID']:
                        select_query.LokasiID = args['LokasiID']
                    if args['AlamatBadan']:
                        select_query.AlamatBadan = args['AlamatBadan']
                    if args['KotaBadan']:
                        select_query.KotaBadan = args['KotaBadan']
                    if args['KecamatanBadan']:
                        select_query.KecamatanBadan = args['KecamatanBadan']
                    if args['KelurahanBadan']:
                        select_query.KelurahanBadan = args['KelurahanBadan']
                    if args['RWBadan'] == 'null':
                        select_query.RWBadan = None
                    else :
                        select_query.RWBadan = args['RWBadan']
                    if args['RTBadan'] == 'null':
                        select_query.RTBadan = None
                    else :
                        select_query.RTBadan = args['RTBadan']
                    if args['NoTelpBadan']:
                        select_query.NoTelpBadan = args['NoTelpBadan']
                    if args['NoFaxBadan']:
                        select_query.NoFaxBadan = args['NoFaxBadan']
                    if args['NamaPemilik']:
                        select_query.NamaPemilik = args['NamaPemilik']
                    if args['JabatanPemilik']:
                        select_query.JabatanPemilik = args['JabatanPemilik']
                    if args['AlamatPemilik']:
                        select_query.AlamatPemilik = args['AlamatPemilik']
                    if args['KotaPemilik']:
                        select_query.KotaPemilik = args['KotaPemilik']
                    if args['KecamatanPemilik']:
                        select_query.KecamatanPemilik = args['KecamatanPemilik']
                    if args['KelurahanPemilik']:
                        select_query.KelurahanPemilik = args['KelurahanPemilik']
                    if args['RWPemilik'] == 'null':
                        select_query.RWPemilik = None
                    else:
                        select_query.RWPemilik = args['RWPemilik']
                    if args['RTPemilik'] == 'null':
                        select_query.RTPemilik = None
                    else :
                        select_query.RTPemilik = args['RTPemilik']
                    if args['NoTelpPemilik']:
                        select_query.NoTelpPemilik = args['NoTelpPemilik']
                    if args['NoFaxPemilik']:
                        select_query.NoFaxPemilik = args['NoFaxPemilik']
                    if args['TglPendaftaran']:
                        select_query.TglPendaftaran = args['TglPendaftaran']
                    if args['TglPengesahan']:
                        select_query.TglPengesahan = args['TglPengesahan']
                    if args['NoPengesahan']:
                        select_query.NoPengesahan = args['NoPengesahan']
                    select_query.TglPenghapusan = sqlalchemy.sql.null()
                    if args['PetugasPendaftar']:
                        select_query.PetugasPendaftar = args['PetugasPendaftar']
                    if args['Insidentil']:
                        select_query.Insidentil = args['Insidentil']
                    select_query.UserUpd = uid
                    select_query.DateUpd = datetime.now()
                    if args['NamaPengelola']:
                        select_query.NamaPengelola = args['NamaPengelola']
                    if args['AlamatPengelola']:
                        select_query.AlamatPengelola = args['AlamatPengelola']
                    if args['KotaPengelola']:
                        select_query.KotaPengelola = args['KotaPengelola']
                    if args['KecamatanPengelola']:
                        select_query.KecamatanPengelola = args['KecamatanPengelola']
                    if args['KelurahanPengelola']:
                        select_query.KelurahanPengelola = args['KelurahanPengelola']
                    if args['RWPengelola'] == 'null':
                        select_query.RWPengelola = None
                    else :
                        select_query.RWPengelola = args['RWPengelola']
                    if args['RTPengelola'] =='null':
                        select_query.RTPengelola = None
                    else :
                        select_query.RTPengelola = args['RTPengelola']
                    if args['NoTelpPengelola']:
                        select_query.NoTelpPengelola = args['NoTelpPengelola']
                    if args['NoFaxPengelola']:
                        select_query.NoFaxPengelola = args['NoFaxPengelola']
                    if args['NPWPPemilik']:
                        select_query.NPWPPemilik = args['NPWPPemilik']
                    if args['NPWPPengelola']:
                        select_query.NPWPPengelola = args['NPWPPengelola']
                    if args['NPWPUsaha']:
                        select_query.NPWPUsaha = args['NPWPUsaha']
                    # # select_query.ObyekBadanNo = args['ObyekBadanNo']
                    db.session.commit()
                    # return success_create({'id': id})
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_create({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsWPData.query.filter_by(WPID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})

# class MsWPData2(db.Model, SerializerMixin):
#     __bind_key__ = 'db_b'
#     __tablename__ = 'MsWPData'
#     __table_args__ = {"useexisting": True}
#     WPID = db.Column( db.Integer, primary_key=True )
#     ObyekBadanNo = db.Column( db.String, nullable=False )
#     NamaBadan = db.Column( db.String, nullable=False )
#     GrupUsahaID = db.Column( db.String, nullable=False )
#     KlasifikasiID = db.Column( db.String, nullable=False )
#     LokasiID = db.Column( db.String, nullable=False )
#     AlamatBadan = db.Column( db.String, nullable=False )
#     KotaBadan = db.Column( db.String, nullable=False )
#     KecamatanBadan = db.Column( db.Integer, nullable=False )
#     KelurahanBadan = db.Column( db.Integer, nullable=False )
#     RWBadan = db.Column( db.Integer, nullable=True )
#     RTBadan = db.Column( db.Integer, nullable=True )
#     NoTelpBadan = db.Column( db.String, nullable=False )
#     NoFaxBadan = db.Column( db.String, nullable=False )
#
#     NamaPemilik = db.Column( db.String, nullable=False )
#     JabatanPemilik = db.Column( db.String, nullable=False )
#     AlamatPemilik = db.Column( db.String, nullable=False )
#     KotaPemilik = db.Column( db.String, nullable=False )
#     KecamatanPemilik = db.Column( db.Integer, nullable=False )
#     KelurahanPemilik = db.Column( db.Integer, nullable=False )
#     RWPemilik = db.Column( db.Integer, nullable=True )
#     RTPemilik = db.Column( db.Integer, nullable=True )
#     NoTelpPemilik = db.Column( db.String, nullable=False )
#     NoFaxPemilik = db.Column( db.String, nullable=False )
#
#     TglPendaftaran = db.Column( db.TIMESTAMP, nullable=False )
#     TglPengesahan = db.Column( db.TIMESTAMP, nullable=False )
#     NoPengesahan = db.Column( db.String, nullable=False )
#     TglPenghapusan = db.Column( db.TIMESTAMP, nullable=True, default=NULL )
#     PetugasPendaftar = db.Column( db.String, nullable=False )
#     Insidentil = db.Column( db.String, nullable=False )
#     Koordinat = db.Column( db.String, nullable=True )
#     JalanID = db.Column( db.Integer, nullable=True )
#     UserUpd = db.Column( db.String, nullable=False )
#     DateUpd = db.Column( db.TIMESTAMP, nullable=False )
#     avatar = db.Column( db.String, nullable=True )
#     latlng = db.Column( db.String, nullable=True )
#     NIK = db.Column( db.String, nullable=True )