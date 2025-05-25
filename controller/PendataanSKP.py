import string
from datetime import datetime, timedelta, date

import sqlalchemy
from flask_restful import Resource, reqparse
from sqlalchemy import case
from sqlalchemy import or_
from sqlalchemy.dialects.mssql import pymssql
from win32con import NULL

from config.api_message import success_reads_pagination, failed_reads, success_reads, failed_create, success_create, \
    success_update, failed_update, success_delete, failed_delete
from config.config import appFrontWebLogo, appFrontWebUrl, appName
from config.database import db
from config.helper import logger
from controller.GeneralParameter import GeneralParameter
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsJenisUsaha import MsJenisUsaha
from controller.MsMapOpsen import MsMapOpsen
from controller.MsPegawai import MsPegawai
from controller.MsTarifLokasi import MsTarifLokasi
from controller.PendataanByOmzet import PendataanByOmzet
from controller.PendataanByOmzetDtl import PendataanByOmzetDtl
from controller.PenetapanByOmzet import PenetapanByOmzet
from controller.notifications.fcm_session import sendNotificationNative
from controller.notifications.notifications import Notifications
from controller.tblGroupUser import tblGroupUser
from controller.tblUser import tblUser
from controller.vw_obyekbadan import vw_obyekbadan
from controller.vw_pendataanskp import vw_pendataanskp


class PendataanSKP2(Resource):
    def get(self, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT OBN,OPDID,ObyekBadanNo,NamaBadan,NamaJenisPendapatan AS Jenis,TglSah,"
            f"(CASE WHEN MasaPendapatan='B' THEN 'Bulanan' ELSE '' END) AS Masa,(CASE WHEN TglData IS NULL "
            f"THEN 'Baru' ELSE 'Terdata' END) AS [Status],Kecamatan FROM vw_obyekbadan WHERE  SelfAssesment = 'N' "
            f"AND TglHapus IS NULL AND  OPDID IN (select distinct OPDID from MsObyekBadan "
            f"where Insidentil = 'N')  ORDER BY OBN")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


class PendataanSKP3(Resource):
    def get(self, opdid, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT OPDID,ObyekBadanNo, NamaBadan,NamaPemilik,AlamatBadan, Kota,Kecamatan,Kelurahan, "
            f"vw.KodeRekening, KodePos,UsahaBadan, vw.NamaJenisPendapatan AS Sub,ISNULL(GroupAttribute,0) "
            f"AS GroupAttribute,vw.OmzetBase,vw.OmzetID,vw.MasaPendapatan FROM vw_obyekbadan vw "
            f"LEFT JOIN MsJenisPendapatan jp ON vw.UsahaBadan = jp.JenisPendapatanID WHERE OPDID='{opdid}'")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


class PendataanSKPOmzet(Resource):
    def get(self, opdid, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('JenisPendapatanID', type=str)
        args = parser.parse_args()
        check_jenis = MsJenisPendapatan.query.filter_by(
            JenisPendapatanID=args['JenisPendapatanID']
        ).first()
        # untuk selain reklame
        if check_jenis.SelfAssessment == 'Y' and 'reklame' not in check_jenis.NamaJenisPendapatan.lower():
            select_query = db.session.execute(
                f"SELECT DISTINCT x.UPTID,x.SPT,x.MasaAwal,x.MasaAkhir,x.TglPendataan,pbod.DetailID,v.AlamatPemilik,v.KodeRekening,"
                f"v.NamaJenisPendapatan,v.NamaBadan,v.ObyekBadanNo,v.NamaPemilik,(CASE WHEN TglPenetapan IS NULL "
                f"THEN 'Terdata' ELSE 'SPTP' END) AS Penetapan, 0 AS Jumlah,'' AS Lokasi,x.TarifPajak AS Pajak,x.TarifPajakOpsen AS PajakOpsen FROM "
                f"PendataanByOmzet x LEFT JOIN PenetapanByOmzet p ON x.OPDID = p.OPDID AND x.MasaAwal = "
                f"p.MasaAwal AND x.MasaAkhir = p.MasaAkhir AND x.UrutTgl = p.UrutTgl LEFT JOIN vw_obyekbadan v ON "
                f"x.OPDID = v.OPDID LEFT JOIN PendataanByOmzetDtl AS pbod ON pbod.PendataanID=x.PendataanID "
                f"WHERE x.OPDID = '{opdid}' AND (pbod.DetailID != '' or pbod.DetailID != NULL) ORDER BY x.MasaAwal DESC")
        elif check_jenis.SelfAssessment == 'N' and 'reklame' not in check_jenis.NamaJenisPendapatan.lower():
            select_query = db.session.execute(
                f"SELECT DISTINCT x.UPTID,x.SPT,x.MasaAwal,x.MasaAkhir,x.TglPendataan,pbod.DetailID,v.AlamatPemilik,v.KodeRekening,"
                f"v.NamaJenisPendapatan,v.NamaBadan,v.ObyekBadanNo,v.NamaPemilik,(CASE WHEN TglPenetapan IS NULL "
                f"THEN 'Terdata' ELSE 'SKP' END) AS Penetapan, 0 AS Jumlah,'' AS Lokasi,x.TarifPajak AS Pajak FROM "
                f"PendataanByOmzet x LEFT JOIN PenetapanByOmzet p ON x.OPDID = p.OPDID AND x.MasaAwal = "
                f"p.MasaAwal AND x.MasaAkhir = p.MasaAkhir AND x.UrutTgl = p.UrutTgl LEFT JOIN vw_obyekbadan v ON "
                f"x.OPDID = v.OPDID LEFT JOIN PendataanByOmzetDtl AS pbod ON pbod.PendataanID=x.PendataanID "
                f"WHERE x.OPDID = '{opdid}' AND (pbod.DetailID != '' or pbod.DetailID != NULL) ORDER BY x.MasaAwal DESC" )
        else:
        # untuk reklame
            select_query = db.session.execute(
                f"SELECT x.UPTID,x.SPT,x.MasaAwal,x.MasaAkhir,x.TglPendataan,y.DetailID, v.AlamatPemilik,v.KodeRekening,"
                f"v.NamaJenisPendapatan,v.NamaBadan,v.ObyekBadanNo,v.NamaPemilik,(CASE WHEN TglPenetapan IS NULL THEN 'Terdata' "
                f"ELSE 'SKP' END) AS Penetapan, JumlahReklame AS Jumlah, (select distinct NamaLokasi from MsTitikLokasiHdr h "
                f"where h.LokasiID = y.LokasiID) + (case when AlamatPasang = '' OR AlamatPasang IS null then ' - '+ NamaLokasi else ' - ' + AlamatPasang end) AS Lokasi, "
                f"y.TarifPajak AS Pajak FROM (((PendataanReklameHdr x LEFT JOIN PenetapanReklameHdr p ON x.OPDID = p.OPDID "
                f"AND x.MasaAwal = p.MasaAwal AND x.MasaAkhir = p.MasaAkhir AND x.UrutTgl = p.UrutTgl) LEFT JOIN vw_obyekbadan v ON x.OPDID = v.OPDID)  "
                f"LEFT JOIN PendataanReklameDtl y ON x.SPT = y.SPT) WHERE x.OPDID = '{opdid}' "
                f"AND (y.DetailID != '' or y.DetailID != NULL) ORDER BY x.MasaAwal DESC")
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


class AddPendataanSKP(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}
    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('OPDID', type=str)
        parser.add_argument('TglPendataan', type=str)
        parser.add_argument('MasaAwal', type=str)
        parser.add_argument('MasaAkhir', type=str)
        parser.add_argument('JmlOmzetAwal', type=str)
        parser.add_argument('JumlahOmzetAwal', type=str)
        parser.add_argument('LKecamatan', type=str)
        parser.add_argument('LKelurahan', type=str)
        parser.add_argument('LokasiID', type=str)
        parser.add_argument('NamaBadan', type=str)
        parser.add_argument('@NomorSPT', type=str)
        parser.add_argument('WapuID', type=str)
        try:
            uid = kwargs['claim']["UID"]
            args = parser.parse_args()

            result = db.session.execute(
                f"exec [SP_SPT2] '{args['TglPendataan']}'" )
            result2 = []
            for row in result:
                result2.append( row )
                # print(row[0])
            spt = result2[0][0]
            print( spt )


            select_data = vw_obyekbadan.query.filter_by(
                OPDID=args['OPDID']
            ).first()

            select_query = db.session.execute(
                f"SELECT DISTINCT isnull(max(UrutTgl) + 1,1) FROM PendataanByOmzet "
                f"WHERE OPDID = '{args['OPDID']}' AND MasaAwal='{args['MasaAwal']}' AND MasaAkhir='{args['MasaAkhir']}'")
            result3 = select_query.first()[0]
            uruttgl = result3

            jmlomzetawal = args['JumlahOmzetAwal']
            opdid = args['OPDID']
            tglpendataan = args['TglPendataan']

            PegawaiID = kwargs['claim']["PegawaiID"] if "PegawaiID" in kwargs['claim'] else None

            if PegawaiID:
                select_query = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
                    tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
                result = select_query[0]
                uptid = result
                print(uptid)
            else:
                select_query = db.session.execute(
                    f"SELECT mu.UPTID FROM MsUPT AS mu WHERE mu.KDUNIT IN(SELECT gp.ParamStrValue "
                    f"FROM GeneralParameter AS gp WHERE gp.ParamID='satker_sipkd') AND RIGHT(mu.KodeUPT,3)='05.'")
                result = select_query.first()[0]
                uptid = result

            if jmlomzetawal != 0 or jmlomzetawal is not None:
                add_record = PendataanByOmzet(
                    SPT=spt,
                    OPDID=opdid,
                    WapuID=args['WapuID'],
                    TglPendataan=tglpendataan,
                    MasaAwal=args['MasaAwal'],
                    MasaAkhir=args['MasaAkhir'],
                    UrutTgl=uruttgl,
                    JmlOmzetAwal=jmlomzetawal,
                    TarifPajak=0,
                    TarifPajakOpsen=0,
                    UPTID=uptid,
                    Status=1,
                    LKecamatan=args['LKecamatan'],
                    LKelurahan=args['LKelurahan'],
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
                        'OPDID': add_record.OPDID,
                        'SPT': add_record.SPT,
                        'LKecamatan': add_record.LKecamatan,
                        'LKelurahan': add_record.LKelurahan,
                        'UsahaID': args['LokasiID'],
                        'Luas': str(add_record.JmlOmzetAwal),
                        'DateUpd': add_record.DateUpd

                    }
                    add_record_detail = PendataanByOmzetDtl.AddPPendataanDetil(data)
                    if not add_record_detail:
                        db.session.rollback()
                        return failed_create({})

                    selfassessment = db.session.query( vw_obyekbadan.SelfAssesment ).filter(
                        vw_obyekbadan.OPDID == opdid).first()
                    result0 = []
                    for row in selfassessment:
                        result0.append( row )
                    self = result0[0][0]
                    print( self )

                    query = db.session.query( GeneralParameter.ParamStrValue ).filter(
                            GeneralParameter.ParamID == 'autovalid' ).first()
                    result0 = []
                    for row in query:
                        result0.append( row )
                    autovalid = result0[0][0]
                    print( autovalid )
                    if autovalid == '1' and self == 'Y':

                        result1 = db.session.execute(
                            f"exec [SP_KOHIR_BLN2]" )
                        result2 = []
                        for row in result1:
                            result2.append( row )
                        kohirid = result2[0][0]
                        print( kohirid )

                        result3 = db.session.execute(
                            f"exec [SP_KOHIR2]"
                        )
                        result4 = []
                        for row in result3:
                            result4.append( row )
                        nokohir = result4[0][0]
                        print( nokohir )


                        tgltempo = datetime.strptime( tglpendataan, "%Y-%m-%d" ) + timedelta( days=30 )
                        print( tgltempo )

                        db.session.execute(
                            f"exec [SP_NomorKohir] '{add_record.SPT}', '{kohirid}', '{add_record.MasaAwal}', "
                            f"'{add_record.MasaAkhir}','{add_record.TglPendataan}','{uid}'" )
                        db.session.commit()

                        usahaid = data['UsahaID']
                        omzet = data['Luas']
                        select_query = db.session.query( MsTarifLokasi.TarifPajak ).filter(
                            MsTarifLokasi.LokasiID == usahaid )
                        trfpajak = select_query.first()[0] if select_query else None
                        if not trfpajak:
                            return False

                        tarifpajak = float( omzet ) * float( trfpajak )

                        select_query = db.session.execute(
                            f"SELECT TOP 1 ISNULL(JenispendapatanID,'') FROM vw_obyekbadan "
                            f"WHERE OPDID = '{opdid}' ")
                        jpid = select_query.first()[0]
                        print(jpid)

                        select_query = db.session.execute(
                            f"SELECT TOP 1 ISNULL(NamaJenisPendapatan,'') FROM MsJenisPendapatan "
                            f"WHERE JenisPendapatanID = '{jpid}' ")
                        nmjpid = select_query.first()[0]
                        print(jpid)
                        tarifpajakopsen = 0

                        mblb = None

                        if nmjpid == 'Mineral Bukan Logam dan Batuan':
                            select_query = db.session.query(MsMapOpsen.JPIDOpsen).filter(
                                MsMapOpsen.JPID == jpid)
                            jpidopsen = select_query.first()[0]

                            select_query = db.session.query(MsJenisPendapatan.NamaJenisPendapatan).filter(
                                MsJenisPendapatan.JenisPendapatanID == jpidopsen)
                            result = select_query.first()
                            mblb = result[0] if result else None

                            lokasiidopsen = None
                            trfpajakopsen = 0

                            if mblb is not None:
                                select_query = db.session.query(MsTarifLokasi.LokasiID).filter(
                                    MsTarifLokasi.JenisPendapatanID == jpidopsen)
                                lokasiidopsen = select_query.first()[0]

                                select_query = db.session.query(MsTarifLokasi.TarifPajak).filter(
                                    MsTarifLokasi.LokasiID == lokasiidopsen)
                                trfpajakopsen = select_query.first()[0] if select_query else None

                                tarifpajakopsen = float(tarifpajak) * float(trfpajakopsen)

                        add_record_parent = PenetapanByOmzet(
                            NoKohir=nokohir,
                            KohirID=kohirid,
                            OPDID=opdid,
                            WapuID=args['WapuID'],
                            TglPenetapan=tglpendataan,
                            TglJatuhTempo=tgltempo,
                            MasaAwal=add_record.MasaAwal,
                            MasaAkhir=add_record.MasaAkhir,
                            UrutTgl=uruttgl,
                            JmlOmzetAwal=jmlomzetawal,
                            TarifPajak=tarifpajak,
                            TarifPajakOpsen=tarifpajakopsen if tarifpajakopsen else 0,
                            Denda=sqlalchemy.sql.null(),
                            Kenaikan=sqlalchemy.sql.null(),
                            IsPaid='N',
                            TglBayar=sqlalchemy.sql.null(),
                            JmlBayar=sqlalchemy.sql.null(),
                            TglKurangBayar=sqlalchemy.sql.null(),
                            JmlKurangBayar=sqlalchemy.sql.null(),
                            JmlPeringatan=sqlalchemy.sql.null(),
                            UPTID=uptid,
                            Status=1,
                            KodeStatus='' if select_data.SelfAssesment == 'Y' else '70',
                            LKecamatan=add_record.LKecamatan,
                            LKelurahan=add_record.LKelurahan,
                            UserUpd=uid,
                            DateUpd=add_record.DateUpd
                        )
                        db.session.add( add_record_parent )
                        db.session.commit()
                        if add_record_parent.KohirID:
                            db.session.execute(
                                f"UPDATE PendataanByOmzetDtl SET NoKohir='{nokohir}',UserUpd='{uid}',DateUpd=getdate() WHERE SPT = '{spt}'" )
                            db.session.commit()
                            db.session.execute(
                                f"exec [SP_Penetapan] '{add_record_parent.KohirID}',1" )
                            db.session.commit()

                        # notif ke group penetapan
                    else:
                        list_user = tblUser.query.join(tblGroupUser).filter(tblGroupUser.IsPenetapan == 1).all()
                        for row in list_user:
                            if row.DeviceId:
                                namaBadan = args['NamaBadan'] if args['NamaBadan'] else ""
                                notifBody = f"Halo {row.nama_user}, ada pendataan baru {namaBadan} yang harus segera anda tetapkan."
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
                                           'TarifPajak': add_record.TarifPajak,
                                           'PendataanID': add_record.PendataanID})
                else:
                    logger.error('gagal insert pendataan ke db')
                    db.session.rollback()
                    return failed_create({})
            else:
                db.session.rollback()
                return failed_create({})
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return failed_create({})

##################33333333################## MPOS ###########################################################
class pendataanpajak(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('opdid', type=str)
        parser.add_argument( 'tglpendataan', type=str )
        parser.add_argument('masaawal', type=str)
        parser.add_argument('masaakhir', type=str)
        parser.add_argument('jmlomzet', type=str)

        try:
            uid = kwargs['claim']["UID"]
            args = parser.parse_args()
            select_data = vw_obyekbadan.query.filter_by(
                OPDID=args['opdid']
            ).first()

            result = db.session.execute(
                f"exec [SP_SPT2] '{args['tglpendataan']}'")
            result2 = []
            for row in result:
                result2.append(row)
                # print(row[0])
            spt = result2[0][0]

            select_query = db.session.execute(
                f"SELECT DISTINCT isnull(max(UrutTgl) + 1,1) FROM PendataanByOmzet "
                f"WHERE OPDID = '{args['opdid']}' AND MasaAwal='{args['masaawal']}' AND MasaAkhir='{args['masaakhir']}'")
            result3 = select_query.first()[0]
            uruttgl = result3

            jmlomzetawal = args['jmlomzet']
            opdid = args['opdid']
            tglpendataan = args['tglpendataan']

            PegawaiID = kwargs['claim']["PegawaiID"] if "PegawaiID" in kwargs['claim'] else None

            if PegawaiID:
                select_query = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
                    tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
                result = select_query[0]
                uptid = result
                print(uptid)
            else:
                select_query = db.session.execute(
                    f"SELECT mu.UPTID FROM MsUPT AS mu WHERE mu.KDUNIT IN(SELECT gp.ParamStrValue "
                    f"FROM GeneralParameter AS gp WHERE gp.ParamID='satker_sipkd') AND RIGHT(mu.KodeUPT,3)='05.'")
                result = select_query.first()[0]
                uptid = result

            if jmlomzetawal != 0:
                add_record = PendataanByOmzet(
                    SPT=spt,
                    OPDID=opdid,
                    TglPendataan=datetime.now().strftime('%Y-%m-%d'),
                    MasaAwal=args['masaawal'],
                    MasaAkhir=args['masaakhir'],
                    UrutTgl=uruttgl,
                    JmlOmzetAwal=jmlomzetawal,
                    TarifPajak=0,
                    UPTID=uptid,
                    Status=1,
                    LKecamatan=select_data.KecamatanID,
                    LKelurahan=select_data.KelurahanID,
                    UserUpd=uid,
                    DateUpd=datetime.now()
                )

                db.session.add(add_record)
                db.session.commit()
                if add_record.PendataanID:
                    db.session.execute(
                        f"UPDATE MsOPD SET TglPendataan = '{tglpendataan}' WHERE OPDID = {opdid} "
                        f"AND TglPendataan IS NULL")

                    select_query = db.session.query( MsTarifLokasi.LokasiID ).filter(
                        MsTarifLokasi.JenisPendapatanID == select_data.JenisPendapatanID )
                    usahaid = select_query.first()[0]

                    data = {
                        'uid': uid,
                        'PendataanID': add_record.PendataanID,
                        'SPT': add_record.SPT,
                        'LKecamatan': add_record.LKecamatan,
                        'LKelurahan': add_record.LKelurahan,
                        'UsahaID': usahaid,
                        'Luas': add_record.JmlOmzetAwal,

                    }
                    add_record_detail = PendataanByOmzetDtl.AddPPendataanDetil(data)
                    if not add_record_detail:
                        db.session.rollback()
                        return failed_create({})

                    selfassessment = db.session.query( vw_obyekbadan.SelfAssesment ).filter(
                        vw_obyekbadan.OPDID == opdid).first()
                    result0 = []
                    for row in selfassessment:
                        result0.append( row )
                    self = result0[0][0]
                    print( self )

                    query = db.session.query( GeneralParameter.ParamStrValue ).filter(
                            GeneralParameter.ParamID == 'autovalid' ).first()
                    result0 = []
                    for row in query:
                        result0.append( row )
                    autovalid = result0[0][0]
                    print( autovalid )
                    if autovalid == '1' and self == 'Y':

                        result1 = db.session.execute(
                            f"exec [SP_KOHIR_BLN2]" )
                        result2 = []
                        for row in result1:
                            result2.append( row )
                        kohirid = result2[0][0]
                        print(kohirid)

                        # blth = date.today().year
                        # result1 = db.session.execute(
                        #     f"DECLARE @kohirid varchar(8) EXEC [SP_KOHIR_BLN] "
                        #     f"@blth='{blth}',@JPID='{usahaid}', @NoKohir= @kohirid OUTPUT "
                        #     f"SELECT @kohirid AS kohirid "
                        # )
                        # result = result1.first()[0]
                        # print( result )
                        # kohirid = result

                        result3 = db.session.execute(
                            f"exec [SP_KOHIR2]"
                        )
                        result4 = []
                        for row in result3:
                            result4.append( row )
                        nokohir = result4[0][0]
                        print( nokohir )

                        tgltempo = datetime.strptime( tglpendataan, "%Y-%m-%d" ) + timedelta( days=30 )
                        print( tgltempo )

                        db.session.execute(
                            f"exec [SP_NomorKohir] '{add_record.SPT}', '{kohirid}', '{add_record.MasaAwal}', "
                            f"'{add_record.MasaAkhir}','{add_record.TglPendataan}','{uid}'" )
                        db.session.commit()

                        usahaid = data['UsahaID']
                        omzet = data['Luas']
                        select_query = db.session.query( MsTarifLokasi.TarifPajak ).filter(
                            MsTarifLokasi.LokasiID == usahaid )
                        trfpajak = select_query.first()[0] if select_query else None
                        if not trfpajak:
                            return False

                        tarifpajak = float( omzet ) * float( trfpajak )

                        # add_record_parent = PenetapanByOmzet(
                        #     NoKohir=nokohir,
                        #     KohirID=kohirid,
                        #     OPDID=opdid,
                        #     TglPenetapan=tglpendataan,
                        #     TglJatuhTempo=tgltempo,
                        #     MasaAwal=args['masaawal'],
                        #     MasaAkhir=args['masaakhir'],
                        #     UrutTgl=uruttgl,
                        #     JmlOmzetAwal=jmlomzetawal,
                        #     TarifPajak=tarifpajak,
                        #     Denda=sqlalchemy.sql.null(),
                        #     Kenaikan=sqlalchemy.sql.null(),
                        #     IsPaid='N',
                        #     TglBayar=sqlalchemy.sql.null(),
                        #     JmlBayar=sqlalchemy.sql.null(),
                        #     TglKurangBayar=sqlalchemy.sql.null(),
                        #     JmlKurangBayar=sqlalchemy.sql.null(),
                        #     JmlPeringatan=sqlalchemy.sql.null(),
                        #     UPTID=uptid,
                        #     Status=1,
                        #     KodeStatus= '' if select_data.SelfAssesment == 'Y' else '70',
                        #     LKecamatan=add_record.LKecamatan,
                        #     LKelurahan=add_record.LKecamatan,
                        #     UserUpd=uid,
                        #     DateUpd=datetime.now()
                        # )
                        # db.session.add( add_record_parent )
                        # db.session.commit()

                        NoKohir = nokohir
                        KohirID = kohirid
                        OPDID = opdid
                        TglPenetapan = tglpendataan
                        TglJatuhTempo = tgltempo
                        MasaAwal = args['masaawal']
                        MasaAkhir = args['masaakhir']
                        UrutTgl = uruttgl
                        JmlOmzetAwal = jmlomzetawal
                        TarifPajak = tarifpajak
                        Denda = NULL
                        Kenaikan = NULL
                        IsPaid = 'N'
                        TglBayar = NULL
                        JmlBayar = NULL
                        TglKurangBayar = NULL
                        JmlKurangBayar = NULL
                        JmlPeringatan = 0
                        UPTID = uptid
                        Status = 1
                        KodeStatus = '' if select_data.SelfAssesment == 'Y' else '70'
                        LKecamatan = add_record.LKecamatan
                        LKelurahan = add_record.LKecamatan
                        UserUpd = uid
                        DateUpd = datetime.now().strftime("%Y-%m-%d") #datetime.now()
                        KegSatker = uptid

                        add_record_parent = db.session.execute(
                            f"INSERT INTO [dbo].[PenetapanByOmzet] "
                            f"([NoKohir],[KohirID],[OPDID],[TglPenetapan],[TglJatuhTempo],[MasaAwal],[MasaAkhir],[UrutTgl],"
                            f"[JmlOmzetAwal],[TarifPajak],[Denda],[Kenaikan],[IsPaid],[TglBayar],[JmlBayar],[TglKurangBayar],"
                            f"[JmlKurangBayar],[JmlPeringatan],[UPTID],[Status],[UserUpd],[DateUpd],[LKecamatan],[LKelurahan],"
                            f"[KodeStatus],[KegSatker]) "
                            f"VALUES "
                            f"('{NoKohir}','{KohirID}',{OPDID},'{TglPenetapan}','{TglJatuhTempo}','{MasaAwal}','{MasaAkhir}',{UrutTgl},"
                            f"'{JmlOmzetAwal}','{TarifPajak}','{Denda}','{Kenaikan}','{IsPaid}',NULL,'{JmlBayar}',NULL,"
                            f"'{JmlKurangBayar}',{JmlPeringatan},'{UPTID}',{Status},'{UserUpd}','{DateUpd}','{LKecamatan}', '{LKelurahan}',"
                            f"'{KodeStatus}','{KegSatker}' )"
                        )
                        db.session.commit()

                        if add_record_parent:
                            db.session.execute(
                                f"UPDATE PendataanByOmzetDtl SET NoKohir='{nokohir}',UserUpd='{uid}',DateUpd=getdate() WHERE SPT = '{spt}'" )
                            db.session.commit()
                            # db.session.execute(
                            #     f"exec [SP_Penetapan] '{KohirID}',1" )
                            # db.session.commit()

                        # notif ke group penetapan
                    else:
                        list_user = tblUser.query.join(tblGroupUser).filter(tblGroupUser.IsPenetapan == 1).all()
                        for row in list_user:
                            if row.DeviceId:
                                namaBadan = select_data.NamaBadan if select_data.NamaBadan else ""
                                notifBody = f"Halo {row.nama_user}, ada pendataan baru {namaBadan} yang harus segera anda tetapkan."
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
                    return success_create({'spt': add_record.SPT,
                                           'opdid': add_record.OPDID,
                                           'tarifpajak': add_record.TarifPajak,
                                           })
                else:
                    logger.error('gagal insert pendataan ke db')
                    db.session.rollback()
                    return failed_create({})
            else:
                db.session.rollback()
                return failed_create({})
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return failed_create({})
#####################################

class AddPendataanBPHTB(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}
    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('OPDID', type=str)
        parser.add_argument('TglPendataan', type=str)
        parser.add_argument('MasaAwal', type=str)
        parser.add_argument('MasaAkhir', type=str)
        parser.add_argument('LuasBg', type=str)
        parser.add_argument( 'LuasTnh', type=str )
        parser.add_argument('LKecamatan', type=str)
        parser.add_argument('LKelurahan', type=str)
        parser.add_argument('JenisPerolehan', type=str)
        parser.add_argument('Nop', type=str)
        parser.add_argument('tarifBphtb', type=str)
        parser.add_argument('TarifPajak', type=str)
        parser.add_argument('NamaBadan', type=str)
        try:
            uid = kwargs['claim']["UID"]
            args = parser.parse_args()
            result = db.session.execute(
                f"exec [SP_SPT2] '{args['TglPendataan']}'")
            result2 = []
            for row in result:
                result2.append(row)
                # print(row[0])
            spt = result2[0][0]
            print(spt)

            select_data = vw_obyekbadan.query.filter_by(
                OPDID=args['OPDID']
            ).first()

            select_query = db.session.execute(
                f"SELECT DISTINCT isnull(max(UrutTgl) + 1,1) FROM PendataanByOmzet "
                f"WHERE OPDID = '{args['OPDID']}' AND MasaAwal='{args['MasaAwal']}' AND MasaAkhir='{args['MasaAkhir']}'")
            result3 = select_query.first()[0]
            uruttgl = result3

            jmlomzetawal = float(args['LuasBg']) + float(args['LuasTnh'])
            print(jmlomzetawal)
            opdid = args['OPDID']
            tglpendataan = args['TglPendataan']
            tarifpajak = args['TarifPajak']

            PegawaiID = kwargs['claim']["PegawaiID"] if "PegawaiID" in kwargs['claim'] else None

            if PegawaiID:
                select_query = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
                    tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
                result = select_query[0]
                uptid = result
                print(uptid)
            else:
                select_query = db.session.execute(
                    f"SELECT mu.UPTID FROM MsUPT AS mu WHERE mu.KDUNIT IN(SELECT gp.ParamStrValue "
                    f"FROM GeneralParameter AS gp WHERE gp.ParamID='satker_sipkd') AND RIGHT(mu.KodeUPT,3)='01.'")
                result = select_query.first()[0]
                uptid = result

                add_record = PendataanByOmzet(
                    SPT=spt,
                    OPDID=opdid,
                    TglPendataan=tglpendataan,
                    MasaAwal=args['MasaAwal'],
                    MasaAkhir=args['MasaAkhir'],
                    UrutTgl=uruttgl,
                    JmlOmzetAwal=jmlomzetawal,
                    TarifPajak=tarifpajak,
                    UPTID=uptid,
                    Status=1,
                    LKecamatan=args['LKecamatan'],
                    LKelurahan=args['LKelurahan'],
                    UserUpd=uid,
                    DateUpd=datetime.now()
                )

                db.session.add(add_record)
                db.session.commit()
                if add_record.PendataanID:
                    db.session.execute(
                        f"UPDATE MsOPD SET TglPendataan = '{tglpendataan}' WHERE OPDID = {opdid} "
                        f"AND TglPendataan IS NULL")

                    db.session.execute(
                        f"exec SP_OMZETDTL {add_record.PendataanID},'{spt}',1,'{args['Nop']}',{args['JenisPerolehan']}, "
                        f"'{uid}',{args['JenisPerolehan']}, NULL " )
                    db.session.execute(
                        f"exec SP_OMZETDTL {add_record.PendataanID},'{spt}',2,'{args['Nop']}',{args['JenisPerolehan']}, "
                        f"'{uid}',{args['JenisPerolehan']}, NULL " )

                    db.session.execute(
                        f"UPDATE PendataanByOmzetDtl SET TarifPajak={args['LuasTnh']} WHERE SPT='{spt}' AND Luas=1 " )
                    db.session.execute(
                        f"UPDATE PendataanByOmzetDtl SET TarifPajak={args['LuasBg']} WHERE SPT='{spt}' AND Luas=2 " )


                    selfassessment = db.session.query( vw_obyekbadan.SelfAssesment ).filter(
                        vw_obyekbadan.OPDID == opdid).first()
                    result0 = []
                    for row in selfassessment:
                        result0.append( row )
                    self = result0[0][0]
                    print( self )

                    query = db.session.query( GeneralParameter.ParamStrValue ).filter(
                            GeneralParameter.ParamID == 'autovalid' ).first()
                    result0 = []
                    for row in query:
                        result0.append( row )
                    autovalid = result0[0][0]
                    print( autovalid )
                    if autovalid == '1' and self == 'Y':

                        result1 = db.session.execute(
                            f"exec [SP_KOHIR_BLN2]" )
                        result2 = []
                        for row in result1:
                            result2.append( row )
                        kohirid = result2[0][0]
                        print(kohirid)

                        result3 = db.session.execute(
                            f"exec [SP_KOHIR2]"
                        )
                        result4 = []
                        for row in result3:
                            result4.append( row )
                        nokohir = result4[0][0]
                        print( nokohir )

                        # blth = date.today().year
                        # result1 = db.session.execute(
                        #     f"DECLARE @kohirid varchar(8) EXEC [SP_KOHIR_BLN] "
                        #     f"@blth='{blth}',@JPID='{args['LokasiID']}', @NoKohir= @kohirid OUTPUT "
                        #     f"SELECT @kohirid AS kohirid "
                        # )
                        # result = result1.first()[0]
                        # print( result )
                        # kohirid = result
                        #
                        # result3 = db.session.execute(
                        #     f"DECLARE @nomorkohir varchar(8) EXEC [SP_KOHIR_BLN] "
                        #     f"@mode='1', @NoKohir= @nomorkohir OUTPUT "
                        #     f"SELECT @nomorkohir AS NoKohir "
                        # )
                        # result2 = result2.first()[0]
                        # print( result2 )
                        # nokohir = result2

                        tgltempo = datetime.strptime( tglpendataan, "%Y-%m-%d" ) + timedelta( days=30 )
                        print( tgltempo )

                        db.session.execute(
                            f"exec [SP_NomorKohir] '{add_record.SPT}', '{kohirid}', '{add_record.MasaAwal}', "
                            f"'{add_record.MasaAkhir}','{add_record.TglPendataan}','{uid}'" )
                        db.session.commit()

                        # usahaid = args['JenisPerolehan ']
                        # select_query = db.session.query( MsJenisUsaha.TarifUsaha ).filter(
                        #     MsJenisUsaha.UsahaID == usahaid )
                        # trfpajak = select_query.first()[0] if select_query else None
                        # if not trfpajak:
                        #     return False

                        add_record_parent = PenetapanByOmzet(
                            NoKohir=nokohir,
                            KohirID=kohirid,
                            OPDID=opdid,
                            TglPenetapan=tglpendataan,
                            TglJatuhTempo=tgltempo,
                            MasaAwal=args['MasaAwal'],
                            MasaAkhir=args['MasaAkhir'],
                            UrutTgl=uruttgl,
                            JmlOmzetAwal=jmlomzetawal,
                            TarifPajak=tarifpajak,
                            Denda=sqlalchemy.sql.null(),
                            Kenaikan=sqlalchemy.sql.null(),
                            IsPaid='N',
                            TglBayar=sqlalchemy.sql.null(),
                            JmlBayar=sqlalchemy.sql.null(),
                            TglKurangBayar=sqlalchemy.sql.null(),
                            JmlKurangBayar=sqlalchemy.sql.null(),
                            JmlPeringatan=sqlalchemy.sql.null(),
                            UPTID=uptid,
                            Status=1,
                            KodeStatus='' ,
                            LKecamatan=args['LKecamatan'],
                            LKelurahan=args['LKelurahan'],
                            UserUpd=uid,
                            DateUpd=datetime.now()
                        )
                        db.session.add( add_record_parent )
                        db.session.commit()
                        if add_record_parent.KohirID:
                            db.session.execute(
                                f"UPDATE PendataanByOmzetDtl SET NoKohir='{nokohir}',UserUpd='{uid}',DateUpd=getdate() WHERE SPT = '{spt}'" )
                            db.session.commit()
                            db.session.execute(
                                f"exec [SP_Penetapan] '{add_record_parent.KohirID}',1" )
                            db.session.commit()

                        # notif ke group penetapan
                    else:
                        list_user = tblUser.query.join(tblGroupUser).filter(tblGroupUser.IsPenetapan == 1).all()
                        for row in list_user:
                            if row.DeviceId:
                                namaBadan = args['NamaBadan'] if args['NamaBadan'] else ""
                                notifBody = f"Halo {row.nama_user}, ada pendataan baru {namaBadan} yang harus segera anda tetapkan."
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
                                           'TarifPajak': add_record.TarifPajak,
                                           'PendataanID': add_record.PendataanID})
                else:
                    logger.error('gagal insert pendataan ke db')
                    db.session.rollback()
                    return failed_create({})
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return failed_create({})


class UpdatePendataanSKP(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        print(kwargs['claim'])

        parser.add_argument('SPT', type=str)
        parser.add_argument('OPDID', type=str)
        parser.add_argument('WapuID', type=str)
        parser.add_argument('TglPendataan', type=str)
        parser.add_argument('MasaAwal', type=str)
        parser.add_argument('MasaAkhir', type=str)
        parser.add_argument('UrutTgl', type=str)
        parser.add_argument('JmlOmzetAwal', type=str)
        parser.add_argument('TarifPajak', type=str)
        parser.add_argument('UPTID', type=str)
        parser.add_argument('Status', type=str)
        parser.add_argument('LKecamatan', type=str)
        parser.add_argument('LKelurahan', type=str)
        parser.add_argument('UserUpd', type=str)
        # parser.add_argument('DateUpd', type=str)

        parser.add_argument('PendataanID', type=str)
        parser.add_argument('LokasiID', type=int)
        parser.add_argument('Luas', type=str)
        parser.add_argument('NoUrut', type=str)
        parser.add_argument('DetailID', type=int)

        args = parser.parse_args()
        uid = kwargs['claim']["UID"]
        try:
            select_query = PendataanByOmzet.query.filter_by(SPT=id).first()
            if select_query:
                if args['OPDID']:
                    select_query.OPDID = f"{args['OPDID']}"
                if args['WapuID']:
                    select_query.OPDID = f"{args['WapuID']}"
                if args['TglPendataan']:
                    select_query.TglPendataan = args['TglPendataan']
                if args['MasaAwal']:
                    select_query.MasaAwal = args['MasaAwal']
                if args['MasaAkhir']:
                    select_query.MasaAkhir = args['MasaAkhir']
                if args['UrutTgl']:
                    select_query.UrutTgl = args['UrutTgl']
                if args['JmlOmzetAwal']:
                    select_query.JmlOmzetAwal = args['JmlOmzetAwal']
                if args['TarifPajak']:
                    select_query.TarifPajak = args['TarifPajak']
                if args['UPTID']:
                    select_query.UPTID = args['UPTID']
                if args['Status']:
                    select_query.Status = args['Status']
                if args['LKecamatan']:
                    select_query.LKecamatan = args['LKecamatan']
                if args['LKelurahan']:
                    select_query.LKelurahan = args['LKelurahan']
                select_query.UserUpd = uid
                select_query.DateUpd = datetime.now()
                db.session.commit()
                print('sukses update ke header')
                if select_query.SPT:
                    data = {
                        'uid': uid,
                        'PendataanID': select_query.PendataanID,
                        'SPT': select_query.SPT,
                        'LKecamatan': select_query.LKecamatan,
                        'LKelurahan': select_query.LKelurahan,
                        'UsahaID': args['LokasiID'],
                        'Luas': select_query.JmlOmzetAwal,
                        'NoUrut': args['NoUrut'],
                        'DetailID': args['DetailID']
                    }
                    update_record_detail = PendataanByOmzetDtl.UpdatePendataanDetail(data)
                    if update_record_detail:
                        return success_update({'SPT': select_query.SPT,
                                               'UPTID': select_query.UPTID,
                                               'OPDID': select_query.OPDID,
                                               'TarifPajak': select_query.TarifPajak})
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


class DeletePendataanSKP(Resource):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}

    def delete(self, id, *args, **kwargs):
        try:
            delete_record_detail = PendataanByOmzetDtl.query.filter_by(DetailID=id)
            delete_detail = delete_record_detail.first()
            if delete_detail.NoKohir == None:
                spt = delete_detail.SPT
                check_detail = PendataanByOmzetDtl.query.filter_by(SPT=spt).all()
                print(len(check_detail))
                if len(check_detail) == 1:
                    delete_record_detail.delete()
                    check_header = PendataanByOmzet.query.filter_by(SPT=spt)
                    opdid = check_header.first().OPDID
                    select_query = db.session.execute(
                        f"UPDATE MsOPD SET TglPendataan = GETDATE() WHERE OPDID = {opdid}")
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
#######################################################################

class PendataanSKP(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):

        # PARSING PARAMETER DARI REQUEST
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('length', type=int)
        parser.add_argument('sort', type=str)
        parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
        parser.add_argument('search', type=str)
        parser.add_argument('filter_jenis', type=str)
        parser.add_argument('filter_wapuid', type=str)
        parser.add_argument('filter_uptid', type=str)
        parser.add_argument('filter_kecamatanid', type=str)
        parser.add_argument('filter_kelurahanid', type=str)
        parser.add_argument('kategori', type=str, choices=('true', 'false'), help='diisi dengan true atau false')
        parser.add_argument('nonwp', type=str, choices=('true', 'false'), help='diisi dengan true atau false')

        args = parser.parse_args()
        UserId = kwargs['claim']["UserId"]
        IsWP = kwargs['claim']["IsWP"]

        result = []
        try:
            select_query = db.session.query(vw_pendataanskp.WapuID,vw_pendataanskp.WajibPungut,vw_pendataanskp.WPID, vw_pendataanskp.OPDID,
                                            vw_pendataanskp.ObyekBadanNo, vw_pendataanskp.NamaBadan,
                                            vw_pendataanskp.NamaPemilik,
                                            vw_pendataanskp.KodeRekening, vw_pendataanskp.JenisPendapatanID,
                                            vw_pendataanskp.NamaJenisPendapatan,
                                            vw_pendataanskp.TglPengesahan, vw_pendataanskp.AlamatBadan,
                                            case([(vw_pendataanskp.MasaPendapatan == 'B', 'Bulanan')]
                                                 ,
                                                 else_=''
                                                 ).label('Masa'),
                                            case([(vw_pendataanskp.TglData == None, 'Baru')]
                                                 ,
                                                 else_='Terdata'
                                                 ).label('Status'),
                                            vw_pendataanskp.KecamatanID, vw_pendataanskp.Kecamatan,
                                            vw_pendataanskp.FaxKecamatan,
                                            vw_pendataanskp.KelurahanID, vw_pendataanskp.Kelurahan,
                                            vw_pendataanskp.Insidentil,
                                            vw_pendataanskp.SelfAssesment, vw_pendataanskp.avatar
                                            ) \
                .filter(
                vw_pendataanskp.TglHapus == None
            )

            # FILTER_UPT
            if args['filter_uptid']:
                select_query = select_query.filter(
                    vw_pendataanskp.FaxKecamatan == args['filter_uptid']
                )

            # FILTER_KECAMATAN
            if args['filter_kecamatanid']:
                select_query = select_query.filter(
                    vw_pendataanskp.KecamatanID == args['filter_kecamatanid']
                )

            # FILTER_KELURAHAN
            if args['filter_kelurahanid']:
                select_query = select_query.filter(
                    vw_pendataanskp.KelurahanID == args['filter_kelurahanid']
                )

            # FILTER_JENIS
            if args['filter_jenis']:
                select_query = select_query.filter(
                    vw_pendataanskp.JenisPendapatanID == args['filter_jenis']
                )

            # kategori
            if IsWP != 1:
                if args['kategori'] or args['kategori'] == "true":
                    select_query = select_query.filter(vw_pendataanskp.SelfAssesment == 'Y')
                else:
                    select_query = select_query.filter(vw_pendataanskp.SelfAssesment == 'N')

            # nonwp
            if args['nonwp'] or args['nonwp'] == "true":
                select_query = select_query.filter(vw_pendataanskp.Insidentil == 'Y')
            else:
                select_query = select_query.filter(vw_pendataanskp.Insidentil == 'N')

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_pendataanskp.NamaBadan.ilike(search),
                        vw_pendataanskp.ObyekBadanNo.ilike(search),
                        vw_pendataanskp.TglData.ilike(search)
                        )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    if args['sort'] == "Status":
                        sort = getattr(vw_pendataanskp, 'TglData').desc()
                    elif args['sort'] == "Masa":
                        sort = getattr(vw_pendataanskp, 'MasaPendapatan').desc()
                    else:
                        sort = getattr(vw_pendataanskp, args['sort']).desc()
                else:
                    if args['sort'] == "Status":
                        sort = getattr(vw_pendataanskp, 'TglData').asc()
                    elif args['sort'] == "Masa":
                        sort = getattr(vw_pendataanskp, 'MasaPendapatan').asc()
                    else:
                        sort = getattr(vw_pendataanskp, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_pendataanskp.TglData.desc())

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


class PendataanSKPOmset(Resource):
    # method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, opdid, *args, **kwargs):

        # PARSING PARAMETER DARI REQUEST
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('length', type=int)
        parser.add_argument('sort', type=str)
        parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
        parser.add_argument('search', type=str)
        parser.add_argument('search_jenis', type=str)

        args = parser.parse_args()
        # UserId = kwargs['claim']["UserId"]

        result = []
        try:
            select_query = db.session.query(PendataanByOmzet.UPTID, PendataanByOmzet.MasaAwal,
                                            PendataanByOmzet.MasaAkhir, PendataanByOmzet.TglPendataan,
                                            case([(PenetapanByOmzet.TglPenetapan == None, 'Terdata')]
                                                 ,
                                                 else_='SKP'
                                                 ).label('Penetapan'),
                                            PendataanByOmzet.TarifPajak, PendataanByOmzet.TarifPajakOpsen) \
                .join(PenetapanByOmzet, (PenetapanByOmzet.OPDID == PendataanByOmzet.OPDID) &
                      (PenetapanByOmzet.MasaAwal == PendataanByOmzet.MasaAwal) &
                      (PenetapanByOmzet.MasaAkhir == PendataanByOmzet.MasaAkhir) &
                      (PenetapanByOmzet.UrutTgl == PendataanByOmzet.UrutTgl), isouter=True) \
                .join(vw_obyekbadan, vw_obyekbadan.OPDID == PendataanByOmzet.OPDID) \
                .filter(
                PendataanByOmzet.OPDID == opdid
            )

            # # SEARCH_JENIS
            # if args['search_jenis']:
            #     select_query = select_query.filter(
            #         MsJenisPendapatan.JenisPendapatanID == args['search_jenis']
            #     )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_obyekbadan.NamaBadan.ilike(search),
                        vw_obyekbadan.ObyekBadanNo.ilike(search),
                        vw_obyekbadan.TglPendataan.ilike(search)
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
                select_query = select_query.order_by(vw_obyekbadan.ObyekBadanNo)

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
                d['Jumlah'] = 0
                d['Lokasi'] = ''
            return success_reads_pagination(query_execute, result)
        except Exception as e:
            print(e)
            return failed_reads(result)