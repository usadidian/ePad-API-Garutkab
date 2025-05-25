from datetime import datetime

import sqlalchemy
from flask_restful import Resource, reqparse
from sqlalchemy import case
from sqlalchemy import or_
from config.api_message import success_reads_pagination, failed_reads, success_reads, failed_create, success_create, \
    success_update, failed_update, success_delete, failed_delete
from config.database import db
from controller.MsBendahara import MsBendahara
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsPegawai import MsPegawai
from controller.NomorKohir import NomorKohir
from controller.SetoranHist import SetoranHist
from controller.tblUser import tblUser
from controller.vw_obyekbadan import vw_obyekbadan


class PembayaranSPTP2(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}
    def get(self, *args, **kwargs):
        uid = kwargs['claim']["UID"]
        PegawaiID = kwargs['claim']["PegawaiID"]
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
        select_query = db.session.execute(
            f"SELECT OBN,ObyekBadanNo,(CASE WHEN TglHapus IS NOT NULL THEN NamaBadan ELSE NamaBadan END) AS NamaBadan,"
            f"Jenis,TglJatuhTempo,(CASE WHEN NIsPaid <> 'Lunas' THEN NIsPaid ELSE (case when (select top 1 "
            f"NTPD from SetoranHist s where s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir) is not null then "
            f"(case when (select sum(s.JmlBayar) + sum(s.JmlBayarDenda) from SetoranHist s where s.SubKohir = v.KohirID "
            f"and s.NoKohir = v.NoKohir and NTPD is not null) = HarusBayar then 'Lunas' else 'Kode Bayar' end) else "
            f"'Kode Bayar' end) END) AS NIsPaid,NoKohir,ISNULL(KohirID,'') AS KohirID,(case when CekSTS + "
            f"CekSTSDenda = '' then '' else 'STS' end) AS STS,(select top 1 NoSSPD from SetoranHist s where "
            f"s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir) AS KodeBayar, (select top 1 (case when KodeUPT in "
            f"(select kode_badan from vw_header) then (select badan_singkat from vw_header) else UPT end) from MsUPT u "
            f"where u.UPTID = v.SKPOwner) AS Dinas,(select top 1 TglNTPD from SetoranHist s where s.SubKohir = v.KohirID "
            f"and s.NoKohir = v.NoKohir) AS TglNTPD,(select top 1 NTPD from SetoranHist s where s.SubKohir = v.KohirID "
            f"and s.NoKohir = v.NoKohir) AS NTPD,isnull((select top 1 right('0'+convert(varchar,datepart(day,TglNTPD)),2) "
            f"+ '/' + right('0'+convert(varchar,datepart(month,TglNTPD)),2) + '/' + right(convert(varchar,datepart(year,TglNTPD)),2) "
            f"+ right(NTB,10) from SetoranHist s where s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir),'-') AS NTPDNT "
            f"FROM vw_penetapanomzet v WHERE ParentID = '1'  AND OPDID IN (select distinct OPDID from "
            f"MsObyekBadan where SelfAssesment = 'Y' and Insidentil = 'N')  UNION SELECT OBN,ObyekBadanNo,"
            f"(CASE WHEN TglHapus IS NOT NULL THEN NamaBadan ELSE NamaBadan END) AS NamaBadan,Jenis,TglJatuhTempo,"
            f"(CASE WHEN NIsPaid <> 'Lunas' THEN NIsPaid ELSE (case when (select top 1 NTPD from SetoranHist s "
            f"where s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir) is not null then (case when (select sum(s.JmlBayar) + "
            f"sum(s.JmlBayarDenda) from SetoranHist s where s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir and NTPD is not null) "
            f"= HarusBayar then 'Lunas' else 'Kode Bayar' end) else 'Kode Bayar' end) END) AS NIsPaid,NoKohir,"
            f"ISNULL(KohirID,'') AS KohirID,(case when CekSTS + CekSTSDenda = '' then '' else 'STS' end) AS STS,"
            f"(select top 1 NoSSPD from SetoranHist s where s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir) AS KodeBayar, "
            f"(select top 1 (case when KodeUPT in (select kode_badan from vw_header) then (select badan_singkat from vw_header) "
            f"else UPT end) from MsUPT u where u.UPTID = v.SKPOwner) AS Dinas,(select top 1 TglNTPD from SetoranHist s "
            f"where s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir) AS TglNTPD,(select top 1 NTPD from SetoranHist s "
            f"where s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir) AS NTPD,isnull((select top 1 right('0'+convert"
            f"(varchar,datepart(day,TglNTPD)),2) + '/' + right('0'+convert(varchar,datepart(month,TglNTPD)),2) + '/' + "
            f"right(convert(varchar,datepart(year,TglNTPD)),2) + right(NTB,10) from SetoranHist s where s.SubKohir = v.KohirID "
            f"and s.NoKohir = v.NoKohir),'-') AS NTPDNT FROM vw_penetapanreklame v WHERE ParentID = '1'  "
            f"AND OPDID IN (select distinct OPDID from MsObyekBadan where SelfAssesment = 'Y' and Insidentil = 'N')  "
            f"ORDER BY KohirID DESC, Jenis"
        )
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


class PembayaranSPTP3(Resource):
    def get(self, kohirid, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT *,isnull((select sum(JmlBayarDenda) from SetoranHist s where s.SubKohir = o.KohirID and s.NoKohir = "
            f"o.NoKohir),0) AS JBD, isnull((select sum(JmlBayar) from SetoranHist s where s.SubKohir = o.KohirID and "
            f"s.NoKohir = o.NoKohir),0) AS JBPK, isnull((select top 1 Penagih from NomorKohir k where k.KohirID = "
            f"o.KohirID),'') AS Tagih FROM vw_penetapanomzet o WHERE KohirID = '{kohirid}' UNION SELECT *,"
            f"isnull((select sum(JmlBayarDenda) from SetoranHist s where s.SubKohir = r.KohirID and s.NoKohir = "
            f"r.NoKohir),0) AS JBD, isnull((select sum(JmlBayar) from SetoranHist s where s.SubKohir = r.KohirID "
            f"and s.NoKohir = r.NoKohir),0) AS JBPK, isnull((select top 1 Penagih from NomorKohir k where k.KohirID = "
            f"r.KohirID),'') AS Tagih FROM vw_penetapanreklame r WHERE KohirID = '{kohirid}' ")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                if key == 'Pajak' or key == 'JmlBayar' or key == 'JBayar' or key == 'JmlKurangBayar' or key == 'JKurang'\
                        or key == 'Denda' or key == 'JDenda' or key == 'Kenaikan' or key == 'JKenaikan' or key == 'HarusBayar' \
                        or key == 'JOA' or key == 'JBD' or key == 'JBPK':
                    d[key] = str(getattr(row, key))
                else:
                    d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


class PembayaranSPTP4(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, kohirid, *args, **kwargs):

        uid = kwargs['claim']["UID"]
        PegawaiID = kwargs['claim']["PegawaiID"]
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

        select_query = db.session.execute(
            f"SELECT NoUrut, s.TglBayar, (case when Transaksi='T' then 'Tunai' else 'Transfer' end) AS Transaksi, "
            f"isnull(s.JmlBayar,0) AS JmlBayar, isnull(JmlBayarDenda,0) AS JmlBayarDenda, NoSSPD, NamaPenyetor,s.NoKohir,"
            f"isnull(right('0'+convert(varchar,datepart(day,TglNTPD)),2) + '/' + right('0'+convert(varchar,datepart(month,TglNTPD)),2) "
            f"+ '/' + right(convert(varchar,datepart(year,TglNTPD)),2) + NTB,'-') AS NTPDNT FROM SetoranHist s LEFT JOIN "
            f"vw_penetapanomzet o ON s.NoKohir = o.NoKohir AND s.SubKohir = o.KohirID WHERE Jenis IS NOT NULL AND "
            f"s.SubKohir = '{kohirid}' AND OPDID IN (select distinct OPDID from MsObyekBadan where  "
            f"SelfAssesment = 'Y' and Insidentil = 'N') UNION SELECT NoUrut,s.TglBayar, (case when Transaksi='T' then "
            f"'Tunai' else 'Transfer' end) AS Transaksi, isnull(s.JmlBayar,0) AS JmlBayar, isnull(JmlBayarDenda,0) "
            f"AS JmlBayarDenda, NoSSPD, NamaPenyetor,s.NoKohir,isnull(right('0'+convert(varchar,datepart(day,TglNTPD)),2) "
            f"+ '/' + right('0'+convert(varchar,datepart(month,TglNTPD)),2) + '/' + right(convert(varchar,datepart(year,TglNTPD)),2) + NTB,'-') "
            f"AS NTPDNT FROM SetoranHist s LEFT JOIN vw_penetapanreklame r ON s.NoKohir = r.NoKohir AND s.SubKohir = r.KohirID "
            f"WHERE Jenis IS NOT NULL AND s.SubKohir = '{kohirid}' AND OPDID IN (select distinct OPDID "
            f"from MsObyekBadan where  SelfAssesment = 'Y' and Insidentil = 'N') ORDER BY s.TglBayar DESC")
            # replace(cast('{nokohir}' as int), '.', '')

        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                if key == 'JmlBayar' or key == 'JmlBayarDenda':
                    d[key] = str(getattr(row, key))
                else:
                    d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


class PembayaranSPTP5(Resource):
    def get(self, subkohir, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT * FROM SetoranHist WHERE subkohir = '{subkohir}'")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                if key == 'Pajak' or key == 'JmlBayar' or key == 'JBayar' or key == 'JmlKurangBayar' or key == 'JKurang'\
                        or key == 'Denda' or key == 'JDenda' or key == 'Kenaikan' or key == 'JKenaikan' or key == 'HarusBayar' or key == 'JOA':
                    d[key] = str(getattr(row, key))
                else:
                    d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)

class AddPembayaranSPTP(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('NoKohir', type=str)
        parser.add_argument('NoUrut', type=str)
        parser.add_argument('SubKohir', type=str)
        parser.add_argument('TglBayar', type=str)
        parser.add_argument('JmlBayar', type=str)
        parser.add_argument('JmlBayarDenda', type=str)
        parser.add_argument('Transaksi', type=str)
        parser.add_argument('NoSSPD', type=str)
        parser.add_argument('NamaPenyetor', type=str)
        # parser.add_argument('STS', type=str)
        # parser.add_argument('STSDenda', type=str)
        parser.add_argument('Keterangan', type=str)
        # parser.add_argument('NTPD', type=str)
        # parser.add_argument('NTB', type=str)
        # parser.add_argument('TglNTPD', type=str)
        parser.add_argument('BendID', type=str)
        parser.add_argument('KodeStatus', type=str)
        parser.add_argument('UserUpd', type=str)
        parser.add_argument('DateUpd', type=str)

        parser.add_argument('KohirID', type=str)
        parser.add_argument('Penagih', type=str)

        try:
            uid = kwargs['claim']["UID"]
            PegawaiID = kwargs['claim']["PegawaiID"]
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

            if PegawaiID:
                select_query = db.session.query(MsBendahara.BendaharaID).filter(
                    MsBendahara.PegawaiID == PegawaiID).first()
                result = select_query[0]
                bendaharaid = result
                print(bendaharaid)
            else:
                select_query = db.session.execute(
                    f"SELECT TOP 1 mb.BendaharaID FROM MsBendahara AS mb WHERE mb.PegawaiID in(SELECT mp.PegawaiID "
                    f"FROM MsPegawai mp WHERE mp.UPTID IN(SELECT mu.UPTID FROM MsUPT mu WHERE mu.KDUNIT "
                    f"IN(SELECT gp.ParamStrValue FROM GeneralParameter AS gp WHERE gp.ParamID='satker_sipkd') " 
                    f"AND RIGHT(mu.KodeUPT,3)='01.'))")
                result = select_query.first()[0]
                bendaharaid = result

            args = parser.parse_args()

            result1 = db.session.execute(
                f"exec [SP_SSPD]")
            result2 = []
            for row in result1:
                result2.append(row)
            nosspd = result2[0][0]

            select_query = db.session.execute(
                f"SELECT DISTINCT ISNULL(MAX(NoUrut),0) + 1 FROM SetoranHist WHERE SubKohir = '{args['SubKohir']}'")
            result3 = select_query.first()[0]
            nourut = result3

            jmlbayar = float(args['JmlBayar'])
            if args['JmlBayarDenda']:
                jmlbayardenda = float(args['JmlBayarDenda'])
            totalbayar = jmlbayar + jmlbayardenda

            result = []
            for row in result:
                result.append(row)

            add_record = SetoranHist(
                NoKohir=args['NoKohir'],
                NoUrut=nourut,
                SubKohir=args['SubKohir'],
                TglBayar=args['TglBayar'],
                JmlBayar=jmlbayar,
                JmlBayarDenda=jmlbayardenda,
                Transaksi=args['Transaksi'],
                NoSSPD=nosspd,
                NamaPenyetor=args['NamaPenyetor'],
                Keterangan=args['Keterangan'],
                BendID=bendaharaid,
                KodeStatus=args['KodeStatus'],
                UserUpd=uid,
                DateUpd=datetime.now()
            )
            db.session.add(add_record)
            if args['Penagih']:
                update_query = db.session.execute(
                    f"UPDATE NomorKohir SET Penagih='{args['Penagih']}',UserUpd='{uid}',DateUpd=getdate() "
                    f"WHERE KohirID='{args['SubKohir']}'")
                db.session.commit()
            return success_create({'SetoranHistID': add_record.SetoranHistID,
                                   'SubKohir': add_record.SubKohir,
                                   'NoSSPD': add_record.NoSSPD,
                                   'Transaksi': add_record.Transaksi,
                                   'TglBayar': add_record.TglBayar,
                                   'TotalBayar':totalbayar})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_create({})


class UpdatePembayaranSPTP(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}
    def put(self, id, *args, **kwargs):
        uid = kwargs['claim']["UID"]
        parser = reqparse.RequestParser()
        print(kwargs['claim'])
        parser.add_argument('TglBayar', type=str)
        parser.add_argument('SubKohir', type=str)
        parser.add_argument('Penagih', type=str)
        parser.add_argument('Transaksi', type=str)
        args = parser.parse_args()
        try:
            select_query = SetoranHist.query.filter_by(SetoranHistID=id).first()
            if select_query:
                if args['TglBayar']:
                    select_query.TglBayar = args['TglBayar']
                if args['Transaksi']:
                    select_query.Transaksi = args['Transaksi']
                if args['Penagih']:
                    update_query = db.session.execute(
                        f"UPDATE NomorKohir SET Penagih='{args['Penagih']}',UserUpd='{uid}',DateUpd=getdate() "
                        f"WHERE KohirID='{args['SubKohir']}'")
                db.session.commit()
                return success_update({'id': id})
        except Exception as e:

            db.session.rollback()
            print(e)
            return failed_update({})


class DeletePembayaranSPTP(Resource):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}

    def delete(self, id, *args, **kwargs):
        try:
            delete_record = SetoranHist.query.filter_by(SetoranHistID=id)
            delete_record.delete()
            db.session.commit()
            return success_delete({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_delete({})

#######################################################################
#######################################################################

class PembayaranSPTP(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):

        # PARSING PARAMETER DARI REQUEST
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('length', type=int)
        parser.add_argument('sort', type=str)
        parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
        parser.add_argument('search', type=str)
        parser.add_argument('search_jenis', type=str)

        args = parser.parse_args()
        UserId = kwargs['claim']["UserId"]

        result = []
        try:
            select_query = db.session.query(vw_obyekbadan.OBN, vw_obyekbadan.OPDID,
                                            vw_obyekbadan.ObyekBadanNo, vw_obyekbadan.NamaBadan,
                                            vw_obyekbadan.NamaJenisPendapatan,
                                            vw_obyekbadan.TglSah,
                                            case([(vw_obyekbadan.MasaPendapatan == 'B', 'Bulanan')]
                                                 ,
                                                 else_=''
                                                 ).label('Masa'),
                                            case([(vw_obyekbadan.TglData == None, 'Baru')]
                                                 ,
                                                 else_='Terdata'
                                                 ).label('Status'),
                                            vw_obyekbadan.Kecamatan) \
                .filter(
                vw_obyekbadan.TglHapus == None, vw_obyekbadan.SelfAssesment == 'Y', vw_obyekbadan.Insidentil == 'N'
            )

            # SEARCH_JENIS
            if args['search_jenis']:
                select_query = select_query.filter(
                    MsJenisPendapatan.JenisPendapatanID == args['search_jenis']
                )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_obyekbadan.NamaBadan.ilike(search),
                        vw_obyekbadan.ObyekBadanNo.ilike(search),
                        vw_obyekbadan.TglData.ilike(search)
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
            return success_reads_pagination(query_execute, result)
        except Exception as e:
            print(e)
            return failed_reads(result)


class PembayaranSPTPOmset(Resource):
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
            select_query = db.session.query(SetoranHist.UPTID, SetoranHist.MasaAwal,
                                            SetoranHist.MasaAkhir, SetoranHist.TglBayar,
                                            case([(SetoranHist.TglBayar == None, 'Terdata')]
                                                 ,
                                                 else_='SPTP'
                                                 ).label('Pembayaran'),
                                            SetoranHist.TarifPajak) \
                .join(SetoranHist, (SetoranHist.OPDID == SetoranHist.OPDID) &
                      (SetoranHist.MasaAwal == SetoranHist.MasaAwal) &
                      (SetoranHist.MasaAkhir == SetoranHist.MasaAkhir) &
                      (SetoranHist.UrutTgl == SetoranHist.UrutTgl), isouter=True) \
                .join(vw_obyekbadan, vw_obyekbadan.OPDID == SetoranHist.OPDID) \
                .filter(
                SetoranHist.OPDID == opdid
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
                        vw_obyekbadan.TglBayar.ilike(search)
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