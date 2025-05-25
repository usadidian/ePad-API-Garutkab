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
from config.helper import toDict, logger
from controller.MsGrupUsaha import MsGrupUsaha
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsKecamatan import MsKecamatan
from controller.MsKelurahan import MsKelurahan
from controller.MsKlasifikasiUsaha import MsKlasifikasiUsaha
from controller.MsKota import MsKota
from controller.MsLokasiKhusus import MsLokasiKhusus
from controller.MsPegawai import MsPegawai
from controller.MsWP import MsWP
from controller.MsWPO import MsWPO
from controller.tblUser import tblUser
from controller.w_obyekbadanwpo import vw_obyekbadanwpo


class MsWPOData(db.Model, SerializerMixin):
    # serialize_only = ('WPID',)
    __tablename__ = 'MsWPOData'
    WPID = db.Column(db.Integer, primary_key=True)
    NamaBadan = db.Column(db.String, nullable=False)
    GrupUsahaID = db.Column(db.String, nullable=False)
    KlasifikasiID = db.Column(db.String, nullable=False)
    LokasiID = db.Column(db.String, nullable=False)
    AlamatBadan = db.Column(db.String, nullable=False)
    KotaBadan = db.Column(db.String, nullable=False)
    KecamatanBadan = db.Column(db.Integer, nullable=False)
    KelurahanBadan = db.Column(db.Integer, nullable=True)
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
    Insidentil = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)
    avatar = db.Column(db.String, nullable=True)
    latlng = db.Column(db.String, nullable=True)
    NIK = db.Column(db.String, nullable=True)


    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT OBN,OPDID,ObyekBadanNo,NamaBadan,NamaJenisPendapatan,vw_al_usaha,TglSah,(CASE WHEN Kota"
                f" = 'Kabupaten Ciamis' THEN Kecamatan ELSE '' END) AS Kecamatan, NamaLokasi,UsahaBadan AS JenisPendapatanId, "
                f"Insidentil FROM vw_obyekbadanwpo "
                f"WHERE  OPDID IN (select distinct OPDID from vw_obyekbadanwpo where TglHapus IS NULL)  "
                f"ORDER BY substring(obyekbadanno,5,8) DESC")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll3(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, wpid, *args, **kwargs):
            select_query = db.session.query(vw_obyekbadanwpo, vw_obyekbadanwpo.OPDID, vw_obyekbadanwpo.WPID, MsJenisPendapatan.ParentID, MsGrupUsaha.GrupUsaha,
                                            MsKlasifikasiUsaha.JenisUsaha, MsKlasifikasiUsaha.KlasUsaha, vw_obyekbadanwpo.NIK,
                                            MsLokasiKhusus.Lokasi, vw_obyekbadanwpo.avatar, vw_obyekbadanwpo.latlng
                                            ) \
                .outerjoin(MsJenisPendapatan, vw_obyekbadanwpo.UsahaBadan == MsJenisPendapatan.JenisPendapatanID) \
                .outerjoin(MsGrupUsaha, MsGrupUsaha.GrupUsahaID == vw_obyekbadanwpo.GrupUsahaID) \
                .outerjoin(MsKlasifikasiUsaha, MsKlasifikasiUsaha.KlasifikasiID == vw_obyekbadanwpo.KlasifikasiID) \
                .outerjoin(MsLokasiKhusus, MsLokasiKhusus.LokasiID == vw_obyekbadanwpo.LokasiID) \
                .filter(vw_obyekbadanwpo.WPID == wpid) \
                .first()
            if select_query:


                data = toDict(select_query.vw_obyekbadanwpo)
                select_obyekbadan = vw_obyekbadanwpo.query.filter_by(WPID=wpid).all()
                ob = []
                for row in select_obyekbadan:
                    ob.append({'NamaJenisPendapatan': row.NamaJenisPendapatan})
                data.update({'ObyekPajak': ob})
                data.update({'ParentID': select_query.ParentID})
                data.update({'Insidentil': False if select_query.vw_obyekbadanwpo.Insidentil == 'N' else True})
                data.update({
                    'optionGrupUsaha': {
                        'GrupUsaha': select_query.GrupUsaha,
                        'GrupUsahaID': select_query.vw_obyekbadanwpo.GrupUsahaID
                    }
                })
                data.update({
                    'optionKlasifikasiUsaha': {
                        'Klasifikasi': f"{select_query.JenisUsaha} - {select_query.KlasUsaha}" if select_query.KlasUsaha else '',
                        'KlasifikasiID': select_query.vw_obyekbadanwpo.KlasifikasiID
                    }
                })
                data.update({
                    'optionKlasifikasiKhusus': {
                        'Lokasi': select_query.Lokasi,
                        'LokasiID': select_query.vw_obyekbadanwpo.KlasifikasiID
                    }
                })

                cities = db.session.query(
                    MsKota, MsKecamatan, MsKelurahan
                ).join(MsKecamatan, MsKecamatan.KotaID == MsKota.KotaID) \
                    .join(MsKelurahan, MsKelurahan.KecamatanID == MsKecamatan.KecamatanID)
                if select_query.vw_obyekbadanwpo.Kelurahan:
                    cityBadan = cities.filter(
                        MsKelurahan.KelurahanID == select_query.vw_obyekbadanwpo.KelurahanID).first()
                    data.update({
                        'optionCitiesBadan': {
                            'name': cityBadan.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                    + ', Kec.' + cityBadan.MsKecamatan.Kecamatan
                                    + ', Kel.' + cityBadan.MsKelurahan.Kelurahan
                                    + ' - ' + cityBadan.MsKelurahan.KodePos,
                        }
                    })
                if select_query.vw_obyekbadanwpo.KelurahanPemilik:
                    cityOwner = cities.filter(
                        MsKelurahan.KelurahanID == select_query.vw_obyekbadanwpo.KelurahanPemilik).first()
                    data.update({
                        'optionCitiesPemilik': {
                            'name': cityOwner.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                    + ', Kec.' + cityOwner.MsKecamatan.Kecamatan
                                    + ', Kel.' + cityOwner.MsKelurahan.Kelurahan
                                    + ' - ' + cityOwner.MsKelurahan.KodePos,
                        }
                    })
                return success_reads(data)
            else:
                logger.error
                return success_reads({})

    class ProfileWp(Resource):
        method_decorators = {'get': [tblUser.auth_apikey]}

        def get(self, npwpd, *args, **kwargs):
            try:
                select_query = MsWPOData.query.filter_by(ObyekBadanNo=npwpd).first()
                return success_reads(toDict(select_query))
            except Exception as e:
                print(e)
                return failed_reads({})

    class ListAll(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            # parser = reqparse.RequestParser()
            # parser.add_argument('page', type=int)
            # parser.add_argument('length', type=int)
            # parser.add_argument('sort', type=str)
            # parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
            # parser.add_argument('search', type=str)
            # parser.add_argument('search_jenis', type=str)
            # parser.add_argument( 'kategori', type=str, choices=('true', 'false'), help='diisi dengan true atau false' )
            # parser.add_argument('nonwp', type=str, choices=('true', 'false'), help='diisi dengan true atau false')
            # args = parser.parse_args()
            result = []
            try:
                select_query = db.session.query(MsWPOData.WPID, #vw_obyekbadanwpo.OBN,
                                                # vw_obyekbadanwpo.OPDID,
                                                MsWPOData.DateUpd,
                                                MsWPOData.NamaBadan,
                                                # vw_obyekbadanwpo.NamaJenisPendapatan,
                                                MsWPOData.AlamatBadan,
                                                # vw_obyekbadanwpo.RWBadan, vw_obyekbadanwpo.RTBadan,
                                                # vw_obyekbadanwpo.Kecamatan, vw_obyekbadanwpo.NamaLokasi,
                                                # vw_obyekbadanwpo.JenisPendapatanID, vw_obyekbadanwpo.Insidentil,
                                                # vw_obyekbadanwpo.SelfAssesment,
                                                MsWPOData.avatar
                                                # , vw_obyekbadanwpo.latlng
                                                ).order_by(MsWPOData.DateUpd.desc()).all()

                # # SEARCH_JENIS
                # if args['search_jenis']:
                #     select_query = select_query.filter(
                #         vw_obyekbadanwpo.JenisPendapatanID == args['search_jenis']
                #     )
                #
                # # kategori
                # if args['kategori'] or args['kategori'] == "true":
                #     select_query = select_query.filter( vw_obyekbadanwpo.SelfAssesment == 'Y' )
                # # else:
                # #     select_query = select_query.filter( vw_obyekbadanwpo.SelfAssesment == 'N' )
                #
                # # nonwp
                # if args['nonwp'] or args['nonwp'] == "true":
                #     select_query = select_query.filter(vw_obyekbadanwpo.Insidentil == 'Y')
                # # else:
                # #     select_query = select_query.filter(vw_obyekbadanwpo.Insidentil == 'N')

                # # SEARCH
                # if args['search'] and args['search'] != 'null':
                #     search = '%{0}%'.format(args['search'])
                #     select_query = select_query.filter(
                #         or_(MsWPOData.NamaBadan.ilike(search),
                #             MsWPOData.NamaPemilik.ilike(search)),
                #     )
                #
                # # SORT
                # if args['sort']:
                #     if args['sort_dir'] == "desc":
                #         sort = getattr(MsWPOData, args['sort']).desc()
                #     else:
                #         sort = getattr(MsWPOData, args['sort']).asc()
                #     select_query = select_query.order_by(sort)
                # else:
                #     select_query = select_query.order_by(desc(MsWPOData.DateUpd))

                # # PAGINATION
                # page = args['page'] if args['page'] else 1
                # length = args['length'] if args['length'] else 10
                # lengthLimit = length if length < 101 else 100
                # query_execute = select_query.paginate(page, lengthLimit)


                # print(query_execute.items)
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        # print(key,  getattr(row, key))
                        d[key] = getattr(row, key)
                    result.append(d)
                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_reads(result)

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsWPOData.query.filter_by(WPID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})