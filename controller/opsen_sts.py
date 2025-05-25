from datetime import datetime

import requests
from flask import jsonify, request
from flask_restful import reqparse, Resource
from sqlalchemy import Integer, String, DateTime, Numeric, Identity, or_, func, and_, literal, distinct
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from sqlalchemy.orm import aliased
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination, success_reads
from config.config import baseUrlScheme, baseUrl, baseUrlPort
from config.database import db
from config.helper import parser
from controller.GeneralParameter import GeneralParameter
from controller.SetoranUPTDtl import SetoranUPTDtl
from controller.SetoranUPTHdr import SetoranUPTHdr
from controller.tblGroupUser import tblGroupUser
from controller.tblOpsen import tblOpsen
from controller.tblUPTOpsen import tblUPTOpsen
from controller.tblUser import tblUser

from sqlalchemy.orm import aliased
from sqlalchemy.sql import func, over
from sqlalchemy import select

    # Resource CRUD
class OpsenListResourceNotSTS4(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, headerid, *args, **kwargs):
        uid = kwargs['claim']["UID"]

        # Ambil API Key
        query = db.session.query(tblUser.APIKey).filter(tblUser.UID == uid).first()
        apikey = query[0] if query else None  # Ambil nilai API key langsung

        if not apikey:
            print("API Key tidak ditemukan!")
            return jsonify({"status": "error", "message": "API Key tidak valid"}), 401

        print(f"API Key: {apikey}")  # Debugging

        # Buat URL endpoint
        url = f"{baseUrlScheme}://{baseUrl}/opsensourcenotsend?HeaderID={headerid}"
        if baseUrlPort:
            url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/opsensourcenotsend?HeaderID={headerid}"

        try:
            # Panggil API eksternal
            response = requests.get(
                url,
                headers={
                    "APIKey": apikey
                }
            )

            if response.status_code != 200:
                return jsonify(
                    {"status": "error", "message": f"API Error: {response.status_code}"}), response.status_code

            # Parsing JSON dari response
            data = response.json()
            print("Response JSON:", data)

            # Validasi dan ambil data "HeaderID"
            list_data = data.get("data", [])
            header_ids = [item.get("HeaderID") for item in list_data if "HeaderID" in item]
            tgl_opsen = [item.get("TglSetoranOpsen") for item in list_data if "TglSetoranOpsen" in item]
            kota_kend = [item.get("KotaKendaraan") for item in list_data if "KotaKendaraan" in item]
            nmrek_opsen = [item.get("NamaRekeningOpsen") for item in list_data if "NamaRekeningOpsen" in item]

            if not header_ids:
                return jsonify({"status": "error", "message": "Data HeaderID tidak ditemukan"}), 404

            first_header_id = header_ids[0]  # Ambil HeaderID pertama
            print(f"HeaderID Pertama: {first_header_id}")

            first_tgl_opsen = tgl_opsen[0]
            first_kota_kend = kota_kend[0]
            first_nmrek_opsen = nmrek_opsen[0]

            # Ubah string ke objek datetime
            # first_tgl_opsen = '2025-01-06 00:00:00.000000'

            try:
                # Parsing string ke datetime
                try:
                    date_obj = datetime.strptime(first_tgl_opsen, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    # Coba format tanpa microsecond
                    date_obj = datetime.strptime(first_tgl_opsen, '%Y-%m-%d %H:%M:%S')

                # Format ulang ke 'YYYY-MM-DD'
                first_tgl_opsen = date_obj.strftime('%Y-%m-%d')

            except ValueError as e:
                print(f"Format tanggal salah: {e}")
                return jsonify({"status": "error", "message": "Format tanggal tidak valid"}), 400

            print(f"Tanggal setelah format: {first_tgl_opsen}")

            # Eksekusi query SQL untuk hasil berdasarkan HeaderID
            select_query = db.session.execute(
                f"""
                SELECT * FROM (
                    SELECT DISTINCT :headerid AS HeaderID,
                           pk.NoReg AS ObyekBadanNo, 
                    pk.NamaBadan, 
                    pk.Pemilik AS NamaPemilik, 

                    (CASE WHEN mjp.NamaJenisPendapatan IN('Opsen PKB','Opsen BBN-KB') THEN 
                                            (SELECT TOP(1) pk.KodeRekeningOpsen FROM PenetapanKB pk WHERE 
                                            pk.KodeRekeningOpsen =mjp.KodeRekening AND pk.NoReg = sbd.NoReg ) ELSE 
                                            mjp.KodeRekening END) KodeRekeningOpsen,
                    (CASE WHEN mjp.NamaJenisPendapatan IN('Opsen PKB','Opsen BBN-KB') THEN 
                                            'Opsen ' + (SELECT TOP(1) pk.NamaRekening FROM PenetapanKB pk WHERE 
                                            pk.KodeRekeningOpsen =mjp.KodeRekening AND pk.NoReg = sbd.NoReg ) ELSE 
                                            mjp.NamaJenisPendapatan END) AS Jenis,

                    '' AS TglJatuhTempo, 
                    'Lunas' AS StatPaid, 
                    pk.NoReg AS NoKohir, 
                    pk.NoReg AS OBN, 
                    pk.MasaPajak AS MP, 
                    pk.MasaPajak AS UrutMP, 
                    (CASE WHEN mjp.NamaJenisPendapatan IN('Opsen PKB','Opsen BBN-KB') THEN 
                                            (SELECT TOP(1) CAST(pk.JmlSetoranOpsen AS MONEY)
                                                          FROM PenetapanKB pk WHERE 
                                            pk.KodeRekeningOpsen =mjp.KodeRekening AND pk.NoReg = sbd.NoReg ) ELSE 
                                            CAST(pk.JmlDendaOpsen AS MONEY) END) AS JmlSetoran, 
                    pk.KohirID AS KohirID, 
                    'STS' AS STS, 
                    pk.NoReg AS KID, 
                    KodeBayar AS SSPD, 
                    '' AS CekSTS, 
                    KotaKendaraan AS Wilayah,
                    pk.ID AS DetailID 
                    FROM tblOpsen pk  
                    INNER JOIN SetoranUPTHdr sud ON LTRIM(RTRIM(sud.SetoranDari)) = LTRIM(RTRIM(pk.KotaKendaraan)) 
                    AND sud.TglSetoran = pk.TglSetoranOpsen  AND LTRIM(RTRIM(sud.Keterangan)) = LTRIM(RTRIM(pk.NamaRekeningOpsen)) 
                    INNER JOIN SetoranUPTDtl AS sbd ON sbd.HeaderID = sud.HeaderID AND pk.NoReg=sbd.NoReg 
                    INNER JOIN MsJenisPendapatan AS mjp ON mjp.JenisPendapatanID = sbd.JenisPendapatanID 
                    WHERE sbd.HeaderID=:headerid AND TglSetoranOpsen = :tglopsen AND  KotaKendaraan = :kotakend AND NamaRekeningOpsen=:nmrekopsen
                    ) AS sub
                    ORDER BY sub.ObyekBadanNo, sub.DetailID,sub.KodeRekeningOpsen
                    """,
                {"headerid": first_header_id,
                 "tglopsen": first_tgl_opsen,
                 'kotakend': first_kota_kend,
                 'nmrekopsen': first_nmrek_opsen
                 }
            )

            # Parsing hasil query
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)

            return success_reads(result)

        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": f"Request error: {str(e)}"}), 500

class OpsenListResourceNotSTS7(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        uid = kwargs['claim']["UID"]
        parser = reqparse.RequestParser()
        parser.add_argument('HeaderID', type=str, required=True, location='args')  # Tambahkan lokasi args
        args = parser.parse_args()
        headerid = args['HeaderID']

        query = db.session.query(tblUser.APIKey).filter(tblUser.UID == uid).first()
        apikey = query[0] if query else None  # Ambil nilai API key langsung

        if not apikey:
            print("API Key tidak ditemukan!")
            return jsonify({"status": "error", "message": "API Key tidak valid"}), 401

        print(f"API Key: {apikey}")  # Debugging

        url = f"{baseUrlScheme}://{baseUrl}/opsensourcenotsend?HeaderID={headerid}"
        if baseUrlPort:
            url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/opsensourcenotsend?HeaderID={headerid}"

        try:
            response = requests.get(
                url,
                headers={
                    "APIKey": apikey
                }
            )

            if response.status_code != 200:
                return jsonify(
                    {"status": "error", "message": f"API Error: {response.status_code}"}), response.status_code

            # Parsing JSON dari response
            data = response.json()
            print("Response JSON:", data)

            list_data = data.get("data", [])
            header_ids = [item.get("HeaderID") for item in list_data if "HeaderID" in item]
            tgl_opsen = [item.get("TglSetoranOpsen") for item in list_data if "TglSetoranOpsen" in item]
            kota_kend = [item.get("KotaKendaraan") for item in list_data if "KotaKendaraan" in item]
            nmrek_opsen = [item.get("NamaRekeningOpsen") for item in list_data if "NamaRekeningOpsen" in item]

            if not header_ids:
                return jsonify({"status": "error", "message": "Data HeaderID tidak ditemukan"}), 404

            first_header_id = header_ids[0]  # Ambil HeaderID pertama
            print(f"HeaderID Pertama: {first_header_id}")

            first_tgl_opsen = tgl_opsen[0]
            first_kota_kend = kota_kend[0]
            first_nmrek_opsen = nmrek_opsen[0]

            try:
                try:
                    date_obj = datetime.strptime(first_tgl_opsen, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    date_obj = datetime.strptime(first_tgl_opsen, '%Y-%m-%d %H:%M:%S')
                first_tgl_opsen = date_obj.strftime('%Y-%m-%d')

            except ValueError as e:
                print(f"Format tanggal salah: {e}")
                return jsonify({"status": "error", "message": "Format tanggal tidak valid"}), 400

            print(f"Tanggal setelah format: {first_tgl_opsen}")

            select_query = db.session.execute(
                f"""
                    SELECT :headerid AS HeaderID,
                           pk.NoReg AS ObyekBadanNo, 
                           pk.NamaBadan, 
                           pk.Pemilik AS NamaPemilik,

                           (CASE WHEN mjp.NamaJenisPendapatan IN('Opsen PKB','Opsen BBN-KB') THEN 
                                                (SELECT TOP(1) pk.KodeRekening FROM PenetapanKB pk WHERE 
                                                pk.KodeRekeningOpsen =mjp.KodeRekening AND pk.NoReg = sbd.NoReg ) ELSE 
                                                mjp.KodeRekening END) KodeRekening,
                            (CASE WHEN mjp.NamaJenisPendapatan IN('Opsen PKB','Opsen BBN-KB') THEN 
                                                (SELECT TOP(1) pk.NamaRekening FROM PenetapanKB pk WHERE 
                                                pk.KodeRekeningOpsen =mjp.KodeRekening AND pk.NoReg = sbd.NoReg ) ELSE 
                                                Replace(mjp.NamaJenisPendapatan,'Opsen','') END) AS Jenis,

                           '' AS TglJatuhTempo, 
                           'Lunas' AS StatPaid, 
                           pk.NoReg AS NoKohir, 
                           pk.NoReg AS OBN, 
                           pk.MasaPajak AS MP, 
                           pk.MasaPajak AS UrutMP, 
                           (CASE WHEN mjp.NamaJenisPendapatan IN('Opsen PKB','Opsen BBN-KB') THEN 
                                                (SELECT TOP(1) CAST(pk.Pajak AS MONEY)
                                                              FROM PenetapanKB pk WHERE 
                                                pk.KodeRekeningOpsen =mjp.KodeRekening AND pk.NoReg = sbd.NoReg ) ELSE 
                                                CAST(pk.Denda AS MONEY) END) AS JmlSetoran,  
                           pk.KohirID AS KohirID, 
                           'STS' AS STS, 
                           pk.NoReg AS KID, 
                           KodeBayar AS SSPD, 
                           '' AS CekSTS, 
                           KotaKendaraan AS Wilayah,
                           pk.ID AS DetailID 
                        FROM tblOpsen pk  
                        INNER JOIN SetoranUPTHdr sud ON LTRIM(RTRIM(sud.SetoranDari)) = LTRIM(RTRIM(pk.KotaKendaraan)) 
                        AND sud.TglSetoran = pk.TglSetoranOpsen  
                        AND LTRIM(RTRIM(sud.Keterangan)) = LTRIM(RTRIM(pk.NamaRekeningOpsen)) 
                        INNER JOIN SetoranUPTDtl AS sbd ON sbd.HeaderID = sud.HeaderID AND pk.NoReg=sbd.NoReg 
                        INNER JOIN MsJenisPendapatan AS mjp ON mjp.JenisPendapatanID = sbd.JenisPendapatanID
                    WHERE sbd.HeaderID=:headerid AND TglSetoranOpsen = :tglopsen AND  KotaKendaraan = :kotakend AND NamaRekeningOpsen=:nmrekopsen
                    ORDER BY pk.NoReg, sbd.DetailID,pk.KodeRekening
                    """,
                {"headerid": first_header_id,
                 "tglopsen": first_tgl_opsen,
                 'kotakend': first_kota_kend,
                 'nmrekopsen': first_nmrek_opsen
                 }
            )

            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)

            return success_reads(result)

        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": f"Request error: {str(e)}"}), 500


class OpsenListResourceNotSTS(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):

        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('length', type=int)
        parser.add_argument('sort', type=str)
        parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
        parser.add_argument('search', type=str)
        parser.add_argument('filter_upt', type=str)
        parser.add_argument('filter_tgl', type=str)
        parser.add_argument('HeaderID', type=str)

        args = parser.parse_args()
        # Aliases untuk tabel
        # tbl_opsen_alias = aliased(tblOpsen)
        # setoran_upthdr_alias = aliased(SetoranUPTHdr)
        # setoran_uptdtl_alias = aliased(SetoranUPTDtl)
        wapuid = kwargs['claim']["WapuID"]
        tbl_opsen_alias = aliased(tblOpsen)
        setoran_upthdr_alias = aliased(SetoranUPTHdr)
        setoran_uptdtl_alias = aliased(SetoranUPTDtl)
        groupid = kwargs['claim']["GroupId"]
        checkadmin = tblGroupUser.query.filter_by(
            GroupId=groupid
        ).first()

        query1 = db.session.query(GeneralParameter.ParamStrValue).filter(
            GeneralParameter.ParamID == 'propid'
        ).first()
        kode_prov = str(query1[0]) if query1 else None

        query2 = db.session.query(tblUPTOpsen.UPTID).filter(
            tblUPTOpsen.KotaPropID.like(f"{kode_prov}%")
        ).all()
        uptid_list = [row[0] for row in query2] if query2 else []

        if checkadmin.IsAdmin == 1:
        # Query for CTE
            select_query = (
                db.session.query(
                    # func.row_number().over(
                    #     order_by=[
                    #         tbl_opsen_alias.KotaKendaraan,
                    #         tbl_opsen_alias.TglSetoranOpsen,
                    #         tbl_opsen_alias.NamaRekeningOpsen
                    #     ]
                    # ).label("HeaderID"),
                    setoran_upthdr_alias.HeaderID,
                    tbl_opsen_alias.KotaKendaraan,
                    setoran_upthdr_alias.HeaderID.label("NoSTS"),
                    tbl_opsen_alias.KodeRekeningOpsen,
                    tbl_opsen_alias.NamaRekeningOpsen,
                    tbl_opsen_alias.TglSetoranOpsen,
                    func.sum(setoran_uptdtl_alias.JmlSetoran) .label("JmlSetoranOpsen")
                )
                .outerjoin(
                    setoran_upthdr_alias,
                    and_(
                        func.ltrim(func.rtrim(setoran_upthdr_alias.SetoranDari)) ==
                        func.ltrim(func.rtrim(tbl_opsen_alias.KotaKendaraan)),
                        setoran_upthdr_alias.TglSetoran == tbl_opsen_alias.TglSetoranOpsen,
                        func.ltrim(func.rtrim(setoran_upthdr_alias.Keterangan)) ==
                        func.ltrim(func.rtrim(tbl_opsen_alias.NamaRekeningOpsen))
                    )
                )
                .outerjoin(
                    setoran_uptdtl_alias,
                    and_(
                        setoran_uptdtl_alias.HeaderID == setoran_upthdr_alias.HeaderID,
                        tbl_opsen_alias.NoReg == setoran_uptdtl_alias.NoReg,
                        tbl_opsen_alias.OpsenID == setoran_uptdtl_alias.id
                    )
                )
                .filter(tbl_opsen_alias.UPTID.in_(uptid_list))
                .group_by(
                    tbl_opsen_alias.KotaKendaraan,
                    setoran_upthdr_alias.HeaderID,
                    tbl_opsen_alias.KodeRekeningOpsen,
                    tbl_opsen_alias.NamaRekeningOpsen,
                    tbl_opsen_alias.TglSetoranOpsen
                )
            )

            # Membuat subquery tanpa eksekusi
            subquery = select_query.subquery()
            aliased_query = db.session.query(subquery)
        else:
            select_query = (
                db.session.query(
                    # func.row_number().over(
                    #     order_by=[
                    #         tbl_opsen_alias.KotaKendaraan,
                    #         tbl_opsen_alias.TglSetoranOpsen,
                    #         tbl_opsen_alias.NamaRekeningOpsen
                    #     ]
                    # ).label("HeaderID"),
                    setoran_upthdr_alias.HeaderID,
                    tbl_opsen_alias.KotaKendaraan,
                    setoran_upthdr_alias.HeaderID.label("NoSTS"),
                    tbl_opsen_alias.KodeRekeningOpsen,
                    tbl_opsen_alias.NamaRekeningOpsen,
                    tbl_opsen_alias.TglSetoranOpsen,
                    func.sum(setoran_uptdtl_alias.JmlSetoran).label("JmlSetoranOpsen")
                )
                .outerjoin(
                    setoran_upthdr_alias,
                    and_(
                        func.ltrim(func.rtrim(setoran_upthdr_alias.SetoranDari)) ==
                        func.ltrim(func.rtrim(tbl_opsen_alias.KotaKendaraan)),
                        setoran_upthdr_alias.TglSetoran == tbl_opsen_alias.TglSetoranOpsen,
                        func.ltrim(func.rtrim(setoran_upthdr_alias.Keterangan)) ==
                        func.ltrim(func.rtrim(tbl_opsen_alias.NamaRekeningOpsen))
                    )
                )
                .outerjoin(
                    setoran_uptdtl_alias,
                    and_(
                        setoran_uptdtl_alias.HeaderID == setoran_upthdr_alias.HeaderID,
                        tbl_opsen_alias.NoReg == setoran_uptdtl_alias.NoReg,
                        tbl_opsen_alias.OpsenID == setoran_uptdtl_alias.id
                    )
                )
                .group_by(
                    tbl_opsen_alias.KotaKendaraan,
                    setoran_upthdr_alias.HeaderID,
                    tbl_opsen_alias.KodeRekeningOpsen,
                    tbl_opsen_alias.NamaRekeningOpsen,
                    tbl_opsen_alias.TglSetoranOpsen
                )
            ).filter(tbl_opsen_alias.UPTID == wapuid)

            # Membuat subquery tanpa eksekusi
            subquery = select_query.subquery()
            aliased_query = db.session.query(subquery)

        if args['HeaderID']:
            subquery = select_query.subquery()
            aliased_query = db.session.query(subquery)

            select_query = db.session.query(subquery).filter(
                subquery.c.HeaderID == args['HeaderID']
            )

        # FILTER_TGL
        if args['filter_tgl']:
            select_query = select_query.filter(
                (tbl_opsen_alias.TglSetoranOpsen) == args['filter_tgl']
            )

        # FILTER_UPT
        if args['filter_upt']:
            select_query = select_query.filter(
                (tbl_opsen_alias.UPTID) == args['filter_upt']
            )

        # SEARCH
        if args['search'] and args['search'] != 'null':
            search = '%{0}%'.format(args['search'])
            select_query = select_query.filter(
                or_(tbl_opsen_alias.NoReg.ilike(search),
                    tbl_opsen_alias.Pemilik.ilike(search))
            )

        # SORT
        if args['sort']:
            if args['sort_dir'] == "desc":
                sort = getattr(tbl_opsen_alias, args['sort']).desc()
            else:
                sort = getattr(tbl_opsen_alias, args['sort']).asc()
            select_query = select_query.order_by(sort)
        else:
            select_query = select_query.order_by(tbl_opsen_alias.TglSetoranOpsen,tbl_opsen_alias.KotaKendaraan,
                                                     tbl_opsen_alias.NamaRekeningOpsen.desc())

        # PAGINATION
        page = args['page'] if args['page'] else 1
        length = args['length'] if args['length'] else 10
        lengthLimit = length if length < 101 else 100
        query_execute = select_query.paginate(page, lengthLimit)

        result = []
        for row in query_execute.items:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads_pagination(query_execute, result)

class KotaKend(Resource):
    def get(self, headerid, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT DISTINCT KotaKendaraan FROM tblOpsen ORDER BY KotaKendaraan '")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)