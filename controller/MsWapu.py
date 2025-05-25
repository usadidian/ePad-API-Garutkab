from asyncio.windows_events import NULL

from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import or_, literal
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads, failed_reads, success_reads_pagination
from config.database import db
from config.helper import toDict
from controller.MsJenisPungut import MsJenisPungut
from controller.MsKecamatan import MsKecamatan
from controller.MsKelurahan import MsKelurahan
from controller.MsKota import MsKota
from controller.MsPegawai import MsPegawai
from controller.tblGroupUser import tblGroupUser
from controller.tblUPTOpsen import tblUPTOpsen
from controller.tblUser import tblUser
from controller.vw_obyekbadanwapu import vw_obyekbadanwapu


class MsWapu(db.Model, SerializerMixin):
    __tablename__ = 'MsWapu'
    WapuID = db.Column(db.Integer, primary_key=True)
    JenisPungutID = db.Column(db.Integer, nullable=True)
    UPTID = db.Column(db.Integer, nullable=True)
    ObyekBadanNo = db.Column(db.String, nullable=True)
    NamaBadan = db.Column(db.String, nullable=False)
    AlamatBadan = db.Column(db.String, nullable=True)
    NoTelpBadan = db.Column(db.String, nullable=True)
    KotaBadan = db.Column(db.Integer, nullable=False)
    KecamatanBadan = db.Column(db.Integer, nullable=False)
    KelurahanBadan = db.Column(db.Integer, nullable=True)
    TglPendaftaran = db.Column(db.TIMESTAMP, nullable=False)
    # TglPengesahan = db.Column(db.TIMESTAMP, nullable=False)
    TglPenghapusan = db.Column(db.TIMESTAMP, nullable=True, default=None)
    PetugasPendaftar = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)
    avatar = db.Column(db.String, nullable=True)
    latlng = db.Column(db.String, nullable=True)
    NIK = db.Column(db.String, nullable=True)

    JenisPungutID = db.Column(db.String, db.ForeignKey('MsJenisPungut.JenisPungutID'), nullable=False)

    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('search', type=str)
            parser.add_argument('length', type=int)
            args = parser.parse_args()

            query1 = db.session.query(
                MsWapu.WapuID.label("WapuID"),
                MsWapu.ObyekBadanNo.label("ObyekBadanNo"),
                MsWapu.NamaBadan.label("NamaBadan"),
                MsWapu.KotaBadan.label("KotaBadan"),
                MsWapu.PetugasPendaftar.label("PetugasPendaftar"),
                MsKota.Kota.label("Kota")
            ).outerjoin(MsKota, MsWapu.KotaBadan == MsKota.KotaID) \
                .filter(MsWapu.TglPenghapusan == None)

            query2 = db.session.query(
                tblUPTOpsen.UPTID.label("WapuID"),
                literal("000").label("ObyekBadanNo"),
                tblUPTOpsen.UPT.label("NamaBadan"),
                literal("").label("KotaBadan"),
                literal("").label("PetugasPendaftar"),
                literal("").label("Kota")
            )

            # UNION kedua query
            union_subquery = query1.union(query2).subquery()

            q = db.session.query(union_subquery)

            # Jika ada search
            if args['search'] and len(args['search']) > 0:
                search = f"%{args['search']}%"
                q = q.filter(union_subquery.c.NamaBadan.like(search))

            # Order dan limit berdasarkan WapuID
            q = q.order_by(union_subquery.c.WapuID).limit(args['length'] or 5)


            # Eksekusi query
            result_set = q.all()

            # Konversi ke format list of dict
            result = []
            for row in result_set:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)

            return success_reads(result)

    class ListAll3(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, wapuid, *args, **kwargs):

            select_query = db.session.query(vw_obyekbadanwapu,  # MsJenisPendapatan.ParentID,
                                            MsPegawai.Nama, MsJenisPungut.KdLevel
                                            ) \
                .outerjoin(MsPegawai, MsPegawai.PegawaiID == vw_obyekbadanwapu.PetugasPendaftar) \
                .outerjoin(MsJenisPungut, MsJenisPungut.JenisPungutID == vw_obyekbadanwapu.JenisPungutID) \
                .filter(vw_obyekbadanwapu.WapuID == wapuid) \
                .first()
            if select_query:
                data = toDict(select_query.vw_obyekbadanwapu)
                print(data)
                cities = db.session.query(
                    MsKota, MsKecamatan, MsKelurahan
                ).join(MsKecamatan, MsKecamatan.KotaID == MsKota.KotaID) \
                    .join(MsKelurahan, MsKelurahan.KecamatanID == MsKecamatan.KecamatanID)
                if select_query.vw_obyekbadanwapu.KelurahanBadan:
                    cityBadan = cities.filter(
                        MsKelurahan.KelurahanID == select_query.vw_obyekbadanwapu.KelurahanBadan).first()
                    data.update({
                        'optionCitiesBadan': {
                            'name': cityBadan.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                    + ', Kec.' + cityBadan.MsKecamatan.Kecamatan
                                    + ', Kel.' + cityBadan.MsKelurahan.Kelurahan
                                    + ' - ' + cityBadan.MsKelurahan.KodePos,
                        }
                    })

                    data.update({
                        'optionPetugas': {
                            'Petugas': select_query.Nama,
                            'PetugasID': select_query.vw_obyekbadanwapu.PetugasPendaftar
                        }
                    })

                    data.update({
                        'optionJenisPungut': {
                            'JenisPungut': select_query.vw_obyekbadanwapu.JenisPungut,
                            'JenisPungutID': select_query.vw_obyekbadanwapu.JenisPungutID,
                            'KdLevel': select_query.KdLevel
                        }
                    })

                    return success_reads(data)
                else:
                    return success_reads({})

    class ListAll5(Resource):
        def get(self, *args, **kwargs):

            select_query = db.session.execute(
                f"SELECT WapuID, NamaBadan AS WajibPungut FROM MsWapu "
                f"where (TglPenghapusan IS NULL) order by WapuID")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)


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
            parser.add_argument('search_jenis_pungut', type=str)

            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            # IsPendaftaran = kwargs['claim']["IsPendaftaran"]
            # wapuid = kwargs['claim']["WapuID"]
            result = []
            try:
                # query = db.session.query(
                #     GeneralParameter.ParamNumValue ).filter( GeneralParameter.ParamID == 'varian_epad' )
                # varian = query.first()[0]
                # if varian == 1:
                # if IsPendaftaran == 1:
                #     select_query = db.session.query(vw_obyekbadanwapu.WapuID, vw_obyekbadanwapu.ObyekBadanNo, vw_obyekbadanwapu.NamaBadan,
                #                                     vw_obyekbadanwapu.AlamatBadan, vw_obyekbadanwapu.NoTelpBadan, vw_obyekbadanwapu.KotaBadan,
                #                                     vw_obyekbadanwapu.KecamatanBadan,vw_obyekbadanwapu.KelurahanBadan, vw_obyekbadanwapu.TglPendaftaran,
                #                                     vw_obyekbadanwapu.Kota, vw_obyekbadanwapu.avatar, vw_obyekbadanwapu.latlng , vw_obyekbadanwapu.JenisPungut) \
                #         .distinct()\
                #         .filter(vw_obyekbadanwapu.WapuID == wapuid)
                # else:
                select_query = db.session.query(vw_obyekbadanwapu.WapuID,
                                                vw_obyekbadanwapu.NamaBadan,
                                                vw_obyekbadanwapu.AlamatBadan, vw_obyekbadanwapu.NoTelpBadan,
                                                vw_obyekbadanwapu.KotaBadan,
                                                vw_obyekbadanwapu.KecamatanBadan, vw_obyekbadanwapu.KelurahanBadan,
                                                vw_obyekbadanwapu.TglPendaftaran,
                                                vw_obyekbadanwapu.TglPenghapusan,
                                                vw_obyekbadanwapu.Kota, vw_obyekbadanwapu.avatar,
                                                vw_obyekbadanwapu.latlng, vw_obyekbadanwapu.JenisPungut) \
                    .distinct()\
                    .filter(vw_obyekbadanwapu.TglPenghapusan == None)

                if args['search_jenis_pungut']:
                    select_query = select_query.filter(
                        vw_obyekbadanwapu.JenisPungutID == args['search_jenis_pungut']
                    )

                # SEARCH
                if args['search'] and args['search'] != 'null':
                    search = '%{0}%'.format(args['search'])
                    select_query = select_query.filter(
                        or_(vw_obyekbadanwapu.NamaBadan.ilike(search),
                            vw_obyekbadanwapu.ObyekBadanNo.ilike(search)),
                    )

                # SORT
                if args['sort']:
                    if args['sort_dir'] == "desc":
                        sort = getattr(vw_obyekbadanwapu, args['sort']).desc()
                    else:
                        sort = getattr(vw_obyekbadanwapu, args['sort']).asc()
                    select_query = select_query.order_by(sort)
                else:
                    select_query = select_query.order_by(vw_obyekbadanwapu.WapuID, vw_obyekbadanwapu.NamaBadan.desc())

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
                    result.append(d)
                return success_reads_pagination(query_execute, result)
            except Exception as e:
                print(e)
                return failed_reads(result)

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('UPTID', type=str)
            parser.add_argument('ObyekBadanNo', type=str)
            parser.add_argument('NamaBadan', type=str)
            parser.add_argument('AlamatBadan', type=str)
            parser.add_argument('NoTelpBadan', type=str)
            parser.add_argument('KotaBadan', type=str)
            parser.add_argument('KecamatanBadan', type=str)
            parser.add_argument('KelurahanBadan', type=str)
            parser.add_argument('TglPendaftaran', type=str)
            parser.add_argument('JenisPungutID', type=str)
            parser.add_argument('PetugasPendaftar', type=str)

            uid = kwargs['claim']["UID"]
            print(uid)

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            add_record = MsWapu(
                UPTID=args['UPTID'] if args['UPTID'] else '',
                ObyekBadanNo=args['ObyekBadanNo'] if args['ObyekBadanNo'] else '',
                NamaBadan=args['NamaBadan'] if args['NamaBadan'] else '',
                AlamatBadan=args['AlamatBadan'] if args['AlamatBadan'] else '',
                KotaBadan=args['KotaBadan'] if args['KotaBadan'] else '',
                KecamatanBadan=args['KecamatanBadan'] if args['KecamatanBadan'] else '',
                KelurahanBadan=args['KelurahanBadan'] if args['KelurahanBadan'] else '',
                TglPendaftaran=args['TglPendaftaran'] if args['TglPendaftaran'] else '',
                TglPengesahan=args['JenisPungutID'] if args['JenisPungutID'] else '',
                PetugasPendaftar=args['PetugasPendaftar'] if args['PetugasPendaftar'] else '',

            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsWapu.query.filter_by(NamaBadan=id).first()
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
            parser.add_argument('AlamatBadan', type=str)
            parser.add_argument('KotaBadan', type=str)
            parser.add_argument('KecamatanBadan', type=str)
            parser.add_argument('KelurahanBadan', type=str)
            parser.add_argument('TglPendaftaran', type=str)
            # parser.add_argument('TglPengesahan', type=str)
            parser.add_argument('PetugasPendaftar', type=str)

            uid = kwargs['claim']["UID"]
            print(uid)

            args = parser.parse_args()
            try:
                select_query = MsWapu.query.filter_by(WapuID=id).first()
                if select_query:
                    select_query.ObyekBadanNo = f"{args['ObyekBadanNo']}"
                    select_query.NamaBadan = args['NamaBadan']
                    select_query.AlamatBadan = args['AlamatBadan']
                    select_query.KotaBadan = args['KotaBadan']
                    if args['KecamatanBadan']:
                        select_query.KecamatanBadan = args['KecamatanBadan']
                    if args['KelurahanBadan']:
                        select_query.KelurahanBadan = args['KelurahanBadan']
                    if args['TglPendaftaran']:
                        select_query.TglPendaftaran = args['TglPendaftaran']
                    # if args['TglPengesahan']:
                    #     select_query.TglPengesahan = args['TglPengesahan']
                    if args['PetugasPendaftar']:
                        select_query.PetugasPendaftar = args['PetugasPendaftar']
                    db.session.commit()
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsWapu.query.filter_by(WapuID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})
