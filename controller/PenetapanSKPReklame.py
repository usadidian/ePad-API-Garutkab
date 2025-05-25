import decimal
from datetime import datetime

import sqlalchemy
from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy import case, text
from sqlalchemy import or_
from config.api_message import success_reads_pagination, failed_reads, success_reads, failed_create, success_create, \
    success_update, failed_update, success_delete, failed_delete
from config.database import db
from controller.GeneralParameter import GeneralParameter
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsPegawai import MsPegawai
from controller.MsUPT import MsUPT
from controller.MsOPD import MsOPD
from controller.MsWPData import MsWPData
from controller.NomorKohir import NomorKohir
from controller.PenetapanReklameDtl import PenetapanReklameDtl
from controller.PenetapanReklameHdr import PenetapanReklameHdr
from controller.tblUser import tblUser
from controller.vw_obyekbadan import vw_obyekbadan
from controller.vw_penetapan import vw_penetapan


class PenetapanSKPReklame2(Resource):
    def get(self, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT PendataanID, OBN,SPT,o.OPDID,ObyekBadanNo,cast(o.TarifPajak as varchar) AS Pajak,o.TglPendataan,NamaJenisPendapatan AS Jenis,"
            f"NamaBadan,o.MasaAwal, o.MasaAkhir FROM ((PendataanByOmzet o LEFT JOIN vw_obyekbadan v ON "
            f"o.OPDID = v.OPDID) LEFT JOIN PenetapanReklameHdr pbo ON o.OPDID = pbo.OPDID "
            f"AND o.MasaAwal = pbo.MasaAwal AND o.MasaAkhir = pbo.MasaAkhir AND o.UrutTgl = pbo.UrutTgl) "
            f"WHERE  SelfAssesment = 'N' AND o.[Status] = '1' AND TglPenetapan IS NULL AND TglHapus IS NULL "
            f"union "
            f"SELECT PendataanID, OBN,SPT,o.OPDID,ObyekBadanNo,cast (o.TotalPajak as varchar) AS Pajak,o.TglPendataan,NamaJenisPendapatan AS Jenis,"
            f"NamaBadan,o.MasaAwal, o.MasaAkhir FROM ((PendataanReklameHdr o LEFT JOIN vw_obyekbadan v ON "
            f"o.OPDID = v.OPDID) LEFT JOIN PenetapanReklameHdr p ON o.OPDID = p.OPDID "
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


class PenetapanSKPReklame3(Resource):
    def get(self, pendataanid, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT DISTINCT datediff(day,MasaAwal,MasaAkhir)+1 AS hitper,r.OPDID,ObyekBadanNo,NamaBadan,"
            f"NamaPemilik,AlamatBadan,Kota,Kecamatan, Kelurahan,v.KodeRekening,KodePos,v.NamaJenisPendapatan AS Sub,"
            f"UsahaBadan,CAST(TotalPajak AS VARCHAR) AS TotalPajak,MasaAwal,MasaAkhir,r.[Status],r.SPT,r.TglPendataan,"
            f"v.WPID, isnull((select top 1 (select FaxKecamatan from MsKecamatan c where c.KecamatanID = a.LKecamatan) "
            f"from PendataanReklameDtl a where a.SPT = r.SPT),'') AS LoKec,isnull(GroupAttribute,0) AS GA,"
            f"max(NoUrut) AS NoUrut,v.OmzetID,HariJatuhTempo,Insidentil,UrutTgl,r.UPTID "
            f"FROM (((PendataanReklameHdr r LEFT JOIN vw_obyekbadan v ON r.OPDID = v.OPDID) "
            f"LEFT JOIN MsJenisPendapatan p ON v.UsahaBadan = p.JenisPendapatanID) "
            f"LEFT JOIN PendataanReklameDtl d ON r.SPT = d.SPT) WHERE r.PendataanID='{pendataanid}' "
            f"GROUP BY ObyekBadanNo,NamaBadan,NamaPemilik,AlamatBadan,Kota,v.OmzetID, Kecamatan,Kelurahan,"
            f"v.KodeRekening,KodePos,UsahaBadan,TotalPajak,MasaAwal,r.UPTID,MasaAkhir,r.[Status],r.SPT,r.TglPendataan,"
            f"r.OPDID, HariJatuhTempo,v.NamaJenisPendapatan,p.GroupAttribute,Insidentil,UrutTgl,WPID")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


class PenetapanSKPReklame4(Resource):
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
            f"SELECT PenetapanID,OBN,ObyekBadanNo,(CASE WHEN TglHapus IS NOT NULL THEN NamaBadan ELSE NamaBadan END) "
            f"AS NamaBadan,Jenis,NoKohir,(case when JBayar > 0 then (CASE WHEN NIsPaid <> 'Lunas' THEN NIsPaid "
            f"ELSE (case when (select top 1 NTPD from SetoranHist s where s.SubKohir = v.KohirID and s.NoKohir = "
            f"v.NoKohir) is not null then (case when (select sum(s.JmlBayar) + sum(s.JmlBayarDenda) "
            f"from SetoranHist s where s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir and NTPD is not null) = "
            f"HarusBayar then 'Lunas' else 'Kode Bayar' end) else 'Kode Bayar' end) END) else JatuhTempo end) "
            f"AS JatuhTempo,KohirID,(select top 1 (case when KodeUPT in (select kode_badan from vw_header) "
            f"then (select badan_singkat from vw_header) else UPT end) from MsUPT u where u.UPTID = v.SKPOwner) "
            f"AS Dinas FROM vw_penetapanomzet v WHERE TglHapus IS NULL  AND OPDID IN "
            f"(select distinct OPDID from MsObyekBadan WHERE v.SKPOwner = '{uptid}' AND SelfAssesment = 'N' "
            f"and Insidentil = 'N')  UNION "
            f"SELECT PenetapanID,OBN,ObyekBadanNo,(CASE WHEN TglHapus IS NOT NULL THEN NamaBadan "
            f"ELSE NamaBadan END) AS NamaBadan,Jenis,NoKohir,(case when JBayar > 0 then (CASE WHEN NIsPaid <> 'Lunas' "
            f"THEN NIsPaid ELSE (case when (select top 1 NTPD from SetoranHist s where s.SubKohir = v.KohirID "
            f"and s.NoKohir = v.NoKohir) is not null then (case when (select sum(s.JmlBayar) + sum(s.JmlBayarDenda) "
            f"from SetoranHist s where s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir and NTPD is not null) = "
            f"HarusBayar then 'Lunas' else 'Kode Bayar' end) else 'Kode Bayar' end) END) else JatuhTempo end) "
            f"AS JatuhTempo,KohirID,(select top 1 (case when KodeUPT in (select kode_badan from vw_header) then "
            f"(select badan_singkat from vw_header) else UPT end) from MsUPT u where u.UPTID = v.SKPOwner) AS Dinas "
            f"FROM vw_penetapanreklame v WHERE TglHapus IS NULL  AND OPDID IN (select distinct OPDID "
            f"from MsObyekBadan WHERE v.SKPOwner = '{uptid}' AND SelfAssesment = 'N' and Insidentil = 'N')  "
            f"ORDER BY KohirID DESC, Jenis")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


class PenetapanSKPReklame5(Resource):
    def get(self, penetapanid, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT * FROM vw_penetapanreklame WHERE PenetapanID = '{penetapanid}'")
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


class AddPenetapanSKPReklame(Resource):
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
        parser.add_argument('UserUpd', type=str)
        parser.add_argument('DateUpd', type=str)

        parser.add_argument('JudulReklame', type=str)
        parser.add_argument('JenisLokasi', type=str)
        parser.add_argument('LokasiID', type=str)
        parser.add_argument('AlamatPasang', type=str)
        parser.add_argument('LuasReklame', type=int)
        parser.add_argument('PanjangReklame', type=str)
        parser.add_argument('LebarReklame', type=str)
        parser.add_argument('SudutPandang', type=str)
        parser.add_argument('JumlahReklame', type=int)
        parser.add_argument('TarifPajak', type=str)
        parser.add_argument('LKecamatan', type=str)
        parser.add_argument('LKelurahan', type=str)

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

            add_record = PenetapanReklameHdr(
                NoKohir=nokohir,
                KohirID=kohirid,
                OPDID=args['OPDID'],
                TglPenetapan=args['TglPenetapan'],
                TglJatuhTempo=args['TglJatuhTempo'],
                MasaAwal=args['MasaAwal'],
                MasaAkhir=args['MasaAkhir'],
                UrutTgl=args['UrutTgl'],
                TotalPajak=args['TarifPajak'],
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
                UserUpd=uid,
                DateUpd=datetime.now()
            )
            db.session.add(add_record)
            db.session.commit()
            if add_record:
                db.session.execute(
                    f"exec [SP_REKLAMEDTL] '{nokohir}', '{uid}', '{args['SPT']}'")
                db.session.commit()
                db.session.execute(
                    f"exec [SP_Penetapan] '{add_record.KohirID}',1")
                db.session.commit()

                query = db.session.execute(
                    f"SELECT mw.WPID FROM MsOPD AS mw "
                    f"LEFT JOIN PenetapanReklameHdr AS prh ON prh.OPDID = mw.OPDID "
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

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_create({})


class UpdatePenetapanSKPReklame(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}
    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        print(kwargs['claim'])
        parser.add_argument('TglPenetapan', type=str)
        args = parser.parse_args()
        try:
            select_query = PenetapanReklameHdr.query.filter_by(PenetapanID=id).first()
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


class UpdatePenetapanSKPReklameKurangBayar(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}
    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        print(kwargs['claim'])

        parser.add_argument('KohirID', type=str)
        parser.add_argument('TotalPajak', type=str)
        parser.add_argument('TglJatuhTempo', type=str)
        parser.add_argument('Denda', type=str)
        parser.add_argument('Kenaikan', type=str)
        parser.add_argument('TglKurangBayar', type=str)
        parser.add_argument('JmlKurangBayar', type=str)
        parser.add_argument('Penagih', type=str)

        args = parser.parse_args()
        # totalpajak = args['TotalPajak']
        # denda = args['Denda']
        # jumlahkurangbayar = float(totalpajak) + float(denda)

        try:
            select_query = PenetapanReklameHdr.query.filter_by( PenetapanID=id ).first()
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
                jumlahkurangbayar = 0
            else:
                denda = select_detail.Denda
                totalpajak = select_detail.Pajak
                jumlahkurangbayar = float(totalpajak) + float(denda)

            if select_query:
                if args['TglJatuhTempo']:
                    select_query.TglJatuhTempo = select_detail.TglJatuhTempo
                if args['Denda']:
                    select_query.Denda
                if args['Kenaikan']:
                    select_query.Kenaikan = args['Kenaikan']
                if args['TglKurangBayar']:
                    select_query.TglKurangBayar = args['TglKurangBayar']
                if denda:
                    jumlahkurangbayar
                db.session.commit()
                db.session.execute(
                    f"exec [SP_Penetapan] '{select_query.KohirID}',3")
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
                                       'TotalPajak': select_query.TotalPajak,
                                       'Denda': denda,
                                       'JumlahKurangBayar': jumlahkurangbayar})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_update({})

class DeletePenetapanSKPReklame(Resource):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}

    def delete(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        print(kwargs['claim'])
        parser.add_argument('NoKohir', type=str)
        parser.add_argument('KohirID', type=str)
        parser.add_argument('OPDID', type=str)
        parser.add_argument('OmzetBase', type=str)
        parser.add_argument('MasaAwal', type=str)
        parser.add_argument('MasaAkhir', type=str)
        parser.add_argument('UrutTgl', type=str)
        parser.add_argument('NoSKHapus', type=str)
        parser.add_argument('TglSKHapus', type=str)
        args = parser.parse_args()
        uid = kwargs['claim']["UID"]
        try:
            delete_record = PenetapanReklameHdr.query.filter_by(PenetapanID=id)
            # delete_record.delete()
            # select_query = db.session.execute(
            #     f"exec [SP_DEL_KOHIR] '{args['NoKohir']}','{args['KohirID']}',{args['OPDID']},'{args['OmzetBase']}',"
            #     f"'{args['MasaAwal']}', '{args['MasaAkhir']}', '{args['UrutTgl']}','{uid}','{args['NoSKHapus']}', '{args['TglSKHapus']}'")
            # db.session.commit()
            # db.session.execute(
            #     f"exec [SP_Penetapan] '{args['KohirID']}',0 ")
            # db.session.commit()
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

class PenetapanSKPReklame(Resource):
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
                vw_obyekbadan.TglHapus == None, vw_obyekbadan.SelfAssesment == 'N', vw_obyekbadan.Insidentil == 'N'
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


class PenetapanSKPReklameOmset(Resource):
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
            select_query = db.session.query(PenetapanReklameHdr.UPTID, PenetapanReklameHdr.MasaAwal,
                                            PenetapanReklameHdr.MasaAkhir, PenetapanReklameHdr.TglPenetapan,
                                            case([(PenetapanReklameHdr.TglPenetapan == None, 'Terdata')]
                                                 ,
                                                 else_='SKP'
                                                 ).label('Penetapan'),
                                            PenetapanReklameHdr.TotalPajak) \
                .join(PenetapanReklameHdr, (PenetapanReklameHdr.OPDID == PenetapanReklameHdr.OPDID) &
                      (PenetapanReklameHdr.MasaAwal == PenetapanReklameHdr.MasaAwal) &
                      (PenetapanReklameHdr.MasaAkhir == PenetapanReklameHdr.MasaAkhir) &
                      (PenetapanReklameHdr.UrutTgl == PenetapanReklameHdr.UrutTgl), isouter=True) \
                .join(vw_obyekbadan, vw_obyekbadan.OPDID == PenetapanReklameHdr.OPDID) \
                .filter(
                PenetapanReklameHdr.OPDID == opdid
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