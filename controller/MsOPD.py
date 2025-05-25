from asyncio.windows_events import NULL
from datetime import datetime

import sqlalchemy
from flask import jsonify, request
from flask_restful import Resource, reqparse
from sqlalchemy import text, engine, or_, null, desc
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
from controller.MsWP import MsWP
from controller.tblUser import tblUser
from controller.vw_obyekbadan import vw_obyekbadan

class MsOPD(db.Model):
    __tablename__ = 'MsOPD'

    OPDID = db.Column(db.Integer, primary_key=True)
    WapuID = db.Column(db.Integer)
    WPID = db.Column(db.Integer)
    UsahaBadan = db.Column(db.String, nullable=False)
    NOP = db.Column(db.String)
    TglNOP = db.Column(db.DateTime)
    TglPendataan = db.Column(db.DateTime, nullable=True)
    NamaOPD = db.Column(db.String)
    GrupUsahaID = db.Column(db.Integer)
    KlasifikasiID = db.Column(db.Integer)
    LokasiID = db.Column(db.Integer)
    AlamatOPD = db.Column(db.String)
    KotaOPD = db.Column(db.String)
    KecamatanOPD = db.Column(db.String)
    KelurahanOPD = db.Column(db.String)
    RWOPD = db.Column(db.Integer)
    RTOPD = db.Column(db.Integer)
    NoTelpOPD = db.Column(db.String)
    TglPendaftaran = db.Column(db.DateTime)
    TglPenghapusan = db.Column(db.DateTime)
    Insidentil = db.Column(db.Boolean)
    UserUpd = db.Column(db.String)
    DateUpd = db.Column(db.DateTime)
    NamaPengelola = db.Column(db.String)
    AlamatPengelola = db.Column(db.String)
    KotaPengelola = db.Column(db.String)
    KecamatanPengelola = db.Column(db.String)
    KelurahanPengelola = db.Column(db.String)
    RWPengelola = db.Column(db.Integer)
    RTPengelola = db.Column(db.Integer)
    NoTelpPengelola = db.Column(db.String)
    NPWPPengelola = db.Column(db.String)
    NPWPUsaha = db.Column(db.String)
    avatar = db.Column(db.String)
    latlng = db.Column(db.String)

    
    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT OPDID,NOP,NamaBadan,NamaJenisPendapatan,vw_al_usaha,TglSah,NamaLokasi,UsahaBadan AS JenisPendapatanID, "
                f"Insidentil FROM vw_obyekbadan "
                f"WHERE  OPDID IN (select distinct OPDID from vw_obyekbadan)  "
                f"ORDER BY substring(NOP,5,8) DESC")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll3(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, opdid, *args, **kwargs):
            parser = reqparse.RequestParser()
            args = parser.parse_args()
            print(kwargs['claim'])
            wapuid = kwargs['claim']["WapuID"]
            # wpid = kwargs['claim']["WPID"]

            select_query = db.session.query(vw_obyekbadan, MsJenisPendapatan.ParentID, MsGrupUsaha.GrupUsaha,vw_obyekbadan.WPID,vw_obyekbadan.NamaBadan,vw_obyekbadan.WapuID,vw_obyekbadan.WajibPungut,
                                            MsKlasifikasiUsaha.JenisUsaha, MsKlasifikasiUsaha.KlasUsaha, MsKlasifikasiUsaha.IdKlasifikasi, MsKlasifikasiUsaha.KlasifikasiID,
                                            MsLokasiKhusus.Lokasi,  vw_obyekbadan.klas
                                            ) \
                .join(MsJenisPendapatan, vw_obyekbadan.UsahaBadan == MsJenisPendapatan.JenisPendapatanID) \
                .outerjoin(MsGrupUsaha, MsGrupUsaha.GrupUsahaID == vw_obyekbadan.GrupUsahaID) \
                .outerjoin(MsKlasifikasiUsaha, MsKlasifikasiUsaha.IdKlasifikasi == vw_obyekbadan.KlasifikasiID) \
                .outerjoin(MsLokasiKhusus, MsLokasiKhusus.LokasiID == vw_obyekbadan.LokasiID) \
                    .filter(vw_obyekbadan.OPDID == opdid, vw_obyekbadan.WapuID == wapuid) \
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
                # data.update({
                #     'optionPetugas': {
                #         'Petugas': select_query.Nama,
                #         'PetugasID': select_query.vw_obyekbadan.PetugasPendaftar
                #     }
                # })

                data.update({
                    'optionWapu': {
                        'WajibPungut': select_query.WajibPungut,
                        'WapuID': select_query.vw_obyekbadan.WapuID
                    }
                })

                data.update({
                    'optionWajibPajak': {
                        'NamaBadan': select_query.NamaBadan,
                        'WPID': select_query.vw_obyekbadan.WPID
                    }
                })

                cities = db.session.query(
                    MsKota, MsKecamatan, MsKelurahan
                ).join(MsKecamatan, MsKecamatan.KotaID == MsKota.KotaID) \
                    .join(MsKelurahan, MsKelurahan.KecamatanID == MsKecamatan.KecamatanID)
                if select_query.vw_obyekbadan.KelurahanOPD:
                    cityBadan = cities.filter(
                        MsKelurahan.KelurahanID == select_query.vw_obyekbadan.KelurahanOPD).first()
                    data.update({
                        'optionCitiesBadan': {
                            'name': cityBadan.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                    + ', Kec.' + cityBadan.MsKecamatan.Kecamatan
                                    + ', Kel.' + cityBadan.MsKelurahan.Kelurahan
                                    + ' - ' + cityBadan.MsKelurahan.KodePos,
                        }
                    })
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

        def get(self, nop, *args, **kwargs):
            try:
                select_query = MsOPD.query.filter_by(NOP=nop).first()
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
            parser.add_argument('searchWP', type=str)
            parser.add_argument('filter_jenis', type=str)
            parser.add_argument('filter_wapuid', type=str)
            parser.add_argument('filter_wpid', type=str)
            parser.add_argument( 'kategori', type=str, choices=('true', 'false'), help='diisi dengan true atau false' )
            parser.add_argument('nonwp', type=str, choices=('true', 'false'), help='diisi dengan true atau false')
            parser.add_argument('klas', type=str, choices=('true', 'false'), help='diisi dengan true atau false')
            args = parser.parse_args()
            result = []
            try:

                subquery_wpid = db.session.query(MsOPD.WPID).subquery()
                select_query = db.session.query(vw_obyekbadan.WPID, vw_obyekbadan.NamaBadan, vw_obyekbadan.OPDID,
                                                vw_obyekbadan.WapuID,vw_obyekbadan.WajibPungut,vw_obyekbadan.klas,
                                                vw_obyekbadan.NamaOPD, vw_obyekbadan.TglPendataan,vw_obyekbadan.TglPendaftaran,
                                                vw_obyekbadan.NamaJenisPendapatan, vw_obyekbadan.vw_al_usaha,
                                                vw_obyekbadan.KecamatanOPD, vw_obyekbadan.NamaLokasi,
                                                vw_obyekbadan.JenisPendapatanID, vw_obyekbadan.Insidentil,
                                                vw_obyekbadan.SelfAssesment, vw_obyekbadan.avatar, vw_obyekbadan.latlng,
                                                vw_obyekbadan.NOP,vw_obyekbadan.TglNOP,vw_obyekbadan.TglPenghapusan
                                                ) \
                  .distinct()\
                .filter(vw_obyekbadan.TglHapusOPD == None, vw_obyekbadan.WPID.in_(subquery_wpid))

                # SEARCH_JENIS
                if args['filter_jenis']:
                    select_query = select_query.filter(
                        vw_obyekbadan.JenisPendapatanID == args['filter_jenis']
                    )

                if args['filter_wapuid']:
                    select_query = select_query.filter(
                        vw_obyekbadan.WapuID == args['filter_wapuid']
                    )

                if args['filter_wpid']:
                    select_query = select_query.filter(
                        vw_obyekbadan.WPID == args['filter_wpid']
                    )

                # kategori
                if args['kategori'] or args['kategori'] == "true":
                    select_query = select_query.filter( vw_obyekbadan.SelfAssesment == 'Y' )
                # else:
                #     select_query = select_query.filter( vw_obyekbadan.SelfAssesment == 'N' )

                # nonwp
                if args['nonwp'] or args['nonwp'] == "true":
                    select_query = select_query.filter(vw_obyekbadan.Insidentil == 'Y')
                else:
                    select_query = select_query.filter(vw_obyekbadan.Insidentil == 'N')

                if args['klas'] or args['klas'] == "true":
                    select_query = select_query.filter(vw_obyekbadan.klas == '1')
                else:
                    select_query = select_query.filter(vw_obyekbadan.klas == '2')

                # SEARCH
                if args['search'] and args['search'] != 'null':
                    search = '%{0}%'.format(args['search'])
                    select_query = select_query.filter(
                        or_(vw_obyekbadan.NamaOPD.ilike(search),
                            vw_obyekbadan.NOP.ilike(search),
                            vw_obyekbadan.NamaJenisPendapatan.ilike(search)),
                    )

                if args['searchWP'] and args['searchWP'] != 'null':
                    searchWP = '%{0}%'.format(args['searchWP'])
                    select_query = select_query.filter(
                        (vw_obyekbadan.NamaBadan.ilike(searchWP)
                            )
                    )

                # SORT
                if args['sort']:
                    if args['sort_dir'] == "desc":
                        sort = getattr(vw_obyekbadan, args['sort']).desc()
                    else:
                        sort = getattr(vw_obyekbadan, args['sort']).asc()
                    select_query = select_query.order_by(sort)
                else:
                    select_query = select_query.order_by(vw_obyekbadan.OPDID.desc(),vw_obyekbadan.TglPendataan.desc())

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
                    d['badge'] = 'Baru' if row.TglPendataan == None else ''
                    result.append(d)
                return success_reads_pagination(query_execute, result)
            except Exception as e:
                print(e)
                return failed_reads(result)