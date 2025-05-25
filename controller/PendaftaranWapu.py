import base64
import os
import re
from datetime import datetime
from multiprocessing import Process
from time import strftime, strptime

import sqlalchemy
from flask import request, make_response, jsonify
from flask_restful import reqparse, Resource, abort
from sqlalchemy.sql.elements import or_

from config.api_message import failed_create, success_read, success_create, success_update, failed_update, \
    success_delete, failed_delete, success_reads_pagination, success_reads, failed_reads
from config.database import db
from config.helper import non_empty_string, parser, allowed_file, logger, toDict
from controller.MsGrupUsaha import MsGrupUsaha
from controller.MsKecamatan import MsKecamatan
from controller.MsKelurahan import MsKelurahan
from controller.MsKlasifikasiUsaha import MsKlasifikasiUsaha
from controller.MsKota import MsKota
from controller.MsLokasiKhusus import MsLokasiKhusus
from controller.MsPegawai import MsPegawai
from controller.MsWapu import MsWapu
from controller.MsWapu import MsWapu
from controller.task.task_bridge import GoToTaskUploadWPAvatar, GoToTaskDeleteWPAvatar, GoToTaskUploadWaPuAvatar
from controller.tblUser import tblUser


class AddPendaftaranWapu(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('NamaBadan', required=True, nullable=False,
                            help="Harus diisi")
        parser.add_argument('JenisPungutID', type=str)
        parser.add_argument('AlamatBadan', type=str)
        parser.add_argument('NoTelpBadan', type=str)
        parser.add_argument('KotaBadan', type=str, required=True, help="Harus diisi")
        parser.add_argument('KecamatanBadan', required=True, nullable=False,
                            help="Harus diisi")
        parser.add_argument('KelurahanBadan', required=False, nullable=False,
                            help="Harus diisi")
        parser.add_argument('NoTelpBadan', type=str, required=False, help="Harus diisi")

        parser.add_argument('PetugasPendaftar', type=str, required=True, help="Harus diisi")
        parser.add_argument('TglPendaftaran', required=True, nullable=False,
                            help="Harus diisi")
        parser.add_argument('TglPenghapusan',  nullable=True)
        parser.add_argument('avatar', type=str)
        parser.add_argument('latlng', type=str)
        parser.add_argument('NIK', type=str)
        args = parser.parse_args()
        try:

            uid = kwargs['claim']["UID"]
            add_record = MsWapu(
                NamaBadan=args['NamaBadan'] if args['NamaBadan'] else '',
                JenisPungutID=args['JenisPungutID'] if args['JenisPungutID'] else '',
                AlamatBadan=args['AlamatBadan'] if args['AlamatBadan'] else '',
                KotaBadan=args['KotaBadan'] if args['KotaBadan'] else '',
                KecamatanBadan=args['KecamatanBadan'] if args['KecamatanBadan'] else '',
                KelurahanBadan=args['KelurahanBadan'] if args['KelurahanBadan'] else '',
                NoTelpBadan=args['NoTelpBadan'] if args['NoTelpBadan'] else '',
                TglPendaftaran=args['TglPendaftaran'] if args['TglPendaftaran'] else '',
                TglPenghapusan=args['TglPenghapusan'] if args['TglPenghapusan'] else None,
                PetugasPendaftar=args['PetugasPendaftar'] if args['PetugasPendaftar'] else '',
                UserUpd=uid,
                DateUpd=datetime.now(),
                latlng=args['latlng'] if args['latlng'] else '',
                NIK=args['NIK'] if args['NIK'] else ''
            )
            db.session.add(add_record)
            db.session.commit()
            print('sukses insert ke header')
            if add_record:
                data = {
                    'uid': uid,
                    'WapuID': add_record.WapuID
                }
                # ////INCLUDE IMG
                files_img = request.files
                if files_img:
                    if not os.path.exists(f'./static/uploads/avatar_wapu_temp'):
                        os.makedirs(f'./static/uploads/avatar_wapu_temp')
                    folder_temp = f'./static/uploads/avatar_wapu_temp'

                    # add item img and upload
                    filenames = []

                    for img_row in files_img.items():
                        img_row_ok = img_row[1]
                        if img_row_ok.filename == '':
                            logger.info('file image dengan nama avatar wajib disertakan')
                        if img_row_ok:
                            new_filename = f"{add_record.WapuID}.png"
                            img_row_ok.save(os.path.join(folder_temp, new_filename))
                            filenames.append(new_filename)
                    filenames_str = ','.join([str(elem) for elem in filenames])
                    # logger.info(filenames_str)
                    if filenames_str != '':
                        thread = Process(target=GoToTaskUploadWaPuAvatar,
                                         args=(folder_temp, filenames_str, add_record.WapuID, kwargs['claim']['UserId'], False, request.origin))
                        thread.daemon = True
                        thread.start()
            else:
                db.session.rollback()
                return failed_create({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_create({})


class UpdatePendaftaranWapu(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('ObyekBadanNo', type=str)
        parser.add_argument('NamaBadan', type=str)
        parser.add_argument('AlamatBadan', type=str)
        parser.add_argument('KotaBadan', type=str)
        parser.add_argument('KecamatanBadan', type=str)
        parser.add_argument('KelurahanBadan', type=str)
        parser.add_argument('NoTelpBadan', type=str)
        parser.add_argument('TglPendaftaran', type=str)
        parser.add_argument('TglPenghapusan', type=str)
        parser.add_argument('JenisPungutID', type=str)
        parser.add_argument('PetugasPendaftar', type=str)
        # parser.add_argument('Insidentil', type=str)
        parser.add_argument('UserUpd', type=str)
        parser.add_argument('DateUpd', type=str)
        parser.add_argument('WapuID', type=str)
        parser.add_argument('latlng', type=str)
        parser.add_argument('NIK', type=str)

        try:
            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            # result = db.session.execute(
            #     f"exec [SP_NPWPD] '{args['KotaBadan']}','{args['KecamatanBadan']}'")
            #
            # result2 = []
            # for row in result:
            #     result2.append(row)
            # ObyekBadanNo = result2[0][0].replace(' ', '')

            select_query = MsWapu.query.filter_by(WapuID=id).first()
            if select_query:
                if args['NamaBadan']:
                    select_query.NamaBadan = f"{args['NamaBadan']}"
                if args['AlamatBadan']:
                    select_query.AlamatBadan = args['AlamatBadan']
                if args['KotaBadan']:
                    select_query.KotaBadan = args['KotaBadan']
                if args['KecamatanBadan']:
                    select_query.KecamatanBadan = args['KecamatanBadan']
                if args['KelurahanBadan']:
                    select_query.KelurahanBadan = args['KelurahanBadan']
                if args['NoTelpBadan']:
                    select_query.NoTelpBadan = args['NoTelpBadan']
                if args['TglPendaftaran']:
                    select_query.TglPendaftaran = args['TglPendaftaran']
                if args['TglPenghapusan']:
                    select_query.TglPenghapusan = args['TglPenghapusan']
                if args['JenisPungutID']:
                    select_query.JenisPungutID = args['JenisPungutID']
                if args['PetugasPendaftar']:
                    select_query.PetugasPendaftar = args['PetugasPendaftar']
                    select_query.UserUpd = uid
                    select_query.DateUpd = datetime.now()
                if args['latlng']:
                    select_query.latlng = args['latlng']
                if args['NIK']:
                    select_query.latlng = args['NIK']
                db.session.commit()

                print('sukses update ke header')

                if select_query.WapuID:
                    data = {
                        'WapuID': args['WapuID'],
                        'uid': uid,
                        'WapuID': select_query.WapuID
                    }
                    # ////INCLUDE IMG
                    files_img = request.files
                    if files_img:
                        if not os.path.exists(f'./static/uploads/avatar_wapu_temp'):
                            os.makedirs(f'./static/uploads/avatar_wapu_temp')
                        folder_temp = f'./static/uploads/avatar_wapu_temp'

                        # add item img and upload
                        filenames = []

                        for img_row in files_img.items():
                            img_row_ok = img_row[1]
                            if img_row_ok.filename == '':
                                logger.info('file image dengan nama avatar wajib disertakan')
                            if img_row_ok:
                                new_filename = f"{id}.png"
                                img_row_ok.save(os.path.join(folder_temp, new_filename))
                                filenames.append(new_filename)
                        filenames_str = ','.join([str(elem) for elem in filenames])
                        # logger.info(filenames_str)
                        if filenames_str != '':
                            thread = Process(target=GoToTaskUploadWaPuAvatar,
                                             args=(folder_temp, filenames_str, id, kwargs['claim']['UserId'], False, request.origin))
                            thread.daemon = True
                            thread.start()

                else:
                    db.session.rollback()
                    return failed_update({})
            else:
                return failed_update({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_update({})


class DeletePendaftaranWapu(Resource):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}

    def delete(self, id, *args, **kwargs):
        try:
            check_header = MsWapu.query.filter_by(WapuID=id)
            avatar = check_header.first()
            if avatar:
                thread = Process(target=GoToTaskDeleteWPAvatar(avatar.avatar, request.origin))
                thread.daemon = True
                thread.start()
                if check_header:
                    check_header.delete()
                    db.session.commit()
                return success_delete({})
            else:
                db.session.rollback()
            return failed_delete({})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_delete({})

class DeletePendaftaranWapuMulti(Resource):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}

    def delete(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('id', action='append', required=True, nullable=False, help="Name cannot be blank!")
        args = parser.parse_args()
        try:
            ids_success = []
            ids_failed = []
            for id in args['id']:
                check_header = MsWapu.query.filter_by(WapuID=id)
                check_header.delete()
                db.session.commit()
                if check_header:
                    ids_success.append(id)
                else:
                    ids_failed.append(id)
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_delete({})


class PenonaktifanWapu(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        result = []
        try:
            select_query = db.session.query(MsWapu.WapuID, MsWapu.NamaBadan, MsWapu.AlamatBadan,
                                            MsWapu.avatar, MsWapu.DateUpd
                                            )\
                .order_by(MsWapu.DateUpd.desc()).all()
            for row in select_query:

                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)

                result.append(d)
            return success_reads(result)

        except Exception as e:
            print(e)
            return failed_reads(result)


class PenonaktifanWapuEdit(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, wapuid, *args, **kwargs):
        # select_query = db.session.execute( f"SELECT o.*,j.ParentID FROM MsWapu o LEFT JOIN
        # MsJenisPendapatan j ON o.UsahaBadan = j.JenisPendapatanID " f"WHERE WapuID='{opdid}'")
        select_query = db.session.query(MsWapu, MsPegawai.Nama, MsWapu.NIK,
                                        ) \
            .outerjoin(MsPegawai, MsPegawai.PegawaiID == MsWapu.PetugasPendaftar) \
            .filter( MsWapu.WapuID == wapuid)\
            .first()
        if select_query:
            data = toDict(select_query.MsWapu)
            # data.update({'ParentID': select_query.ParentID})
            data.update({'Insidentil': False if select_query.MsWapu.Insidentil == 'N' else True})

            data.update({
                'optionPetugas': {
                    'Petugas': select_query.Nama,
                    'PetugasID': select_query.MsWapu.PetugasPendaftar
                }
            })

            cities = db.session.query(
                MsKota, MsKecamatan, MsKelurahan
            ).join(MsKecamatan, MsKecamatan.KotaID == MsKota.KotaID) \
                .join(MsKelurahan, MsKelurahan.KecamatanID == MsKecamatan.KecamatanBadan)
            if select_query.MsWapu.KelurahanBadan:
                cityBadan = cities.filter(
                    MsKelurahan.KelurahanID == select_query.MsWapu.KelurahanBadan).first()
                data.update({
                    'optionCitiesBadan': {
                        'name': cityBadan.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                + ', Kec.' + cityBadan.MsKecamatan.Kecamatan
                                + ', Kel.' + cityBadan.MsKelurahan.Kelurahan,
                    }
                })

            return success_reads(data)
        else:
            return success_reads({})


class UpdatePenonaktifanWapu(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()

        try:
            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            select_query = MsWapu.query.filter_by(WapuID=id).first()
            if select_query:
                select_query.TglPenghapusan = datetime.now()
                select_query.UserUpd = uid
                select_query.DateUpd = datetime.now()
            db.session.commit()
            return success_update({'WapuID': select_query.WapuID, 'NamaBadan': select_query.NamaBadan})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_update({})


class AktivasiWapu(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        result = []
        try:
            select_query = db.session.query(MsWapu.WapuID, MsWapu.NamaBadan, MsWapu.AlamatBadan,
                                            MsWapu.avatar, MsWapu.DateUpd
                                            ) \
                .filter(MsWapu.TglPenghapusan != None) \
                .order_by(MsWapu.DateUpd.desc()).all()
            for row in select_query:

                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)

                result.append(d)
            return success_reads(result)

        except Exception as e:
            print(e)
            return failed_reads(result)


class AktivasiWapuEdit(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, wapuid, *args, **kwargs):
        # select_query = db.session.execute( f"SELECT o.*,j.ParentID FROM MsWapu o LEFT JOIN
        # MsJenisPendapatan j ON o.UsahaBadan = j.JenisPendapatanID " f"WHERE WapuID='{opdid}'")
        select_query = db.session.query(MsWapu, MsPegawai.Nama, MsWapu.NIK,
                                        ) \
            .outerjoin(MsPegawai, MsPegawai.PegawaiID == MsWapu.PetugasPendaftar) \
            .filter(MsWapu.WapuID == wapuid)\
            .first()
        if select_query:
            data = toDict(select_query.MsWapu)

            data.update({
                'optionPetugas': {
                    'Petugas': select_query.Nama,
                    'PetugasID': select_query.MsWapu.PetugasPendaftar
                }
            })

            cities = db.session.query(
                MsKota, MsKecamatan, MsKelurahan
            ).join(MsKecamatan, MsKecamatan.KotaID == MsKota.KotaID) \
                .join(MsKelurahan, MsKelurahan.KecamatanID == MsKecamatan.KecamatanID)
            if select_query.MsWapu.KelurahanBadan:
                cityBadan = cities.filter(
                    MsKelurahan.KelurahanID == select_query.MsWapu.KelurahanBadan).first()
                data.update({
                    'optionCitiesBadan': {
                        'name': cityBadan.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                + ', Kec.' + cityBadan.MsKecamatan.Kecamatan
                                + ', Kel.' + cityBadan.MsKelurahan.Kelurahan,
                    }
                })
            return success_reads(data)
        else:
            return success_reads({})


class UpdateAktivasiWapu(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()

        try:
            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            select_query = MsWapu.query.filter_by(WapuID=id).first()
            if select_query:
                select_query.TglPenghapusan = None
                select_query.UserUpd = uid
                select_query.DateUpd = datetime.now()
            db.session.commit()
            return success_update({'WapuID': select_query.WapuID, 'NamaBadan': select_query.NamaBadan})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_update({})