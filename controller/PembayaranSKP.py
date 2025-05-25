from datetime import datetime, timedelta, date

import sqlalchemy
from flask_restful import Resource, reqparse
from sqlalchemy import case, func, text
from sqlalchemy import or_
from sqlalchemy.sql.elements import and_

from config.api_message import success_reads_pagination, failed_reads, success_reads, failed_create, success_create, \
    success_update, failed_update, success_delete, failed_delete
from config.database import db
from config.helper import logger
from controller.GeneralParameter import GeneralParameter
from controller.MsBendahara import MsBendahara
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsPegawai import MsPegawai
from controller.MsUPT import MsUPT
from controller.NomorKohir import NomorKohir
from controller.Pembayaran import Pembayaran
from controller.SetoranHist import SetoranHist
from controller.tblGroupUser import tblGroupUser
from controller.tblUser import tblUser
from controller.vw_obyekbadan import vw_obyekbadan
from controller.vw_pembayaran import vw_pembayaran
from controller.vw_penetapanomzet import vw_penetapanomzet
from controller.vw_penetapanreklame import vw_penetapanreklame


class PembayaranSKP(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):

        # PARSING PARAMETER DARI REQUEST
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('length', type=int)
        parser.add_argument('sort', type=str)
        parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
        parser.add_argument('search', type=str)
        parser.add_argument('kohirid', type=int)
        parser.add_argument('filter_jenis', type=str)
        parser.add_argument('kategori', type=str, choices=('true', 'false'), help='diisi dengan true atau false')
        parser.add_argument('nonwp', type=str, choices=('true', 'false'), help='diisi dengan true atau false')
        parser.add_argument('statusbayar', type=str)

        args = parser.parse_args()
        uid = kwargs['claim']["UID"]
        groupid = kwargs['claim']["GroupId"]

        # else:
        #     select_query = db.session.execute(
        #         f"SELECT mu.UPTID FROM MsUPT AS mu WHERE mu.KDUNIT IN(SELECT gp.ParamStrValue "
        #         f"FROM GeneralParameter AS gp WHERE gp.ParamID='satker_sipkd') AND RIGHT(mu.KodeUPT,3)='01.'")
        #     result = select_query.first()[0]
        #     uptid = result

        result = []
        try:
            subquery_saldo = db.session.query(
                Pembayaran.WPID,
                func.sum(Pembayaran.Saldo).label('Saldo')
            ).group_by(Pembayaran.WPID).subquery()

            select_query = db.session.query(Pembayaran.WPID,Pembayaran.OPDID, Pembayaran.OBN, Pembayaran.ObyekBadanNo,
                                            Pembayaran.NamaBadan, Pembayaran.TglJatuhTempo, Pembayaran.NoKohir,
                                            Pembayaran.KohirID, Pembayaran.SKPOwner, Pembayaran.UsahaBadan,
                                            Pembayaran.NoSSPD, Pembayaran.Insidentil, Pembayaran.UPT,
                                            Pembayaran.NamaBadan, Pembayaran.NamaPemilik, Pembayaran.AlamatBadan,
                                            Pembayaran.AlamatPemilik, Pembayaran.Pajak, Pembayaran.PajakOpsen,Pembayaran.JatuhTempo,
                                            Pembayaran.Denda, Pembayaran.SelfAssesment, Pembayaran.avatar,
                                            Pembayaran.JmlKurangBayar, Pembayaran.Kenaikan, Pembayaran.Transaksi,
                                            Pembayaran.strjml,Pembayaran.decjml,
                                            func.coalesce(
                                                db.session.query(subquery_saldo.c.Saldo).filter(
                                                    subquery_saldo.c.WPID == Pembayaran.WPID
                                                ),
                                                0
                                            ).label('Saldo'),
                                            Pembayaran.KodeRekening, Pembayaran.SetoranHistID,
                                            Pembayaran.NamaJenisPendapatan, Pembayaran.JenisPendapatanID,
                                            Pembayaran.UPTID, Pembayaran.JmlBayar, Pembayaran.JmlBayarOpsen,Pembayaran.TglBayar,
                                            Pembayaran.MasaAwal, Pembayaran.MasaAkhir, Pembayaran.IsPaid,
                                            Pembayaran.StatusBayar, Pembayaran.KodeStatus, Pembayaran.LabelStatus,Pembayaran.DateUpd,
                                            case( [(Pembayaran.SelfAssesment == 'Y', 'SPT')],
                                   else_='SKP'
                                   ).label( 'Kategori')

                                            )
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
                    Pembayaran.SKPOwner == uptid
                )

            if checkwp.IsWP == 1:
                ObyekBadanNo = kwargs['claim']["ObyekBadanNo"]
                select_query = select_query.filter(
                    Pembayaran.ObyekBadanNo == ObyekBadanNo
                )
            # if checkadmin.IsAdmin == 1:
            #     select_query = select_query

            # FILTER_ID
            if args['kohirid']:
                select_query = select_query.filter(
                    Pembayaran.KohirID == args['kohirid']
                )
            # FILTER_JENIS
            if args['filter_jenis']:
                select_query = select_query.filter(
                    Pembayaran.JenisPendapatanID == args['filter_jenis']
                )

            # # FILTER_JENIS
            # if args['bayar']:
            #     select_query = select_query.filter(
            #         Pembayaran.IsPaid == 'Y'
            #     )

            # kategori
            if args['kategori'] or args['kategori'] == "true":
                select_query = select_query.filter(Pembayaran.SelfAssesment == 'Y')
            else:
                select_query = select_query.filter(Pembayaran.SelfAssesment == 'N')

            # nonwp
            if args['nonwp'] or args['nonwp'] == "true":
                select_query = select_query.filter(Pembayaran.Insidentil == 'Y')
            else:
                select_query = select_query.filter(Pembayaran.Insidentil == 'N')

            # statusbayar
            if args['statusbayar'] == "1":
                select_query = select_query.filter(Pembayaran.StatusBayar == 'Lunas')
            elif args['statusbayar'] == "2":
                select_query = select_query.filter(Pembayaran.StatusBayar == 'Kode Bayar')
            elif args['statusbayar'] == "3":
                select_query = select_query.filter(Pembayaran.StatusBayar == '')
            elif args['statusbayar'] == "4":
                select_query = select_query.filter( Pembayaran.StatusBayar == 'Jatuh Tempo' )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])

                select_query = select_query.filter(
                    or_(Pembayaran.NamaBadan.ilike(search),
                        Pembayaran.ObyekBadanNo.ilike(search),
                        Pembayaran.JenisPendapatanID.ilike(search),
                        Pembayaran.NamaJenisPendapatan.ilike(search),
                        Pembayaran.KohirID.ilike(search),
                        Pembayaran.NoSSPD.ilike( search ),
                        )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(Pembayaran, args['sort']).desc()
                else:
                    sort = getattr(Pembayaran, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(Pembayaran.DateUpd.desc(),Pembayaran.TglPenetapan.desc())

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


class HitungDenda(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('KohirID', type=str)
        args = parser.parse_args()

        try:
            # uid = kwargs['claim']["UID"]
            # groupid = kwargs['claim']["GroupId"]
            # PegawaiID = kwargs['claim']["PegawaiID"]
            # uptid = ''
            # if PegawaiID:
            #     select_query_uptid = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
            #         tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
            #     result = select_query_uptid[0]
            #     uptid = result
            #     print(uptid)
            # FILTER_ID
            if args['KohirID']:
                args['KohirID']
            print( args['KohirID'])
            select_detail = Pembayaran.query.filter_by(
                KohirID=args['KohirID']
            ).first()
            # date_1 = ''
            # if select_detail.JatuhTempo != '':
            if select_detail.JatuhTempo.rstrip() == ('Jatuh Tempo'):
                date_1 = select_detail.TglJatuhTempo
                print(date_1)
                date_2 = datetime.now()
                print(date_2)

                diff = (date_2.date() - date_1.date()).days
                trfpajak = select_detail.Pajak

                if diff > 0:
                    if diff <= 30:
                        diff == 1
                    elif diff >= 40:
                        diff = (date_2.date().month - date_1.date().month)
                print(diff)

                query = db.session.query(GeneralParameter.ParamNumValue) \
                    .filter(GeneralParameter.ParamID == 'num_denda').first()
                result1 = []
                for row in query:
                    result1.append(row)
                decDenda = result1[0]

                denda = round(((float(decDenda) * float(diff)) * float(trfpajak)) / 100)
                print(denda)
            else:
                denda = select_detail.Denda
            return success_reads({'denda': denda})
        except Exception as e:
            logger.error(e)
            return failed_reads({})


class PembayaranSKP3(Resource):
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
                if key == 'Pajak' or key == 'JmlBayar' or key == 'JBayar' or key == 'JmlKurangBayar' or key == 'JKurang' \
                        or key == 'Denda' or key == 'JDenda' or key == 'Kenaikan' or key == 'JKenaikan' or key == 'HarusBayar' \
                        or key == 'JOA' or key == 'JBD' or key == 'JBPK':
                    d[key] = str(getattr(row, key))
                else:
                    d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


class PembayaranSKP4(Resource):
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
            f"s.SubKohir = '{kohirid}' AND OPDID IN (select distinct OPDID from MsObyekBadan ) UNION "
            f"SELECT NoUrut,s.TglBayar, (case when Transaksi='T' then "
            f"'Tunai' else 'Transfer' end) AS Transaksi, isnull(s.JmlBayar,0) AS JmlBayar, isnull(JmlBayarDenda,0) "
            f"AS JmlBayarDenda, NoSSPD, NamaPenyetor,s.NoKohir,isnull(right('0'+convert(varchar,datepart(day,TglNTPD)),2) "
            f"+ '/' + right('0'+convert(varchar,datepart(month,TglNTPD)),2) + '/' + right(convert(varchar,datepart(year,TglNTPD)),2) + NTB,'-') "
            f"AS NTPDNT FROM SetoranHist s LEFT JOIN vw_penetapanreklame r ON s.NoKohir = r.NoKohir AND s.SubKohir = r.KohirID "
            f"WHERE Jenis IS NOT NULL AND s.SubKohir = '{kohirid}' AND OPDID IN (select distinct OPDID "
            f"from MsObyekBadan) ORDER BY s.TglBayar DESC")
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


class PembayaranSKP5(Resource):
    def get(self, subkohir, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT * FROM SetoranHist WHERE subkohir = '{subkohir}'")
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


#################################################

class statuspembayaran(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):

        # PARSING PARAMETER DARI REQUEST
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('length', type=int)
        parser.add_argument('sort', type=str)
        parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
        parser.add_argument('search', type=str)
        parser.add_argument('kohirid', type=int)
        parser.add_argument('filter_jenis', type=str)
        parser.add_argument('statusbayar', type=str)

        args = parser.parse_args()

        result = []
        try:

            select_query = db.session.query(Pembayaran.ObyekBadanNo.label('npwpd'),
                                            Pembayaran.NamaBadan.label('namabadan'),
                                            Pembayaran.AlamatBadan.label('alamatbadan'),
                                            Pembayaran.TglJatuhTempo.label('tgljatuhtempo'),
                                            Pembayaran.KohirID.label('kohirid'),
                                            Pembayaran.NoSSPD.label('nosspd'),
                                            Pembayaran.UPT.label('satker'),
                                            Pembayaran.Pajak.label('pajak'),
                                            Pembayaran.Denda.label('denda'),
                                            Pembayaran.JmlKurangBayar.label('jmlkurangbayar'),
                                            Pembayaran.Kenaikan.label('kenaikan'),
                                            Pembayaran.NamaJenisPendapatan.label('jenispajak'),
                                            Pembayaran.JmlBayar.label('jmlbayar'),
                                            Pembayaran.TglBayar.label('tglbayar'),
                                            Pembayaran.MasaAwal.label('masaawal'),
                                            Pembayaran.MasaAkhir.label('masaakhir'),
                                            case( [
                                                (Pembayaran.StatusBayar == '', 'tagihan'),
                                                (Pembayaran.StatusBayar == 'Jatuh Tempo', 'tunggakan')
                                            ], else_=Pembayaran.StatusBayar
                                                  ).label( 'statusbayar' )
                                            )\
            .join(MsJenisPendapatan, Pembayaran.JenisPendapatanID == MsJenisPendapatan.JenisPendapatanID)\
            .filter(MsJenisPendapatan.SelfAssessment == 'Y', Pembayaran.Insidentil == 'N',
                    MsJenisPendapatan.ParentID <= 2, MsJenisPendapatan.ParentID != '')


            # FILTER_ID
            if args['kohirid']:
                select_query = select_query.filter(
                    Pembayaran.KohirID == args['kohirid']
                )
            # FILTER_JENIS
            if args['filter_jenis']:
                select_query = select_query.filter(
                    Pembayaran.JenisPendapatanID == args['filter_jenis']
                )


            # statusbayar
            if args['statusbayar'] == "1":
                select_query = select_query.filter(Pembayaran.StatusBayar == 'Lunas')
            elif args['statusbayar'] == "2":
                select_query = select_query.filter(Pembayaran.StatusBayar == 'Kode Bayar')
            elif args['statusbayar'] == "3":
                select_query = select_query.filter(Pembayaran.StatusBayar == '')

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])

                select_query = select_query.filter(
                    or_(Pembayaran.NamaBadan.ilike(search),
                        Pembayaran.ObyekBadanNo.ilike(search),
                        func.replace( func.replace( func.replace( Pembayaran.ObyekBadanNo,
                                                                  '.', '' ), '-', '' ), ' ', '' ).ilike( search ),
                        Pembayaran.JenisPendapatanID.ilike(search),
                        Pembayaran.NamaJenisPendapatan.ilike(search),
                        Pembayaran.KohirID.ilike(search),
                        )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(Pembayaran, args['sort']).desc()
                else:
                    sort = getattr(Pembayaran, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(Pembayaran.TglPenetapan.desc())

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 5
            lengthLimit = length if length < 21 else 20
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
##############################################################################


class AddPembayaranSKP(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        # parser.add_argument('NoKohir', type=str)
        # parser.add_argument('NoUrut', type=str)
        # parser.add_argument('SubKohir', type=str)
        # parser.add_argument('TglBayar', type=str)
        parser.add_argument('JmlBayar', type=str)
        parser.add_argument('JmlBayarOpsen', type=str)
        parser.add_argument('JmlBayarDenda', type=str)
        # parser.add_argument('Transaksi', type=str)
        # parser.add_argument('NoSSPD', type=str)
        # parser.add_argument('NamaPenyetor', type=str)
        # parser.add_argument('STS', type=str)
        # parser.add_argument('STSDenda', type=str)
        # parser.add_argument('Keterangan', type=str)
        # parser.add_argument('NTPD', type=str)
        # parser.add_argument('NTB', type=str)
        # parser.add_argument('TglNTPD', type=str)
        # parser.add_argument('BendID', type=str)
        parser.add_argument('KodeStatus', type=str)
        # parser.add_argument('UserUpd', type=str)
        # parser.add_argument('DateUpd', type=str)

        parser.add_argument('KohirID', type=str)
        # parser.add_argument('Penagih', type=str)
        # parser.add_argument('SelfAssesment', type=str)
        # parser.add_argument('JmlKurangBayar', type=str)
        # parser.add_argument('OPDID', type=str)
        # parser.add_argument('TglJatuhTempo', type=str)
        # parser.add_argument( 'StatusBayar', type=str )
        # parser.add_argument( 'IsPaid', type=str )
        # parser.add_argument( 'LabelStatus', type=str )

        try:
            uid = kwargs['claim']["UID"]
            groupid = kwargs['claim']["GroupId"]
            PegawaiID = ''
            args = parser.parse_args()
            select_data = vw_pembayaran.query.filter_by(
                KohirID=args['KohirID']
            ).first()

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
                # select_query = select_data.filter(
                #     Pembayaran.SKPOwner == uptid
                # )

            if checkadmin.IsAdmin == 1 or checkwp.IsWP == 1:
                # ObyekBadanNo = kwargs['claim']["ObyekBadanNo"]
                select_query_uptid = db.session.query(vw_pembayaran.UPTID).filter(
                    vw_pembayaran.KohirID == args['KohirID']).first()
                result = select_query_uptid[0]
                uptid = result

            # PegawaiID = kwargs['claim']["PegawaiID"]
            # if PegawaiID:
            #     select_query = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
            #         tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
            #     result = select_query[0]
            #     uptid = result
            # else:
            #     select_query = db.session.execute(
            #         f"SELECT mu.UPTID FROM MsUPT AS mu WHERE mu.KDUNIT IN(SELECT gp.ParamStrValue "
            #         f"FROM GeneralParameter AS gp WHERE gp.ParamID='satker_sipkd') AND RIGHT(mu.KodeUPT,3)='01.'")
            #     result = select_query.first()[0]
            #     uptid = result

            if PegawaiID:
                select_query = db.session.query(MsBendahara.BendaharaID) \
                    .join(MsPegawai, MsBendahara.PegawaiID == MsPegawai.PegawaiID) \
                    .join(MsUPT, MsPegawai.UPTID == MsUPT.UPTID) \
                    .filter(
                    MsPegawai.UPTID == uptid).first()
                result = select_query[0]
                bendaharaid = result
                print(bendaharaid)
            else:
                select_query = db.session.execute(
                    f"SELECT TOP 1 mb.BendaharaID FROM MsBendahara AS mb WHERE mb.PegawaiID in(SELECT mp.PegawaiID "
                    f"FROM MsPegawai mp WHERE mp.UPTID IN(SELECT mu.UPTID FROM MsUPT mu WHERE mu.KDUNIT "
                    f"IN(SELECT gp.ParamStrValue FROM GeneralParameter AS gp WHERE gp.ParamID='satker_sipkd') "
                    f"AND RIGHT(mu.KodeUPT,3)='05.'))")
                result = select_query.first()[0]
                bendaharaid = result

            result1 = db.session.execute(
                f"exec [SP_SSPD]")
            result2 = []
            for row in result1:
                result2.append(row)
            nosspd = result2[0][0]

            select_query = db.session.execute(
                f"SELECT DISTINCT ISNULL(MAX(NoUrut),0) + 1 FROM SetoranHist WHERE SubKohir = '{select_data.KohirID}'")
            result3 = select_query.first()[0]
            nourut = result3

            # select_detail = Pembayaran.query.filter_by(
            #     KohirID=args['KohirID']
            # ).first()
            # if select_detail.JatuhTempo.rstrip() == ('Jatuh Tempo'):
            #     date_1 = select_detail.TglJatuhTempo
            #     date_2 = datetime.now()
            #     diff = (date_2.date() - date_1.date()).days
            #     trfpajak = select_detail.Pajak
            #
            #     if diff > 0:
            #         if diff <= 30:
            #             diff == 1
            #         else:
            #             diff = (date_2.date().month - date_1.date().month)
            #     print(diff)
            #
            #     query = db.session.query(GeneralParameter.ParamNumValue) \
            #         .filter(GeneralParameter.ParamID == 'num_denda').first()
            #     result1 = []
            #     for row in query:
            #         result1.append(row)
            #     decDenda = result1[0] / 100
            #
            #     denda = round(((float(decDenda) * float(diff)) * float(trfpajak)) / 100)
            #     print(denda)
            # else:
            #     denda = select_detail.Denda

            jmlbayar = float(args['JmlBayar'] or 0)
            jmlbayaropsen = float(args['JmlBayarOpsen'] or 0)
            jmlbayardenda = float(args['JmlBayarDenda'] or 0)  # if args['JmlBayarDenda'] else denda or 0
            totalbayar = jmlbayar + jmlbayardenda

            transaksi = 'B' if str.rstrip(args['KodeStatus']) == '16' else 'T'

            add_record = SetoranHist(
                NoKohir=select_data.NoKohir,
                NoUrut=nourut,
                SubKohir=select_data.KohirID,
                TglBayar=datetime.now(),
                JmlBayar=jmlbayar,
                JmlBayarOpsen=jmlbayaropsen if args['JmlBayarOpsen'] else 0,
                JmlBayarDenda=jmlbayardenda,
                Transaksi=transaksi,
                NoSSPD=nosspd,
                NamaPenyetor=select_data.NamaBadan,
                Keterangan=select_data.NamaJenisPendapatan,
                BendID=bendaharaid,
                KodeStatus=args['KodeStatus'],
                UserUpd=uid,
                DateUpd=datetime.now()
            )
            db.session.add(add_record)
            db.session.commit()

            setoranhistid = add_record.SetoranHistID
            nosspd = add_record.NoSSPD

            if add_record.JmlBayar > 0:
                select_data2 = vw_pembayaran.query.filter_by(
                    SetoranHistID=add_record.SetoranHistID
                ).first()
                select_status = db.session.execute(
                    f"SELECT DISTINCT StatusBayar FROM vw_pembayaran WHERE NoKohir='{select_data2.NoKohir}' AND OPDID='{select_data2.OPDID}' "
                )
                result4 = []
                for row in select_status:
                    result4.append(row)
                statusbayar = result4[0][0]
                if select_data.OmzetBase == 'Y':
                    db.session.execute(
                        f"UPDATE PenetapanByOmzet SET JmlBayar='{totalbayar}',JmlBayarOpsen='{jmlbayaropsen}',IsPaid='Y',TglBayar={datetime.now().strftime('%Y-%m-%d')},"
                        f"Denda='{jmlbayardenda}',"
                        f"JmlKurangBayar='{select_data.JmlKurangBayar or 0}', UserUpd='{uid}',DateUpd={datetime.now().strftime('%Y-%m-%d')} "
                        f"WHERE NoKohir='{select_data.NoKohir}' AND OPDID='{select_data.OPDID}' "
                    )
                    db.session.execute(
                        f"exec [SP_Pembayaran] '{select_data2.SetoranHistID}',1")
                    # db.session.execute(
                    #     f"UPDATE Pembayaran SET JmlBayar='{totalbayar}',IsPaid='Y',TglBayar={datetime.now().strftime('%Y-%m-%d')},"
                    #     f"Denda='{jmlbayardenda}', JmlKurangBayar='{select_data2.JmlKurangBayar or 0}', DateUpd={datetime.now().strftime('%Y-%m-%d')}, "
                    #     f"SetoranHistID='{setoranhistid}',NoSSPD='{nosspd}',StatusBayar='{statusbayar}', "
                    #     f"KodeStatus= '{add_record.KodeStatus}', LabelStatus= '{select_data2.LabelStatus}' "
                    #     f"WHERE NoKohir='{select_data2.NoKohir}' AND OPDID='{select_data2.OPDID}' "
                    # )
                else:
                    db.session.execute(
                        f"UPDATE PenetapanReklameHdr SET JmlBayar='{totalbayar}',IsPaid='Y',TglBayar={datetime.now().strftime('%Y-%m-%d')},"
                        f"Denda='{jmlbayardenda}',"
                        f"JmlKurangBayar='{select_data.JmlKurangBayar or 0}', UserUpd='{uid}',DateUpd={datetime.now().strftime('%Y-%m-%d')} "
                        f"WHERE NoKohir='{select_data.NoKohir}' AND OPDID='{select_data.OPDID}' "
                    )

                    db.session.execute(
                        f"exec [SP_Pembayaran] '{select_data2.SetoranHistID}',1")
                    db.session.commit()
                    db.session.execute(
                        f"exec [dbo].[Update_PendataanByOmzetDtl] @NoKohir='{select_data.NoKohir}'")
                    # db.session.execute(
                    #     f"UPDATE Pembayaran SET JmlBayar='{totalbayar}',IsPaid='Y',TglBayar={datetime.now().strftime('%Y-%m-%d')},"
                    #     f"Denda='{jmlbayardenda}', JmlKurangBayar='{select_data.JmlKurangBayar or 0}', DateUpd={datetime.now().strftime('%Y-%m-%d')}, "
                    #     f"SetoranHistID='{setoranhistid}',NoSSPD='{nosspd}',StatusBayar='{select_data2.StatusBayar}', "
                    #     f"KodeStatus= '16', LabelStatus= 'Penerimaan Rek BUD' "
                    #     f"WHERE NoKohir='{select_data2.NoKohir}' AND OPDID='{select_data2.OPDID}' "
                    # )
                db.session.commit()
            return success_create({'SetoranHistID': add_record.SetoranHistID,
                                   'SubKohir': add_record.SubKohir,
                                   'NoSSPD': add_record.NoSSPD,
                                   'Transaksi': add_record.Transaksi,
                                   'TglBayar': add_record.TglBayar,
                                   'TotalBayar': totalbayar})

            # if args['JmlBayar'] > 0:
            #     if select_data.OmzetBase == 'Y':
            #         db.session.execute(
            #             f"UPDATE PenetapanByOmzet SET JmlBayar='{totalbayar}',IsPaid='Y',TglBayar='{args['TglBayar']}',"
            #             f"Denda='{jmlbayardenda}',"
            #             f"JmlKurangBayar='{args['JmlKurangBayar']}', UserUpd='{uid}',DateUpd=getdate() "
            #             f"WHERE NoKohir='{args['NoKohir']}' AND OPDID='{args['OPDID']}' "
            #         )
            #         db.session.execute(
            #             f"UPDATE Pembayaran SET JmlBayar='{totalbayar}',IsPaid='Y',TglBayar='{args['TglBayar']}',"
            #             f"Denda='{jmlbayardenda}', JmlKurangBayar='{args['JmlKurangBayar']}', DateUpd=getdate(), "
            #             f"SetoranHistID='{setoranhistid}',NoSSPD='{nosspd}',Statusbayar={statusbayar}, "
            #             f"KodeStatus= '{args['KodeStatus']}', LabelStatus= '{args['LabelStatus']}' "
            #             f"WHERE NoKohir='{args['NoKohir']}' AND OPDID='{args['OPDID']}' "
            #         )
            #     else:
            #         db.session.execute(
            #             f"UPDATE PenetapanReklameHdr SET JmlBayar='{totalbayar}',IsPaid='Y',TglBayar='{args['TglBayar']}',"
            #             f"Denda='{jmlbayardenda}',"
            #             f"JmlKurangBayar='{args['JmlKurangBayar']}', UserUpd='{uid}',DateUpd=getdate() "
            #             f"WHERE NoKohir='{args['NoKohir']}' AND OPDID='{args['OPDID']}' "
            #         )
            #         db.session.execute(
            #             f"UPDATE Pembayaran SET JmlBayar='{totalbayar}',IsPaid='Y',TglBayar='{args['TglBayar']}',"
            #             f"Denda='{jmlbayardenda}', JmlKurangBayar='{args['JmlKurangBayar']}', DateUpd=getdate(), "
            #             f"SetoranHistID='{setoranhistid}',NoSSPD='{nosspd}',Statusbayar={statusbayar},"
            #             f"KodeStatus= '{args['KodeStatus']}', LabelStatus= '{args['LabelStatus']}' "
            #             f"WHERE NoKohir='{args['NoKohir']}' AND OPDID='{args['OPDID']}' "
            #         )
            #     db.session.commit()
            # return success_create({'SetoranHistID': add_record.SetoranHistID,
            #                        'SubKohir': add_record.SubKohir,
            #                        'NoSSPD': add_record.NoSSPD,
            #                        'Transaksi': add_record.Transaksi,
            #                        'TglBayar': add_record.TglBayar,
            #                        'TotalBayar':totalbayar})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_create({})
########################################################################################

class genkodebayar(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('kohirid', type=str)

        try:
            uid = kwargs['claim']["UID"]
            groupid = kwargs['claim']["GroupId"]
            PegawaiID = ''
            args = parser.parse_args()
            select_data = vw_pembayaran.query.filter_by(
                KohirID=args['kohirid']
            ).first()

            checkadmin = tblGroupUser.query.filter_by(
                GroupId=groupid
            ).first()

            checkwp = tblGroupUser.query.filter_by(
                GroupId=groupid
            ).first()

            checkmpos = tblGroupUser.query.filter_by(
                GroupId=groupid
            ).first()

            if checkadmin.IsAdmin != 1 and checkwp.IsWP != 1 and checkmpos.code_group != 'MPOS':
                PegawaiID = kwargs['claim']["PegawaiID"]
                uptid = ''
                if PegawaiID:
                    select_query_uptid = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
                        tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
                    result = select_query_uptid[0]
                    uptid = result

            if checkadmin.IsAdmin == 1 or checkwp.IsWP == 1 or checkmpos.code_group != 'MPOS':
                select_query_uptid = db.session.query(vw_pembayaran.UPTID).filter(
                    vw_pembayaran.KohirID == args['kohirid']).first()
                result = select_query_uptid[0]
                uptid = result


            if PegawaiID:
                select_query = db.session.query(MsBendahara.BendaharaID) \
                    .join(MsPegawai, MsBendahara.PegawaiID == MsPegawai.PegawaiID) \
                    .join(MsUPT, MsPegawai.UPTID == MsUPT.UPTID) \
                    .filter(
                    MsPegawai.UPTID == uptid).first()
                result = select_query[0]
                bendaharaid = result
                print(bendaharaid)
            else:
                select_query = db.session.execute(
                    f"SELECT TOP 1 mb.BendaharaID FROM MsBendahara AS mb WHERE mb.PegawaiID in(SELECT mp.PegawaiID "
                    f"FROM MsPegawai mp WHERE mp.UPTID IN(SELECT mu.UPTID FROM MsUPT mu WHERE mu.KDUNIT "
                    f"IN(SELECT gp.ParamStrValue FROM GeneralParameter AS gp WHERE gp.ParamID='satker_sipkd') "
                    f"AND RIGHT(mu.KodeUPT,3)='05.'))")
                result = select_query.first()[0]
                bendaharaid = result

            result1 = db.session.execute(
                f"exec [SP_SSPD]")
            result2 = []
            for row in result1:
                result2.append(row)
            nosspd = result2[0][0]

            select_query = db.session.execute(
                f"SELECT DISTINCT ISNULL(MAX(NoUrut),0) + 1 FROM SetoranHist WHERE SubKohir = '{select_data.KohirID}'")
            result3 = select_query.first()[0]
            nourut = result3

            # jmlbayar = float(args['JmlBayar'] or 0)
            pokok = float(select_data.Pajak)

            ### Hitung Denda###
            if args['kohirid']:
                args['kohirid']


            if select_data.JatuhTempo.rstrip() == ('Jatuh Tempo'):
                date_1 = select_data.TglJatuhTempo
                date_2 = datetime.now()

                diff = (date_2.date() - date_1.date()).days
                trfpajak = select_data.Pajak

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
                decDenda = result1[0]

                denda = round(((float(decDenda) * float(diff)) * float(trfpajak)) / 100)
                print(denda)
            else:
                denda = select_data.Denda

            # jmlbayardenda = float(args['JmlBayarDenda'] or 0)  # if args['JmlBayarDenda'] else denda or 0
            jmlkurangbayar = float(select_data.JmlKurangBayar or 0)
            jmlbayardenda = float(denda or 0)
            totalbayar = pokok

            # transaksi = 'B' if args['KodeStatus'] == '16' else 'T'

            # add_record = SetoranHist(
            #     NoKohir=select_data.NoKohir,
            #     NoUrut=nourut,
            #     SubKohir=select_data.KohirID,
            #     TglBayar=datetime.now().strftime('%Y-%m-%d'),
            #     JmlBayar=totalbayar,
            #     JmlBayarDenda=jmlbayardenda,
            #     Transaksi='B',
            #     NoSSPD=nosspd,
            #     NamaPenyetor=select_data.NamaBadan,
            #     Keterangan=select_data.NamaJenisPendapatan,
            #     BendID=bendaharaid,
            #     KodeStatus='16',
            #     UserUpd=uid,
            #     DateUpd=datetime.now()
            # )
            # db.session.add(add_record)
            # db.session.commit()

            NoKohir=select_data.NoKohir
            NoUrut=nourut
            SubKohir=select_data.KohirID
            TglBayar=datetime.now().strftime('%Y-%m-%d')
            JmlBayar=totalbayar
            JmlBayarDenda=jmlbayardenda
            Transaksi='B'
            NoSSPD=nosspd
            NamaPenyetor=select_data.NamaBadan
            Keterangan=select_data.NamaJenisPendapatan
            BendID=bendaharaid
            KodeStatus='16'
            UserUpd=uid
            DateUpd=datetime.now().strftime("%Y-%m-%d")

            add_record = db.session.execute(
                f"INSERT INTO [dbo].[SetoranHist] "
                f"([NoKohir] ,[NoUrut],[SubKohir],[TglBayar],[JmlBayar],[JmlBayarDenda],[Transaksi],[NoSSPD],[NamaPenyetor],"
                f"[STS],[STSDenda],[Keterangan],[UserUpd],[DateUpd],[NTPD],[NTB],[TglNTPD],[BendID],[KodeStatus]) "
                f"SELECT "
                f"NoKohir='{NoKohir}',NoUrut={NoUrut},SubKohir='{SubKohir}',TglBayar='{TglBayar}',JmlBayar='{JmlBayar}',"
                f"JmlBayarDenda='{JmlBayarDenda}',Transaksi='{Transaksi}',NoSSPD='{NoSSPD}',NamaPenyetor='{NamaPenyetor}'"
                f",STS=NULL,STSDenda=NULL,Keterangan='{Keterangan}',UserUpd='{UserUpd}',DateUpd='{DateUpd}',NTPD=NULL,"
                f"NTB=NULL,TglNTPD=NULL,BendID='{BendID}',KodeStatus='{KodeStatus}' "
            )
            db.session.commit()

            # setoranhistid = add_record.SetoranHistID
            # nosspd = add_record.NoSSPD

            if add_record:
                select_data2 = vw_pembayaran.query.filter_by(
                    NoSSPD=NoSSPD
                ).first()
                select_status = db.session.execute(
                    f"SELECT DISTINCT StatusBayar FROM vw_pembayaran WHERE NoKohir='{select_data2.NoKohir}' "
                    f"AND OPDID='{select_data2.OPDID}' "
                )
                result4 = []
                for row in select_status:
                    result4.append(row)
                statusbayar = result4[0][0]
                if select_data.OmzetBase == 'Y':
                    db.session.execute(
                        f"UPDATE PenetapanByOmzet SET JmlBayar='{totalbayar}',IsPaid='Y',TglBayar={datetime.now().strftime('%Y-%m-%d')},"
                        f"Denda='{jmlbayardenda}',"
                        f"JmlKurangBayar='{select_data.JmlKurangBayar or 0}', UserUpd='{uid}',DateUpd={datetime.now().strftime('%Y-%m-%d')} "
                        f"WHERE NoKohir='{select_data.NoKohir}' AND OPDID='{select_data.OPDID}' "
                    )
                    db.session.execute(
                        f"exec [SP_Pembayaran] '{select_data2.SetoranHistID}',1")
                else:
                    db.session.execute(
                        f"UPDATE PenetapanReklameHdr SET JmlBayar='{totalbayar}',IsPaid='Y',TglBayar={datetime.now().strftime('%Y-%m-%d')},"
                        f"Denda='{jmlbayardenda}',"
                        f"JmlKurangBayar='{select_data.JmlKurangBayar or 0}', UserUpd='{uid}',DateUpd={datetime.now().strftime('%Y-%m-%d')} "
                        f"WHERE NoKohir='{select_data.NoKohir}' AND OPDID='{select_data.OPDID}' "
                    )
                    db.session.execute(
                        f"exec [SP_Pembayaran] '{select_data2.SetoranHistID}',1")

                db.session.commit()
            return success_create({
                                   'kohirid': SubKohir,
                                   'kodebayar': NoSSPD,
                                   'tglbayar': TglBayar,
                                   'jmlbayar': totalbayar})


        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_create({})

# =======================================================================================

class AddPembayaranSKPWPO(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()

        parser.add_argument('KohirID', type=str)
        groupid = kwargs['claim']["GroupId"]
        try:
            bendaharaid = None
            args = parser.parse_args()
            select_data = vw_pembayaran.query.filter_by(
                KohirID=args['KohirID']
            ).first()

            # checkadmin = tblGroupUser.query.filter_by(
            #     GroupId=groupid
            # ).first()
            #
            # checkwp = tblGroupUser.query.filter_by(
            #     GroupId=groupid
            # ).first()
            #
            # if checkadmin.IsAdmin != 1 and checkwp.IsWP != 1:
            #     PegawaiID = kwargs['claim']["PegawaiID"]
            #     uptid = ''
            #     if PegawaiID:
            #         select_uptid = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
            #             tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
            #         result = select_uptid[0]
            #         uptid = result
            #         print(uptid)
            #
            #         select_bendahara = db.session.query(MsBendahara.BendaharaID).filter(
            #             MsBendahara.PegawaiID == PegawaiID).first()
            #         result = select_bendahara[0]
            #         bendaharaid = result
            #
            # if checkwp.IsWP == 1:
            #     # ObyekBadanNo = kwargs['claim']["ObyekBadanNo"]
            #     select_bendahara = db.session.execute(
            #         f"SELECT TOP 1 mb.BendaharaID FROM MsBendahara AS mb WHERE mb.PegawaiID in(SELECT mp.PegawaiID "
            #         f"FROM MsPegawai mp WHERE mp.UPTID IN(SELECT mu.UPTID FROM MsUPT mu WHERE mu.KDUNIT "
            #         f"IN(SELECT gp.ParamStrValue FROM GeneralParameter AS gp WHERE gp.ParamID='satker_sipkd') "
            #         f"AND RIGHT(mu.KodeUPT,3)='01.'))")
            #     result = select_bendahara.first()[0]
            #     bendaharaid = result

            PegawaiID = kwargs['claim']["PegawaiID"] if "PegawaiID" in kwargs['claim'] else None
            uptid = ''
            if PegawaiID:
                select_uptid = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
                    tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
                result = select_uptid[0]
                uptid = result
                # print(uptid)

                select_bendahara = db.session.query(MsBendahara.BendaharaID).filter(
                    MsBendahara.PegawaiID == PegawaiID).first()
                result = select_bendahara[0]
                bendaharaid = result
            else:
                select_bendahara = db.session.execute(
                    f"SELECT TOP 1 mb.BendaharaID FROM MsBendahara AS mb WHERE mb.PegawaiID in(SELECT mp.PegawaiID "
                    f"FROM MsPegawai mp WHERE mp.UPTID IN(SELECT mu.UPTID FROM MsUPT mu WHERE mu.KDUNIT "
                    f"IN(SELECT gp.ParamStrValue FROM GeneralParameter AS gp WHERE gp.ParamID='satker_sipkd') "
                    f"AND RIGHT(mu.KodeUPT,3)='01.'))")
                result = select_bendahara.first()[0]
                bendaharaid = result

            uid = kwargs['claim']["UID"]

            result1 = db.session.execute(
                f"exec [SP_SSPD]")
            result2 = []
            for row in result1:
                result2.append(row)
            nosspd = result2[0][0]

            select_query = db.session.execute(
                f"SELECT DISTINCT ISNULL(MAX(NoUrut),0) + 1 FROM SetoranHist WHERE SubKohir = '{select_data.KohirID}'")
            result3 = select_query.first()[0]
            nourut = result3

            # if args['KohirID']:
            #     args['KohirID']

            select_detail = Pembayaran.query.filter_by(
                KohirID=args['KohirID']
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
            else:
                denda = select_detail.Denda

            jmlbayar = float(select_data.Pajak or 0)
            jmlbayardenda = denda or 0
            totalbayar = jmlbayar + jmlbayardenda

            add_record = SetoranHist(
                NoKohir=select_data.NoKohir,
                NoUrut=nourut,
                SubKohir=select_data.KohirID,
                TglBayar=datetime.now(),
                JmlBayar=jmlbayar,
                JmlBayarDenda=jmlbayardenda,
                Transaksi='B',
                NoSSPD=nosspd,
                NamaPenyetor=select_data.NamaBadan,
                Keterangan=select_data.NamaJenisPendapatan,
                BendID=bendaharaid,
                KodeStatus='16',
                UserUpd=uid,
                DateUpd=datetime.now()
            )
            db.session.add(add_record)
            db.session.commit()

            setoranhistid = add_record.SetoranHistID
            nosspd = add_record.NoSSPD

            select_status = db.session.execute(
                f"SELECT DISTINCT StatusBayar FROM vw_pembayaran WHERE NoKohir='{select_data.NoKohir}' "
                f"AND OPDID='{select_data.OPDID}' AND kOHIRid='{select_data.KohirID}'"
            )
            result4 = []
            for row in select_status:
                result4.append(row)
            statusbayar = result4[0][0]

            if add_record.JmlBayar > 0:
                select_data2 = vw_pembayaran.query.filter_by(
                    KohirID=add_record.SubKohir
                ).first()
                if select_data.OmzetBase == 'Y':

                    db.session.execute(
                        f"UPDATE PenetapanByOmzet SET JmlBayar='{totalbayar}',IsPaid='Y',TglBayar={datetime.now().strftime('%Y-%m-%d')},"
                        f"Denda='{jmlbayardenda}',"
                        f"JmlKurangBayar='{select_data.JmlKurangBayar or 0}', UserUpd='{uid}',DateUpd={datetime.now().strftime('%Y-%m-%d')} "
                        f"WHERE NoKohir='{select_data.NoKohir}' AND OPDID='{select_data.OPDID}' "
                    )
                    # db.session.execute(
                    #     f"UPDATE Pembayaran SET JmlBayar='{totalbayar}',IsPaid='Y',TglBayar={datetime.now().strftime('%Y-%m-%d')},"
                    #     f"Denda='{jmlbayardenda}', JmlKurangBayar='{select_data.JmlKurangBayar or 0}', DateUpd={datetime.now().strftime('%Y-%m-%d')}, "
                    #     f"SetoranHistID='{setoranhistid}',NoSSPD='{nosspd}',StatusBayar='{select_data2.StatusBayar}', "
                    #     f"KodeStatus= '16', LabelStatus= 'Penerimaan Rek BUD' "
                    #     f"WHERE NoKohir='{select_data2.NoKohir}' AND OPDID='{select_data2.OPDID}' "
                    # )
                    db.session.execute(
                        f"exec [SP_Pembayaran] '{select_data2.SetoranHistID}',1")
                else:
                    db.session.execute(
                        f"UPDATE PenetapanReklameHdr SET JmlBayar='{totalbayar}',IsPaid='Y',TglBayar={datetime.now().strftime('%Y-%m-%d')},"
                        f"Denda='{jmlbayardenda}',"
                        f"JmlKurangBayar='{select_data.JmlKurangBayar or 0}', UserUpd='{uid}',DateUpd={datetime.now().strftime('%Y-%m-%d')} "
                        f"WHERE NoKohir='{select_data.NoKohir}' AND OPDID='{select_data.OPDID}' "
                    )
                    db.session.execute(
                        f"exec [SP_Pembayaran] '{select_data2.SetoranHistID}',1")
                    # db.session.execute(
                    #     f"UPDATE Pembayaran SET JmlBayar='{totalbayar}',IsPaid='Y',TglBayar={datetime.now().strftime('%Y-%m-%d')},"
                    #     f"Denda='{jmlbayardenda}', JmlKurangBayar='{select_data.JmlKurangBayar or 0}', DateUpd={datetime.now().strftime('%Y-%m-%d')}, "
                    #     f"SetoranHistID='{setoranhistid}',NoSSPD='{nosspd}',StatusBayar='{select_data2.StatusBayar}', "
                    #     f"KodeStatus= '16', LabelStatus= 'Penerimaan Rek BUD' "
                    #     f"WHERE NoKohir='{select_data2.NoKohir}' AND OPDID='{select_data2.OPDID}' "
                    # )
                db.session.commit()
            return success_create({'SetoranHistID': add_record.SetoranHistID,
                                   'SubKohir': add_record.SubKohir,
                                   'NoSSPD': add_record.NoSSPD,
                                   'Transaksi': add_record.Transaksi,
                                   'TglBayar': add_record.TglBayar,
                                   'TotalBayar': totalbayar})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_create({})


class UpdatePembayaranSKP(Resource):
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


class DeletePembayaranSKP(Resource):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}

    def delete(self, id, *args, **kwargs):
        uid = kwargs['claim']["UID"]
        parser = reqparse.RequestParser()
        parser.add_argument('NoKohir', type=str)
        parser.add_argument('KohirID', type=str)
        parser.add_argument('SelfAssesment', type=str)
        parser.add_argument('OPDID', type=str)
        args = parser.parse_args()
        try:
            delete_record = SetoranHist.query.filter_by(SetoranHistID=id)
            delete_detail = delete_record.filter_by(SetoranHistID=id).first()
            # if delete_detail.STS and delete_detail.STSDenda == None:

            setoranhistid = delete_detail.SetoranHistID
            delete_data = Pembayaran.query.filter_by(SetoranHistID=setoranhistid).first()

            if delete_data and not delete_data.STS:
                if delete_data.OmzetBase == 'Y':
                    db.session.execute(
                        text("""
                            UPDATE PenetapanByOmzet 
                            SET JmlBayar = NULL, IsPaid = 'N', TglBayar = NULL,
                                JmlKurangBayar = NULL, Denda = NULL, 
                                UserUpd = :uid, DateUpd = getdate()
                            WHERE NoKohir = :nokohir AND OPDID = :opdid
                        """),
                        {"uid": uid, "nokohir": delete_data.NoKohir, "opdid": delete_data.OPDID}
                    )
                else:
                    db.session.execute(
                        text("""
                            UPDATE PenetapanReklameHdr 
                            SET JmlBayar = NULL, IsPaid = 'N', TglBayar = NULL,
                                JmlKurangBayar = NULL, Denda = NULL, 
                                UserUpd = :uid, DateUpd = getdate()
                            WHERE NoKohir = :nokohir AND OPDID = :opdid
                        """),
                        {"uid": uid, "nokohir": delete_data.NoKohir, "opdid": delete_data.OPDID}
                    )

                # Bagian ini identik untuk OmzetBase dan bukan
                db.session.execute(
                    text("""
                        UPDATE p SET 
                            p.JmlBayar = vp.JmlBayar, p.IsPaid = vp.IsPaid, p.TglBayar = vp.TglBayar,
                            p.Denda = vp.Denda, p.JmlKurangBayar = vp.JmlKurangBayar, p.DateUpd = vp.DateUpd,
                            p.SetoranHistID = vp.SetoranHistID, p.NoSSPD = vp.NoSSPD,
                            p.StatusBayar = vp.StatusBayar, p.KodeStatus = vp.KodeStatus,
                            p.LabelStatus = vp.KodeStatus, p.JatuhTempo = vp.JatuhTempo
                        FROM Pembayaran AS p
                        LEFT JOIN vw_pembayaran AS vp 
                            ON vp.KohirID = p.KohirID AND vp.NoKohir = p.NoKohir
                        WHERE p.NoKohir = :nokohir AND p.OPDID = :opdid
                    """),
                    {"nokohir": delete_data.NoKohir, "opdid": delete_data.OPDID}
                )

                # Jalankan prosedur jika perlu
                db.session.execute(text("EXEC INSERT_PEMBAYARAN"))

                # Asumsikan delete_data adalah objek ORM
                db.session.delete(delete_data)

                db.session.commit()
                return success_delete({})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_delete({})

#######################################################################
#######################################################################