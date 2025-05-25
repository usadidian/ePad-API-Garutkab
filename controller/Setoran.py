import json
from datetime import datetime

import sqlalchemy
from sqlalchemy.orm import scoped_session
from flask_restful import Resource, reqparse
from sqlalchemy import or_, extract, text

from config.api_message import success_reads_pagination, failed_reads, success_reads, failed_create, success_create, \
    success_update, failed_update, success_delete, failed_delete
from config.database import db
from controller.GeneralParameter import GeneralParameter
from controller.SetoranHist import SetoranHist
from controller.SetoranUPTDtl import SetoranUPTDtl
from controller.SetoranUPTHdr import SetoranUPTHdr
from controller.tblGroupUser import tblGroupUser
from controller.tblUPTOpsen import tblUPTOpsen
from controller.tblUser import tblUser
from controller.vw_setoran import vw_setoran


class Setoran2( Resource ):
    def get(self, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT  v.HeaderID,NoSTS,StatusBayar,TglSetoran,JmlSetoran, (CASE WHEN v.KodeSB = '2' THEN "
            f"(case when v.SetoranDariUPT = '' then v.UPT else v.SetoranDariUPT end) ELSE v.UPT END) AS Badan "
            f"FROM vw_setoranupt v LEFT JOIN MsUPT p ON v.ParentID = p.UPTID WHERE v.[Status] = '1' AND UPTStatus = '1' "
            f"ORDER BY TglSetoran DESC" )
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                if key == 'JmlSetoran':
                    d[key] = str( getattr( row, key ) )
                else:
                    d[key] = getattr( row, key )
            result.append( d )
        return success_reads( result )

class Setoran1(Resource):
    def get(self, *args, **kwargs):

        select_query = db.session.execute(
            f"SELECT DISTINCT TglSetoran FROM SetoranUPTHdr AS su  "
        )
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr( row, key )
            result.append( d )
        return success_reads( result )
class AddSetoran( Resource ):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        # parser.add_argument('HeaderID', type=str)
        parser.add_argument( 'UPTID', type=str )
        parser.add_argument( 'SetoranDari', type=str )
        parser.add_argument( 'NoSTS', type=str )
        parser.add_argument( 'STSKe', type=str )
        parser.add_argument( 'TglSetoran', type=str )
        parser.add_argument( 'Keterangan', type=str )
        parser.add_argument( 'StatusBayar', type=str )
        parser.add_argument( 'Status', type=str )
        parser.add_argument( 'BendaharaID', type=str )
        parser.add_argument( 'KodeStatus', type=str )
        parser.add_argument( 'UserUpd', type=str )
        parser.add_argument( 'DateUpd', type=str )


        uid = kwargs['claim']["UID"]

        try:
            args = parser.parse_args()
            select_query = db.session.execute(
                f"SELECT DISTINCT ISNULL(MAX(STSKe),1) + 1 FROM SetoranUPTHdr WHERE UPTID = '{args['UPTID']}' AND NoSTS ='{args['NoSTS']}'" )
            result3 = select_query.first()[0]
            STSKe = result3

            result = []
            for row in result:
                result.append( row )

            add_record = SetoranUPTHdr(
                UPTID=args['UPTID'],
                SetoranDari=args['SetoranDari'],
                NoSTS=args['NoSTS'],
                STSKe=STSKe,
                TglSetoran=args['TglSetoran'],
                Keterangan=args['Keterangan'],
                StatusBayar=args['StatusBayar'],
                Status=1,
                BendaharaID=args['BendaharaID'],
                KodeStatus=args['KodeStatus'],
                UserUpd=uid,
                DateUpd=datetime.now()
            )
            db.session.add( add_record )
            db.session.commit()
            if add_record:
                data = {
                    'uid': uid,
                    'NoSTS': add_record.NoSTS,
                    'HeaderID': add_record.HeaderID,
                    'UPTID': add_record.UPTID,
                    'TglSetoran': add_record.TglSetoran,
                }

                return success_create( {'HeaderID': add_record.HeaderID,
                                        'NoSTS': add_record.NoSTS,
                                        'UPTID': add_record.UPTID,
                                        'TglSetoran': add_record.TglSetoran} )
            else:
                db.session.rollback()
                return failed_create( {} )

        except Exception as e:
            db.session.rollback()
            print( e )
            return failed_create( {} )


class Setoran3( Resource ):
    def get(self, headerid, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT DISTINCT UPTID,NoSTS,UPT,StatusBayar,TglSetoran FROM vw_setoranupt WHERE HeaderID ='{headerid}'" )
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr( row, key )
            result.append( d )
        return success_reads( result )


class Setoran4( Resource ):
    def get(self, headerid, *args, **kwargs):
        select_query = db.session.execute(
            """
            DECLARE @jenis VARCHAR(10) 
            SET @jenis=ISNULL((SELECT Keterangan FROM SetoranUPTHdr AS su WHERE su.HeaderID = :HeaderID),'') 
            IF @jenis NOT LIKE '%Opsen PKB%' AND @jenis NOT LIKE '%Opsen BBN-KB%' 
            BEGIN 
            SELECT s.TglSetoran, u.HeaderID,DetailID,u.NoReg AS Nomor, j.KodeRekening, NamaJenisPendapatan AS Jenis, u.JmlSetoran, StatusBayar 
            FROM SetoranUPTDtl u 
            LEFT JOIN MsJenisPendapatan j ON u.JenisPendapatanID = j.JenisPendapatanID 
            LEFT JOIN vw_setoranupt s ON u.HeaderID = s.HeaderID 
            WHERE u.HeaderID = :HeaderID AND u.[Status] = '1' 
            END 
            ELSE 
            BEGIN 
            SELECT s.TglSetoran,u.HeaderID,DetailID,u.NoReg AS Nomor, 
            j.KodeRekening,  
             (CASE WHEN j.NamaJenisPendapatan IN('Opsen PKB','Opsen BBN-KB') THEN 
            'Opsen ' + (SELECT TOP(1) to1.NamaRekening FROM tblOpsen to1 WHERE 
            to1.KodeRekeningOpsen =j.KodeRekening AND to1.NoReg = u.NoReg ) ELSE 
            j.NamaJenisPendapatan END) AS Jenis, 
            u.JmlSetoran, StatusBayar 
            FROM SetoranUPTDtl u 
            LEFT JOIN MsJenisPendapatan j ON u.JenisPendapatanID = j.JenisPendapatanID 
            LEFT JOIN vw_setoranupt s ON u.HeaderID = s.HeaderID 
            WHERE u.HeaderID = :HeaderID AND u.[Status] = '1'
            ORDER BY s.TglSetoran, u.NoReg, j.KodeRekening
            END 
            """,
            {"HeaderID": headerid}
        )
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                if key == 'JmlSetoran':
                    d[key] = str( getattr( row, key ) )
                else:
                    d[key] = getattr( row, key )
            result.append( d )
        return success_reads( result )


class Setoran5( Resource ):
    def get(self, headerid, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT * FROM vw_setoranupt WHERE HeaderID = '{headerid}'" )
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                if key == 'JmlSetoran':
                    d[key] = str( getattr( row, key ) )
                else:
                    d[key] = getattr( row, key )
            result.append( d )
        return success_reads( result )


class Setoran6( Resource ):
    def get(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        # parser.add_argument('KodeRekening', type=str)
        # parser.add_argument('TglBayar', type=str)
        args = parser.parse_args()
        result = []
        for row in result:
            result.append( row )

        # Mendapatkan nilai tahun dari parameter
        tahun_result = db.session.execute(
            text("SELECT ParamStrValue FROM GeneralParameter WHERE ParamID = :param_id"),
            {"param_id": "tahun_akb"}
        )
        tahun = tahun_result.scalar()

        # Menyusun query SQL dengan parameter binding
        query = text("""
            SELECT
                'o' + s.NoKohir + 'p' + CONVERT(VARCHAR(10), s.nourut) AS NoKohir,
                s.SubKohir,
                vw.Pajak AS JmlBayar,
                (
                    SELECT TOP 1 NamaBadan
                    FROM vw_penetapanomzet v
                    WHERE v.KohirID = s.SubKohir AND v.NoKohir = s.NoKohir
                ) AS NamaBadan,
                'Pokok' AS Jenis,
                vw.KodeRekening,
                vw.Jenis AS NamaJenisPendapatan,
                vw.TglPenetapan,
                s.TglBayar,
                vw.UsahaBadan AS JenisPendapatanID,
                s.SetoranHistID
            FROM SetoranHist s
            INNER JOIN vw_penetapanomzet vw ON vw.NoKohir = s.NoKohir AND vw.KohirID = s.SubKohir
            WHERE s.STS IS NULL AND s.JmlBayar > 0 AND YEAR(s.TglBayar) = :tahun

            UNION ALL

            SELECT
                'o' + s.NoKohir + 'p' + CONVERT(VARCHAR(10), s.nourut),
                s.SubKohir,
                vw.PajakOpsen,
                (
                    SELECT TOP 1 NamaBadan
                    FROM vw_penetapan v
                    WHERE v.KohirID = s.SubKohir AND v.NoKohir = s.NoKohir
                ),
                'Opsen',
                ISNULL((
                    SELECT mjp.KodeRekening
                    FROM MsJenisPendapatan mjp
                    LEFT JOIN MsMapOpsen mmo ON mmo.JPIDOpsen = mjp.JenisPendapatanID
                    WHERE mmo.JPID = vw.JenisPendapatanID
                ), '') AS KodeRekening,
                ISNULL((
                    SELECT mjp.NamaJenisPendapatan
                    FROM MsJenisPendapatan mjp
                    LEFT JOIN MsMapOpsen mmo ON mmo.JPIDOpsen = mjp.JenisPendapatanID
                    WHERE mmo.JPID = vw.JenisPendapatanID
                ), '') AS NamaJenisPendapatan,
                vw.TglPenetapan,
                s.TglBayar,
                ISNULL((
                    SELECT mjp.JenisPendapatanID
                    FROM MsJenisPendapatan mjp
                    INNER JOIN MsMapOpsen mmo ON mmo.JPIDOpsen = mjp.JenisPendapatanID
                    WHERE mmo.JPID = vw.JenisPendapatanID
                ), '') AS JenisPendapatanID,
                s.SetoranHistID
            FROM SetoranHist s
            INNER JOIN vw_penetapan vw ON vw.NoKohir = s.NoKohir AND vw.KohirID = s.SubKohir
            WHERE s.JmlBayar > 0 AND YEAR(s.TglBayar) = :tahun

            UNION ALL

            SELECT
                'r' + s.NoKohir + 'p' + CONVERT(VARCHAR(10), s.nourut),
                s.SubKohir,
                s.JmlBayar,
                (
                    SELECT TOP 1 NamaBadan
                    FROM vw_penetapanreklame v
                    WHERE v.KohirID = s.SubKohir AND v.NoKohir = s.NoKohir
                ),
                'Pokok',
                vw.KodeRekening,
                vw.Jenis AS NamaJenisPendapatan,
                vw.TglPenetapan,
                s.TglBayar,
                vw.UsahaBadan AS JenisPendapatanID,
                s.SetoranHistID
            FROM SetoranHist s
            INNER JOIN vw_penetapanreklame vw ON vw.NoKohir = s.NoKohir AND vw.KohirID = s.SubKohir
            WHERE s.STS IS NULL AND s.JmlBayar > 0 AND YEAR(s.TglBayar) = :tahun

            UNION ALL

            SELECT
                'o' + s.NoKohir + 'd' + CONVERT(VARCHAR(10), s.nourut),
                s.SubKohir,
                s.JmlBayarDenda,
                (
                    SELECT TOP 1 NamaBadan
                    FROM vw_penetapanomzet v
                    WHERE v.KohirID = s.SubKohir AND v.NoKohir = s.NoKohir
                ),
                'Denda',
                vw.KodeRekening,
                vw.Jenis AS NamaJenisPendapatan,
                vw.TglPenetapan,
                s.TglBayar,
                vw.UsahaBadan AS JenisPendapatanID,
                s.SetoranHistID
            FROM SetoranHist s
            INNER JOIN vw_penetapanomzet vw ON vw.NoKohir = s.NoKohir AND vw.KohirID = s.SubKohir
            WHERE s.STSDenda IS NULL AND s.JmlBayarDenda > 0 AND YEAR(s.TglBayar) = :tahun

            UNION ALL

            SELECT
                'r' + s.NoKohir + 'd' + CONVERT(VARCHAR(10), s.nourut),
                s.SubKohir,
                s.JmlBayarDenda,
                (
                    SELECT TOP 1 NamaBadan
                    FROM vw_penetapanreklame v
                    WHERE v.KohirID = s.SubKohir AND v.NoKohir = s.NoKohir
                ),
                'Denda',
                vw.KodeRekening,
                vw.Jenis AS NamaJenisPendapatan,
                vw.TglPenetapan,
                s.TglBayar,
                vw.UsahaBadan AS JenisPendapatanID,
                s.SetoranHistID
            FROM SetoranHist s
            INNER JOIN vw_penetapanreklame vw ON vw.NoKohir = s.NoKohir AND vw.KohirID = s.SubKohir
            WHERE s.STSDenda IS NULL AND s.JmlBayarDenda > 0 AND YEAR(s.TglBayar) = :tahun

            ORDER BY NoKohir, Jenis DESC
        """)

        # Menjalankan query dengan parameter binding
        result = db.session.execute(query, {"tahun": tahun}).fetchall()
        data = []
        for row in result:
            d = {}
            for key in row._mapping.keys():
                if key == 'JmlBayar':
                    value = getattr(row, key)
                    if value == 0:  # lewati jika JmlBayar = 0
                        break
                    d[key] = str(value)
                else:
                    d[key] = getattr(row, key)
            else:
                data.append(d)  # hanya tambah jika tidak break (artinya JmlBayar ≠ 0)

        # data = [
        #     {
        #         key: str(row[key]) if key == 'JmlBayar' else row[key]
        #         for key in row._mapping.keys()
        #     }
        #     for row in result
        #     if row['JmlBayar'] != 0
        # ]

        # Return hasil
        return success_reads(data)

class AddSetoranDtl(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('HeaderID', type=str)
        parser.add_argument('dataDetail', type=str)
        parser.add_argument('SetoranHistID', action='append', nullable=False,
                            help="SetoranHistID cannot be blank!")

        try:
            args = parser.parse_args()
            uid = kwargs['claim']["UID"]

            # /////SKP
            data_detil = json.loads(args['dataDetail'])
            for x in data_detil:
                print(x)
                add_record = SetoranUPTDtl(
                    HeaderID=args['HeaderID'],
                    JenisPendapatanID=x['JenisPendapatanID'],
                    JmlSetoran=x['JmlSetoran'],
                    Status=1,
                    NTB=sqlalchemy.sql.null(),
                    NTPD=sqlalchemy.sql.null(),
                    TglNTPD=sqlalchemy.sql.null(),
                    UserUpd=uid,
                    DateUpd=datetime.now()
                )
                db.session.add(add_record)
                db.session.commit()

            if args['SetoranHistID']:  # Only execute if SetoranHistID exists and is not empty
                for row_id in args['SetoranHistID']:
                    update_record_detail = SetoranHist.query.filter_by(SetoranHistID=row_id).first()
                    if update_record_detail:
                        update_record_detail.STS = args['HeaderID']
                        update_record_detail.STSDenda = args['HeaderID']
                        update_record_detail.STSOpsen = args['HeaderID']
                        db.session.commit()

                return success_create({
                    'DetailID': add_record.DetailID,
                    'HeaderID': add_record.HeaderID,
                    'JenisPendapatanID': add_record.JenisPendapatanID,
                    'JmlSetoran': add_record.JmlSetoran
                })
        except json.JSONDecodeError as e:
            db.session.rollback()
            print(f"JSON decoding failed: {e}")
            return failed_create({"error": "Invalid JSON format."})
        # except Exception as e:
        #     db.session.rollback()
        #     print(f"An error occurred: {e}")
        #     return failed_create({"error": str(e)})


# class AddSetoranDtl( Resource ):
#     method_decorators = {'post': [tblUser.auth_apikey_privilege]}
#
#     def post(self, *args, **kwargs):
#         parser = reqparse.RequestParser()
#         parser.add_argument( 'HeaderID', type=str )
#         parser.add_argument( 'dataDetail', type=str )
#         parser.add_argument( 'SetoranHistID', action='append', required=True, nullable=False,
#                              help="Name cannot be blank!" )
#
#         try:
#             args = parser.parse_args()
#             uid = kwargs['claim']["UID"]
#
#             # /////SKP
#             data_detil = json.loads( args['dataDetail'] )
#             for x in data_detil:
#                 print(data_detil)
#                 add_record = SetoranUPTDtl(
#                     HeaderID=args['HeaderID'],
#                     JenisPendapatanID=x['JenisPendapatanID'],
#                     JmlSetoran=x['JmlSetoran'],
#                     Status=1,
#                     NTB=sqlalchemy.sql.null(),
#                     NTPD=sqlalchemy.sql.null(),
#                     TglNTPD=sqlalchemy.sql.null(),
#                     UserUpd=uid,
#                     DateUpd=datetime.now()
#                 )
#                 db.session.add( add_record )
#                 db.session.commit()
#
#             if len( args['SetoranHistID'] ) >= 1:
#                 for row_id in args['SetoranHistID']:
#                     update_record_detail = SetoranHist.query.filter_by( SetoranHistID=row_id ).first()
#                     update_record_detail.STS = args['HeaderID']
#                     update_record_detail.STSDenda = args['HeaderID']
#                     update_record_detail.STSOpsen = args['HeaderID']
#                     db.session.commit()
#
#             # /////NON SKP
#             else:
#                 JmlSetoran = args['JmlSetoran']
#                 result = []
#                 data_detil = json.loads( args['dataDetail'] )
#                 for x in data_detil:
#
#                     add_record = SetoranUPTDtl(
#                         HeaderID=args['HeaderID'],
#                         JenisPendapatanID=x['JenisPendapatanID'],
#                         JmlSetoran=x['JmlSetoran'],
#                         Status=1,
#                         NTB=sqlalchemy.sql.null(),
#                         NTPD=sqlalchemy.sql.null(),
#                         TglNTPD=sqlalchemy.sql.null(),
#                         UserUpd=uid,
#                         DateUpd=datetime.now()
#                     )
#                     db.session.add( add_record )
#                     db.session.commit()
#
#             return success_create( {'DetailID': add_record.DetailID,
#                                     'HeaderID': add_record.HeaderID,
#                                     'JenisPendapatanID': add_record.JenisPendapatanID,
#                                     'JmlSetoran': add_record.JmlSetoran} )
#         except Exception as e:
#             db.session.rollback()
#             print( e )
#             return failed_create( {} )


class Setoran7( Resource ):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}
    def get(self,  *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('NamaJenisPendapatan', type=str)
        parser.add_argument('HeaderID', type=str)

        args = parser.parse_args()
        result = []
        try:
            namajenispendapatan = args['NamaJenisPendapatan']
            headerid = args['HeaderID']

            select_query = db.session.execute(

                """
                WITH CTE AS (
                    SELECT 
                        sud.HeaderID,
                        ObyekBadanNo, 
                        NamaBadan, 
                        NamaPemilik, 
                        Jenis, 
                        TglJatuhTempo, 
                        (CASE WHEN JBayar > 0 THEN NIsPaid ELSE JatuhTempo END) AS StatPaid, 
                        v.NoKohir, 
                        OBN, 
                        (CASE 
                            WHEN MasaAwal = MasaAkhir THEN dbo.TANGGAL(MasaAwal, 'G') 
                            ELSE 
                                (CASE 
                                    WHEN OmzetBase = 'Y' THEN dbo.TANGGAL(MasaAwal, 'G') 
                                    ELSE dbo.TANGGAL(MasaAwal, 'G') + dbo.TANGGAL(MasaAkhir, 'G') 
                                END) 
                         END) AS MP, 
                        dbo.TANGGAL(MasaAwal, 'U') AS UrutMP, 
                        (SELECT ISNULL(SUM(JmlBayar), 0) 
                         FROM SetoranHist s 
                         WHERE STS = :HeaderID AND s.SubKohir = v.KohirID AND s.NoKohir = v.NoKohir) AS JmlSetoran, 
                        ISNULL((SELECT TOP 1 NoSSPD 
                                FROM SetoranHist s 
                                WHERE s.SubKohir = v.KohirID AND STS = :HeaderID AND s.NoKohir = v.NoKohir), '-') + 
                        ISNULL(KohirID, '') AS KohirID, 
                        (CASE WHEN CekSTS + CekSTSDenda = '' THEN '' ELSE 'STS' END) AS STS, 
                        ISNULL(KohirID, '') AS KID, 
                        ISNULL((SELECT TOP 1 NoSSPD 
                                FROM SetoranHist s 
                                WHERE s.SubKohir = v.KohirID AND STSDenda = '1504' AND s.NoKohir = v.NoKohir), '-') AS SSPD,
                        ISNULL((SELECT TOP 1 ISNULL(STS, STSDenda) 
                                FROM SetoranHist s 
                                WHERE s.SubKohir = v.KohirID AND s.NoKohir = v.NoKohir), '-') AS CekSTS, 
                        sbd.DetailID, 
                        ROW_NUMBER() OVER (PARTITION BY sbd.DetailID ORDER BY sbd.DetailID) AS RowNum 
                    FROM vw_penetapanomzet v 
                    LEFT JOIN SetoranHist AS sh ON sh.SubKohir = v.KohirID AND sh.NoKohir = v.NoKohir
                    LEFT JOIN SetoranUPTHdr sud ON sud.HeaderID = sh.STS
                    LEFT JOIN SetoranUPTDtl AS sbd ON sbd.HeaderID = sud.HeaderID 
                    WHERE v.NoKohir IN (SELECT NoKohir FROM SetoranHist WHERE STS = :HeaderID)
                    
                    UNION ALL
                SELECT sud.HeaderID,ObyekBadanNo, (CASE WHEN TglHapus IS NOT NULL THEN NamaBadan ELSE NamaBadan END) AS NamaBadan, 
                NamaPemilik, mjp.NamaJenisPendapatan AS Jenis, TglJatuhTempo, (CASE WHEN JBayar > 0 THEN NIsPaid ELSE JatuhTempo END) AS StatPaid, 
                v.NoKohir, OBN, (CASE WHEN MasaAwal=MasaAkhir THEN dbo.TANGGAL(MasaAwal,'G') ELSE 
                (CASE WHEN v.OmzetBase = 'Y' THEN dbo.TANGGAL(MasaAwal,'G') ELSE dbo.TANGGAL(MasaAwal,'G') + dbo.TANGGAL(MasaAkhir,'G') END) END) AS MP, 
                dbo.TANGGAL(MasaAwal,'U') AS UrutMP, 
                (SELECT ISNULL(SUM(JmlBayarOpsen), 0) FROM SetoranHist s WHERE STSOpsen = :HeaderID AND s.SubKohir = v.KohirID AND s.NoKohir = v.NoKohir) AS JmlSetoran, 
                ISNULL((SELECT TOP 1 NoSSPD FROM SetoranHist s WHERE s.SubKohir = v.KohirID AND STS = :HeaderID AND s.NoKohir = v.NoKohir), '-') + ISNULL(KohirID, '') AS KohirID, 
                (CASE WHEN CekSTS + CekSTSDenda = '' THEN '' ELSE 'STS' END) AS STS, 
                ISNULL(KohirID, '') AS KID, 
                isnull((select top 1 NoSSPD from SetoranHist s where s.SubKohir = v.KohirID and STSDenda = '1504' and s.NoKohir = v.NoKohir),'-') AS SSPD,
                ISNULL((SELECT TOP 1 ISNULL(STS, STSDenda) FROM SetoranHist s WHERE s.SubKohir = v.KohirID AND s.NoKohir = v.NoKohir), '-') AS CekSTS, 
                sbd.DetailID, ROW_NUMBER() OVER (PARTITION BY sbd.DetailID ORDER BY sbd.DetailID) AS RowNum 
                FROM vw_penetapan v 
                 LEFT JOIN SetoranHist AS sh ON sh.SubKohir=v.KohirID AND sh.NoKohir=v.NoKohir
                LEFT JOIN SetoranUPTHdr sud ON sud.HeaderID=sh.STS
                LEFT JOIN SetoranUPTDtl AS sbd ON sbd.HeaderID = sud.HeaderID 
                LEFT JOIN MsMapOpsen AS mmo ON mmo.JPID = v.JenisPendapatanID 
                INNER JOIN MsJenisPendapatan AS mjp ON mjp.JenisPendapatanID = mmo.JPIDOpsen 
                WHERE v.NoKohir IN (SELECT NoKohir FROM SetoranHist WHERE STSOpsen = :HeaderID) 
                AND mjp.NamaJenisPendapatan like '%{namajenispendapatan}%' 
                UNION ALL
                SELECT sud.HeaderID,ObyekBadanNo,(CASE WHEN TglHapus IS NOT NULL THEN NamaBadan ELSE NamaBadan END) AS NamaBadan, 
                NamaPemilik,Jenis,TglJatuhTempo,(case when JBayar > 0 then NIsPaid else JatuhTempo end) AS StatPaid,
                v.NoKohir,OBN,(case when MasaAwal=MasaAkhir then dbo.TANGGAL(MasaAwal,'G') else (case when OmzetBase='Y' 
                then dbo.TANGGAL(MasaAwal,'G') else dbo.TANGGAL(MasaAwal,'G') + dbo.TANGGAL(MasaAkhir,'G') end) end) AS MP,
                dbo.TANGGAL(MasaAwal,'U') AS UrutMP,(select isnull(sum(JmlBayar),0) from SetoranHist s where STS = :HeaderID 
                and s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir) AS JmlSetoran,isnull((select top 1 NoSSPD from SetoranHist s 
                where s.SubKohir = v.KohirID and STS = :HeaderID and s.NoKohir = v.NoKohir),'-') + isnull(KohirID,'') 
                AS KohirID,(case when CekSTS + CekSTSDenda='' then '' else 'STS' end) AS STS,isnull(KohirID,'') AS KID,
                isnull((select top 1 NoSSPD from SetoranHist s where s.SubKohir = v.KohirID and STS = :HeaderID 
                and s.NoKohir = v.NoKohir),'-') AS SSPD, isnull((select top 1 isnull(STS,STSDenda) from SetoranHist s 
                where s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir),'-') AS CekSTS ,
                sbd.DetailID, ROW_NUMBER() OVER (PARTITION BY sbd.DetailID ORDER BY sbd.DetailID) AS RowNum  
                FROM vw_penetapanreklame v 
                LEFT JOIN SetoranHist AS sh ON sh.SubKohir=v.KohirID AND sh.NoKohir=v.NoKohir
                LEFT JOIN SetoranUPTHdr sud ON sud.HeaderID=sh.STS
                LEFT JOIN SetoranUPTDtl AS sbd ON sbd.HeaderID = sud.HeaderID 
                where v.NoKohir in (select NoKohir from SetoranHist where STS = :HeaderID) 
                UNION ALL
                SELECT sud.HeaderID,ObyekBadanNo,
                (CASE WHEN TglHapus IS NOT NULL THEN NamaBadan ELSE NamaBadan END) AS NamaBadan, NamaPemilik,Jenis,
                TglJatuhTempo,(case when JBayar > 0 then NIsPaid else JatuhTempo end) AS StatPaid,v.NoKohir,OBN,
                (case when MasaAwal=MasaAkhir then dbo.TANGGAL(MasaAwal,'G') else (case when OmzetBase='Y' 
                then dbo.TANGGAL(MasaAwal,'G') else dbo.TANGGAL(MasaAwal,'G') + dbo.TANGGAL(MasaAkhir,'G') end) end) AS 
                MP,dbo.TANGGAL(MasaAwal,'U') AS UrutMP,(select isnull(sum(JmlBayarDenda),0) from SetoranHist s where 
                STSDenda = :HeaderID and s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir) AS JmlSetoran,
                isnull((select top 1 NoSSPD from SetoranHist s where s.SubKohir = v.KohirID and STSDenda = :HeaderID 
                and s.NoKohir = v.NoKohir),'-') + isnull(KohirID,'') AS KohirID,(case when CekSTS + CekSTSDenda='' then '' 
                else 'STS' end) AS STS,isnull(KohirID,'') AS KID,isnull((select top 1 NoSSPD from SetoranHist s where 
                s.SubKohir = v.KohirID and STSDenda = :HeaderID and s.NoKohir = v.NoKohir),'-') AS SSPD, 
                isnull((select top 1 isnull(STS,STSDenda) from SetoranHist s where s.SubKohir = v.KohirID 
                and s.NoKohir = v.NoKohir),'-') AS CekSTS ,
                sbd.DetailID, ROW_NUMBER() OVER (PARTITION BY sbd.DetailID ORDER BY sbd.DetailID) AS RowNum  
                FROM vw_penetapanomzet v 
                LEFT JOIN SetoranHist AS sh ON sh.SubKohir=v.KohirID AND sh.NoKohir=v.NoKohir
                LEFT JOIN SetoranUPTHdr sud ON sud.HeaderID=sh.STS
                LEFT JOIN SetoranUPTDtl AS sbd ON sbd.HeaderID = sud.HeaderID 
                where v.NoKohir in (select NoKohir from 
                SetoranHist where STSDenda = :HeaderID AND JmlBayarDenda<>0) 
                UNION ALL
                SELECT sud.HeaderID,ObyekBadanNo,(CASE WHEN TglHapus IS NOT NULL 
                THEN NamaBadan ELSE NamaBadan END) AS NamaBadan, NamaPemilik,Jenis,TglJatuhTempo,(case when JBayar > 0 
                then NIsPaid else JatuhTempo end) AS StatPaid,v.NoKohir,OBN,(case when MasaAwal=MasaAkhir 
                then dbo.TANGGAL(MasaAwal,'G') else (case when OmzetBase='Y' then dbo.TANGGAL(MasaAwal,'G') 
                else dbo.TANGGAL(MasaAwal,'G') + dbo.TANGGAL(MasaAkhir,'G') end) end) AS MP,dbo.TANGGAL(MasaAwal,'U') 
                AS UrutMP,(select isnull(sum(JmlBayarDenda),0) from SetoranHist s where STSDenda = :HeaderID 
                and s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir) AS JmlSetoran,isnull((select top 1 NoSSPD from SetoranHist s 
                where s.SubKohir = v.KohirID and STSDenda = :HeaderID and s.NoKohir = v.NoKohir),'-') + 
                isnull(KohirID,'') AS KohirID,(case when CekSTS + CekSTSDenda='' then '' else 'STS' end) AS STS,
                isnull(KohirID,'') AS KID,isnull((select top 1 NoSSPD from SetoranHist s where s.SubKohir = v.KohirID and 
                STSDenda = :HeaderID and s.NoKohir = v.NoKohir),'-') AS SSPD, isnull((select top 1 isnull(STS,STSDenda) 
                from SetoranHist s where s.SubKohir = v.KohirID and s.NoKohir = v.NoKohir),'-') AS CekSTS ,
				sbd.DetailID, ROW_NUMBER() OVER (PARTITION BY sbd.DetailID ORDER BY sbd.DetailID) AS RowNum 
                FROM vw_penetapanreklame v 
                LEFT JOIN SetoranHist AS sh ON sh.SubKohir=v.KohirID AND sh.NoKohir=v.NoKohir
                LEFT JOIN SetoranUPTHdr sud ON sud.HeaderID=sh.STS
                LEFT JOIN SetoranUPTDtl AS sbd ON sbd.HeaderID = sud.HeaderID
                where v.NoKohir in (select NoKohir from SetoranHist where STSDenda = :HeaderID
                AND JmlBayarDenda<>0) 
                UNION ALL
               SELECT sud.HeaderID,sbd.NoReg ObyekBadanNo, to1.NamaBadan, Pemilik AS NamaPemilik, 
                (CASE WHEN mjp.NamaJenisPendapatan IN('Opsen PKB','Opsen BBN-KB') THEN 
                        (SELECT TOP(1) to1.NamaRekening FROM tblOpsen to1 WHERE 
                        to1.KodeRekeningOpsen =mjp.KodeRekening AND to1.NoReg = sbd.NoReg ) ELSE 
                        REPLACE(mjp.NamaJenisPendapatan, 'Opsen ','') END) AS Jenis,'' TglJatuhTempo,  
                       'Lunas' AS StatPaid, sbd.NoReg NoKohir, sbd.NoReg OBN, MasaPajak AS MP, MasaPajak AS UrutMP, 
                (CASE WHEN mjp.NamaJenisPendapatan IN('Opsen PKB','Opsen BBN-KB') THEN 
                        Pajak ELSE to1.Denda END) AS JmlSetoran,
                       to1.KohirID AS KohirID, 'STS' AS STS, sbd.NoReg KID, KodeBayar AS SSPD, 
                       :HeaderID AS CekSTS, sbd.DetailID, 
                       ROW_NUMBER() OVER (PARTITION BY sbd.DetailID ORDER BY sbd.DetailID) AS RowNum  
                FROM tblOpsen to1  
                INNER JOIN SetoranUPTHdr sud ON LTRIM(RTRIM(sud.SetoranDari)) = LTRIM(RTRIM(to1.KotaKendaraan)) 
                   AND sud.TglSetoran = to1.TglSetoranOpsen  
                   AND LTRIM(RTRIM(sud.Keterangan)) = LTRIM(RTRIM(to1.NamaRekeningOpsen)) 
                INNER JOIN SetoranUPTDtl AS sbd ON sbd.HeaderID = sud.HeaderID AND to1.NoReg=sbd.NoReg AND to1.OpsenID=sbd.id
                INNER JOIN MsJenisPendapatan AS mjp ON mjp.JenisPendapatanID = sbd.JenisPendapatanID
                WHERE sbd.HeaderID = :HeaderID
                
                    )
                    SELECT * 
                    FROM CTE 
                    WHERE RowNum = 1
                    ORDER BY ObyekBadanNo, Jenis DESC
                    """,
                    {"HeaderID": headerid}

                )

            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    if key == 'JmlSetoran':
                        d[key] = str( getattr( row, key ) )
                    else:
                        d[key] = getattr( row, key )
                result.append( d )
            return success_reads( result )


        except Exception as e:
            print(e)
            return failed_reads(result)

class UpdateSetoran( Resource ):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        print( kwargs['claim'] )

        parser.add_argument( 'UPTID', type=str )
        parser.add_argument( 'SetoranDari', type=str )
        parser.add_argument( 'NoSTS', type=str )
        parser.add_argument( 'STSKe', type=str )
        parser.add_argument( 'TglSetoran', type=str )
        parser.add_argument( 'Keterangan', type=str )
        parser.add_argument( 'StatusBayar', type=str )
        parser.add_argument( 'Status', type=str )
        parser.add_argument( 'BendaharaID', type=str )
        parser.add_argument( 'KodeStatus', type=str )
        parser.add_argument( 'UserUpd', type=str )
        parser.add_argument( 'DateUpd', type=str )

        args = parser.parse_args()
        uid = kwargs['claim']["UID"]
        try:
            select_query = SetoranUPTHdr.query.filter_by( HeaderID=id ).first()
            if select_query:
                if args['UPTID']:
                    select_query.UPTID = args['UPTID']
                if args['SetoranDari']:
                    select_query.SetoranDari = args['SetoranDari']
                if args['NoSTS']:
                    select_query.NoSTS = args['NoSTS']
                # if args['STSKe']:
                #     select_query.STSKe = args['STSKe']
                if args['TglSetoran']:
                    select_query.TglSetoran = args['TglSetoran']
                if args['Keterangan']:
                    select_query.Keterangan = args['Keterangan']
                if args['StatusBayar']:
                    select_query.StatusBayar = args['StatusBayar']
                # if args['Status']:
                #     select_query.Status = args['Status']
                if args['BendaharaID']:
                    select_query.BendaharaID = args['BendaharaID']
                if args['KodeStatus']:
                    select_query.KodeStatus = args['KodeStatus']
                select_query.UserUpd = uid
                select_query.DateUpd = datetime.now()
                db.session.commit()
                print( 'sukses update ke header' )
                if select_query:
                    return success_update( {'NoSTS': select_query.NoSTS,
                                            'TglSetoran': select_query.TglSetoran,
                                            'UPTID': select_query.UPTID,
                                            'BendaharaID': select_query.BendaharaID,
                                            'Keterangan': select_query.Keterangan,
                                            'KodeStatus': select_query.KodeStatus} )
                else:
                    db.session.rollback()
                    return failed_update( {} )
            else:
                return failed_update( {} )
        except Exception as e:
            db.session.rollback()
            print( e )
            return failed_update( {} )


class DeleteSetoranDtl( Resource ):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}

    def delete(self, id, *args, **kwargs):
        try:
            delete_record_detail = SetoranUPTDtl.query.filter_by(DetailID=id)
            if delete_record_detail:
                headerid = delete_record_detail.first().HeaderID
                check_detail = SetoranUPTDtl.query.filter_by(HeaderID=headerid).all()
                print(len(check_detail))
                if len(check_detail) == 1:
                    delete_record_detail.delete()
                    check_header = SetoranUPTHdr.query.filter_by(HeaderID=headerid)
                    check_header.delete()
                    update_record = SetoranHist.query.filter_by(STS=headerid).first()
                    if update_record.SetoranHistID != None:
                        # update_detail = update_record.filter_by(SetoranHistID=id).first()
                        # if delete_detail.STS and delete_detail.STSDenda == None:

                        setoranhistid = update_record.SetoranHistID
                        update_data = SetoranHist.query.filter_by(SetoranHistID=setoranhistid).first()
                        if update_data.STS != '' or update_data.STSDenda != None:
                            db.session.execute(
                                f"UPDATE SetoranHist SET STS=NULL, STSDenda=NULL "
                                f"WHERE SetoranHistID={setoranhistid} AND NoSSPD='{update_data.NoSSPD}' "
                            )
                            db.session.execute(
                                f"EXEC [INSERT_PEMBAYARAN] "
                            )
                        db.session.commit()
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
            # delete_record = SetoranUPTDtl.query.filter_by( DetailID=id )
            # delete_record.delete()
            # db.session.commit()
            # return success_delete( {} )
        except Exception as e:
            db.session.rollback()
            print( e )
            return failed_delete( {} )


class DeleteSetoran( Resource ):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}

    def delete(self, id, *args, **kwargs):
        try:
            # delete_record_detail = SetoranUPTDtl.query.filter_by(DetailID=id)
            # if delete_record_detail:
            #     headerid = delete_record_detail.first().HeaderID
            #     check_detail = SetoranUPTDtl.query.filter_by(HeaderID=headerid).all()
            #     print(len(check_detail))
            #     if len(check_detail) == 1:
            #         delete_record_detail.delete()
            #         check_header = SetoranUPTHdr.query.filter_by(HeaderID=headerid)
            #         opdid = check_header.first().OPDID
            #         select_query = db.session.execute(
            #             f"UPDATE MsWP SET TglPendataan = NULL WHERE OPDID = {opdid}")
            #         check_header.delete()
            #         db.session.commit()
            #         if check_header:
            #             return success_delete({})
            #         else:
            #             db.session.rollback()
            #             return failed_delete({})
            #     else:
            #         delete_record_detail.delete()
            #         db.session.commit()
            #         return success_delete({})
            # else:
            #     db.session.rollback()
            #     return failed_delete({})

            delete_record = SetoranUPTHdr.query.filter_by( HeaderID=id )
            delete_record.delete()

            entry_exists = db.session.query(SetoranHist).filter(
                (SetoranHist.STS == id)
            ).first() is not None

            if entry_exists:
                update_record = SetoranHist.query.filter_by(STS=id).first()
                if update_record.SetoranHistID != None:
                    # update_detail = update_record.filter_by(SetoranHistID=id).first()
                    # if delete_detail.STS and delete_detail.STSDenda == None:

                    setoranhistid = update_record.SetoranHistID
                    update_data = SetoranHist.query.filter_by(SetoranHistID=setoranhistid).first()
                    if update_data.STS != '' or update_data.STSDenda != None:
                        db.session.execute(
                            f"UPDATE SetoranHist SET STS=NULL, STSDenda=NULL "
                            f"WHERE SetoranHistID={setoranhistid} AND NoSSPD='{update_data.NoSSPD}' "
                        )
                    db.session.commit()

            db.session.commit()
            return success_delete( {} )
        except Exception as e:
            db.session.rollback()
            print( e )
            return failed_delete( {} )


#######################################################################
#######################################################################

class Setoran( Resource ):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):

        # PARSING PARAMETER DARI REQUEST
        parser = reqparse.RequestParser()
        parser.add_argument( 'page', type=int )
        parser.add_argument( 'length', type=int )
        parser.add_argument( 'sort', type=str )
        parser.add_argument( 'sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc' )
        parser.add_argument( 'search', type=str )
        parser.add_argument( 'search_jenis', type=str )
        parser.add_argument('filter_upt', type=str)
        parser.add_argument('filter_tgl', type=str)

        args = parser.parse_args()
        session = scoped_session(db.session)
        UserId = kwargs['claim']["UserId"]
        wapuid = kwargs['claim']["WapuID"]
        print(wapuid)
        groupid = kwargs['claim']["GroupId"]
        checkintegrasi = tblGroupUser.query.filter_by(
            GroupId=groupid
        ).first()
        print(checkintegrasi)
        result = []

        query1 = db.session.query(GeneralParameter.ParamStrValue).filter(
            GeneralParameter.ParamID == 'propid'
        ).first()
        kode_prov = str(query1[0]) if query1 else None

        query2 = db.session.query(tblUPTOpsen.UPTID).filter(
            tblUPTOpsen.KotaPropID.like(f"{kode_prov}%")
        ).all()
        uptid_list = [row[0] for row in query2] if query2 else []

        try:
            if checkintegrasi.IsIntegrasi == 1:
                print(checkintegrasi.IsIntegrasi)
                select_query = db.session.query( vw_setoran.HeaderID, vw_setoran.NoSTS, vw_setoran.StatusBayar,
                                                 vw_setoran.TglSetoran,
                                                 vw_setoran.JmlSetoran,
                                                 vw_setoran.Keterangan,
                                                 vw_setoran.SetoranDari,
                                                 vw_setoran.Badan.label( 'DinasPenghasil' ), vw_setoran.KodeStatus
                                                 ).distinct() \
                    .filter(
                    vw_setoran.Status == '1', vw_setoran.UPTStatus == '1', vw_setoran.WapuID == wapuid
                    # , extract('year', vw_setoran.TglSetoran) >= 2025
                )
            else:
                select_query = db.session.query(vw_setoran.HeaderID, vw_setoran.NoSTS, vw_setoran.StatusBayar,
                                                vw_setoran.TglSetoran,
                                                vw_setoran.JmlSetoran,
                                                vw_setoran.Keterangan,
                                                vw_setoran.SetoranDari,
                                                vw_setoran.Badan.label('DinasPenghasil'), vw_setoran.KodeStatus
                                                ).distinct() \
                    .filter(
                    vw_setoran.Status == '1', vw_setoran.UPTStatus == '1', vw_setoran.WapuID.in_(uptid_list)
                    # , extract('year', vw_setoran.TglSetoran) >= 2025
                )

            # FILTER_TGL
            if args['filter_tgl']:
                select_query = select_query.filter(
                    (vw_setoran.TglSetoran) == args['filter_tgl']
                )

            # FILTER_UPT
            if args['filter_upt']:
                select_query = select_query.filter(
                    (vw_setoran.WapuID) == args['filter_upt']
                )

            # SEARCH_JENIS
            if args['search_jenis']:
                select_query = select_query.filter(
                    vw_setoran.JenisPendapatanID == args['search_jenis']
                )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format( args['search'] )
                select_query = select_query.filter(
                    or_( vw_setoran.NoSTS.ilike( search ),
                         vw_setoran.TglSetoran.ilike(search),
                         vw_setoran.JmlSetoran.ilike(search),
                         vw_setoran.Keterangan.ilike(search)
                         )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr( vw_setoran, args['sort'] ).desc()
                else:
                    sort = getattr( vw_setoran, args['sort'] ).asc()
                select_query = select_query.order_by( sort )
            else:
                select_query = select_query.order_by( vw_setoran.TglSetoran,vw_setoran.SetoranDari,
                                                        vw_setoran.Keterangan.desc())

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate( page, lengthLimit )

            # print(query_execute.items)
            for row in query_execute.items:
                d = {}
                for key in row.keys():
                    # print(key,  getattr(row, key))
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads_pagination( query_execute, result )
        except Exception as e:
            print( e )
            return failed_reads( result )
        finally:
            session.close()
