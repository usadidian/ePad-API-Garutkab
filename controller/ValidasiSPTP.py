from datetime import datetime

import sqlalchemy
from flask_restful import Resource, reqparse
from sqlalchemy import case
from sqlalchemy import or_
from config.api_message import success_reads_pagination, failed_reads, success_reads, failed_create, success_create, \
    success_update, failed_update, success_delete, failed_delete
from config.database import db
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsPegawai import MsPegawai
from controller.NomorKohir import NomorKohir
from controller.PendataanByOmzetDtl import PendataanByOmzetDtl
from controller.PenetapanByOmzet import PenetapanByOmzet
from controller.tblUser import tblUser
from controller.vw_obyekbadan import vw_obyekbadan


class ValidasiSPTP2(Resource):
    def get(self, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT OBN,SPT,o.OPDID,ObyekBadanNo,cast(o.TarifPajak as varchar) AS Pajak,o.TglPendataan,NamaJenisPendapatan AS Jenis,"
            f"NamaBadan,o.MasaAwal, o.MasaAkhir FROM ((PendataanByOmzet o LEFT JOIN vw_obyekbadan v ON "
            f"o.OPDID = v.OPDID) LEFT JOIN PenetapanByOmzet pbo ON o.OPDID = pbo.OPDID "
            f"AND o.MasaAwal = pbo.MasaAwal AND o.MasaAkhir = pbo.MasaAkhir AND o.UrutTgl = pbo.UrutTgl) "
            f"WHERE  SelfAssesment = 'Y' AND o.[Status] = '1' AND TglPenetapan IS NULL AND TglHapus IS NULL ORDER BY SPT"
        )
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


class ValidasiSPTP3(Resource):
    def get(self, pendataanid, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT DISTINCT datediff(day,MasaAwal,MasaAkhir)+1 AS hitper, o.OPDID,ObyekBadanNo,NamaBadan,"
            f"NamaPemilik,AlamatBadan,Kota,Kecamatan, Kelurahan,v.KodeRekening,KodePos,v.NamaJenisPendapatan AS Sub,"
            f"UsahaBadan,cast(JmlOmzetAwal as varchar),cast(TarifPajak as varchar),MasaAwal,MasaAkhir,o.[Status],o.TglPendataan, o.SPT,v.WPID,"
            f"isnull(GroupAttribute,0) AS GA,v.OmzetID,HariJatuhTempo,Insidentil,UrutTgl,o.UPTID,isnull(LKecamatan,'') AS Kec,"
            f"isnull(LKelurahan,'') AS Kel,isnull((select FaxKecamatan from MsKecamatan c where c.KecamatanID = o.LKecamatan),'') AS LoKec "
            f"FROM ((PendataanByOmzet o LEFT JOIN vw_obyekbadan v ON o.OPDID = v.OPDID) "
            f"LEFT JOIN MsJenisPendapatan p ON v.UsahaBadan = p.JenisPendapatanID) WHERE o.PendataanID='{pendataanid}'")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


class ValidasiSPTP4(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, vw_header=None, *args, **kwargs):

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
            # f"SELECT OBN,ObyekBadanNo,(CASE WHEN TglHapus IS NOT NULL THEN NamaBadan ELSE NamaBadan END) "
            # f"AS NamaBadan,Jenis,NoKohir,(case when JBayar > 0 then (CASE WHEN NIsPaid <> 'Lunas' THEN NIsPaid "
            # f"ELSE (case when (select top 1 NTPD from SetoranHist s where s.SubKohir = v.KohirID and s.NoKohir = "
            # f"v.NoKohir) is not null then (case when (select sum(s.JmlBayar) + sum(s.JmlBayarDenda) "
            # f"from SetoranHist s where s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir and NTPD is not null) = "
            # f"HarusBayar then 'Lunas' else 'Kode Bayar' end) else 'Kode Bayar' end) END) else JatuhTempo end) "
            # f"AS JatuhTempo,KohirID,(select top 1 (case when KodeUPT in (select kode_badan from vw_header) "
            # f"then (select badan_singkat from vw_header) else UPT end) from MsUPT u where u.UPTID = v.SKPOwner) "
            # f"AS Dinas FROM vw_penetapanomzet v WHERE TglHapus IS NULL  AND OPDID IN "
            # f"(select distinct OPDID from MsObyekBadan WHERE v.SKPOwner = '{uptid}' AND SelfAssesment = 'Y' "
            # f"and Insidentil = 'y') "
            # f"ORDER BY KohirID DESC, Jenis")

            f"SELECT PenetapanID, OBN,ObyekBadanNo,(CASE WHEN TglHapus IS NOT NULL THEN NamaBadan ELSE NamaBadan END) AS NamaBadan,"
            f"Jenis,NoKohir,(case when JBayar > 0 then (CASE WHEN NIsPaid <> 'Lunas' THEN NIsPaid ELSE "
            f"(case when (select top 1 NTPD from SetoranHist s where s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir) "
            f"is not null then (case when (select sum(s.JmlBayar) + sum(s.JmlBayarDenda) from SetoranHist s "
            f"where s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir and NTPD is not null) = HarusBayar then 'Lunas' "
            f"else 'Kode Bayar' end) else 'Kode Bayar' end) END) else JatuhTempo end) AS JatuhTempo,KohirID,"
            f"(select top 1 (case when KodeUPT in (select kode_badan from vw_header) then "
            f"(select badan_singkat from vw_header) else UPT end) from MsUPT u where u.UPTID = v.SKPOwner) AS Dinas "
            f"FROM vw_penetapanomzet v WHERE TglHapus IS NULL  AND OPDID IN (select distinct OPDID "
            f"from MsObyekBadan WHERE SelfAssesment = 'Y' and Insidentil = 'N')  "
            f"ORDER BY KohirID DESC, Jenis")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


class ValidasiSPTP5(Resource):
    def get(self, penetapanid, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT * FROM vw_penetapanomzet WHERE PenetapanID = '{penetapanid}'")
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

class AddValidasiSPTP(Resource):
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
        parser.add_argument('JmlOmzetAwal', type=str)
        parser.add_argument('TarifPajak', type=str)
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
                f"exec [SP_KOHIR_BLN]")
            result2 = []
            for row in result1:
                result2.append(row)
            kohirid = result2[0][0]

            result3 = db.session.execute(
                f"exec [SP_KOHIR]")
            result4 = []
            for row in result3:
                result4.append(row)
            nokohir = result4[0][0]

            select_query = db.session.execute(
                f"exec [SP_NomorKohir] '{args['SPT']}', '{kohirid}', '{args['MasaAwal']}', "
                f"'{args['MasaAkhir']}','{args['TglPenetapan']}','{uid}'")

            add_record = PenetapanByOmzet(
                NoKohir=nokohir,
                KohirID=kohirid,
                OPDID=args['OPDID'],
                TglPenetapan=args['TglPenetapan'],
                TglJatuhTempo=args['TglJatuhTempo'],
                MasaAwal=args['MasaAwal'],
                MasaAkhir=args['MasaAkhir'],
                UrutTgl=args['UrutTgl'],
                JmlOmzetAwal=args['JmlOmzetAwal'],
                TarifPajak=args['TarifPajak'],
                Denda=sqlalchemy.sql.null(),
                Kenaikan=sqlalchemy.sql.null(),
                IsPaid='N',
                TglBayar=sqlalchemy.sql.null(),
                JmlBayar=sqlalchemy.sql.null(),
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
            if add_record:
                data = {'SPT': args['SPT'],
                        'UrutTgl': add_record.UrutTgl,
                        'NoKohir': add_record.NoKohir}

                update_record_parent = PendataanByOmzetDtl.UpdateParent(data)
                if update_record_parent:
                    return success_create({'PenetapanID': add_record.PenetapanID,
                                           'KohirID': add_record.KohirID,
                                           'UPTID': add_record.UPTID,
                                           'OPDID': add_record.OPDID,
                                           'TarifPajak': add_record.TarifPajak})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_create({})


class UpdateValidasiSPTP(Resource):
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
                return success_update({'id': id})
        except Exception as e:

            db.session.rollback()
            print(e)
            return failed_update({})

class UpdateValidasiSPTPKurangBayar(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}
    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        print(kwargs['claim'])

        parser.add_argument('KohirID', type=str)
        parser.add_argument('TarifPajak', type=str)
        parser.add_argument('TglJatuhTempo', type=str)
        parser.add_argument('Denda', type=str)
        parser.add_argument('Kenaikan', type=str)
        parser.add_argument('TglKurangBayar', type=str)
        parser.add_argument('JmlKurangBayar', type=str)
        parser.add_argument('Penagih', type=str)

        args = parser.parse_args()
        totalpajak = args['TarifPajak']
        denda = args['Denda'] #round(float(totalpajak) * 0.02)
        jumlahkurangbayar = float(totalpajak) + float(denda)

        try:
            select_query = PenetapanByOmzet.query.filter_by(PenetapanID=id).first()
            if select_query:
                if args['TglJatuhTempo']:
                    select_query.TglJatuhTempo = args['TglJatuhTempo']
                if denda:
                    select_query.Denda = denda
                if args['Kenaikan']:
                    select_query.Kenaikan = args['Kenaikan']
                if args['TglKurangBayar']:
                    select_query.TglKurangBayar = args['TglKurangBayar']
                if args['Denda']:
                    jumlahkurangbayar
                db.session.commit()

                if select_query.KohirID:
                    kohirid = select_query.KohirID
                    query = NomorKohir.query.filter_by(KohirID=kohirid).first()
                    if query:
                        if args['TglKurangBayar']:
                            query.TglKurangBayar = args['TglKurangBayar']
                        if args['Penagih']:
                            query.Penagih = args['Penagih']
                        db.session.commit()
                return success_update({'KohirID': select_query.KohirID,
                                       'UPTID': select_query.UPTID,
                                       'TarifPajak': select_query.TarifPajak,
                                       'Denda': denda,
                                       'JumlahKurangBayar': jumlahkurangbayar})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_update({})


class DeleteValidasiSPTP(Resource):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}

    def delete(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        print(kwargs['claim'])
        parser.add_argument('KohirID', type=str)
        parser.add_argument('NoKohir', type=str)

        args = parser.parse_args()

        try:
            # select_query = PenetapanByOmzet.query.filter_by(PenetapanID=id).first()
            # if select_query.KohirID:
            #     data = {'KohirID': select_query.KohirID,
            #             'NoKohir': select_query.NoKohir}
            #     delete_record_parent = PendataanByOmzetDtl.DeleteParent(data)
            #     delete_record_parent = NomorKohir.DeleteParent(data)

            delete_record = PenetapanByOmzet.query.filter_by(PenetapanID=id)
            delete_record.delete()
            db.session.commit()
            return success_delete({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_delete({})

#######################################################################
#######################################################################

class ValidasiSPTP(Resource):
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


class ValidasiSPTPOmset(Resource):
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
            select_query = db.session.query(PenetapanByOmzet.UPTID, PenetapanByOmzet.MasaAwal,
                                            PenetapanByOmzet.MasaAkhir, PenetapanByOmzet.TglPenetapan,
                                            case([(PenetapanByOmzet.TglPenetapan == None, 'Terdata')]
                                                 ,
                                                 else_='SKP'
                                                 ).label('Penetapan'),
                                            PenetapanByOmzet.TarifPajak) \
                .join(PenetapanByOmzet, (PenetapanByOmzet.OPDID == PenetapanByOmzet.OPDID) &
                      (PenetapanByOmzet.MasaAwal == PenetapanByOmzet.MasaAwal) &
                      (PenetapanByOmzet.MasaAkhir == PenetapanByOmzet.MasaAkhir) &
                      (PenetapanByOmzet.UrutTgl == PenetapanByOmzet.UrutTgl), isouter=True) \
                .join(vw_obyekbadan, vw_obyekbadan.OPDID == PenetapanByOmzet.OPDID) \
                .filter(
                PenetapanByOmzet.OPDID == opdid
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
                        vw_obyekbadan.TglPenetapan.ilike(search)
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