import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import extract
import sqlalchemy
import yagmail
from flask_restful import Resource, reqparse
from sqlalchemy import case, and_, text, null, func
from sqlalchemy import or_
from config.api_message import success_reads_pagination, failed_reads, success_reads, failed_create, success_create, \
    success_update, failed_update, success_delete, failed_delete
from config.config import appFrontWebLogo, appNameMobile, appFrontWebMobileLogoBig, appFrontWebUrlWp, appEmailPassword, \
    appEmail, appName
from config.database import db
from config.helper import logger, parser, rupiah_format
from controller.GeneralParameter import GeneralParameter
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsPegawai import MsPegawai
from controller.MsUPT import MsUPT
from controller.MsOPD import MsOPD
from controller.MsWPData import MsWPData
from controller.NomorKohir import NomorKohir
from controller.PendataanByOmzet import PendataanByOmzet
from controller.PendataanReklameHdr import PendataanReklameHdr
from controller.PenetapanByOmzet import PenetapanByOmzet
from controller.PenetapanReklameHdr import PenetapanReklameHdr
from controller.SetoranHist import SetoranHist
from controller.notifications.fcm_session import sendNotificationNative
from controller.notifications.notifications import Notifications
from controller.tblGroupUser import tblGroupUser
from controller.tblUser import tblUser
from controller.tblUserWP import tblUserWP
from controller.vw_obyekbadan import vw_obyekbadan
from controller.vw_pembayaran import vw_pembayaran
from controller.vw_pendataan import vw_pendataan
from controller.vw_penetapan import vw_penetapan
from controller.vw_penetapanomzet import vw_penetapanomzet
from controller.vw_penetapanreklame import vw_penetapanreklame


class PenetapanSKP2(Resource):
    def get(self, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT PendataanID, OBN,SPT,o.OPDID,ObyekBadanNo,cast(o.TarifPajak as varchar) AS Pajak,o.TglPendataan,NamaJenisPendapatan AS Jenis,"
            f"NamaBadan,o.MasaAwal, o.MasaAkhir FROM ((PendataanByOmzet o LEFT JOIN vw_obyekbadan v ON "
            f"o.OPDID = v.OPDID) LEFT JOIN PenetapanByOmzet pbo ON o.OPDID = pbo.OPDID "
            f"AND o.MasaAwal = pbo.MasaAwal AND o.MasaAkhir = pbo.MasaAkhir AND o.UrutTgl = pbo.UrutTgl) "
            f"WHERE  SelfAssesment = 'N' AND o.[Status] = '1' AND TglPenetapan IS NULL AND TglHapus IS NULL "

            f"union "

            f"SELECT PendataanID, OBN,SPT,o.OPDID,ObyekBadanNo,cast (o.TotalPajak as varchar) AS Pajak,o.TglPendataan,NamaJenisPendapatan AS Jenis,"
            f"NamaBadan,o.MasaAwal, o.MasaAkhir FROM ((PendataanReklameHdr o LEFT JOIN vw_obyekbadan v ON "
            f"o.OPDID = v.OPDID) LEFT JOIN PenetapanByOmzet p ON o.OPDID = p.OPDID "
            f"AND o.MasaAwal = p.MasaAwal AND o.MasaAkhir = p.MasaAkhir AND o.UrutTgl = p.UrutTgl) "
            f"WHERE  SelfAssesment = 'N' AND o.[Status] = '1' AND TglPenetapan IS NULL AND TglHapus IS NULL ORDER BY SPT"
        )
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


class PenetapanSKP3(Resource):
    def get(self, pendataanid, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument( 'JenisPendapatanID', type=str )
        args = parser.parse_args()
        check_jenis = MsJenisPendapatan.query.filter_by(
            JenisPendapatanID=args['JenisPendapatanID']
        ).first()
        # untuk selain reklame
        if check_jenis.SelfAssessment == 'Y' or 'reklame' not in check_jenis.NamaJenisPendapatan.lower():
            select_query = db.session.execute(
                f"SELECT DISTINCT datediff(day,MasaAwal,MasaAkhir)+1 AS hitper, o.OPDID,ObyekBadanNo,NamaBadan,"
                f"NamaPemilik,AlamatBadan,Kota,Kecamatan, Kelurahan,v.KodeRekening,KodePos,v.NamaJenisPendapatan AS Sub,"
                f"UsahaBadan,cast(JmlOmzetAwal as varchar),cast(TarifPajak as varchar),MasaAwal,MasaAkhir,o.[Status],o.TglPendataan, o.SPT,v.WPID,"
                f"isnull(GroupAttribute,0) AS GA,v.OmzetID,HariJatuhTempo,Insidentil,UrutTgl,o.UPTID,isnull(LKecamatan,'') AS Kec,"
                f"isnull(LKelurahan,'') AS Kel,isnull((select FaxKecamatan from MsKecamatan c where c.KecamatanID = o.LKecamatan),'') AS LoKec "
                f"FROM ((PendataanByOmzet o LEFT JOIN vw_obyekbadan v ON o.OPDID = v.OPDID) "
                f"LEFT JOIN MsJenisPendapatan p ON v.UsahaBadan = p.JenisPendapatanID) WHERE o.PendataanID='{pendataanid}'")
        else:
            #untuk reklame
            select_query = db.session.execute(
                f"SELECT DISTINCT datediff(day,MasaAwal,MasaAkhir)+1 AS hitper, o.OPDID,ObyekBadanNo,NamaBadan, "
                f"NamaPemilik,AlamatBadan,Kota,Kecamatan, Kelurahan,v.KodeRekening,KodePos,v.NamaJenisPendapatan AS Sub,"
                f"UsahaBadan,'' as JmlOmzetAwal,cast(TotalPajak as varchar),MasaAwal,MasaAkhir,o.[Status],o.TglPendataan, "
                f"o.SPT,v.WPID, isnull(GroupAttribute,0) AS GA,v.OmzetID,HariJatuhTempo,Insidentil,UrutTgl,o.UPTID "
                f"FROM ((PendataanReklameHdr o LEFT JOIN vw_obyekbadan v ON o.OPDID = v.OPDID) "
                f"LEFT JOIN MsJenisPendapatan p ON v.UsahaBadan = p.JenisPendapatanID) WHERE o.PendataanID='{pendataanid}'")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)

def HitungDenda(KohirID):
    try:

        select_detail = vw_penetapan.query.filter_by(
            KohirID=KohirID
        ).first()
        if select_detail.JatuhTempo.rstrip() == 'Jatuh Tempo':
            date_1 = select_detail.TglJatuhTempo
            date_2 = datetime.now()
            diff = (date_2.date() - date_1.date()).days
            trfpajak = select_detail.Pajak

            if diff > 0:
                if diff <= 30:
                    diff == 1
                elif diff >= 40:
                    diff = (date_2.date().month - date_1.date().month)

            query = db.session.query(GeneralParameter.ParamNumValue) \
                .filter(GeneralParameter.ParamID == 'num_denda').first()
            result1 = []
            for row in query:
                result1.append(row)
            decDenda = result1[0]

            year_old = extract('year', select_detail.TglJatuhTempo)


            if year_old < '2024':
                denda = round(((float(2) * float(diff)) * float(trfpajak)) / 100)
            else:
                denda = round(((float(decDenda) * float(diff)) * float(trfpajak)) / 100)

        else:
            denda = select_detail.Denda
        return denda

    except Exception as e:
        logger.error(e)
        return False

class PenetapanSKP4(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self,  *args, **kwargs):
        # PARSING PARAMETER DARI REQUEST
        parser = reqparse.RequestParser()
        parser.add_argument( 'page', type=int )
        parser.add_argument( 'length', type=int )
        parser.add_argument( 'sort', type=str )
        parser.add_argument( 'sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc' )
        parser.add_argument( 'search', type=str )
        parser.add_argument( 'filter_jenis', type=str )
        parser.add_argument( 'kategori', type=str, choices=('true', 'false'), help='diisi dengan true atau false' )
        parser.add_argument( 'nonwp', type=str, choices=('true', 'false'), help='diisi dengan true atau false' )

        args = parser.parse_args()
        uid = kwargs['claim']["UID"]
        groupid = kwargs['claim']["GroupId"]
        # PegawaiID = kwargs['claim']["PegawaiID"]
        # if PegawaiID:
        #     select_query = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
        #         tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
        #     result = select_query[0]
        #     uptid = result
        #
        # else:
        #     select_query = db.session.execute(
        #         f"SELECT mu.UPTID FROM MsUPT AS mu WHERE mu.KDUNIT IN(SELECT gp.ParamStrValue "
        #         f"FROM GeneralParameter AS gp WHERE gp.ParamID='satker_sipkd') AND RIGHT(mu.KodeUPT,3)='01.'")
        #     result = select_query.first()[0]
        #     uptid = result

        result = []
        try:
            select_query = db.session.query(vw_penetapan.PenetapanID, vw_penetapan.OBN, vw_penetapan.UPTID, vw_penetapan.JatuhTempo,
                            vw_penetapan.OPDID,vw_penetapan.ObyekBadanNo, vw_penetapan.TglJatuhTempo, vw_penetapan.NoKohir,
                            vw_penetapan.NamaBadan, vw_penetapan.KohirID, vw_penetapan.NamaBadan, vw_penetapan.NamaPemilik,
                            vw_penetapan.AlamatBadan, vw_penetapan.KodeRekening, vw_penetapan.MasaAwal, vw_penetapan.MasaAkhir,
                            vw_penetapan.NamaJenisPendapatan, vw_penetapan.JenisPendapatanID, vw_penetapan.Pajak, vw_penetapan.PajakOpsen,vw_penetapan.Denda,
                            vw_penetapan.TglPenetapan, vw_penetapan.Insidentil, vw_penetapan.UPT, vw_penetapan.Kenaikan, vw_penetapan.TglKurangBayar,
                            vw_penetapan.DateUpd, vw_penetapan.SelfAssesment,vw_penetapan.StatusBayar, vw_penetapan.OmzetBase, vw_penetapan.UrutTgl,
                            case( [(vw_penetapan.SelfAssesment == 'Y', 'SPT')],
                                   else_='SKP'
                                   ).label( 'Kategori'), vw_penetapan.avatar, vw_penetapan.JOA.label('JmlOmzetAwal'),vw_penetapan.KLBayar
                            ) \
            # .filter(
            #     vw_penetapan.SKPOwner == uptid
            # )
            # else:
            #     select_query = db.session.query( vw_penetapan.PenetapanID, vw_penetapan.OBN, vw_penetapan.UPTID,
            #                                      vw_penetapan.OPDID, vw_penetapan.ObyekBadanNo,
            #                                      vw_penetapan.TglJatuhTempo, vw_penetapan.NoKohir,
            #                                      vw_penetapan.NamaBadan, vw_penetapan.KohirID, vw_penetapan.NamaBadan,
            #                                      vw_penetapan.NamaPemilik,
            #                                      vw_penetapan.AlamatBadan, vw_penetapan.KodeRekening,
            #                                      vw_penetapan.MasaAwal, vw_penetapan.MasaAkhir,
            #                                      vw_penetapan.NamaJenisPendapatan, vw_penetapan.JenisPendapatanID,
            #                                      vw_penetapan.Pajak, vw_penetapan.Denda,
            #                                      vw_penetapan.TglPenetapan, vw_penetapan.Insidentil, vw_penetapan.UPT,
            #                                      vw_penetapan.Kenaikan, vw_penetapan.TglKurangBayar,
            #                                      vw_penetapan.DateUpd, vw_penetapan.SelfAssesment,
            #                                      vw_penetapan.StatusBayar, vw_penetapan.OmzetBase, vw_penetapan.UrutTgl,
            #                                      case( [(vw_penetapan.SelfAssesment == 'Y', 'SPTP')],
            #                                            else_='SKP'
            #                                            ).label( 'Kategori' ), vw_penetapan.avatar
            #                                      ) \

            checkadmin = tblGroupUser.query.filter_by(
                GroupId=groupid
            ).first()

            checkwp = tblGroupUser.query.filter_by(
                GroupId=groupid
            ).first()

            if checkadmin.IsAdmin != 1 and checkwp.IsWP != 1:
                PegawaiID = kwargs['claim']["PegawaiID"]
                uptid = ''
                if PegawaiID:
                    select_query_uptid = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
                        tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
                    result = select_query_uptid[0]
                    uptid = result
                    print(uptid)
                select_query = select_query.filter(
                    vw_penetapan.SKPOwner == uptid
                )
            if checkadmin.IsAdmin == 1:
                select_query = select_query

            # filter_jenis
            if args['filter_jenis']:
                select_query = select_query.filter(
                    vw_penetapan.JenisPendapatanID == args['filter_jenis']
                )

            # kategori
            if args['kategori'] or args['kategori'] == "true":
                select_query = select_query.filter( vw_penetapan.SelfAssesment == 'Y' )
            else:
                select_query = select_query.filter( vw_penetapan.SelfAssesment == 'N' )

            # nonwp
            if args['nonwp'] or args['nonwp'] == "true":
                select_query = select_query.filter( vw_penetapan.Insidentil == 'Y' )
            else:
                select_query = select_query.filter( vw_penetapan.Insidentil == 'N' )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_penetapan.NamaBadan.ilike(search),
                        vw_penetapan.ObyekBadanNo.ilike(search),
                        vw_penetapan.NamaPemilik.ilike(search),
                        vw_penetapan.KohirID.ilike(search)
                        )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_penetapan, args['sort']).desc()
                else:
                    sort = getattr(vw_penetapan, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_penetapan.TglPenetapan.desc())


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
                d['Denda'] = HitungDenda(row.KohirID)
                result.append(d)
            return success_reads_pagination(query_execute, result)
        except Exception as e:
            logger.error(e)
            return failed_reads(result)


class PenetapanSKP5(Resource):
    def get(self, penetapanid, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT * FROM vw_penetapanomzet WHERE PenetapanID = '{penetapanid}'")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                if key == 'Pajak' or key == 'JmlBayar' or key == 'JBayar' or key == 'JmlKurangBayar' or key == 'JKurang' \
                        or key == 'Denda' or key == 'JDenda' or key == 'Kenaikan' or key == 'JKenaikan' or key == 'HarusBayar' or key == 'JOA':
                    d[key] = str(getattr(row, key))
                else:
                    d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


def KirimEmail(Email, type, data):
    try:
        logger.info('DO COMPOSSING EMAIL PERINGATAN TAGIHAN...')
        path = Path(__file__).parent
        print(data)
        # COMPOSING EMAIL
        receiver_email = Email
        subject = ""
        messageText = ""
        id_notificationsType = None
        text_NamaPajak = data['NamaJenisPendapatan']
        denda = int(data['Denda'].replace('.00', '')) if 'Denda' in data else 0
        total_price = int(data['Pajak'].replace('.00', '')) + denda
        if type == 'advice':
            id_notificationsType = 8
            subject = f"Tagihan Pajak {text_NamaPajak} Akan Segera Jatuh Tempo"
            messageText = ""
            with open('{}\\notifications\email_bill_reminder.html'.format(path), 'r') as f:
                message = f.read()
            messageUser = message.format(
                UNIT_LOGO=os.environ.get('EPAD_PUBLIC_LOGO_BIG'),
                UNIT_PUBLIC_URL=appFrontWebUrlWp,
                UNIT_NAME=appNameMobile,
                WP_NAME=data['NamaBadan'],
                NPWPD=str(data['ObyekBadanNo']),
                OWNER_NAME=data['NamaPemilik'],
                PAJAK_NAME=text_NamaPajak,
                PAJAK_CODE=data['KodeRekening'],
                REF_CODE=data['KohirID'],
                PAJAK_PRICE=rupiah_format(int(data['Pajak'].replace('.00',''))),
                PAJAK_DENDA=rupiah_format(denda),
                PAJAK_TOTAL=rupiah_format(total_price),
                DUE_DATE=data['TglJatuhTempo'].strftime("%d %B, %Y")
            )
        else:
            id_notificationsType = 9
            subject = f"Tagihan Pajak {text_NamaPajak} Telah Jatuh Tempo"
            messageText = ""
            with open('{}\\notifications\email_bill_reminder.html'.format(path), 'r') as f:
                message = f.read()
            messageUser = message.format(
                UNIT_LOGO=os.environ.get('EPAD_PUBLIC_LOGO_BIG'),
                UNIT_PUBLIC_URL=appFrontWebUrlWp,
                UNIT_NAME=appNameMobile,
                WP_NAME=data['NamaBadan'],
                NPWPD=str(data['ObyekBadanNo']),
                OWNER_NAME=data['NamaPemilik'],
                PAJAK_NAME=text_NamaPajak,
                PAJAK_CODE=data['KodeRekening'],
                REF_CODE=data['KohirID'],
                PAJAK_PRICE=rupiah_format(int(data['Pajak'].replace('.00', ''))),
                PAJAK_DENDA=rupiah_format(denda),
                PAJAK_TOTAL=rupiah_format(total_price),
                DUE_DATE=data['TglJatuhTempo'].strftime("%d %B, %Y")
            )

        # SEND EMAIL
        yag = yagmail.SMTP({appEmail: appName}, appEmailPassword)
        yag.send(receiver_email, subject, [messageUser])
        logger.info('SEND EMAIL PERINGATAN TAGIHAN TO USER {} OK'.format(receiver_email))
        yag.close()

        # ////INSERT TO TABLE NOTIFICATIONS
        add_record = Notifications(UserId=data['UserId'], id_notificationsType=id_notificationsType, attributes=data['KohirID'],
                                   title=subject, description=messageUser)
        db.session.add(add_record)
        db.session.commit()

        return True
    except Exception as e:
        logger.error('DO COMPOSSING EMAIL PERINGATAN TAGIHAN FAILED!')
        logger.error(e)
        db.session.rollback()
        return False


class PenetapanSKP6(Resource):
    def get(self, *args, **kwargs):
        logger.info('kadieu')
        select_query = db.session.execute(
            f"""SELECT distinct vu.UserId,vu.UID,vu.WPID,vu.Email,tu.DeviceId,vp.avatar,vp.avatar AS avatarusaha,mjp.img,
            vu.OPDID, vp.ObyekBadanNo,vp.TglJatuhTempo,vp.NamaBadan,vp.KohirID,vp.NamaPemilik,vp.AlamatBadan,
            vp.AlamatPemilik,vp.KodeRekening,vp.NamaJenisPendapatan,vp.Pajak,vp.StatusBayar, 
            (CASE WHEN dateadd(d, datediff(d,0, GETDATE()), 0) <= vp.TglJatuhTempo THEN 'advice' ELSE 'overdue' END) AS Status
            FROM vw_penetapan AS vp 
            INNER JOIN vw_userwp AS vu ON vp.OPDID=vu.OPDID INNER JOIN tblUser AS tu ON tu.UID = vu.UID 
            INNER JOIN MsJenisPendapatan AS mjp ON mjp.JenisPendapatanID = vu.JenisPendapatanID WHERE vu.Email IS NOT NULL 
            AND (vp.StatusBayar='Jatuh Tempo' OR (vp.TglJatuhTempo>=dateadd(d, datediff(d,0, GETDATE()), 0) AND
            vp.TglJatuhTempo<=dateadd(d, datediff(d,0, GETDATE()), 0)+7)) """
        )
        resultadvis = []
        resultjatuhtempo = []
        for row in select_query:
            if getattr(row, 'StatusBayar') != 'Jatuh Tempo':
                d = {}
                for key in row.keys():
                    if key == 'Pajak' or key == 'Denda':
                        d[key] = str( getattr(row, key))
                    else:
                        d[key] = getattr(row, key)
                resultadvis.append(d)
            else:
                d = {}
                for key in row.keys():
                    if key == 'Pajak' or key == 'Denda':
                        d[key] = str(getattr(row, key))
                    else:
                        d[key] = getattr(row, key)
                resultjatuhtempo.append(d)
        for x in resultadvis:
            checknotif = Notifications.query.filter_by(UserId=x['UserId'], id_notificationsType=8, attributes=x['KohirID']).first()
            if not checknotif:
                # print(x['Email'], 'advice', x['KohirID'])
                KirimEmail(x['Email'], 'advice', x)
        for y in resultjatuhtempo:
            checknotif = Notifications.query.filter_by(UserId=y['UserId'], id_notificationsType=9, attributes=y['KohirID']).first()
            if not checknotif:
                # print(y['Email'], 'jatuh', y['KohirID'])
                KirimEmail(y['Email'], 'JatuhTempo', y)
        return success_reads({})


class AddPenetapanSKP(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('NoKohir', type=str)
        parser.add_argument('KohirID', type=str)
        parser.add_argument('OPDID', type=str)
        parser.add_argument('TglPenetapan', type=str)
        parser.add_argument('TglJatuhTempo', type=str)
        parser.add_argument('MasaAwal', type=str)
        parser.add_argument('MasaAkhir', type=str)
        parser.add_argument('UrutTgl', type=str)
        parser.add_argument('JumlahOmzetAwal', type=str)
        parser.add_argument('JmlOmzetAwal', type=str)
        parser.add_argument('TarifPajak', type=str)
        parser.add_argument('TarifPajakOpsen', type=str)
        parser.add_argument('Denda', type=str)
        parser.add_argument('Kenaikan', type=str)
        parser.add_argument('IsPaid', type=str)
        parser.add_argument('TglBayar', type=str)
        parser.add_argument('JmlBayar', type=str)
        parser.add_argument('TglKurangBayar', type=str)
        parser.add_argument('JmlKurangBayar', type=str)
        parser.add_argument('JmlPeringatan', type=str)
        parser.add_argument('UPTID', type=str)
        parser.add_argument('Status', type=str)
        parser.add_argument('KodeStatus', type=str)
        parser.add_argument('LKecamatan', type=str)
        parser.add_argument('LKelurahan', type=str)
        parser.add_argument('UserUpd', type=str)
        parser.add_argument('DateUpd', type=str)

        parser.add_argument('SPT', type=str)
        uid = kwargs['claim']["UID"]

        try:
            args = parser.parse_args()
            result1 = db.session.execute(
                f"exec [SP_KOHIR_BLN2]")
            result2 = []
            for row in result1:
                result2.append(row)
            kohirid = result2[0][0]

            result3 = db.session.execute(
                f"exec [SP_KOHIR2]")
            result4 = []
            for row in result3:
                result4.append(row)
            nokohir = result4[0][0]

            db.session.execute(
                f"exec [SP_NomorKohir] '{args['SPT']}', '{kohirid}', '{args['MasaAwal']}', "
                f"'{args['MasaAkhir']}','{args['TglPenetapan']}','{uid}'")
            db.session.commit()
            print(args['JmlOmzetAwal'])
            print(args['JumlahOmzetAwal'])

            add_record = PenetapanByOmzet(
                NoKohir=nokohir,
                KohirID=kohirid,
                OPDID=args['OPDID'],
                TglPenetapan=args['TglPenetapan'],
                TglJatuhTempo=args['TglJatuhTempo'],
                MasaAwal=args['MasaAwal'],
                MasaAkhir=args['MasaAkhir'],
                UrutTgl=args['UrutTgl'],
                JmlOmzetAwal=args['JumlahOmzetAwal'] if args['JumlahOmzetAwal'] else args['JmlOmzetAwal'] ,
                TarifPajak=args['TarifPajak'],
                TarifPajakOpsen= 0 if args['TarifPajakOpsen']== None else args['TarifPajakOpsen'] ,
                Denda=sqlalchemy.sql.null(),
                Kenaikan=args['Kenaikan'],
                IsPaid='N',
                TglBayar=sqlalchemy.sql.null(),
                JmlBayar=sqlalchemy.sql.null(),
                JmlBayarOpsen=sqlalchemy.sql.null(),
                TglKurangBayar=sqlalchemy.sql.null(),
                JmlKurangBayar=sqlalchemy.sql.null(),
                JmlPeringatan=sqlalchemy.sql.null(),
                UPTID=args['UPTID'],
                Status=1,
                KodeStatus='70',
                LKecamatan=args['LKecamatan'],
                LKelurahan=args['LKelurahan'],
                UserUpd=uid,
                DateUpd=datetime.now()
            )
            db.session.add(add_record)
            db.session.commit()
            if add_record.KohirID:
                db.session.execute(
                    f"exec [SP_Penetapan] '{add_record.KohirID}',1")
                db.session.commit()

                query = db.session.execute(
                    f"SELECT mw.WPID FROM MsOPD AS mw "
                                           f"LEFT JOIN PenetapanByOmzet AS prh ON prh.OPDID = mw.OPDID "
                                           f"WHERE prh.KohirID='{add_record.KohirID}'"
                )
                result5 = []
                for row in query:
                    result5.append(row)
                wpid = result5[0][0]

                def to_datetime_safe(value):
                    if isinstance(value, str):
                        try:
                            return datetime.strptime(value, "%Y-%m-%d")
                        except ValueError:
                            try:
                                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                raise ValueError(f"Format tanggal tidak valid: {value}")
                    return value

                # Pastikan nilai-nilai bertipe datetime
                add_record.MasaAwal = to_datetime_safe(add_record.MasaAwal)
                add_record.MasaAkhir = to_datetime_safe(add_record.MasaAkhir)
                add_record.TglPenetapan = to_datetime_safe(add_record.TglPenetapan)
                add_record.DateUpd = to_datetime_safe(add_record.DateUpd)

                # Buat query dengan parameter binding
                query = text("""
                IF NOT EXISTS (
                    SELECT * FROM NomorKohir
                    WHERE KohirID = :kohir_id AND MasaAwal = :masa_awal AND MasaAkhir = :masa_akhir
                )
                BEGIN
                    INSERT INTO NomorKohir (
                        KohirID, MasaAwal, MasaAkhir, TglPenetapan, Penagih, WPID, UserUpd, DateUpd
                    )
                    VALUES (
                        :kohir_id, :masa_awal, :masa_akhir, :tgl_penetapan, '', :wpid, :user_upd, :date_upd
                    )
                END
                """)

                # Eksekusi query dengan parameter binding
                db.session.execute(query, {
                    'kohir_id': add_record.KohirID,
                    'masa_awal': add_record.MasaAwal,
                    'masa_akhir': add_record.MasaAkhir,
                    'tgl_penetapan': add_record.TglPenetapan,
                    'wpid': wpid,
                    'user_upd': add_record.UserUpd,
                    'date_upd': add_record.DateUpd
                })
                db.session.commit()

                # notif ke user wpo jika tersedia
                user_pendata = db.session.query(tblUser, MsJenisPendapatan, MsWPData) \
                    .join(tblUserWP, tblUserWP.UserId == tblUser.UserId)\
                    .join(MsOPD, tblUserWP.WPID == MsOPD.WPID) \
                    .join(MsJenisPendapatan, MsOPD.UsahaBadan == MsJenisPendapatan.JenisPendapatanID) \
                    .join(MsWPData, MsWPData.WPID == MsOPD.WPID) \
                    .filter(MsOPD.OPDID == args['OPDID']).first()
                if user_pendata:
                    if user_pendata.tblUser.DeviceId:
                        notifBody = f'Laporan pajak {user_pendata.MsJenisPendapatan.NamaJenisPendapatan} ({user_pendata.MsWPData.NamaBadan}) yang anda ajukan telah di tetapkan oleh petugas. Kini anda dapat membayar dan mendapatkan kode bayar pajak anda. Terima Kasih.'
                        notification_data = {
                            "notification": {
                                "title": 'Pajak Telah Ditetapkan',
                                "body": notifBody,
                                "priority": "high",
                                "icon": appFrontWebLogo,
                                "click_action": "FLUTTER_NOTIFICATION_CLICK",
                            },
                            "data": {
                                "action": "refresh",
                                "type": "confirmed_pendataan",
                                "page": "home"
                            }
                        }
                        sendNotif = sendNotificationNative(user_pendata.tblUser.DeviceId, notification_data)
                        if sendNotif.status_code == 200:
                            add_notif = Notifications(
                                UserId=user_pendata.tblUser.UserId,
                                id_notificationsType=6,
                                title="Pajak Telah Ditetapkan",
                                description=notifBody,
                                created_by="system"
                            )
                            db.session.add(add_notif)
                            db.session.commit()

                return success_create({'KohirID': add_record.KohirID,
                                       'UPTID': add_record.UPTID,
                                       'OPDID': add_record.OPDID,
                                       'TarifPajak': add_record.TarifPajak})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_create({})


class UpdatePenetapanSKP(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        print(kwargs['claim'])
        parser.add_argument('TglPenetapan', type=str)
        args = parser.parse_args()
        try:
            select_query = PenetapanByOmzet.query.filter_by(PenetapanID=id).first()
            if select_query:
                if args['TglPenetapan']:
                    select_query.TglPenetapan = args['TglPenetapan']
                db.session.commit()
                db.session.execute(
                    f"exec [SP_Penetapan] '{select_query.KohirID}',2")
                db.session.commit()
                return success_update({'id': id})
        except Exception as e:

            db.session.rollback()
            print(e)
            return failed_update({})


# class HitungDenda(Resource):
#     # method_decorators = {'get': [tblUser.auth_apikey_privilege]}
#     def get(self, *args, **kwargs):
#         parser = reqparse.RequestParser()
#         parser.add_argument('KohirID', type=str)
#         args = parser.parse_args()
#
#         try:
#             # uid = kwargs['claim']["UID"]
#             # groupid = kwargs['claim']["GroupId"]
#             # PegawaiID = kwargs['claim']["PegawaiID"]
#             # uptid = ''
#             # if PegawaiID:
#             #     select_query_uptid = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
#             #         tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
#             #     result = select_query_uptid[0]
#             #     uptid = result
#             #     print(uptid)
#             # FILTER_ID
#             if args['KohirID']:
#                 args['KohirID']
#
#             select_detail = vw_penetapan.query.filter_by(
#                 KohirID=args['KohirID']
#             ).first()
#             # date_1 = ''
#             # if select_detail.JatuhTempo != '':
#             if select_detail.JatuhTempo.rstrip() == ('Jatuh Tempo'):
#                 date_1 = select_detail.TglJatuhTempo
#                 date_2 =  datetime.now()
#                 # date_format_str = '%Y-%m-%d %H:%M:%S'
#                 # print( date_2 )
#                 # if date_1 != '':
#                 # start = datetime.strptime( date_1, date_format_str )
#                 # end = datetime.strptime( date_2, date_format_str )
#                 # start = date_1
#                 # end = date_2
#                 diff = (date_2.date() - date_1.date()).days
#                 trfpajak = select_detail.Pajak
#
#                 if diff > 0:
#                     if diff <= 30:
#                         diff == 1
#                     else:
#                         diff = (date_2.date().month - date_1.date().month)
#                 print( diff )
#
#                 query = db.session.query( GeneralParameter.ParamNumValue ) \
#                     .filter( GeneralParameter.ParamID == 'num_denda' ).first()
#                 result1 = []
#                 for row in query:
#                     result1.append( row )
#                 decDenda = result1[0] / 100
#
#                 denda = round(((float( decDenda ) * float( diff )) * float( trfpajak )) / 100)
#                 print( denda )
#             else:
#                 denda = select_detail.Denda
#             return success_reads({'denda': denda})
#         except Exception as e:
#             logger.error(e)
#             return failed_reads({})


class UpdatePenetapanSKPKurangBayar(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        print(kwargs['claim'])

        parser.add_argument('KohirID', type=str)
        parser.add_argument('TarifPajak', type=str)
        parser.add_argument( 'TotalPajak', type=str )
        parser.add_argument('TglJatuhTempo', type=str)
        parser.add_argument('Denda', type=str)
        parser.add_argument('Kenaikan', type=str)
        parser.add_argument('TglKurangBayar', type=str)
        parser.add_argument('JmlKurangBayar', type=str)
        parser.add_argument('Penagih', type=str)

        args = parser.parse_args()

        try:
            query_select = vw_penetapan.query.filter_by( PenetapanID=id ).first()

            if query_select.OmzetBase == 'N':
                select_query = PenetapanReklameHdr.query.filter_by( PenetapanID=id ).first()
            else:
                select_query = PenetapanByOmzet.query.filter_by(PenetapanID=id).first()

            select_detail = vw_penetapan.query.filter_by(
                KohirID=select_query.KohirID
                ).first()

            if select_detail.JatuhTempo.rstrip() == ('Jatuh Tempo'):
                date_1 = select_detail.TglJatuhTempo
                date_2 = datetime.now()
                diff = (date_2.date() - date_1.date()).days
                trfpajak = select_detail.Pajak

                if diff > 0:
                    if diff <= 30:
                        diff == 1
                    else:
                        diff = (date_2.date().month - date_1.date().month)
                print(diff)

                query = db.session.query(GeneralParameter.ParamNumValue) \
                    .filter(GeneralParameter.ParamID == 'num_denda').first()
                result1 = []
                for row in query:
                    result1.append(row)
                decDenda = result1[0] / 100

                denda = round(((float(decDenda) * float(diff)) * float(trfpajak)) / 100)
                print(denda)
                totalpajak = select_detail.Pajak
                jumlahkurangbayar = float( totalpajak ) + float( denda )
                # jumlahkurangbayar = 0

                if select_query:
                    if args['TglJatuhTempo']:
                        select_query.TglJatuhTempo = select_detail.TglJatuhTempo
                    if args['Denda']:
                        select_query.Denda = args['Denda']
                    if args['Kenaikan']:
                        select_query.Kenaikan = args['Kenaikan']
                    if args['TglKurangBayar']:
                        select_query.TglKurangBayar = args['TglKurangBayar']
                    select_query.JmlKurangBayar = select_detail.Pajak + float(args['Denda'])
                    db.session.commit()
                    db.session.execute(
                        f"exec [SP_Penetapan] '{select_query.KohirID}',3" )
                    db.session.commit()
                    if select_query.KohirID:
                        kohirid = select_query.KohirID
                        query = NomorKohir.query.filter_by( KohirID=kohirid ).first()
                        if query:
                            if args['TglKurangBayar']:
                                query.TglKurangBayar = args['TglKurangBayar']
                            if args['Penagih']:
                                query.Penagih = args['Penagih']
                            db.session.commit()
                    return success_update( {'KohirID': select_query.KohirID,
                                            'UPTID': select_query.UPTID,
                                            # 'TarifPajak': select_query.TarifPajak if args['TarifPajak'] else select_query.TotalPajak,
                                            'TarifPajak': select_detail.Pajak,
                                            'Denda': denda,
                                            'JumlahKurangBayar': jumlahkurangbayar} )
            # else:
            #     denda = select_detail.Denda
            #     totalpajak = select_detail.Pajak
            #     jumlahkurangbayar = float(totalpajak) + float(denda)
            #
            #     if select_query:
            #         if args['TglJatuhTempo']:
            #             select_query.TglJatuhTempo = select_detail.TglJatuhTempo
            #         if args['Denda']:
            #             denda
            #         if args['Kenaikan']:
            #             select_query.Kenaikan = args['Kenaikan']
            #         if args['TglKurangBayar']:
            #             select_query.TglKurangBayar = args['TglKurangBayar']
            #         if denda:
            #             jumlahkurangbayar
            #         db.session.commit()
            #         db.session.execute(
            #             f"exec [SP_Penetapan] '{select_query.KohirID}',3")
            #         db.session.commit()
            #         if select_query.KohirID:
            #             kohirid = select_query.KohirID
            #             query = NomorKohir.query.filter_by(KohirID=kohirid).first()
            #             if query:
            #                 if args['TglKurangBayar']:
            #                     query.TglKurangBayar = args['TglKurangBayar']
            #                 if args['Penagih']:
            #                     query.Penagih = args['Penagih']
            #                 db.session.commit()
            #         return success_update({'KohirID': select_query.KohirID,
            #                                'UPTID': select_query.UPTID,
            #                                # 'TarifPajak': select_query.TarifPajak if args['TarifPajak'] else select_query.TotalPajak,
            #                                'TarifPajak': select_detail.Pajak,
            #                                'Denda': denda,
            #                                'JumlahKurangBayar': jumlahkurangbayar})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_update({})


class DeletePenetapanSKP(Resource):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}

    def delete(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        print(kwargs['claim'])
        parser.add_argument('NoKohir', type=str)
        parser.add_argument('KohirID', type=str)
        parser.add_argument('OPDID', type=int)
        parser.add_argument('OmzetBase', type=str)
        parser.add_argument('MasaAwal', type=str)
        parser.add_argument('MasaAkhir', type=str)
        parser.add_argument('UrutTgl', type=int)
        parser.add_argument('NoSKHapus', type=str)
        parser.add_argument('TglSKHapus', type=str)
        args = parser.parse_args()
        uid = kwargs['claim']["UID"]

        try:
            delete_record = vw_penetapan.query.filter_by(PenetapanID=id)
            if delete_record:

                # Siapkan parameter dan konversi jika perlu
                urut_tgl = args['UrutTgl'] if args['UrutTgl'] is not None else 0
                tgl_skhapus = args['TglSKHapus'] or '1900-01-01'  # fallback bila kosong

                db.session.execute(
                    text("""
                        exec SP_DEL_KOHIR 
                            :NoKohir, :KohirID, :OPDID, :OmzetBase, 
                            :MasaAwal, :MasaAkhir, :UrutTgl, :UID, 
                            :NoSKHapus, :TglSKHapus
                    """),
                    {
                        'NoKohir': args['NoKohir'],
                        'KohirID': args['KohirID'],
                        'OPDID': args['OPDID'],
                        'OmzetBase': args['OmzetBase'],
                        'MasaAwal': args['MasaAwal'],
                        'MasaAkhir': args['MasaAkhir'],
                        'UrutTgl': urut_tgl,
                        'UID': uid,
                        'NoSKHapus': args['NoSKHapus'],
                        'TglSKHapus': tgl_skhapus
                    }
                )
                db.session.commit()

                db.session.execute(
                    text("exec SP_Penetapan :KohirID, :flag"),
                    {'KohirID': args['KohirID'], 'flag': 0}
                )
                db.session.commit()

                return success_delete({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_delete({})


#######################################################################
#######################################################################

class PenetapanSKP(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1)
        parser.add_argument('length', type=int, default=10)
        parser.add_argument('sort', type=str, default='TglPendataan')
        parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), default='desc')
        parser.add_argument('search', type=str)
        parser.add_argument('filter_jenis', type=str)
        parser.add_argument('kategori', type=str)
        parser.add_argument('nonwp', type=str)
        args = parser.parse_args()

        try:
            query = db.session.query(vw_pendataan).with_entities(
                vw_pendataan.OPDID,vw_pendataan.PendataanID, vw_pendataan.ObyekBadanNo, vw_pendataan.NamaBadan,
                vw_pendataan.TglPendataan, vw_pendataan.TarifPajak, vw_pendataan.JmlOmzetAwal,vw_pendataan.UrutTgl,
                vw_pendataan.KodeRekening,vw_pendataan.NamaJenisPendapatan,vw_pendataan.MasaAwal,vw_pendataan.MasaAkhir,
                case([(vw_pendataan.SelfAssesment == 'Y', 'SPTP')], else_='SKP').label('Kategori')
            ).filter(vw_pendataan.Status == '1', vw_pendataan.TglData != None)

            # Apply filters
            if args['kategori'] or args['kategori'] == "true":
                query = query.filter(vw_pendataan.SelfAssesment == 'Y')
            elif args['kategori'] == "false":
                query = query.filter(vw_pendataan.SelfAssesment == 'N')

            if args['filter_jenis']:
                query = query.filter(vw_pendataan.JenisPendapatanID == args['filter_jenis'])

            if args['nonwp'] == "true":
                query = query.filter(vw_pendataan.Insidentil == 'Y')
            elif args['nonwp'] == "false":
                query = query.filter(vw_pendataan.Insidentil == 'N')

            if args['search']:
                search = f"%{args['search']}%"
                query = query.filter(
                    or_(vw_pendataan.NamaBadan.ilike(search),
                        vw_pendataan.ObyekBadanNo.ilike(search))
                )

            # Sorting
            sort_col = getattr(vw_pendataan, args['sort'], vw_pendataan.TglPendataan)
            sort = sort_col.desc() if args['sort_dir'] == "desc" else sort_col.asc()
            query = query.order_by(sort)

            # Pagination
            page = args['page']
            length = min(args['length'], 100)
            query_paginated = query.paginate(page=page, per_page=length, error_out=False)

            # Convert results to a list of dictionaries
            result = [row._asdict() for row in query_paginated.items]

            # Return success response with pagination
            return success_reads_pagination(query_paginated, result)
        except Exception as e:
            logger.error(e)
            return failed_reads([])



# class PenetapanSKP(Resource):
#     method_decorators = {'get': [tblUser.auth_apikey_privilege]}
#
#     def get(self, *args, **kwargs):
#
#         # PARSING PARAMETER DARI REQUEST
#         parser = reqparse.RequestParser()
#         parser.add_argument('page', type=int)
#         parser.add_argument('length', type=int)
#         parser.add_argument('sort', type=str)
#         parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
#         parser.add_argument('search', type=str)
#         parser.add_argument('filter_jenis', type=str)
#         parser.add_argument('kategori', type=str)
#         parser.add_argument('nonwp', type=str)
#
#         args = parser.parse_args()
#         UserId = kwargs['claim']["UserId"]
#
#         result = []
#         try:
#
#             select_query = db.session.query(vw_pendataan.PendataanID, vw_pendataan.OBN, vw_pendataan.OPDID,
#                                             vw_pendataan.ObyekBadanNo, vw_pendataan.JmlOmzetAwal,vw_pendataan.JmlOmzetAwal.label('JumlahOmzetAwal'),
#                                             vw_pendataan.TarifPajak, vw_pendataan.TarifPajakOpsen,
#                                             vw_pendataan.TglPendataan, vw_pendataan.NamaJenisPendapatan, vw_pendataan.UrutTgl,
#                                             vw_pendataan.NamaBadan, vw_pendataan.MasaAwal, vw_pendataan.SPT,
#                                             vw_pendataan.MasaAkhir, vw_pendataan.TglData, vw_pendataan.AlamatPemilik,
#                                             vw_pendataan.AlamatBadan, vw_pendataan.KodeRekening, vw_pendataan.NamaJenisPendapatan,
#                                             vw_pendataan.SelfAssesment, vw_pendataan.Insidentil, vw_pendataan.avatar,
#                                                  case( [(vw_pendataan.SelfAssesment == 'Y', 'SPTP')],
#                                                        else_='SKP'
#                                                        ).label( 'Kategori' )
#                                             )\
#                 .filter(
#                 vw_pendataan.Status == '1', vw_pendataan.TglData != None
#             ).distinct()
#
#             # select_query = vw_pendataan.query
#
#             # kategori
#             if args['kategori'] or args['kategori'] == "true":
#                 select_query = select_query.filter( vw_pendataan.SelfAssesment == 'Y' )
#             else:
#                 select_query = select_query.filter( vw_pendataan.SelfAssesment == 'N' )
#
#             # filter_jenis
#             if args['filter_jenis']:
#                 select_query = select_query.filter(
#                     vw_pendataan.JenisPendapatanID == args['filter_jenis']
#                 )
#
#             # nonwp
#             if args['nonwp'] or args['nonwp'] == "true":
#                 select_query = select_query.filter( vw_pendataan.Insidentil == 'Y' )
#             else:
#                 select_query = select_query.filter( vw_pendataan.Insidentil == 'N' )
#
#             # SEARCH
#             if args['search'] and args['search'] != 'null':
#                 search = '%{0}%'.format(args['search'])
#                 select_query = select_query.filter(
#                     or_(vw_pendataan.NamaBadan.ilike(search),
#                         vw_pendataan.ObyekBadanNo.ilike(search),
#                         vw_pendataan.NamaPemilik.ilike(search)
#                         )
#                 )
#
#             # SORT
#             if args['sort']:
#                 if args['sort_dir'] == "desc":
#                     sort = getattr(vw_pendataan, args['sort']).desc()
#                 else:
#                     sort = getattr(vw_pendataan, args['sort']).asc()
#                 select_query = select_query.order_by(sort)
#             else:
#                 select_query = select_query.order_by(vw_pendataan.TglPendataan.desc())
#
#             # PAGINATION
#             page = args['page'] if args['page'] else 1
#             length = args['length'] if args['length'] else 10
#             lengthLimit = length if length < 101 else 100
#             query_execute = select_query.paginate(page, lengthLimit)
#
#             result = []
#             for row in select_query:
#                 d = {}
#                 for key in row.keys():
#                     if key == 'Pajak' or key == 'JmlBayar' or key == 'JBayar' or key == 'JmlKurangBayar' or key == 'JKurang' \
#                             or key == 'Denda' or key == 'JDenda' or key == 'Kenaikan' or key == 'JKenaikan' or key == 'HarusBayar' or key == 'JOA':
#                         d[key] = str(getattr(row, key))
#                     else:
#                         d[key] = getattr(row, key)
#                 result.append(d)
#             return success_reads_pagination(query_execute, result)
#         except Exception as e:
#             logger.error(e)
#             return failed_reads(result)