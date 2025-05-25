import base64
import os
import re
from datetime import datetime
from multiprocessing import Process

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
from controller.MsWPData import MsWPData
from controller.MsWP import MsWP
from controller.task.task_bridge import GoToTaskUploadWPAvatar, GoToTaskDeleteWPAvatar
from controller.tblUser import tblUser


class AddPendaftaran(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('klas', required=True, nullable=False,
                            help="Harus diisi")
        parser.add_argument('NamaBadan', required=True, nullable=False,
                            help="Harus diisi")
        parser.add_argument('UsahaBadan', required=False, nullable=True )
        # parser.add_argument('AlamatBadan', type=str, required=True, help="Harus diisi")
        parser.add_argument('AlamatBadan', type=str)
        parser.add_argument('KotaBadan', type=str, required=False)
        parser.add_argument('KecamatanBadan', required=True, nullable=False,
                            help="Harus diisi")
        parser.add_argument('KelurahanBadan', required=True, nullable=False,
                            help="Harus diisi")

        # parser.add_argument('AlamatPemilik', type=str, required=True, help="Harus diisi")
        parser.add_argument('AlamatPemilik', type=str)
        parser.add_argument('KotaPemilik', type=str, required=False)
        parser.add_argument('KecamatanPemilik', type=str, required=False)
        parser.add_argument('KelurahanPemilik', type=str, required=False)
        # parser.add_argument('NoTelpBadan', type=str, required=True, help="Harus diisi")
        parser.add_argument('NoTelpBadan', type=str)
        parser.add_argument('NamaPemilik', type=str, required=False)

        parser.add_argument('PetugasPendaftar', type=str, required=True, help="Harus diisi")
        parser.add_argument('Insidentil', type=str, required=False)
        parser.add_argument('klas', type=str, required=True, help="Harus diisi")
        # parser.add_argument('NoTelpPemilik', type=str, required=True, help="Harus diisi")
        parser.add_argument('NoTelpPemilik', type=str)
        parser.add_argument('TglPendaftaran', required=True, nullable=False,
                            help="Harus diisi")
        parser.add_argument('TglPengesahan', required=True, nullable=False,
                            help="Harus diisi")

        parser.add_argument('GrupUsahaID', type=str)
        parser.add_argument('KlasifikasiID', type=str)
        parser.add_argument('LokasiID', type=str)
        parser.add_argument('RWBadan', type=str)
        parser.add_argument('RTBadan', type=str)
        parser.add_argument('NoFaxBadan', type=str)
        parser.add_argument('JabatanPemilik', type=str)
        parser.add_argument('RWPemilik', type=str)
        parser.add_argument('RTPemilik', type=str)
        parser.add_argument('NoFaxPemilik', type=str)
        parser.add_argument('TglPenghapusan', type=str)

        parser.add_argument('avatar', type=str)
        parser.add_argument('latlng', type=str)
        parser.add_argument('NIK', type=str)
        parser.add_argument('NIB', type=str)
        parser.add_argument('WapuID', type=str)
        args = parser.parse_args()
        try:

            uid = kwargs['claim']["UID"]
            klas = '1' if args['klas'] or args['klas'] == "true" else '2'
            result = db.session.execute(
                f"exec [SP_NPWPD] '{klas}','{args['KecamatanBadan']}','{args['KelurahanBadan']}','{args['TglPengesahan']}'")

            result2 = []
            for row in result:
                result2.append(row)
            ObyekBadanNo = result2[0][0].replace(' ', '')
            NoPengesahan = result2[0][1]

            if ObyekBadanNo and NoPengesahan:
                add_record = MsWPData(
                    NamaBadan=args['NamaBadan'] if args['NamaBadan'] else '',
                    GrupUsahaID=args['GrupUsahaID'] if args['GrupUsahaID'] else '',
                    KlasifikasiID=args['KlasifikasiID'] if args['KlasifikasiID'] else '',
                    LokasiID=args['LokasiID'] if args['LokasiID'] else '',
                    AlamatBadan=args['AlamatBadan'] if args['AlamatBadan'] else '',
                    KotaBadan=args['KotaBadan'] if args['KotaBadan'] else '',
                    KecamatanBadan=args['KecamatanBadan'] if args['KecamatanBadan'] else '',
                    KelurahanBadan=args['KelurahanBadan'] if args['KelurahanBadan'] else '',
                    RWBadan=args['RWBadan'] if args['RWBadan'] else '',
                    RTBadan=args['RTBadan'] if args['RTBadan'] else '',
                    NoTelpBadan=args['NoTelpBadan'] if args['NoTelpBadan'] else '',
                    NoFaxBadan=args['NoFaxBadan'] if args['NoFaxBadan'] else '',
                    NamaPemilik=args['NamaPemilik'] if args['NamaPemilik'] else '',
                    JabatanPemilik=args['JabatanPemilik'] if args['JabatanPemilik'] else '',
                    AlamatPemilik=args['AlamatPemilik'] if args['AlamatPemilik'] else '',
                    KotaPemilik=args['KotaPemilik'] if args['KotaPemilik'] else '',
                    KecamatanPemilik=args['KecamatanPemilik'] if args['KecamatanPemilik'] else '',
                    KelurahanPemilik=args['KelurahanPemilik'] if args['KelurahanPemilik'] else '',
                    RWPemilik=args['RWPemilik'] if args['RWPemilik'] else '',
                    RTPemilik=args['RTPemilik'] if args['RTPemilik'] else '',
                    NoTelpPemilik=args['NoTelpPemilik'] if args['NoTelpPemilik'] else '',
                    NoFaxPemilik=args['NoFaxPemilik'] if args['NoFaxPemilik'] else '',
                    TglPendaftaran=args['TglPendaftaran'] if args['TglPendaftaran'] else '',
                    TglPengesahan=args['TglPengesahan'] if args['TglPengesahan'] else '',
                    NoPengesahan=NoPengesahan,
                    TglPenghapusan=sqlalchemy.sql.null(),
                    PetugasPendaftar=args['PetugasPendaftar'] if args['PetugasPendaftar'] else '',
                    Insidentil='Y' if args['Insidentil'] == "true" else 'N',
                    klas='1' if args['klas'] == "true" else '2',
                    UserUpd=uid,
                    DateUpd=datetime.now(),
                    ObyekBadanNo=ObyekBadanNo,
                    latlng=args['latlng'],
                    NIK=args['NIK'],
                    NIB = args['NIB'],
                    WapuID = args['WapuID']
                )
                db.session.add(add_record)
                db.session.commit()
                print('sukses insert ke header')
                if add_record:
                    data = {
                        'uid': uid,
                        'UsahaBadan': args['UsahaBadan'],
                        'WPID': add_record.WPID
                    }
                    add_record_detail = MsWP.AddPendaftaranDetil(data)

                    # ////INCLUDE IMG
                    files_img = request.files
                    if files_img:
                        if not os.path.exists(f'./static/uploads/avatar_wp_temp'):
                            os.makedirs(f'./static/uploads/avatar_wp_temp')
                        folder_temp = f'./static/uploads/avatar_wp_temp'

                        # add item img and upload
                        filenames = []

                        for img_row in files_img.items():
                            img_row_ok = img_row[1]
                            if img_row_ok.filename == '':
                                logger.info('file image dengan nama avatar wajib disertakan')
                            if img_row_ok:
                                new_filename = f"{add_record.WPID}.png"
                                img_row_ok.save(os.path.join(folder_temp, new_filename))
                                filenames.append(new_filename)
                        filenames_str = ','.join([str(elem) for elem in filenames])
                        # logger.info(filenames_str)
                        if filenames_str != '':
                            thread = Process(target=GoToTaskUploadWPAvatar,
                                             args=(folder_temp, filenames_str, add_record.WPID, kwargs['claim']['UserId'], False, request.origin))
                            thread.daemon = True
                            thread.start()

                    if add_record_detail:
                        return success_create({'WPID': add_record.WPID, 'NamaBadan': add_record.NamaBadan})
                else:
                    db.session.rollback()
                    return failed_create({})
            else:
                db.session.rollback()
                return failed_create({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_create({})


class UpdatePendaftaran(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('WapuID', type=str)
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
        parser.add_argument('klas', type=str)
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

        parser.add_argument('UsahaBadan', type=int)


        parser.add_argument('latlng', type=str)
        parser.add_argument('NIK', type=str)
        parser.add_argument('NIB', type=str)

        try:
            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            select_query = MsWPData.query.filter_by(WPID=id).first()
            if select_query:
                if args['WapuID']:
                    select_query.WapuID = f"{args['WapuID']}"
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
                if args['RWBadan'] == None or args['RTPemilik'] == 'null':
                    0
                else :
                    select_query.RWBadan = args['RWBadan']
                if args['RTBadan'] == None or args['RTPemilik'] == 'null':
                    0
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
                if args['RWPemilik'] != None or args['RTPemilik'] != 'null':
                    select_query.RWPemilik = args['RWPemilik']
                else :
                    None
                if args['RTPemilik'] != None or args['RTPemilik'] != 'null':
                    select_query.RTPemilik = args['RTPemilik']
                else:
                    None
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
                if args['TglPenghapusan']:
                    select_query.TglPenghapusan = args['TglPenghapusan']
                if args['PetugasPendaftar']:
                    select_query.PetugasPendaftar = args['PetugasPendaftar']
                if args['Insidentil']:
                    select_query.Insidentil = args['Insidentil']
                if args['klas']:
                    select_query.klas = args['klas']
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
                if args['RWPengelola']:
                    select_query.RWPengelola = args['RWPengelola']
                if args['RTPengelola']:
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
                if args['ObyekBadanNo']:
                    select_query.ObyekBadanNo = args['ObyekBadanNo']
                if args['latlng']:
                    select_query.latlng = args['latlng']
                if args['NIK']:
                    select_query.NIK = args['NIK']
                if args['NIB']:
                    select_query.NIB = args['NIB']
                db.session.commit()

                print('sukses update ke header')

                if select_query.WPID:
                    data = {
                        'WapuID': args['WapuID'],
                        'uid': uid,
                        'WPID': select_query.WPID
                    }
                    # update_record_detail = MsWP.UpdatePendaftaranDetil(data)

                    # ////INCLUDE IMG
                    files_img = request.files
                    if files_img:
                        if not os.path.exists(f'./static/uploads/avatar_wp_temp'):
                            os.makedirs(f'./static/uploads/avatar_wp_temp')
                        folder_temp = f'./static/uploads/avatar_wp_temp'

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
                            thread = Process(target=GoToTaskUploadWPAvatar,
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


class AddPendaftaranRekening(Resource):
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
            select_query = MsWPData.query.filter_by(WPID=id).first()
            result = {'success': [], 'failed': []}
            if select_query:
                if len(args['UsahaBadan']) > 1:
                    for row_id in args['UsahaBadan']:
                        data = {
                            'uid': uid,
                            'UsahaBadan': row_id,
                            'WPID': select_query.WPID
                        }
                        add_record_detail = MsWP.AddPendaftaranDetil(data)
                        if add_record_detail:
                            result['success'].append(row_id)
                        else:
                            result['failed'].append(row_id)

                    return success_create({'WPID': select_query.WPID, 'UsahaBadan': result})
                else:
                    data = {
                        'uid': uid,
                        'UsahaBadan': args['UsahaBadan'][0],
                        'WPID': select_query.WPID
                    }
                    add_record_detail = MsWP.AddPendaftaranDetil(data)
                    if add_record_detail:
                        return success_create({'WPID': select_query.WPID, 'UsahaBadan': args['UsahaBadan']})
                    else:
                        return failed_create({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_create({})


class DeletePendaftaran(Resource):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}




class DeletePendaftaranMulti(Resource):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}

    def delete(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('id', action='append', required=True, nullable=False, help="Name cannot be blank!")
        args = parser.parse_args()
        try:
            ids_success = []
            ids_failed = []
            for id in args['id']:
                delete_record_detail = MsWP.query.filter_by(OPDID=id)
                if delete_record_detail:
                    wpid = delete_record_detail.first().WPID
                    check_detail = MsWP.query.filter_by(WPID=wpid).all()
                    if len(check_detail) == 1:
                        delete_record_detail.delete()
                        check_header = MsWPData.query.filter_by(WPID=wpid)
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


class Penonaktifan(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        result = []
        try:
            select_query = db.session.query(MsWPData.WPID, MsWPData.NamaBadan, MsWPData.NamaPemilik, MsWPData.AlamatBadan,
                                            MsWPData.avatar, MsWPData.DateUpd
                                            )\
                .filter(MsWPData.TglPenghapusan == None)\
                .order_by(MsWPData.DateUpd.desc()).all()
            for row in select_query:

                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)

                result.append(d)
            return success_reads(result)

        except Exception as e:
            print(e)
            return failed_reads(result)


class PenonaktifanEdit(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, wpid, *args, **kwargs):
        select_query = db.session.query(MsWPData, MsGrupUsaha.GrupUsaha,
                                        MsKlasifikasiUsaha.JenisUsaha, MsKlasifikasiUsaha.KlasUsaha,
                                        MsLokasiKhusus.Lokasi, MsPegawai.Nama, MsWPData.NIK,MsWPData.NIB,
                                        ) \
            .outerjoin(MsGrupUsaha, MsGrupUsaha.GrupUsahaID == MsWPData.GrupUsahaID) \
            .outerjoin(MsKlasifikasiUsaha, MsKlasifikasiUsaha.KlasifikasiID == MsWPData.KlasifikasiID) \
            .outerjoin(MsLokasiKhusus, MsLokasiKhusus.LokasiID == MsWPData.LokasiID) \
            .outerjoin(MsPegawai, MsPegawai.PegawaiID == MsWPData.PetugasPendaftar) \
            .filter(MsWPData.TglPenghapusan == None, MsWPData.WPID == wpid)\
            .first()
        if select_query:
            data = toDict(select_query.MsWPData)
            # data.update({'ParentID': select_query.ParentID})
            data.update({'Insidentil': False if select_query.MsWPData.Insidentil == 'N' else True})
            data.update({'klas': False if select_query.MsWPData.klas == '2' else True})
            data.update({
                'optionGrupUsaha': {
                    'GrupUsaha': select_query.GrupUsaha,
                    'GrupUsahaID': select_query.MsWPData.GrupUsahaID
                }
            })
            data.update({
                'optionKlasifikasiUsaha': {
                    'Klasifikasi': f"{select_query.JenisUsaha} - {select_query.KlasUsaha}" if select_query.KlasUsaha else '',
                    'KlasifikasiID': select_query.MsWPData.KlasifikasiID
                }
            })
            data.update({
                'optionKlasifikasiKhusus': {
                    'Lokasi': select_query.Lokasi,
                    'LokasiID': select_query.MsWPData.KlasifikasiID
                }
            })
            data.update({
                'optionPetugas': {
                    'Petugas': select_query.Nama,
                    'PetugasID': select_query.MsWPData.PetugasPendaftar
                }
            })

            cities = db.session.query(
                MsKota, MsKecamatan, MsKelurahan
            ).join(MsKecamatan, MsKecamatan.KotaID == MsKota.KotaID) \
                .join(MsKelurahan, MsKelurahan.KecamatanID == MsKecamatan.KecamatanID)
            if select_query.MsWPData.KelurahanBadan:
                cityBadan = cities.filter(
                    MsKelurahan.KelurahanID == select_query.MsWPData.KelurahanBadan).first()
                data.update({
                    'optionCitiesBadan': {
                        'name': cityBadan.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                + ', Kec.' + cityBadan.MsKecamatan.Kecamatan
                                + ', Kel.' + cityBadan.MsKelurahan.Kelurahan,
                    }
                })
            if select_query.MsWPData.KelurahanPemilik:
                cityOwner = cities.filter(
                    MsKelurahan.KelurahanID == select_query.MsWPData.KelurahanPemilik).first()
                data.update({
                    'optionCitiesPemilik': {
                        'name': cityOwner.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                + ', Kec.' + cityOwner.MsKecamatan.Kecamatan
                                + ', Kel.' + cityOwner.MsKelurahan.Kelurahan,
                    }
                })
            if select_query.MsWPData.KelurahanPengelola:
                cityManager = cities.filter(
                    MsKelurahan.KelurahanID == select_query.MsWPData.KelurahanPengelola).first()
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


class UpdatePenonaktifan(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()

        try:
            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            select_query = MsWPData.query.filter_by(WPID=id).first()
            if select_query:
                select_query.TglPenghapusan = datetime.now()
                select_query.UserUpd = uid
                select_query.DateUpd = datetime.now()
            db.session.commit()
            return success_update({'WPID': select_query.WPID, 'NamaBadan': select_query.NamaBadan})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_update({})


class Aktivasi(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        result = []
        try:
            select_query = db.session.query(MsWPData.WPID, MsWPData.NamaBadan, MsWPData.NamaPemilik, MsWPData.AlamatBadan,
                                            MsWPData.avatar, MsWPData.DateUpd
                                            )\
                .filter(MsWPData.TglPenghapusan != None)\
                .order_by(MsWPData.DateUpd.desc()).all()
            for row in select_query:

                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)

                result.append(d)
            return success_reads(result)

        except Exception as e:
            print(e)
            return failed_reads(result)


class AktivasiEdit(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, wpid, *args, **kwargs):
        select_query = db.session.query(MsWPData, MsGrupUsaha.GrupUsaha,
                                        MsKlasifikasiUsaha.JenisUsaha, MsKlasifikasiUsaha.KlasUsaha,
                                        MsLokasiKhusus.Lokasi, MsPegawai.Nama, MsWPData.NIK,MsWPData.NIB,
                                        ) \
            .outerjoin(MsGrupUsaha, MsGrupUsaha.GrupUsahaID == MsWPData.GrupUsahaID) \
            .outerjoin(MsKlasifikasiUsaha, MsKlasifikasiUsaha.KlasifikasiID == MsWPData.KlasifikasiID) \
            .outerjoin(MsLokasiKhusus, MsLokasiKhusus.LokasiID == MsWPData.LokasiID) \
            .outerjoin(MsPegawai, MsPegawai.PegawaiID == MsWPData.PetugasPendaftar) \
            .filter(MsWPData.TglPenghapusan != None, MsWPData.WPID == wpid)\
            .first()
        if select_query:
            data = toDict(select_query.MsWPData)
            # data.update({'ParentID': select_query.ParentID})
            data.update({'Insidentil': False if select_query.MsWPData.Insidentil == 'N' else True})
            data.update({'klas': False if select_query.MsWPData.klas == '2' else True})
            data.update({
                'optionGrupUsaha': {
                    'GrupUsaha': select_query.GrupUsaha,
                    'GrupUsahaID': select_query.MsWPData.GrupUsahaID
                }
            })
            data.update({
                'optionKlasifikasiUsaha': {
                    'Klasifikasi': f"{select_query.JenisUsaha} - {select_query.KlasUsaha}" if select_query.KlasUsaha else '',
                    'KlasifikasiID': select_query.MsWPData.KlasifikasiID
                }
            })
            data.update({
                'optionKlasifikasiKhusus': {
                    'Lokasi': select_query.Lokasi,
                    'LokasiID': select_query.MsWPData.KlasifikasiID
                }
            })
            data.update({
                'optionPetugas': {
                    'Petugas': select_query.Nama,
                    'PetugasID': select_query.MsWPData.PetugasPendaftar
                }
            })

            cities = db.session.query(
                MsKota, MsKecamatan, MsKelurahan
            ).join(MsKecamatan, MsKecamatan.KotaID == MsKota.KotaID) \
                .join(MsKelurahan, MsKelurahan.KecamatanID == MsKecamatan.KecamatanID)
            if select_query.MsWPData.KelurahanBadan:
                cityBadan = cities.filter(
                    MsKelurahan.KelurahanID == select_query.MsWPData.KelurahanBadan).first()
                data.update({
                    'optionCitiesBadan': {
                        'name': cityBadan.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                + ', Kec.' + cityBadan.MsKecamatan.Kecamatan
                                + ', Kel.' + cityBadan.MsKelurahan.Kelurahan,
                    }
                })
            if select_query.MsWPData.KelurahanPemilik:
                cityOwner = cities.filter(
                    MsKelurahan.KelurahanID == select_query.MsWPData.KelurahanPemilik).first()
                data.update({
                    'optionCitiesPemilik': {
                        'name': cityOwner.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                                + ', Kec.' + cityOwner.MsKecamatan.Kecamatan
                                + ', Kel.' + cityOwner.MsKelurahan.Kelurahan,
                    }
                })
            if select_query.MsWPData.KelurahanPengelola:
                cityManager = cities.filter(
                    MsKelurahan.KelurahanID == select_query.MsWPData.KelurahanPengelola).first()
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


class UpdateAktivasi(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()

        try:
            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            select_query = MsWPData.query.filter_by(WPID=id).first()
            if select_query:
                select_query.TglPenghapusan = None
                select_query.UserUpd = uid
                select_query.DateUpd = datetime.now()
            db.session.commit()
            return success_update({'WPID': select_query.WPID, 'NamaBadan': select_query.NamaBadan})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_update({})