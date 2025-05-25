import base64
import os
import re
from datetime import datetime
from multiprocessing import Process

import sqlalchemy
from flask import request, make_response, jsonify
from flask_restful import reqparse, Resource, abort
from sqlalchemy import func
from sqlalchemy.sql.elements import or_

from config.api_message import failed_create, success_read, success_create, success_update, failed_update, \
    success_delete, failed_delete, success_reads_pagination, success_reads, failed_reads
from config.database import db
from config.helper import non_empty_string, parser, allowed_file, logger, toDict
from controller.GeneralParameter import GeneralParameter
from controller.MsGrupUsaha import MsGrupUsaha
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsKecamatan import MsKecamatan
from controller.MsKelurahan import MsKelurahan
from controller.MsKlasifikasiUsaha import MsKlasifikasiUsaha
from controller.MsKota import MsKota
from controller.MsLokasiKhusus import MsLokasiKhusus
from controller.MsOPD import MsOPD
from controller.MsWPData import MsWPData
from controller.task.task_bridge import GoToTaskUploadOPDAvatar, GoToTaskDeleteOPDAvatar
from controller.tblUser import tblUser


class AddPendaftaranObjekPajak(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('NamaOPD', required=True, nullable=False,
                            help="Harus diisi")
        parser.add_argument('WapuID', type=str)
        parser.add_argument('WPID', type=str)
        parser.add_argument('UsahaBadan', required=True, nullable=False,
                            help="Harus diisi")
        parser.add_argument('AlamatOPD', type=str)
        parser.add_argument('KotaOPD', type=str, required=True, help="Harus diisi")
        parser.add_argument('KecamatanOPD', required=True, nullable=False,
                            help="Harus diisi")
        parser.add_argument('KelurahanOPD', required=True, nullable=False,
                            help="Harus diisi")

        parser.add_argument('NoTelpOPD', type=str)

        parser.add_argument('PetugasPendaftar', type=str)
        parser.add_argument('TglPendaftaran', required=True, nullable=False,
                            help="Harus diisi")
        parser.add_argument('TglPenghapusan', nullable=True)


        parser.add_argument('GrupUsahaID', type=str)
        parser.add_argument('KlasifikasiID', type=str)
        parser.add_argument('LokasiID', type=str)
        parser.add_argument('RWOPD', type=str)
        parser.add_argument('RTOPD', type=str)
        parser.add_argument('TglPenghapusan', type=str)

        parser.add_argument('avatar', type=str)
        parser.add_argument('latlng', type=str)
        args = parser.parse_args()
        try:

            uid = kwargs['claim']["UID"]
            wapu_id = args['WapuID']
            wp_id = args['WPID']
            usaha_badan = args['UsahaBadan']
            nop = None

            query = db.session.query(GeneralParameter.ParamStrValue).filter(
                GeneralParameter.ParamID == 'option_nop').first()
            result0 = []
            for row in query:
                result0.append(row)
            opsi_nop = result0[0][0]
            print(opsi_nop)
            if opsi_nop == '2':
                if wp_id and usaha_badan and wapu_id:
                    select_query = db.session.query(MsJenisPendapatan.KodeRekening).filter(
                        MsJenisPendapatan.JenisPendapatanID == usaha_badan).first()

                    if select_query:
                        koderek = select_query[0]
                        koderek_clean = koderek[-6:].replace('.', '')
                        wpid_padded = str(wp_id).zfill(6)
                        wapuid_padded = str(wapu_id).zfill(4)
                        nop = koderek_clean + wpid_padded + wapuid_padded
                    # return success_reads({'nop': nop})

            elif opsi_nop == '1':
                if wp_id and usaha_badan:
                    select_query = db.session.query(MsJenisPendapatan.KodeRekening).filter(
                        MsJenisPendapatan.JenisPendapatanID == usaha_badan).first()

                    if select_query:
                        koderek = select_query[0]
                        koderek_clean = koderek[-6:].replace('.', '')
                        wpid_padded = str(wp_id).zfill(6)
                        nop = koderek_clean + wpid_padded
                    # return success_reads({'nop': nop})

            def generate_ObyekBadanID():
                max_id = db.session.query(func.max(MsOPD.OPDID)).scalar()
                return (max_id or 0) + 1



            add_record = MsOPD(
                UsahaBadan=args['UsahaBadan'] if args['UsahaBadan'] else '',
                WapuID=args['WapuID'],
                WPID=wp_id,
                OPDID=generate_ObyekBadanID(),
                NOP=nop,
                TglNOP=datetime.now().strftime('%Y-%m-%d') + ' 00:00:00.000',
                NamaOPD=args['NamaOPD'] if args['NamaOPD'] else '',
                GrupUsahaID=args['GrupUsahaID'] if args['GrupUsahaID'] else '',
                KlasifikasiID=args['KlasifikasiID'] if args['KlasifikasiID'] else '',
                LokasiID=args['LokasiID'] if args['LokasiID'] else '',
                AlamatOPD=args['AlamatOPD'] if args['AlamatOPD'] else '',
                KotaOPD=args['KotaOPD'] if args['KotaOPD'] else '',
                KecamatanOPD=args['KecamatanOPD'] if args['KecamatanOPD'] else '',
                KelurahanOPD=args['KelurahanOPD'] if args['KelurahanOPD'] else '',
                RWOPD=args['RWOPD'] if args['RWOPD'] else '',
                RTOPD=args['RTOPD'] if args['RTOPD'] else '',
                NoTelpOPD=args['NoTelpOPD'] if args['NoTelpOPD'] else '',
                TglPendaftaran=args['TglPendaftaran'] if args['TglPendaftaran'] else '',
                TglPenghapusan=sqlalchemy.sql.null(),
                UserUpd=uid,
                DateUpd=datetime.now(),
                latlng=args['latlng'],
            )
            db.session.add(add_record)
            db.session.commit()
            print('sukses insert ke header')

            # ////INCLUDE IMG
            files_img = request.files
            if files_img:
                if not os.path.exists(f'./static/uploads/avatar_opd_temp'):
                    os.makedirs(f'./static/uploads/avatar_opd_temp')
                folder_temp = f'./static/uploads/avatar_opd_temp'

                # add item img and upload
                filenames = []

                for img_row in files_img.items():
                    img_row_ok = img_row[1]
                    if img_row_ok.filename == '':
                        logger.info('file image dengan nama avatar wajib disertakan')
                    if img_row_ok:
                        new_filename = f"{add_record.OPDID}.png"
                        img_row_ok.save(os.path.join(folder_temp, new_filename))
                        filenames.append(new_filename)
                filenames_str = ','.join([str(elem) for elem in filenames])
                # logger.info(filenames_str)
                if filenames_str != '':
                    thread = Process(target=GoToTaskUploadOPDAvatar,
                                     args=(folder_temp, filenames_str, add_record.OPDID, kwargs['claim']['UserId'], False, request.origin))
                    thread.daemon = True
                    thread.start()

            if add_record:
                return success_create({'OPDID': add_record.OPDID, 'NamaOPD': add_record.NamaOPD})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_create({})

class generate_nop(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}
    def get (self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('wapuid', type=str)
        parser.add_argument('wpid', type=str)
        parser.add_argument('jenispendapatanid', type=str)
        args = parser.parse_args()

        try:
            wapu_id = args['wapuid']
            wp_id = args['wpid']
            usaha_badan = args['jenispendapatanid']

            query = db.session.query(GeneralParameter.ParamStrValue).filter(
                GeneralParameter.ParamID == 'option_nop').first()
            result0 = []
            for row in query:
                result0.append(row)
            opsi_nop = result0[0][0]
            print(opsi_nop)
            if opsi_nop == '2':
                if wp_id and usaha_badan and wapu_id:
                    select_query = db.session.query(MsJenisPendapatan.KodeRekening).filter(
                        MsJenisPendapatan.JenisPendapatanID == usaha_badan).first()

                    if select_query:
                        koderek = select_query[0]
                        koderek_clean = koderek[-6:].replace('.', '')
                        wpid_padded = str(wp_id).zfill(6)
                        wapuid_padded = str(wapu_id).zfill(4)
                        nop = koderek_clean + wpid_padded + wapuid_padded
                    return success_reads({'nop': nop})

            elif opsi_nop == '1':
                if wp_id and usaha_badan:
                    select_query = db.session.query(MsJenisPendapatan.KodeRekening).filter(
                        MsJenisPendapatan.JenisPendapatanID == usaha_badan).first()

                    if select_query:
                        koderek = select_query[0]
                        koderek_clean = koderek[-6:].replace('.', '')
                        wpid_padded = str(wp_id).zfill(6)
                        nop = koderek_clean + wpid_padded
                    return success_reads({'nop': nop})


        except Exception as e:
            logger.error(e)
            return failed_reads({})

class UpdatePendaftaranObjekPajak(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('NamaOPD', type=str)
        parser.add_argument('AlamatOPD', type=str)
        parser.add_argument('KotaOPD', type=str)
        parser.add_argument('KecamatanOPD', type=str)
        parser.add_argument('KelurahanOPD', type=str)
        parser.add_argument('RWOPD', type=str)
        parser.add_argument('RTOPD', type=str)
        parser.add_argument('NoTelpOPD', type=str)
        parser.add_argument('TglPendaftaran', type=str)
        parser.add_argument('NoPengesahan', type=str)
        parser.add_argument('TglPenghapusan', type=str)
        parser.add_argument('PetugasPendaftar', type=str)
        parser.add_argument('NOP', type=str)
        parser.add_argument('TglNOP', type=str)
        parser.add_argument('UserUpd', type=str)
        parser.add_argument('DateUpd', type=str)
        parser.add_argument('UsahaBadan', type=int)
        parser.add_argument('OPDID', type=str)
        parser.add_argument('latlng', type=str)


        try:
            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            select_query = MsOPD.query.filter_by(OPDID=id).first()
            if select_query:
                if args['NamaOPD']:
                    select_query.NamaOPD = f"{args['NamaOPD']}"
                if args['AlamatOPD']:
                    select_query.AlamatOPD = args['AlamatOPD']
                if args['KotaOPD']:
                    select_query.KotaOPD = args['KotaOPD']
                if args['KecamatanOPD']:
                    select_query.KecamatanOPD = args['KecamatanOPD']
                if args['KelurahanOPD']:
                    select_query.KelurahanOPD = args['KelurahanOPD']

                if args['NoTelpOPD']:
                    select_query.NoTelpOPD = args['NoTelpOPD']
                if args['TglPendaftaran']:
                    select_query.TglPendaftaran = args['TglPendaftaran']

                    select_query.UserUpd = uid
                    select_query.DateUpd = datetime.now()
                if args['latlng']:
                    select_query.latlng = args['latlng']
                db.session.commit()

                print('sukses update ke header')

                if select_query.OPDID:
                    data = {
                        'OPDID': args['OPDID'],
                        'uid': uid,
                        'UsahaBadan': args['UsahaBadan'],
                        'OPDID': select_query.OPDID
                    }
                    # update_record_detail = MsOPD.UpdatePendaftaranObjekPajakDetil(data)

                    # ////INCLUDE IMG
                    files_img = request.files
                    if files_img:
                        if not os.path.exists(f'./static/uploads/avatar_opd_temp'):
                            os.makedirs(f'./static/uploads/avatar_opd_temp')
                        folder_temp = f'./static/uploads/avatar_opd_temp'

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
                            thread = Process(target=GoToTaskUploadOPDAvatar,
                                             args=(folder_temp, filenames_str, id, kwargs['claim']['UserId'], False, request.origin))
                            thread.daemon = True
                            thread.start()

                    if select_query:
                        return success_update({'OPDID': select_query.OPDID, 'NamaOPD': select_query.NamaOPD,
                                                   'UsahaBadan': args['UsahaBadan'], 'OPDID': args['OPDID']})
                    else:
                        db.session.rollback()
                        return failed_update({})
                else:
                    db.session.rollback()
                    return failed_update({})
            else:
                return failed_update({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_update({})


class AddPendaftaranObjekPajakRekening(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, id,  *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('UsahaBadan', action='append', required=True, nullable=False, help="Name cannot be blank!")
        # parser.add_argument('UsahaBadan', type=non_empty_string, required=True, nullable=False,
        #                     help="Name cannot be blank!")
        # if not args['UsahaBadan'] or args['UsahaBadan'] == '':
        #     return failed_create({})
        try:
            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            select_query = MsOPD.query.filter_by(OPDID=id).first()
            result = {'success': [], 'failed': []}
            if select_query:
                if len(args['UsahaBadan']) > 1:
                    for row_id in args['UsahaBadan']:
                        data = {
                            'uid': uid,
                            'UsahaBadan': row_id,
                            'OPDID': select_query.OPDID
                        }
                        add_record_detail = MsOPD.AddPendaftaranObjekPajakDetil(data)
                        if add_record_detail:
                            result['success'].append(row_id)
                        else:
                            result['failed'].append(row_id)

                    return success_create({'OPDID': select_query.OPDID, 'UsahaBadan': result})
                else:
                    data = {
                        'uid': uid,
                        'UsahaBadan': args['UsahaBadan'][0],
                        'OPDID': select_query.OPDID
                    }
                    add_record_detail = MsOPD.AddPendaftaranObjekPajakDetil(data)
                    if add_record_detail:
                        return success_create({'OPDID': select_query.OPDID, 'UsahaBadan': args['UsahaBadan']})
                    else:
                        return failed_create({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_create({})


class DeletePendaftaranObjekPajak(Resource):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}

    def delete(self, id, *args, **kwargs):
        try:

            check_header = MsOPD.query.filter_by(OPDID=id)
            avatar = check_header.first()
            if avatar:
                thread = Process(target=GoToTaskDeleteOPDAvatar(avatar.avatar, request.origin))
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


class DeletePendaftaranObjekPajakMulti(Resource):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}

    def delete(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('id', action='append', required=True, nullable=False, help="Name cannot be blank!")
        args = parser.parse_args()
        try:
            ids_success = []
            ids_failed = []
            for id in args['id']:
                delete_record_detail = MsOPD.query.filter_by(OPDID=id)
                if delete_record_detail:
                    opdid = delete_record_detail.first().OPDID
                    check_detail = MsOPD.query.filter_by(OPDID=opdid).all()
                    if len(check_detail) == 1:
                        delete_record_detail.delete()
                        check_header = MsOPD.query.filter_by(OPDID=opdid)
                        check_header.delete()
                        db.session.commit()
                        if check_header:
                            ids_success.append(id)
                        else:
                            ids_failed.append(id)
                    else:
                        delete_record_detail.delete()
                        db.session.commit()
                        ids_success.append(id)
                else:
                    db.session.rollback()
            return success_delete({'deleted': ids_success, 'failed': ids_failed})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_delete({})


class PenonaktifanOPD(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        result = []
        try:
            select_query = db.session.query(MsOPD.OPDID, MsOPD.NamaOPD,  MsOPD.AlamatOPD,
                                            MsOPD.avatar, MsOPD.DateUpd
                                            )\
                .filter(MsOPD.TglPenghapusan == None)\
                .order_by(MsOPD.DateUpd.desc()).all()
            for row in select_query:

                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)

                result.append(d)
            return success_reads(result)

        except Exception as e:
            print(e)
            return failed_reads(result)


class PenonaktifanOPDEdit(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, opdid, *args, **kwargs):
        # select_query = db.session.execute( f"SELECT o.*,j.ParentID FROM MsOPD o LEFT JOIN
        # MsJenisPendapatan j ON o.UsahaBadan = j.JenisPendapatanID " f"WHERE OPDID='{opdid}'")
        select_query = db.session.query(MsOPD, MsGrupUsaha.GrupUsaha,
                                        MsKlasifikasiUsaha.JenisUsaha, MsKlasifikasiUsaha.KlasUsaha,
                                        MsLokasiKhusus.Lokasi
                                        ) \
            .outerjoin(MsGrupUsaha, MsGrupUsaha.GrupUsahaID == MsOPD.GrupUsahaID) \
            .outerjoin(MsKlasifikasiUsaha, MsKlasifikasiUsaha.KlasifikasiID == MsOPD.KlasifikasiID) \
            .outerjoin(MsLokasiKhusus, MsLokasiKhusus.LokasiID == MsOPD.LokasiID) \
            .filter(MsOPD.TglPenghapusan == None, MsOPD.OPDID == opdid)\
            .first()
        if select_query:
            data = toDict(select_query.MsOPD)
            # data.update({'ParentID': select_query.ParentID})
            # data.update({'Insidentil': False if select_query.MsOPD.Insidentil == 'N' else True})
            # data.update({'klas': False if select_query.MsOPD.klas == '2' else True})
            data.update({
                'optionGrupUsaha': {
                    'GrupUsaha': select_query.GrupUsaha,
                    'GrupUsahaID': select_query.MsOPD.GrupUsahaID
                }
            })
            data.update({
                'optionKlasifikasiUsaha': {
                    'Klasifikasi': f"{select_query.JenisUsaha} - {select_query.KlasUsaha}" if select_query.KlasUsaha else '',
                    'KlasifikasiID': select_query.MsOPD.KlasifikasiID
                }
            })
            data.update({
                'optionKlasifikasiKhusus': {
                    'Lokasi': select_query.Lokasi,
                    'LokasiID': select_query.MsOPD.KlasifikasiID
                }
            })


            cities = db.session.query(
                MsKota, MsKecamatan, MsKelurahan
            ).join(MsKecamatan, MsKecamatan.KotaID == MsKota.KotaID) \
                .join(MsKelurahan, MsKelurahan.KecamatanID == MsKecamatan.KecamatanID)
            if select_query.MsOPD.KelurahanOPD:
                cityBadan = cities.filter(
                    MsKelurahan.KelurahanID == select_query.MsOPD.KelurahanOPD).first()
                data.update({
                    'optionCitiesBadan': {
                        'name': cityBadan.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                + ', Kec.' + cityBadan.MsKecamatan.Kecamatan
                                + ', Kel.' + cityBadan.MsKelurahan.Kelurahan,
                    }
                })

            if select_query.MsOPD.KelurahanPengelola:
                cityManager = cities.filter(
                    MsKelurahan.KelurahanID == select_query.MsOPD.KelurahanPengelola).first()
                data.update({
                    'optionCitiesPengelola': {
                        'name': cityManager.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                + ', Kec.' + cityManager.MsKecamatan.Kecamatan
                                + ', Kel.' + cityManager.MsKelurahan.Kelurahan,
                    }
                })
            return success_reads(data)
        else:
            return success_reads({})


class UpdatePenonaktifanOPD(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()

        try:
            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            select_query = MsOPD.query.filter_by(OPDID=id).first()
            if select_query:
                select_query.TglPenghapusan = datetime.now()
                select_query.UserUpd = uid
                select_query.DateUpd = datetime.now()
            db.session.commit()
            return success_update({'OPDID': select_query.OPDID, 'NamaOPD': select_query.NamaOPD})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_update({})


class AktivasiOPD(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        result = []
        try:
            select_query = db.session.query(MsOPD.WPID, MsWPData.NamaBadan, MsWPData.NamaPemilik,
                                            MsOPD.OPDID, MsOPD.NamaOPD, MsOPD.AlamatOPD,
                                            MsOPD.avatar, MsOPD.DateUpd) \
                .select_from(MsOPD) \
                .join(MsWPData, MsOPD.WPID == MsWPData.WPID) \
                .filter(MsOPD.TglPenghapusan != None) \
                .order_by(MsOPD.DateUpd.desc()).all()

            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)

                result.append(d)
            return success_reads(result)

        except Exception as e:
            print(e)
            return failed_reads(result)


class AktivasiOPDEdit(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, opdid, *args, **kwargs):
        select_query = db.session.query(MsOPD, MsGrupUsaha.GrupUsaha, MsWPData.NamaPemilik,
                                        MsKlasifikasiUsaha.JenisUsaha, MsKlasifikasiUsaha.KlasUsaha,
                                        MsLokasiKhusus.Lokasi
                                        ) \
            .select_from(MsOPD) \
            .join(MsWPData, MsOPD.WPID == MsWPData.WPID) \
            .outerjoin(MsGrupUsaha, MsGrupUsaha.GrupUsahaID == MsOPD.GrupUsahaID) \
            .outerjoin(MsKlasifikasiUsaha, MsKlasifikasiUsaha.KlasifikasiID == MsOPD.KlasifikasiID) \
            .outerjoin(MsLokasiKhusus, MsLokasiKhusus.LokasiID == MsOPD.LokasiID) \
            .filter(MsOPD.TglPenghapusan != None, MsOPD.OPDID == opdid)\
            .first()
        if select_query:
            data = toDict(select_query.MsOPD)
            # data.update({'ParentID': select_query.ParentID})
            # data.update({'Insidentil': False if select_query.MsOPD.Insidentil == 'N' else True})
            # data.update({'klas': False if select_query.MsOPD.klas == '2' else True})
            data.update({
                'optionPemilik': {
                    'NamaPemilik': select_query.NamaPemilik,
                }
            })
            data.update({
                'optionGrupUsaha': {
                    'GrupUsaha': select_query.GrupUsaha,
                    'GrupUsahaID': select_query.MsOPD.GrupUsahaID
                }
            })
            data.update({
                'optionKlasifikasiUsaha': {
                    'Klasifikasi': f"{select_query.JenisUsaha} - {select_query.KlasUsaha}" if select_query.KlasUsaha else '',
                    'KlasifikasiID': select_query.MsOPD.KlasifikasiID
                }
            })
            data.update({
                'optionKlasifikasiKhusus': {
                    'Lokasi': select_query.Lokasi,
                    'LokasiID': select_query.MsOPD.KlasifikasiID
                }
            })

            cities = db.session.query(
                MsKota, MsKecamatan, MsKelurahan
            ).join(MsKecamatan, MsKecamatan.KotaID == MsKota.KotaID) \
                .join(MsKelurahan, MsKelurahan.KecamatanID == MsKecamatan.KecamatanID)
            if select_query.MsOPD.KelurahanOPD:
                cityBadan = cities.filter(
                    MsKelurahan.KelurahanID == select_query.MsOPD.KelurahanOPD).first()
                data.update({
                    'optionCitiesBadan': {
                        'name': cityBadan.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                + ', Kec.' + cityBadan.MsKecamatan.Kecamatan
                                + ', Kel.' + cityBadan.MsKelurahan.Kelurahan,
                    }
                })

            if select_query.MsOPD.KelurahanPengelola:
                cityManager = cities.filter(
                    MsKelurahan.KelurahanID == select_query.MsOPD.KelurahanPengelola).first()
                data.update({
                    'optionCitiesPengelola': {
                        'name': cityManager.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                + ', Kec.' + cityManager.MsKecamatan.Kecamatan
                                + ', Kel.' + cityManager.MsKelurahan.Kelurahan,
                    }
                })
            return success_reads(data)
        else:
            return success_reads({})


class UpdateAktivasiOPD(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()

        try:
            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            select_query = MsOPD.query.filter_by(OPDID=id).first()
            if select_query:
                select_query.TglPenghapusan = None
                select_query.UserUpd = uid
                select_query.DateUpd = datetime.now()
            db.session.commit()
            return success_update({'OPDID': select_query.OPDID, 'NamaOPD': select_query.NamaOPD})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_update({})