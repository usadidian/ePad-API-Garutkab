from datetime import datetime
from flask_restful import Resource, reqparse
from config.api_message import success_reads, failed_create, success_create, \
    success_update, failed_update, success_delete, failed_delete
from config.config import appName, appFrontWebLogo, appFrontWebUrl
from config.database import db
from config.helper import logger
from controller.MsPegawai import MsPegawai
from controller.MsStrategisDtl import MsStrategisDtl
from controller.MsStrategisHdr import MsStrategisHdr
from controller.MsTitikLokasiHdr import MsTitikLokasiHdr
from controller.PendataanReklameDtl import PendataanReklameDtl
from controller.PendataanReklameHdr import PendataanReklameHdr
from controller.notifications.fcm_session import sendNotificationNative
from controller.notifications.notifications import Notifications
from controller.tblGroupUser import tblGroupUser
from controller.tblUser import tblUser
from controller.vw_obyekbadan import vw_obyekbadan
from controller.vw_pendataan import vw_pendataan


class PendataanSKPReklame(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, opdid, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT x.UPTID,x.SPT,x.MasaAwal,x.MasaAkhir,TglPendataan,y.DetailID, v.AlamatPemilik,v.KodeRekening,"
            f"v.NamaJenisPendapatan,v.NamaBadan,v.ObyekBadanNo,v.NamaPemilik,(CASE WHEN TglPenetapan IS NULL THEN 'Terdata' "
            f"ELSE 'SKP' END) AS Penetapan, JumlahReklame AS Jumlah, (select distinct NamaLokasi from MsTitikLokasiHdr h "
            f"where h.LokasiID = y.LokasiID) + (case when AlamatPasang = '' OR AlamatPasang IS null then ' - '+ NamaLokasi else ' - ' + AlamatPasang end) AS Lokasi, "
            f"y.TarifPajak AS Pajak FROM (((PendataanReklameHdr x LEFT JOIN PenetapanReklameHdr p ON x.OPDID = p.OPDID "
            f"AND x.MasaAwal = p.MasaAwal AND x.MasaAkhir = p.MasaAkhir AND x.UrutTgl = p.UrutTgl) LEFT JOIN vw_obyekbadan v ON x.OPDID = v.OPDID)  "
            f"LEFT JOIN PendataanReklameDtl y ON x.SPT = y.SPT) WHERE x.OPDID = '{opdid}' ORDER BY x.MasaAwal DESC")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                if key == 'Pajak':
                    d[key] = str(getattr(row, key))
                else:
                    d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


class HitungSKPReklame(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('MasaAwal', type=str)
        parser.add_argument('MasaAkhir', type=str)

        parser.add_argument('LokasiID', type=str)
        parser.add_argument('AlamatPasang', type=str)
        parser.add_argument('LuasReklame', type=int)
        parser.add_argument('PanjangReklame', type=str)
        parser.add_argument('LebarReklame', type=str)
        parser.add_argument( 'TinggiReklame', type=str )
        parser.add_argument('SudutPandang', type=str)
        parser.add_argument('JumlahReklame', type=int)
        parser.add_argument('TarifPajak', type=str)
        parser.add_argument('StrategisID1', type=int)
        parser.add_argument('StrategisID2', type=int)
        parser.add_argument( 'StrategisID3', type=int )
        parser.add_argument( 'StrategisID4', type=int )
        parser.add_argument( 'StrategisID5', type=int )
        parser.add_argument( 'StrategisID6', type=int )
        parser.add_argument( 'StrategisID7', type=int )

        args = parser.parse_args()

        masaawal = args['MasaAwal']
        masaakhir = args['MasaAkhir']

        panjang = args['PanjangReklame']
        lebar = args['LebarReklame']
        tinggi = args['TinggiReklame']
        luas = float(panjang) * float(lebar)
        jumlahreklame = args['JumlahReklame']
        klasjalan = args['StrategisID1']
        kawasan = args['StrategisID2']
        sudutpandang = args['StrategisID3']
        nilaistrategis = args['StrategisID4']
        nilaiketinggian = args['StrategisID5']
        klasifikasi = args['StrategisID6']
        rokok = args['StrategisID7']


        select_query = db.session.execute(
            f"exec [SP_WPO_HITREKLA] '{masaawal}','{masaakhir}','{panjang}','{lebar}','{tinggi}','{jumlahreklame}',"
            f"'{klasjalan}','{kawasan}', '{sudutpandang}','{nilaistrategis}','{nilaiketinggian}','{klasifikasi}',"
            f"'{rokok}','{args['LokasiID']}'")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)

class AddPendataanSKPReklame(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('SPT', type=str)
        parser.add_argument('OPDID', type=str)
        parser.add_argument('TglPendataan', type=str)
        parser.add_argument('MasaAwal', type=str)
        parser.add_argument('MasaAkhir', type=str)
        parser.add_argument('UrutTgl', type=str)
        parser.add_argument('TotalPajak', type=str)
        # parser.add_argument('UPTID', type=str)
        parser.add_argument('Status', type=str)
        parser.add_argument('UserUpd', type=str)
        parser.add_argument('DateUpd', type=str)

        parser.add_argument('PendataanID', type=str)
        parser.add_argument('JudulReklame', type=str)
        parser.add_argument('JenisLokasi', type=str)
        parser.add_argument('LokasiID', type=str)
        parser.add_argument('AlamatPasang', type=str)
        parser.add_argument('LuasReklame', type=int)
        parser.add_argument( 'TinggiReklame', type=int )
        parser.add_argument('PanjangReklame', type=str)
        parser.add_argument('LebarReklame', type=str)
        parser.add_argument('SudutPandang', type=str)
        parser.add_argument('JumlahReklame', type=int)
        parser.add_argument('TarifPajak', type=str)
        parser.add_argument('LKecamatan', type=str)
        parser.add_argument('LKelurahan', type=str)
        parser.add_argument('StrategisID1', type=int)
        parser.add_argument('StrategisID2', type=int)
        parser.add_argument( 'StrategisID3', type=int )
        parser.add_argument( 'StrategisID4', type=int )
        parser.add_argument( 'StrategisID5', type=int )
        parser.add_argument( 'StrategisID6', type=int )
        parser.add_argument( 'StrategisID7', type=int )

        uid = kwargs['claim']["UID"]

        try:
            args = parser.parse_args()

            result = db.session.execute(
                f"exec [SP_SPT2] '{args['TglPendataan']}'" )
            result2 = []
            for row in result:
                result2.append( row )
                # print(row[0])
            spt = result2[0][0]
            print( spt )

            select_query = db.session.execute(
                f"SELECT DISTINCT isnull(max(UrutTgl) + 1,1) FROM PendataanReklameHdr "
                f"WHERE OPDID = '{args['OPDID']}' AND MasaAwal='{args['MasaAwal']}' AND MasaAkhir='{args['MasaAkhir']}'")
            result3 = select_query.first()[0]
            uruttgl = result3

            opdid = args['OPDID']
            tglpendataan = args['TglPendataan']
            masaawal = args['MasaAwal']
            masaakhir = args['MasaAkhir']

            panjang = args['PanjangReklame']
            lebar = args['LebarReklame']
            tinggi = args['TinggiReklame']
            luas = float( panjang ) * float( lebar )
            jumlahreklame = args['JumlahReklame']
            klasjalan = args['StrategisID1']
            kawasan = args['StrategisID2']
            sudutpandang = args['StrategisID3']
            nilaistrategis = args['StrategisID4']
            nilaiketinggian = args['StrategisID5']
            klasifikasi = args['StrategisID6']
            rokok = args['StrategisID7']

            select_query = db.session.execute(
                f"exec [SP_WPO_HITREKLA] '{masaawal}','{masaakhir}','{panjang}','{lebar}','{tinggi}','{jumlahreklame}',"
                f"'{klasjalan}','{kawasan}', '{sudutpandang}','{nilaistrategis}','{nilaiketinggian}','{klasifikasi}',"
                f"'{rokok}','{args['LokasiID']}'")
            result3 = select_query.first()[0]
            tarifpajak = float(result3)

            PegawaiID = kwargs['claim']["PegawaiID"] if "PegawaiID" in kwargs['claim'] else None
            if PegawaiID:
                select_query = db.session.query( MsPegawai.UPTID ).join( tblUser ).filter(
                    tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID ).first()
                result = select_query[0]
                uptid = result
                print( uptid )
            else:
                select_query = db.session.execute(
                    f"SELECT mu.UPTID FROM MsUPT AS mu WHERE mu.KDUNIT IN(SELECT gp.ParamStrValue "
                    f"FROM GeneralParameter AS gp WHERE gp.ParamID='satker_sipkd') AND RIGHT(mu.KodeUPT,3)='05.'" )
                result = select_query.first()[0]
                uptid = result

            if args['PanjangReklame'] != None:

                add_record = PendataanReklameHdr(
                    SPT=spt,
                    OPDID=opdid,
                    TglPendataan=tglpendataan,
                    MasaAwal=args['MasaAwal'],
                    MasaAkhir=args['MasaAkhir'],
                    UrutTgl=uruttgl,
                    TotalPajak=0,
                    UPTID=uptid if uptid else '',
                    Status=1,
                    UserUpd=uid,
                    DateUpd=datetime.now()
                )
                db.session.add(add_record)
                db.session.commit()
                if add_record.PendataanID:
                    db.session.execute(
                        f"UPDATE MsOPD SET TglPendataan = '{tglpendataan}' WHERE OPDID = {opdid} "
                        f"AND TglPendataan IS NULL")
                    data = {
                        'uid': uid,
                        'PendataanID': add_record.PendataanID,
                        'SPT': add_record.SPT,
                        'JudulReklame': args['JudulReklame'],
                        'LokasiID': args['LokasiID'],
                        'AlamatPasang': args['AlamatPasang'],
                        'TinggiReklame': args['TinggiReklame'],
                        'PanjangReklame': args['PanjangReklame'],
                        'LebarReklame': args['LebarReklame'],
                        'SudutPandang': args['SudutPandang'],
                        'JumlahReklame': args['JumlahReklame'],
                        'LKecamatan': args['LKecamatan'],
                        'LKelurahan': args['LKelurahan'],
                        'StrategisID1': args['StrategisID1'],
                        'StrategisID2': args['StrategisID2'],
                        'LuasReklame': luas,
                        'TarifPajak': tarifpajak,
                        'kawasan': args['StrategisID1'],
                        'lokasi': args['StrategisID1']

                    }
                    add_record_detail = PendataanReklameDtl.AddPPendataanDetil(data)
                    if not add_record_detail:
                        db.session.rollback()
                        return failed_create({})

                    # notif ke group penetapan
                    vw_obyekbadans = vw_obyekbadan.query.filter_by(OPDID=opdid).first()
                    list_user = tblUser.query.join(tblGroupUser).filter(tblGroupUser.IsPenetapan == 1).all()
                    for row in list_user:
                        if row.DeviceId:
                            notifBody = f"Halo {row.nama_user}, ada pendataan baru {vw_obyekbadans.NamaBadan} yang harus segera anda tetapkan. Anda menerima pemberitahuan ini karena anda adalah petugas pajak bagian penetapan atau administrator."
                            notification_data = {
                                "notification": {
                                    "title": appName,
                                    "body": notifBody,
                                    "priority": "high",
                                    "icon": appFrontWebLogo,
                                    "click_action": f"{appFrontWebUrl()}#/admin/penetapan/await",
                                },
                                "data": {
                                    "type": "new_lapor",
                                    "page": "penetapan-confirm",
                                }
                            }
                            sendNotif = sendNotificationNative(row.DeviceId, notification_data)
                            if sendNotif.status_code == 200:
                                add_notif = Notifications(
                                    UserId=row.UserId,
                                    id_notificationsType=5,
                                    title="Pendataan Baru",
                                    description=notifBody,
                                    created_by="system"
                                )
                                db.session.add(add_notif)
                                db.session.commit()
                    return success_create({'SPT': add_record.SPT,
                                           'UPTID': add_record.UPTID,
                                           'OPDID': add_record.OPDID,
                                           'PendataanID': add_record.PendataanID
                                           })
            else:
                db.session.rollback()
                return failed_create({})

        except Exception as e:
            db.session.rollback()
            logger.error(e)
            return failed_create({})


class UpdatePendataanSKPReklame(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):

        parser = reqparse.RequestParser()
        print(kwargs['claim'])
        parser.add_argument('SPT', type=str)
        parser.add_argument('OPDID', type=str)
        parser.add_argument('TglPendataan', type=str)
        parser.add_argument('MasaAwal', type=str)
        parser.add_argument('MasaAkhir', type=str)
        parser.add_argument('UrutTgl', type=str)
        parser.add_argument('TotalPajak', type=str)
        parser.add_argument('UPTID', type=str)
        parser.add_argument('Status', type=str)
        parser.add_argument('UserUpd', type=str)
        parser.add_argument('DateUpd', type=str)

        parser.add_argument('PendataanID', type=str)
        parser.add_argument('JudulReklame', type=str)
        parser.add_argument('JenisLokasi', type=str)
        parser.add_argument('LokasiID', type=str)
        parser.add_argument('AlamatPasang', type=str)
        parser.add_argument('LuasReklame', type=str)
        parser.add_argument('PanjangReklame', type=str)
        parser.add_argument('LebarReklame', type=str)
        parser.add_argument('SudutPandang', type=str)
        parser.add_argument('JumlahReklame', type=str)
        parser.add_argument('TarifPajak', type=str)
        parser.add_argument('LKecamatan', type=str)
        parser.add_argument('LKelurahan', type=str)
        parser.add_argument('StrategisID1', type=int)
        parser.add_argument('StrategisID2', type=int)
        parser.add_argument('NoUrut', type=int)
        parser.add_argument('DetailID', type=int)

        args = parser.parse_args()
        uid = kwargs['claim']["UID"]
        opdid = args['OPDID']
        tglpendataan = args['TglPendataan']
        masaawal = args['MasaAwal']
        masaakhir = args['MasaAkhir']

        panjang = args['PanjangReklame']
        lebar = args['LebarReklame']
        luas = float(panjang) * float(lebar)
        sudutpandang = args['SudutPandang']
        jumlahreklame = args['JumlahReklame']

        select_query = db.session.query(MsTitikLokasiHdr.LokasiID).filter(
            MsTitikLokasiHdr.LokasiID == args['LokasiID'])
        lokasiid = select_query.first()[0]

        select_query = db.session.query(MsStrategisDtl.DetailID).join(MsStrategisHdr).filter(
            MsStrategisHdr.StrategisID == args['StrategisID1'])
        kawasan = select_query.first()[0]

        select_query2 = db.session.query(MsStrategisDtl.DetailID).join(MsStrategisHdr).filter(
            MsStrategisHdr.StrategisID == args['StrategisID2'])
        lokasi = select_query2.first()[0]

        select_query = db.session.execute(
            f"exec [SP_WPO_HITREKLA] '{masaawal}','{masaakhir}','{panjang}',"
            f"'{lebar}','{sudutpandang}','{jumlahreklame}',"
            f"'{kawasan}','{lokasi}','{lokasiid}'")
        result3 = select_query.first()[0]
        tarifpajak = float(result3)

        try:
            select_query = PendataanReklameHdr.query.filter_by(SPT=id).first()
            if select_query:
                if args['OPDID']:
                    select_query.OPDID = args['OPDID']
                if args['TglPendataan']:
                    select_query.TglPendataan = args['TglPendataan']
                if args['MasaAwal']:
                    select_query.MasaAwal = args['MasaAwal']
                if args['MasaAkhir']:
                    select_query.MasaAkhir = args['MasaAkhir']
                if args['UrutTgl']:
                    select_query.UrutTgl = args['UrutTgl']
                if args['TotalPajak']:
                    select_query.TotalPajak = args['TotalPajak']
                if args['UPTID']:
                    select_query.UPTID = args['UPTID']
                if args['Status']:
                    select_query.Status = args['Status']
                select_query.UserUpd = uid
                select_query.DateUpd = datetime.now()
                db.session.commit()
                print('sukses update ke header')
                if select_query.SPT:
                    data = {
                        'uid': uid,
                        'PendataanID': select_query.PendataanID,
                        'SPT': select_query.SPT,
                        'MasaAwal': select_query.MasaAwal,
                        'MasaAkhir': select_query.MasaAkhir,
                        'JudulReklame': args['JudulReklame'],
                        'LokasiID': args['LokasiID'],
                        'AlamatPasang': args['AlamatPasang'],
                        'PanjangReklame': args['PanjangReklame'],
                        'LebarReklame': args['LebarReklame'],
                        'SudutPandang': args['SudutPandang'],
                        'JumlahReklame': args['JumlahReklame'],
                        'LKecamatan': args['LKecamatan'],
                        'LKelurahan': args['LKelurahan'],
                        'StrategisID1': args['StrategisID1'],
                        'StrategisID2': args['StrategisID2'],
                        'LuasReklame': luas,
                        'TarifPajak': tarifpajak,
                        'NoUrut': args['NoUrut'],
                        'DetailID': args['DetailID']
                    }
                    update_record_detail = PendataanReklameDtl.UpdatePendataanDetail(data)
                    if update_record_detail:
                        return success_update({'SPT': select_query.SPT,
                                               'UPTID': select_query.UPTID,
                                               'OPDID': select_query.OPDID,
                                               'TotalPajak': select_query.TotalPajak})
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


class DeletePendataanSKPReklame(Resource):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}

    def delete(self, id, *args, **kwargs):
        try:

            delete_record_detail = PendataanReklameDtl.query.filter_by(DetailID=id)
            if delete_record_detail:
                spt = delete_record_detail.first().SPT
                check_detail = PendataanReklameDtl.query.filter_by(SPT=spt).all()
                delete_header = vw_pendataan.query.filter_by(SPT=spt)
                tglpenetapan = delete_header.first().TglPenetapan
                if tglpenetapan == None:
                    if len(check_detail) == 1:
                        delete_record_detail.delete()
                        check_header = PendataanReklameHdr.query.filter_by(SPT=spt)
                        opdid = check_header.first().OPDID
                        select_query = db.session.execute(
                            f"UPDATE MsOPD SET TglPendataan = NULL WHERE OPDID = {opdid}")
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


#######################################################################