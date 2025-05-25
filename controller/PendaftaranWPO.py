import os
from datetime import datetime
from multiprocessing import Process

import sqlalchemy
from flask import request
from flask_restful import reqparse, Resource
from config.api_message import failed_create, success_read, success_create, success_update, failed_update, \
    success_delete, failed_delete
from config.config import appName, appFrontWebLogo, appFrontWebUrl
from config.database import db
from config.helper import non_empty_string, parser, logger
from controller.MsGrupUsaha import MsGrupUsaha
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsKlasifikasiUsaha import MsKlasifikasiUsaha
from controller.MsLokasiKhusus import MsLokasiKhusus
from controller.MsPegawai import MsPegawai
from controller.MsWP import MsWP
from controller.MsWPData import MsWPData
from controller.MsWPOData import MsWPOData
from controller.MsWPO import MsWPO
from controller.notifications.fcm_session import sendNotificationNative
from controller.notifications.notifications import Notifications
from controller.task.task_bridge import GoToTaskUploadWPAvatar
from controller.tblGroupUser import tblGroupUser
from controller.tblUser import tblUser
from controller.tblUserWP import tblUserWP
from controller.vw_obyekbadan import vw_obyekbadan
from controller.w_obyekbadanwpo import vw_obyekbadanwpo


class AddPendaftaranWPO(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('NamaBadan', required=True, nullable=False,
                            help="Harus diisi")
        parser.add_argument('UsahaBadan', required=True, nullable=False,
                            help="Harus diisi", type=int)
        parser.add_argument('AlamatBadan', type=str)
        parser.add_argument('KotaBadan', type=str, required=True, help="Harus diisi")
        parser.add_argument('KecamatanBadan', required=True, nullable=False,
                            help="Harus diisi")
        parser.add_argument('KelurahanBadan', required=False, nullable=True,
                            help="Harus diisi")

        parser.add_argument('AlamatPemilik', type=str)
        parser.add_argument('KotaPemilik', type=str, required=True, help="Harus diisi")
        parser.add_argument('KecamatanPemilik', type=str, required=True, help="Harus diisi")
        parser.add_argument('KelurahanPemilik', type=str, required=True, help="Harus diisi")
        parser.add_argument('NoTelpBadan', type=str)
        parser.add_argument('NamaPemilik', type=str, required=True, help="Harus diisi")
        parser.add_argument('Insidentil', type=str, help="Harus diisi")
        parser.add_argument('NoTelpPemilik', type=str)
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
        parser.add_argument('avatar', type=str)
        parser.add_argument('latlng', type=str)
        parser.add_argument('NIK', type=str)
        args = parser.parse_args()

        if not args['UsahaBadan'] or args['UsahaBadan'] == '' or args['UsahaBadan'] == ' ':
            return failed_create({})

        try:
            UserId = kwargs['claim']["UserId"]
            email = kwargs['user_info'].Email
            add_record = MsWPOData(
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
                Insidentil='Y' if args['Insidentil'] else 'N',
                UserUpd=UserId,
                DateUpd=datetime.now(),
                latlng=args['latlng'],
                # avatar=args['avatar'],
                NIK=args['NIK']
            )
            db.session.add(add_record)
            db.session.commit()
            # print('sukses insert ke header')
            if add_record:
                data = {
                    'UsahaBadan': args['UsahaBadan'],
                    'WPID': add_record.WPID
                }
                add_record_detail = MsWPO.AddPendaftaranDetilWPO(data)
                if add_record_detail:

                    # ADD AVATAR
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
                                             args=(
                                             folder_temp, filenames_str, add_record.WPID, kwargs['claim']['UserId'], True, request.origin))
                            thread.daemon = True
                            thread.start()

                    # NOTIF TO USERS
                    list_user = tblUser.query.join(tblGroupUser).filter(tblGroupUser.IsPendaftaran == 1).all()
                    for row in list_user:
                        if row.DeviceId and row.APIKey:
                            notifBody = f"Halo {row.nama_user}, ada pengajuan pendaftaran usaha baru ({args['NamaBadan']}) yang harus segera anda konfirmasi di aplikasi {appName}. Anda menerima pemberitahuan ini karena anda adalah petugas pajak bagian pendaftaran atau administrator."
                            notification_data = {
                                "notification": {
                                    "title": appName,
                                    "body": notifBody,
                                    "priority": "high",
                                    "icon": appFrontWebLogo,
                                    "click_action": f"{appFrontWebUrl()}#/admin/pendaftaran/confirm",
                                },
                                "data": {
                                    "type": "new_reg_wp",
                                    "page": "pendaftaran-confirm",
                                    "id": add_record.WPID,
                                    "new_row": {
                                        "WPID": add_record.WPID,
                                        "NamaBadan": args['NamaBadan'],
                                        "AlamatBadan": args['AlamatBadan'],
                                        "avatar": "",
                                        "DateUpd": add_record.DateUpd.strftime("%Y-%m-%d %H:%M:%S")
                                    }
                                }
                            }
                            sendNotif = sendNotificationNative(row.DeviceId, notification_data)
                            if sendNotif.status_code == 200:
                                add_notif = Notifications(
                                    UserId=row.UserId,
                                    id_notificationsType=4,
                                    title="Pendaftaran Baru",
                                    description=notifBody,
                                    created_by="system"
                                )
                                db.session.add(add_notif)
                                db.session.commit()
                    return success_create({'WPID': add_record.WPID, 'NamaBadan': add_record.NamaBadan})
            else:
                db.session.rollback()
                return failed_create({})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_create({})


class UpdatePendaftaranWPO(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('WPID', type=int)
        parser.add_argument('TglPengesahan', type=str)
        parser.add_argument('PetugasPendaftar', type=str)
        try:
            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            select_query = vw_obyekbadanwpo.query.filter_by(WPID=args['WPID']).first()
            result = db.session.execute(
                f"exec [SP_NPWPD] '{select_query.KecamatanBadan}','{select_query.KelurahanBadan}','{args['TglPengesahan']}'")
            result2 = []
            for row in result:
                result2.append(row)
            ObyekBadanNo = result2[0][0].replace(' ', '')
            NoPengesahan = result2[0][1]

            if ObyekBadanNo and NoPengesahan:
                add_record = MsWPData(
                    NamaBadan=select_query.NamaBadan,
                    GrupUsahaID=select_query.GrupUsahaID,
                    KlasifikasiID='',
                    LokasiID=select_query.LokasiID,
                    AlamatBadan=select_query.AlamatBadan,
                    KotaBadan=select_query.KotaBadan,
                    KecamatanBadan=select_query.KecamatanBadan,
                    KelurahanBadan=select_query.KelurahanBadan if select_query.KelurahanBadan else '',
                    RWBadan='',
                    RTBadan='',
                    NoTelpBadan=select_query.NoTelpBadan,
                    NoFaxBadan='',
                    NamaPemilik=select_query.NamaPemilik,
                    JabatanPemilik=select_query.JabatanPemilik,
                    AlamatPemilik=select_query.AlamatPemilik,
                    KotaPemilik=select_query.KotaPemilik,
                    KecamatanPemilik=select_query.KecamatanPemilik,
                    KelurahanPemilik=select_query.KelurahanPemilik,
                    RWPemilik='',
                    RTPemilik='',
                    NoTelpPemilik=select_query.NoTelpPemilik,
                    NoFaxPemilik='',
                    TglPendaftaran=select_query.DateUpd,
                    TglPengesahan=args['TglPengesahan'],
                    NoPengesahan=NoPengesahan,
                    TglPenghapusan=sqlalchemy.sql.null(),
                    PetugasPendaftar=args['PetugasPendaftar'],
                    Insidentil='N',
                    UserUpd=uid,
                    DateUpd=datetime.now(),
                    ObyekBadanNo=ObyekBadanNo,
                    avatar=select_query.avatar,
                    latlng=select_query.latlng,
                    NIK=select_query.NIK
                )
                db.session.add(add_record)
                db.session.commit()
                # print('sukses insert ke header')
                if add_record:
                    data = {
                        'uid': uid,
                        'UsahaBadan': select_query.UsahaBadan,
                        'WPID': add_record.WPID
                    }
                    add_record_detail = MsWP.AddPendaftaranDetil(data)
                    if add_record_detail:
                        datawpo = {
                            'OPDID': select_query.OPDID,
                        }

                        # CHECK APAKAH YANG MENGUPDATE SEBELUMNYA DATA ADALAH WP ?
                        # check_user_pendaftar = tblUserWP.query.filter_by(UID=select_query.UserUpd).first()
                        user_pendaftar = tblUser.query.filter_by(UID=uid)\
                            .filter(tblUser.Group.has(IsWP=1))\
                            .first()

                        UID_user_pendaftar = None
                        if user_pendaftar:
                            UID_user_pendaftar = user_pendaftar.UID.split("@")[0]
                        else:
                            # JIKA BUKAN WP BERARTI ADALAH PETUGAS
                            user_pendaftar = tblUser.query.filter_by(UID=uid).first()
                            UID_user_pendaftar = user_pendaftar.UID

                        delete_wpo = DeletePendaftaranWPO(datawpo)
                        if delete_wpo:
                            if user_pendaftar:
                                # user_pendaftar = tblUser.query.filter_by(UserId=select_query.UserUpd).first()

                                # ////add to mapping tblUserWp
                                db.session.execute(
                                    f"""INSERT INTO [dbo].[tblUserWP] ([UserId],[UID],[WPID])
                                                            VALUES ( {user_pendaftar.UserId},'{UID_user_pendaftar}',{add_record.WPID} );"""
                                )
                                # NOTIF USER PENDAFTAR
                                if user_pendaftar.DeviceId:
                                    notifBody = f'Pendaftaran usaha {add_record.NamaBadan} yang anda ajukan telah di konfirmasi dan disetujui. Kini anda dapat melaporkan pajak usaha anda. Terima Kasih.'
                                    notification_data = {
                                        "notification": {
                                            "title": f'Pendaftaran Usaha {add_record.NamaBadan} Telah Dikonfirmasi',
                                            "body": notifBody,
                                            "priority": "high",
                                            "icon": appFrontWebLogo,
                                            "click_action": "FLUTTER_NOTIFICATION_CLICK",
                                        },
                                        "data": {
                                            "action": "refresh",
                                            "type": "confirmed_usaha",
                                            "page": "home"
                                        }
                                    }
                                    sendNotif = sendNotificationNative(user_pendaftar.DeviceId, notification_data)
                                    if sendNotif.status_code == 200:
                                        add_notif = Notifications(
                                            UserId=user_pendaftar.UserId,
                                            id_notificationsType=1,
                                            title=f"Pendaftaran Usaha {add_record.NamaBadan} Dikonfirmasi",
                                            description=notifBody,
                                            created_by="system"
                                        )
                                        db.session.add(add_notif)
                                        db.session.commit()
                            return success_create({'WPID': add_record.WPID, 'NamaBadan': add_record.NamaBadan})
                else:
                    db.session.rollback()
                    return failed_update({})
            else:
                return failed_update({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_update({})


def DeletePendaftaranWPO(datawpo):
    try:
        delete_record_detail = MsWPO.query.filter_by(OPDID=datawpo['OPDID'])
        if delete_record_detail:
            wpid = delete_record_detail.first().WPID
            check_detail = MsWPO.query.filter_by(WPID=wpid).all()
            # print(len(check_detail))
            if len(check_detail) == 1:
                delete_record_detail.delete()
                check_header = MsWPOData.query.filter_by(WPID=wpid)
                check_header.delete()
                db.session.commit()
                if check_header:
                    return success_delete({})
                else:
                    db.session.rollback()
                    return failed_delete({})
            else:
                delete_record_detail.delete()
                db.session.commit()
                return success_delete({})
        else:
            db.session.rollback()
            return failed_delete({})
    except Exception as e:
        db.session.rollback()
        print(e)
        return failed_delete({})
#
# class AddPendaftaranRekening(Resource):
#     method_decorators = {'post': [tblUser.auth_apikey_privilege]}
#
#     def post(self, id,  *args, **kwargs):
#         parser = reqparse.RequestParser()
#         parser.add_argument('UsahaBadan', action='append', required=True, nullable=False, help="Name cannot be blank!")
#         # parser.add_argument('UsahaBadan', type=non_empty_string, required=True, nullable=False,
#         #                     help="Name cannot be blank!")
#         try:
#             args = parser.parse_args()
#             uid = kwargs['claim']["UID"]
#             select_query = MsWPOData.query.filter_by(WPID=id).first()
#             result = {'success': [], 'failed': []}
#             if select_query:
#                 if len(args['UsahaBadan']) > 1:
#                     for row_id in args['UsahaBadan']:
#                         data = {
#                             'uid': uid,
#                             'UsahaBadan': row_id,
#                             'WPID': select_query.WPID
#                         }
#                         add_record_detail = MsWPO.AddPendaftaranDetil(data)
#                         if add_record_detail:
#                             result['success'].append(row_id)
#                         else:
#                             result['failed'].append(row_id)
#
#                     return success_create({'WPID': select_query.WPID, 'UsahaBadan': result})
#                 else:
#                     data = {
#                         'uid': uid,
#                         'UsahaBadan': args['UsahaBadan'][0],
#                         'WPID': select_query.WPID
#                     }
#                     add_record_detail = MsWPO.AddPendaftaranDetil(data)
#                     if add_record_detail:
#                         return success_create({'WPID': select_query.WPID, 'UsahaBadan': args['UsahaBadan']})
#                     else:
#                         return failed_create({})
#         except Exception as e:
#             db.session.rollback()
#             print(e)
#             return failed_create({})
#
#
# class DeletePendaftaran(id):
#     method_decorators = {'delete': [tblUser.auth_apikey_privilege]}
#
#     def delete(self, id, *args, **kwargs):
#         try:
#             delete_record_detail = MsWPO.query.filter_by(OPDID=id)
#             if delete_record_detail:
#                 wpid = delete_record_detail.first().WPID
#                 check_detail = MsWPO.query.filter_by(WPID=wpid).all()
#                 # print(len(check_detail))
#                 if len(check_detail) == 1:
#                     delete_record_detail.delete()
#                     check_header = MsWPOData.query.filter_by(WPID=wpid)
#                     check_header.delete()
#                     db.session.commit()
#                     if check_header:
#                         return success_delete({})
#                     else:
#                         db.session.rollback()
#                         return failed_delete({})
#                 else:
#                     delete_record_detail.delete()
#                     db.session.commit()
#                     return success_delete({})
#             else:
#                 db.session.rollback()
#                 return failed_delete({})
#         except Exception as e:
#             db.session.rollback()
#             print(e)
#             return failed_delete({})
#
#
# class DeletePendaftaranMulti(Resource):
#     method_decorators = {'delete': [tblUser.auth_apikey_privilege]}
#
#     def delete(self, *args, **kwargs):
#         parser = reqparse.RequestParser()
#         parser.add_argument('id', action='append', required=True, nullable=False, help="Name cannot be blank!")
#         args = parser.parse_args()
#         try:
#             ids_success = []
#             ids_failed = []
#             for id in args['id']:
#                 delete_record_detail = MsWPO.query.filter_by(OPDID=id)
#                 if delete_record_detail:
#                     wpid = delete_record_detail.first().WPID
#                     check_detail = MsWPO.query.filter_by(WPID=wpid).all()
#                     if len(check_detail) == 1:
#                         delete_record_detail.delete()
#                         check_header = MsWPOData.query.filter_by(WPID=wpid)
#                         check_header.delete()
#                         db.session.commit()
#                         if check_header:
#                             ids_success.append(id)
#                         else:
#                             ids_failed.append(id)
#                     else:
#                         delete_record_detail.delete()
#                         db.session.commit()
#                         ids_success.append(id)
#                 else:
#                     db.session.rollback()
#             return success_delete({'deleted': ids_success, 'failed': ids_failed})
#         except Exception as e:
#             db.session.rollback()
#             print(e)
#             return failed_delete({})