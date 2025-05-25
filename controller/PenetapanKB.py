import json
import logging
import re

import requests
import hashlib
import time
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, literal, text, case
import requests
from flask import jsonify, request
from flask_restful import reqparse, Resource
from sqlalchemy import Integer, String, DateTime, Numeric, Identity, or_, func, and_, literal, literal_column
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from sqlalchemy.orm import aliased
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination, success_reads, failed_reads
from config.config import baseUrlScheme, baseUrl, baseUrlPort
from config.database import db
from config.helper import parser, logger
from controller.ApiUrl import ApiUrl
from controller.GeneralParameter import GeneralParameter
from controller.MsPropinsi import MsPropinsi
from controller.tblGroupUser import tblGroupUser
from controller.tblOpsen import tblOpsen
from controller.tblUPTOpsen import tblUPTOpsen
from controller.tblUser import tblUser

# Mengatur Base dengan metadata khusus jika diperlukan
Base = declarative_base()


class PenetapanKB(db.Model, SerializerMixin):
    __tablename__ = 'PenetapanKB'

    ID = db.Column(db.BigInteger, primary_key=True, autoincrement=True, nullable=False)
    HeaderID = db.Column(db.Integer, nullable=True)
    NoReg = db.Column(db.String(50), nullable=False)
    KohirID = db.Column(db.String(50), nullable=False)
    NamaBadan = db.Column(db.String(100), nullable=True)
    Pemilik = db.Column(db.String(100), nullable=True)
    Wilayah = db.Column(db.String(100), nullable=True)
    UPTID = db.Column(db.Integer, nullable=True)
    KotaKendaraan = db.Column(db.String(50), nullable=False)
    KodeRekening = db.Column(db.String(50), nullable=True)
    NamaRekening = db.Column(db.String(100), nullable=True)
    MasaPajak = db.Column(db.String(30), nullable=True)
    Pajak = db.Column(db.Float, nullable=True)
    Denda = db.Column(db.Float, nullable=True)
    JmlBayar = db.Column(db.Float, nullable=True)
    KodeBayar = db.Column(db.String(50), nullable=True)
    TglBayar = db.Column(db.DateTime, nullable=True)
    Channel = db.Column(db.String(50), nullable=True)
    NoSTS = db.Column(db.String(50), nullable=True)
    KodeRekeningOpsen = db.Column(db.String(50), nullable=True)
    NamaRekeningOpsen = db.Column(db.String(100), nullable=True)
    TglSetoranOpsen = db.Column(db.DateTime, nullable=True)
    JmlSetoranOpsen = db.Column(db.Float, nullable=True)
    JmlDendaOpsen = db.Column(db.Float, nullable=True)
    Keterangan = db.Column(db.String(255), nullable=True)
    NTPD = db.Column(db.String(50), nullable=True)
    UserUpd = db.Column(db.String(50), nullable=True)
    DateUpd = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Parsers
    parse = reqparse.RequestParser()
    parser.add_argument('NoReg', type=str, required=True, help="NoReg tidak boleh kosong.")
    parser.add_argument('KohirID', type=str, required=True, help="KohirID tidak boleh kosong.")
    parser.add_argument('Pemilik', type=str, required=True, help="Nama Pemilik tidak boleh kosong.")
    parser.add_argument('Wilayah', type=str, required=True, help="Wilayah tidak boleh kosong.")
    parser.add_argument('UPTID', type=str, required=True, help="UPTID tidak boleh kosong.")
    parser.add_argument('KotaKendaraan', type=str, required=True, help="Wilayah tidak boleh kosong.")
    parser.add_argument('Masapajak', type=str, required=True, help="Masapajak tidak boleh kosong.")
    parser.add_argument('KodeRekening', type=str, required=True, help="Kode Rekening tidak boleh kosong.")
    parser.add_argument('NamaRekening', type=str, required=True, help="Nama Rekening tidak boleh kosong.")
    parser.add_argument('Pajak', type=float, required=True, help="Pajak harus berupa angka.")
    parser.add_argument('Denda', type=float, required=True, help="Denda harus berupa angka.")
    parser.add_argument('TglBayar', type=str, required=False, help="Tanggal Bayar dalam format YYYY-MM-DD.")
    parser.add_argument('Channel', type=str, required=True, help="Channel tidak boleh kosong.")
    parser.add_argument('NoSTS', type=str, required=True, help="NoSTS tidak boleh kosong.")
    parser.add_argument('KodeRekeningOpsen', type=str, required=False, help="Kode Rekening Opsen tidak wajib.")
    parser.add_argument('NamaRekeningOpsen', type=str, required=False, help="Nama Rekening Opsen tidak wajib.")
    parser.add_argument('TglSetoranOpsen', type=str, required=False,
                        help="Tanggal Setoran Opsen dalam format YYYY-MM-DD.")
    parser.add_argument('JmlSetoranOpsen', type=float, required=False, help="Jumlah Setoran Opsen harus berupa angka.")
    parser.add_argument('JmlDendaOpsen', type=float, required=False, help="Jumlah Denda Opsen harus berupa angka.")
    parser.add_argument('Keterangan', type=str, required=False, help="Keterangan tidak wajib.")
    parser.add_argument('NTPD', type=str, required=True, help="NTPD tidak boleh kosong.")

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    # Resource CRUD
    class listAll(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege]}

        def get(self,*args, **kwargs):

            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int, default=1)
            parser.add_argument('length', type=int, default=10)
            parser.add_argument('sort', type=str, default='OpsenID')
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
            parser.add_argument('search', type=str)
            parser.add_argument('filter_upt', type=str)
            parser.add_argument('filter_tgl', type=str)

            args = parser.parse_args()
            uid = kwargs['claim']["UID"]

            select_query = db.session.query(PenetapanKB)

            # Filter berdasarkan parameter (jika ada)
            if args['search']:
                select_query = select_query.filter(tblOpsen.name.ilike(f"%{args['search']}%"))

            # Sorting
            if args['sort_dir'] == 'desc':
                select_query = select_query.order_by(getattr(tblOpsen, args['sort']).desc())
            else:
                select_query = select_query.order_by(getattr(tblOpsen, args['sort']).asc())

            # Pagination
            page = args['page']
            length = args['length']
            paginated_query = select_query.paginate(page=page, per_page=length, error_out=False)

            # Konversi hasil query ke JSON
            json_data = [row.as_dict() for row in paginated_query.items]

            # Response JSON
            return jsonify({
                "status": "success",
                "page": page,
                "length": length,
                "total": paginated_query.total,
                "data": json_data
            })

    class PenetapanKBResource4(Resource):
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
            url = f"{baseUrlScheme}://{baseUrl}/opsensource?HeaderID={headerid}"
            if baseUrlPort:
                url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/opsensource?HeaderID={headerid}"

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

                print(first_tgl_opsen)
                print(first_kota_kend)
                print(first_nmrek_opsen)

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

                # Eksekusi query SQL untuk hasil berdasarkan HeaderID
                from sqlalchemy import text

                select_query = db.session.execute(
                    text("""
                        SELECT HeaderID, ObyekBadanNo,
                               NamaBadan,
                               NamaPemilik,
                               KodeRekeningOpsen,
                               Jenis,
                               TglJatuhTempo,
                               StatPaid,
                               NoKohir,
                               OBN,
                               MP,
                               UrutMP,
                               JmlSetoran,
                               KohirID,
                               STS,
                               KID,
                               SSPD,
                               CekSTS,
                               Wilayah,
                               DetailID
                        FROM (
                            -- Bagian Setoran Opsen
                            SELECT :headerid AS HeaderID,
                                   pk.NoReg AS ObyekBadanNo,
                                   pk.NamaBadan,
                                   pk.Pemilik AS NamaPemilik,
                                   pk.KodeRekeningOpsen,
                                   'Opsen ' + ISNULL(rek.NamaRekening, '') AS Jenis,
                                   '' AS TglJatuhTempo,
                                   'Lunas' AS StatPaid,
                                   pk.NoReg AS NoKohir,
                                   pk.NoReg AS OBN,
                                   pk.MasaPajak AS MP,
                                   pk.MasaPajak AS UrutMP,
                                   CAST(pk.JmlSetoranOpsen AS MONEY) AS JmlSetoran,
                                   pk.KohirID,
                                   'STS' AS STS,
                                   pk.NoReg AS KID,
                                   pk.KodeBayar AS SSPD,
                                   '' AS CekSTS,
                                   pk.KotaKendaraan AS Wilayah,
                                   pk.ID AS DetailID
                            FROM PenetapanKB pk
                            OUTER APPLY (
                                SELECT TOP 1 NamaRekening
                                FROM PenetapanKB sub
                                WHERE sub.ID = pk.ID
                            ) AS rek
                            LEFT JOIN MsJenisPendapatan mjp
                              ON LTRIM(RTRIM(mjp.KodeRekening)) = LTRIM(RTRIM(pk.KodeRekeningOpsen))
                            WHERE 
                                pk.TglSetoranOpsen = :tglopsen
                              AND pk.KotaKendaraan = :kotakend
                              AND pk.NamaRekeningOpsen = :nmrekopsen
                              AND 
                              pk.HeaderID = :headerid

                            UNION ALL

                            -- Bagian Denda Opsen
                            SELECT :headerid AS HeaderID,
                                   pk.NoReg AS ObyekBadanNo,
                                   pk.NamaBadan,
                                   pk.Pemilik AS NamaPemilik,
                                   CASE
                                       WHEN pk.JmlDendaOpsen > 0 AND mjp.NamaJenisPendapatan = 'Opsen PKB' THEN '4.1.04.25.01.0001.'
                                       WHEN pk.JmlDendaOpsen > 0 AND mjp.NamaJenisPendapatan = 'Opsen BBN-KB' THEN '4.1.04.26.01.0001.'
                                       ELSE NULL
                                   END AS KodeRekeningOpsen,
                                   CASE
                                       WHEN pk.JmlDendaOpsen > 0 AND mjp.NamaJenisPendapatan = 'Opsen PKB'
                                           THEN 'Denda Opsen ' + ISNULL(rek2.NamaRekening, '')
                                       WHEN pk.JmlDendaOpsen > 0 AND mjp.NamaJenisPendapatan = 'Opsen BBN-KB'
                                           THEN 'Denda Opsen ' + ISNULL(REPLACE(rek2.NamaRekening, 'PKB', 'BBN-KB'), '')
                                       ELSE NULL
                                   END AS Jenis,
                                   '' AS TglJatuhTempo,
                                   'Lunas' AS StatPaid,
                                   pk.NoReg AS NoKohir,
                                   pk.NoReg AS OBN,
                                   pk.MasaPajak AS MP,
                                   pk.MasaPajak AS UrutMP,
                                   CAST(pk.JmlDendaOpsen AS MONEY) AS JmlSetoran,
                                   pk.KohirID,
                                   'STS' AS STS,
                                   pk.NoReg AS KID,
                                   pk.KodeBayar AS SSPD,
                                   '' AS CekSTS,
                                   pk.KotaKendaraan AS Wilayah,
                                   pk.ID AS DetailID
                            FROM PenetapanKB pk
                            OUTER APPLY (
                                SELECT TOP 1 NamaRekening
                                FROM PenetapanKB sub
                                WHERE sub.ID = pk.ID
                            ) AS rek2
                            LEFT JOIN MsJenisPendapatan mjp
                              ON LTRIM(RTRIM(mjp.KodeRekening)) = LTRIM(RTRIM(pk.KodeRekeningOpsen))
                            WHERE 
                              pk.TglSetoranOpsen = :tglopsen
                              AND pk.KotaKendaraan = :kotakend
                              AND pk.NamaRekeningOpsen = :nmrekopsen
                              AND 
                              pk.HeaderID = :headerid
                        ) A
                        WHERE A.KodeRekeningOpsen IS NOT NULL
                        ORDER BY A.ObyekBadanNo, A.NamaPemilik, A.KodeRekeningOpsen
                    """),
                    # text("EXEC GetDataPenetapanKB :headerid, :tglopsen, :kotakend, :nmrekopsen"),
                    {
                        "headerid": first_header_id,
                        "tglopsen": first_tgl_opsen,
                        "kotakend": first_kota_kend,
                        "nmrekopsen": first_nmrek_opsen
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

    class PenetapanKBResource7(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege]}

        def get(self,  *args, **kwargs):
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

            url = f"{baseUrlScheme}://{baseUrl}/opsensource?HeaderID={headerid}"
            if baseUrlPort:
                url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/opsensource?HeaderID={headerid}"

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
                        SELECT HeaderID, ObyekBadanNo, 
                        NamaBadan, 
                        NamaPemilik, 
                        KodeRekeningOpsen,
                        Jenis,
                        TglJatuhTempo, 
                        StatPaid, 
                        NoKohir, 
                        OBN, 
                        MP, 
                        UrutMP, 
                        JmlSetoran,                        
                        KohirID, 
                        STS, 
                        KID, 
                        SSPD, 
                        CekSTS, 
                        Wilayah,
                        DetailID FROM (
    
                        SELECT :headerid AS HeaderID,
                        pk.NoReg AS ObyekBadanNo, 
                        pk.NamaBadan, 
                        pk.Pemilik AS NamaPemilik, 
                        pk.KodeRekeningOpsen,
                        pk.NamaRekening AS Jenis,
                        '' AS TglJatuhTempo, 
                        'Lunas' AS StatPaid, 
                        pk.NoReg AS NoKohir, 
                        pk.NoReg AS OBN, 
                        pk.MasaPajak AS MP, 
                        pk.MasaPajak AS UrutMP, 
                        CAST(pk.Pajak AS MONEY) AS JmlSetoran,                        
                        pk.KohirID AS KohirID, 
                        'STS' AS STS, 
                        pk.NoReg AS KID, 
                        KodeBayar AS SSPD, 
                        '' AS CekSTS, 
                        KotaKendaraan AS Wilayah,
                        pk.ID AS DetailID 
                        FROM PenetapanKB pk  
                        LEFT JOIN MsJenisPendapatan AS mjp ON LTRIM(RTRIM(mjp.KodeRekening)) = LTRIM(RTRIM(pk.KodeRekeningOpsen))
                        WHERE TglSetoranOpsen = :tglopsen AND  KotaKendaraan = :kotakend AND NamaRekeningOpsen=:nmrekopsen
    
                        UNION ALL
    
                        SELECT :headerid AS HeaderID,
                        pk.NoReg AS ObyekBadanNo, 
                        pk.NamaBadan, 
                        pk.Pemilik AS NamaPemilik, 
                        (CASE WHEN pk.JmlDendaOpsen>0 AND mjp.NamaJenisPendapatan ='Opsen PKB' THEN '4.1.04.25.01.0001.' ELSE 
                        (CASE WHEN pk.JmlDendaOpsen>0 AND mjp.NamaJenisPendapatan ='Opsen BBN-KB' THEN '4.1.04.26.01.0001.' END) END) AS KodeRekeningOpsen,
                        (CASE WHEN pk.JmlDendaOpsen>0 AND mjp.NamaJenisPendapatan ='Opsen PKB' THEN 'Denda ' + (SELECT TOP(1) pk.NamaRekening FROM PenetapanKB pk1 WHERE pk1.ID=pk.ID) ELSE 
                        (CASE WHEN pk.JmlDendaOpsen>0 AND mjp.NamaJenisPendapatan ='Opsen BBN-KB' THEN 'Denda ' + (SELECT TOP(1) pk.NamaRekening FROM PenetapanKB pk1 WHERE pk1.ID=pk.ID)                                         
                         END) END) AS Jenis,
                        '' AS TglJatuhTempo, 
                        'Lunas' AS StatPaid, 
                        pk.NoReg AS NoKohir, 
                        pk.NoReg AS OBN, 
                        pk.MasaPajak AS MP, 
                        pk.MasaPajak AS UrutMP, 
                        CAST(pk.Denda AS MONEY) AS JmlSetoran,                        
                        pk.KohirID AS KohirID, 
                        'STS' AS STS, 
                        pk.NoReg AS KID, 
                        KodeBayar AS SSPD, 
                        '' AS CekSTS, 
                        KotaKendaraan AS Wilayah,
                        pk.ID AS DetailID 
                        FROM PenetapanKB pk  
                        LEFT JOIN MsJenisPendapatan AS mjp ON LTRIM(RTRIM(mjp.KodeRekening)) = LTRIM(RTRIM(pk.KodeRekeningOpsen))
                        WHERE TglSetoranOpsen = :tglopsen AND  KotaKendaraan = :kotakend AND NamaRekeningOpsen=:nmrekopsen
                        )A
                        WHERE A.KodeRekeningOpsen IS NOT NULL
                        ORDER BY A.ObyekBadanNo,A.NamaPemilik, A.KodeRekeningOpsen
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

    class PenetapanKBResource(Resource):
        method_decorators = {'post': [tblUser.auth_apikey_privilege], 'get': [tblUser.auth_apikey_privilege]}

        # API_URL = "http://103.168.147.14:5003/opsen.svc/transaksi"
        # API_URL = "http://103.79.130.156:5080/opsen.svc/transaksi"
        # API_URL = "http://103.79.130.156:8888/opsen.svc/transaksi"

        def post(self, *args, **kwargs):

            filter_tgl = request.args.get('filter_tgl', default=None, type=str)
            filter_upt = request.args.get('filter_upt', default=None, type=str)

            # 🔹 Ambil WapuID & GroupId dari klaim JWT
            wapu_id = kwargs['claim'].get("WapuID")
            groupid = kwargs['claim'].get("GroupId")
            print(f"🔹 WapuID: {wapu_id}, GroupID: {groupid}")
            wapuid = wapu_id if wapu_id else filter_upt

            query = db.session.query(func.left(tblUPTOpsen.KotaPropID, 2)).filter(
                tblUPTOpsen.UPTID == wapuid
            ).first()
            kode_prop = query[0] if query else None

            query2 = db.session.query(MsPropinsi.PropinsiID).filter(MsPropinsi.Kode == kode_prop).first()
            prov_id = query2[0] if query2 else None

            query3 = db.session.query(ApiUrl.Url).filter(ApiUrl.PropinsiID == prov_id).first()
            api_url = query3[0] if query3 else None

            self.API_URL = api_url
            print(f"➡ [POST] API URL:{self.API_URL}")

            print(f"➡ filter_tglL:{filter_tgl}")
            print(f"➡ filter_upt:{filter_upt}")
            print("\n🔹 [DEBUG] Memulai proses transaksi...")
            print(f"➡ [POST] API URL: {self.API_URL}")
            print(f"[DEBUG] kode_prov: {kode_prop}")
            print(f"[DEBUG] prov_id: {prov_id}")
            print(f"[DEBUG] api_url: {api_url}")

            # 🔹 Ambil wilayah dari database
            query = db.session.query(tblUPTOpsen.KotaPropID).filter(tblUPTOpsen.UPTID == wapuid).first()
            wilayah = query[0] if query else None
            if not wilayah:
                print("❌ Wilayah tidak ditemukan dalam database!")
                return {"message": "Wilayah tidak ditemukan!"}, 400
            print(f"✅ Wilayah ditemukan: {wilayah}")

            # 🔹 Ambil waktu server dari API
            server_time_obj = self.get_server_time_from_api()
            if not server_time_obj:
                print("❌ Gagal mendapatkan waktu server dari API!")
                return {"message": "Gagal mendapatkan waktu server dari API!"}, 500

            # 🔹 Format waktu & timestamp sesuai server
            time_str = server_time_obj.strftime("%Y-%m-%d %H:%M:%S")
            timestamp = str(int(server_time_obj.replace(tzinfo=timezone.utc).timestamp()))

            # 🔹 String sebelum hash
            mode = "Integrasi-Opsen"
            sign_string = f"{mode}{time_str}{timestamp}"

            # 🔹 Buat hash SHA-256
            sign = hashlib.sha256(sign_string.encode('utf-8')).hexdigest().lower()

            # 🔹 Debugging Sign
            print("\n🔹 [DEBUG] Hashing Details:")
            print(f"   - String sebelum hash: {sign_string}")
            print(f"   - SHA-256 Hash yang dikirim: {sign}")
            print(f"   - Timestamp: {timestamp}")
            print(f"   - Waktu yang digunakan untuk request: {time_str}")

            # 🔹 Format JSON Payload
            request_body = {
                "mode": mode,
                "time": time_str,  # ✅ Sesuai waktu yang digunakan dalam hash
                "sign": sign,
                "wilayah": str(wilayah),
                "tanggal": filter_tgl
            }

            # 🔹 Kirim ke API
            api_response = self.call_api_transaksi(request_body)

            if not api_response:
                print("❌ Gagal mendapatkan data dari API transaksi.")
                return {
                    'message': 'Gagal mengambil data dari API transaksi.',
                    'api_url': self.API_URL,
                    'request_body': request_body
                }, 500

            # 🔹 Debugging Response
            print("\n🔹 [DEBUG] Response API:")
            print(json.dumps(api_response, indent=2))

            if not api_response.get("transaksi"):
                print("⚠️ Data transaksi kosong, tetapi tidak dianggap error.")
                return {
                    "message": "Data transaksi kosong",
                    "api_response": api_response
                }, 200  # ⬅️ Ubah dari 400 ke 200

            print("✅ Data berhasil diterima dari API!")

            # 🔹 Hapus data lama berdasarkan WapuID dan TglSetoranOpsen
            delete_count = db.session.query(PenetapanKB).filter(
                PenetapanKB.UPTID == wapuid,
                PenetapanKB.TglSetoranOpsen == filter_tgl
            ).delete()
            db.session.commit()

            print(f"✅ {delete_count} data lama dihapus sebelum insert data baru.")

            new_entries = self.prepare_new_entries(kwargs, api_response,
                                                   wapuid)  # 🔄 Ini sekarang akan dieksekusi
            if new_entries:
                db.session.add_all(new_entries)
                db.session.commit()  # Pastikan perubahan disimpan
                print(f"✅ {len(new_entries)} entri baru berhasil dimasukkan ke database!")
                update_headerid_sql = """
                WITH CTE_Group AS (
                    SELECT
                        ID,
                        DENSE_RANK() OVER (
                            ORDER BY KotaKendaraan, NamaRekeningOpsen, TglSetoranOpsen
                        ) AS HeaderGroup
                    FROM PenetapanKB
                )
                UPDATE p
                SET HeaderID = g.HeaderGroup
                FROM PenetapanKB p
                JOIN CTE_Group g ON p.ID = g.ID;
                """

                db.session.execute(text(update_headerid_sql))
                db.session.commit()

            else:
                print(f"✅ {len(new_entries)} entri siap disimpan ke database.")

            print("⚠ Tidak ada entri baru yang perlu dimasukkan ke database.")

            return {
                'message': 'Data berhasil diterima dan disimpan ke database!',
                'api_response': api_response
            }, 200



        def get_server_time_from_api(self):
            """
            Ambil waktu server dari response API transaksi terakhir.
            """
            print("\n🔹 [DEBUG] Mengambil waktu server dari API...")

            dummy_payload = {
                "mode": "Cek Waktu",
                "time": "",
                "sign": "",
                "wilayah": "",
                "tanggal": ""
            }

            try:
                response = requests.post(self.API_URL, data=json.dumps(dummy_payload))
                print(f"➡ Status code dari server time: {response.status_code}")

                if response.status_code == 200:
                    response_json = response.json()
                    server_time_str = response_json.get("serverTime")
                    print(f"✅ Waktu server yang diterima: {server_time_str}")

                    if server_time_str:
                        return datetime.strptime(server_time_str, "%Y-%m-%d %H:%M:%S")
            except requests.exceptions.RequestException as e:
                print("❌ Terjadi error saat request waktu server:", str(e))

            return datetime.now()  # Jika gagal, pakai waktu lokal

        def call_api_transaksi(self, payload):
            """
            Mengirim request transaksi ke API dengan format JSON.
            """

            payload_str = json.dumps(payload, ensure_ascii=False)

            print("\n🔹 [DEBUG] Request yang dikirim:")
            print("➡ URL:", self.API_URL)
            print("🔹 Payload:", json.dumps(payload, indent=2, ensure_ascii=False))

            try:
                with requests.Session() as session:
                    response = session.post(self.API_URL, data=payload_str, verify=False)

                print("\n🔹 [DEBUG] Response API:")
                print("➡ Status code:", response.status_code)
                print("➡ Response body:", response.text[:500])

                if response.status_code == 200:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        print("❌ Gagal decode JSON.")
                        return None
                else:
                    print(f"❌ Gagal mengambil data. Status code: {response.status_code}")
                    return None
            except requests.exceptions.RequestException as e:
                print("❌ Terjadi error saat request:", str(e))
                return None

        def prepare_new_entries(self, kwargs, data, wapuid):
            print(f"\n🔹 [DEBUG] Mulai prepare_new_entries. Total data dari API: {len(data)}")
            uid = kwargs['claim']["UID"]

            # 🛠️ Periksa apakah data adalah list atau dictionary
            if isinstance(data, list):
                print("🔹 [DEBUG] Data adalah list, mencoba mengambil elemen pertama...")
                if len(data) > 0:
                    first_entry = data[0]  # Ambil elemen pertama
                    if isinstance(first_entry, dict) and "tanggal" in first_entry and "lokasi_bayar" in first_entry:
                        data = first_entry  # Gunakan entry ini sebagai dictionary utama
                    else:
                        print("❌ ERROR: Struktur data tidak sesuai! Tidak ditemukan 'tanggal' dan 'lokasi_bayar'.")
                        print(json.dumps(first_entry, indent=2, ensure_ascii=False))
                        return []  # Hentikan jika struktur salah
                else:
                    print("❌ ERROR: Data dari API kosong!")
                    return []  # Hentikan jika kosong

            if not isinstance(data, dict):
                print(f"❌ ERROR: Data bukan dictionary setelah proses awal! Tipe: {type(data)}")
                return []

            # ✅ Ambil tanggal dan lokasi bayar
            tanggal_str = data.get("tanggal", "1970-01-01")
            lokasi_bayar = data.get("lokasi_bayar", "UNKNOWN")
            print(f"🔹 [DEBUG] Tanggal dari API setelah get(): {tanggal_str}")
            print(f"🔹 [DEBUG] Lokasi Bayar dari API setelah get(): {lokasi_bayar}")

            # Konversi tanggal string ke objek datetime
            try:
                tgl_bayar = datetime.strptime(tanggal_str, "%Y-%m-%d")
                tgl_setoran_opsen = datetime.strptime(tanggal_str, "%Y-%m-%d")
            except ValueError:
                print(f"❌ ERROR: Format tanggal salah! Tidak bisa diubah: {tanggal_str}")
                return []

            # 🔹 Ambil data transaksi
            transaksi_list = data.get("transaksi", [])
            if not isinstance(transaksi_list, list):
                print("❌ ERROR: Data transaksi bukan list!")
                return []

            print(f"✅ Data transaksi berhasil diambil. Total data transaksi: {len(transaksi_list)}")

            # 🔹 Ambil data dari database dengan filter WapuID
            # existing_entries = {
            #     (rec.NoReg, rec.KodeRekening, rec.TglSetoranOpsen)
            #     for rec in db.session.query(PenetapanKB.NoReg, PenetapanKB.KodeRekening, PenetapanKB.TglSetoranOpsen)
            #     .filter(PenetapanKB.UPTID == wapuid)  # Filter berdasarkan WapuID
            #     .all()
            # }

            new_entries = []
            for transaksi in transaksi_list:
                if not any(transaksi.values()):
                    print("⚠️ Data transaksi kosong, dilewati.")
                    continue

                query = db.session.query(tblUPTOpsen.KotaPropID).filter(tblUPTOpsen.UPTID == wapuid).first()
                wilayah = query[0] if query else None

                if lokasi_bayar != str(wilayah):  # Bandingkan dengan wilayah
                    print(
                        f"⚠ WARNING! Data {transaksi.get('nopol')} dilewati karena wilayah tidak cocok ({lokasi_bayar} ≠ {wilayah})")
                    continue

                # if (transaksi.get('nopol'), transaksi.get('kode_rekening'), tgl_setoran_opsen) in existing_entries:
                #     continue  # Lewati jika sudah ada

                masa_awal = transaksi.get('masa_awal', None)
                masa_akhir = transaksi.get('masa_akhir', None)

                if masa_awal and masa_akhir:
                    query = db.session.execute(
                        text(
                            "SELECT CASE WHEN :masa_awal = :masa_akhir THEN dbo.TANGGAL(:masa_awal, 'G') "
                            "ELSE dbo.TANGGAL(:masa_awal, 'G') + ' - ' + dbo.TANGGAL(:masa_akhir, 'G') END"
                        ),
                        {"masa_awal": masa_awal, "masa_akhir": masa_akhir}
                    )
                    periode_pajak = query.scalar()
                else:
                    periode_pajak = ""

                select_query = db.session.execute(f"SELECT DISTINCT UPT FROM tblUPTOpsen WHERE UPTID = {wapuid} ")
                result3 = select_query.first()[0]
                upt = result3

                # Memproses data PKB
                if transaksi.get('pokok_pkb') and transaksi.get('pokok_pkb') != "0":
                    pajak_pkb = float(transaksi.get('pokok_pkb').replace('.', '').replace(',', '.'))
                    denda_pkb = float(transaksi.get('denda_pkb').replace('.', '').replace(',', '.'))

                    new_entries.append(PenetapanKB(
                        NoReg=transaksi.get('nopol', ''),
                        KohirID=transaksi.get('nomor_skp', ''),
                        NamaBadan=transaksi.get('nama_pemilik', ''),
                        Pemilik=transaksi.get('nama_pemilik', ''),
                        Wilayah=upt,
                        UPTID=wapuid,
                        KotaKendaraan=upt,
                        KodeRekening=transaksi.get('kode_rekening', ''),
                        NamaRekening=transaksi.get('nama_rekening', ''),
                        MasaPajak=periode_pajak,
                        Pajak=pajak_pkb,
                        Denda=denda_pkb,
                        JmlBayar=pajak_pkb + denda_pkb,
                        KodeBayar=transaksi.get('kode_bayar', ''),
                        TglBayar=tgl_bayar,
                        Channel=transaksi.get('channel', ''),
                        NoSTS=tgl_bayar.strftime("%d%m%Y") + '/STS/Opsen PKB',
                        KodeRekeningOpsen="4.1.01.20.01.0001.",
                        NamaRekeningOpsen="Opsen PKB",
                        TglSetoranOpsen=tgl_setoran_opsen,
                        JmlSetoranOpsen=pajak_pkb,
                        JmlDendaOpsen=denda_pkb,
                        Keterangan="Opsen " + transaksi.get('nama_rekening', '') ,
                        NTPD=transaksi.get('ntpd', ''),
                        UserUpd=uid,
                        DateUpd=datetime.now()
                    ))

                # Memproses data BBN-KB
                if transaksi.get('pokok_bbnkb') and transaksi.get('pokok_bbnkb') != "0":
                    pajak_bbnkb = float(transaksi.get('pokok_bbnkb').replace('.', '').replace(',', '.'))
                    denda_bbnkb = float(transaksi.get('denda_bbnkb').replace('.', '').replace(',', '.'))

                    nama_rekening_asli = transaksi.get('nama_rekening', '')
                    if "PKB" in nama_rekening_asli:
                        nama_rekening_bbnkb = re.sub(r'\bPKB\b', 'BBN-KB', nama_rekening_asli)
                    else:
                        nama_rekening_bbnkb = nama_rekening_asli

                    new_entries.append(PenetapanKB(
                        NoReg=transaksi.get('nopol', ''),
                        KohirID=transaksi.get('nomor_skp', ''),
                        NamaBadan=transaksi.get('nama_pemilik', ''),
                        Pemilik=transaksi.get('nama_pemilik', ''),
                        Wilayah=upt,
                        UPTID=wapuid,
                        KotaKendaraan=upt,
                        KodeRekening="4.1.1.03.10.001",
                        NamaRekening=nama_rekening_bbnkb,
                        MasaPajak=periode_pajak,
                        Pajak=pajak_bbnkb,
                        Denda=denda_bbnkb,
                        JmlBayar=pajak_bbnkb + denda_bbnkb,
                        KodeBayar=transaksi.get('kode_bayar', ''),
                        TglBayar=tgl_bayar,
                        Channel=transaksi.get('channel', ''),
                        NoSTS=tgl_bayar.strftime("%d%m%Y") + '/STS/Opsen BBN-KB',
                        KodeRekeningOpsen="4.1.01.21.01.0001.",
                        NamaRekeningOpsen="Opsen BBN-KB",
                        TglSetoranOpsen=tgl_setoran_opsen,
                        JmlSetoranOpsen=pajak_bbnkb,
                        JmlDendaOpsen=denda_bbnkb,
                        Keterangan="Opsen "+nama_rekening_bbnkb,
                        NTPD=transaksi.get('ntpd', ''),
                        UserUpd=uid,
                        DateUpd=datetime.now()
                    ))

            print(f"✅ Selesai. Total entri baru yang akan dimasukkan: {len(new_entries)}")
            return new_entries


            # new_entries = []
            # for transaksi in transaksi_list:
            #     if not any(transaksi.values()):
            #         print("⚠️ Data transaksi kosong, dilewati.")
            #         continue
            #     query = db.session.query(tblUPTOpsen.KotaPropID).filter(tblUPTOpsen.UPTID == wapuid).first()
            #     wilayah = query[0] if query else None
            #
            #     if lokasi_bayar != str(wilayah):  # Bandingkan dengan wilayah
            #         print(
            #             f"⚠ WARNING! Data {transaksi.get('nopol')} dilewati karena wilayah tidak cocok ({lokasi_bayar} ≠ {wilayah})"
            #         )
            #         continue
            #
            #     if (transaksi.get('nopol'), transaksi.get('kode_rekening'), tgl_setoran_opsen) in existing_entries:
            #         continue  # Lewati jika sudah ada
            #
            #     masa_awal = transaksi.get('masa_awal', None)
            #     masa_akhir = transaksi.get('masa_akhir', None)
            #
            #     if masa_awal and masa_akhir:
            #         query = db.session.execute(
            #             text(
            #                 "SELECT CASE WHEN :masa_awal = :masa_akhir THEN dbo.TANGGAL(:masa_awal, 'G') "
            #                 "ELSE dbo.TANGGAL(:masa_awal, 'G') + ' - ' + dbo.TANGGAL(:masa_akhir, 'G') END"
            #             ),
            #             {"masa_awal": masa_awal, "masa_akhir": masa_akhir}
            #         )
            #         periode_pajak = query.scalar()  # Lebih tepat menggunakan scalar() jika hasil hanya satu nilai
            #     else:
            #         periode_pajak = ""
            #
            #     print(periode_pajak)
            #
            #     select_query = db.session.execute(
            #         f"SELECT DISTINCT UPT FROM tblUPTOpsen WHERE UPTID = {wapuid} ")
            #     result3 = select_query.first()[0]
            #     upt = result3
            #
            #     pajak = float(transaksi.get('pokok_pkb').replace('.', '').replace(',', '.')) if transaksi.get(
            #         'pokok_pkb') and transaksi.get('pokok_pkb') != "" else (
            #         float(transaksi.get('pokok_bbnkb').replace('.', '').replace(',', '.')) if transaksi.get(
            #             'pokok_bbnkb') and transaksi.get('pokok_bbnkb') != "" else 0.0)
            #
            #     denda = float(transaksi.get('denda_pkb').replace('.', '').replace(',', '.')) if transaksi.get(
            #         'denda_pkb') and transaksi.get('denda_pkb') != "" else (
            #         float(transaksi.get('denda_bbnkb').replace('.', '').replace(',', '.')) if transaksi.get(
            #             'denda_bbnkb') and transaksi.get('denda_bbnkb') != "" else 0.0)
            #
            #     opsen = pajak
            #     denda_opsen = denda
            #     jml_bayar = pajak + opsen + denda + denda_opsen
            #
            #     nama_rekening = transaksi.get('nama_rekening', '')
            #
            #     if 'PKB' in nama_rekening:
            #         kode_rekening_opsen = '4.1.01.20.01.0001.'
            #         nama_rekening_opsen = 'Opsen PKB'
            #     elif 'BBN-KB' in nama_rekening:
            #         kode_rekening_opsen = '4.1.01.21.01.0001.'
            #         nama_rekening_opsen = 'Opsen BBN-KB'
            #     else:
            #         kode_rekening_opsen = None
            #         nama_rekening_opsen = None
            #
            #     keterangan = 'Opsen' + transaksi.get('nama_rekening', '')
            #
            #     new_entries.append(PenetapanKB(
            #         NoReg=transaksi.get('nopol', ''),
            #         KohirID=transaksi.get('nomor_skp', ''),
            #         NamaBadan=transaksi.get('nama_pemilik', '') if transaksi.get('nama_pemilik', '') else transaksi.get('nama_pemilik',''),
            #         Pemilik=transaksi.get('nama_pemilik', ''),
            #         Wilayah=upt,
            #         UPTID=wapuid,
            #         KotaKendaraan=upt,
            #         KodeRekening=transaksi.get('kode_rekening', ''),
            #         NamaRekening=transaksi.get('nama_rekening', ''),
            #         MasaPajak=periode_pajak,
            #         Pajak=pajak if pajak else 0,
            #         Denda=denda if denda else 0,
            #         JmlBayar=jml_bayar,
            #         KodeBayar=transaksi.get('kode_bayar', ''),
            #         TglBayar=tgl_bayar,
            #         Channel=transaksi.get('channel', ''),
            #         NoSTS=tgl_bayar.strftime("%d%m%Y") + '/STS/'+"" + (nama_rekening_opsen or ""),
            #         KodeRekeningOpsen=kode_rekening_opsen,
            #         NamaRekeningOpsen=nama_rekening_opsen,
            #         TglSetoranOpsen=tgl_setoran_opsen,
            #         JmlSetoranOpsen=opsen,
            #         JmlDendaOpsen=denda_opsen,
            #         Keterangan=keterangan,
            #         NTPD=transaksi.get('ntpd', ''),
            #         UserUpd=uid,
            #         DateUpd=datetime.now()
            #     ))
            # print(f"✅ Selesai. Total entri baru yang akan dimasukkan: {len(new_entries)}")
            # return new_entries

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
            uid = kwargs['claim']["UID"]

            wapuid = kwargs['claim']["WapuID"]
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
                select_query = (
                    db.session.query(
                        # func.row_number()
                        # .over(
                        #     order_by=(
                        #         PenetapanKB.KotaKendaraan,
                        #         PenetapanKB.TglSetoranOpsen,
                        #         PenetapanKB.NamaRekeningOpsen
                        #     )
                        # )
                        # .label('HeaderID'),
                        PenetapanKB.HeaderID,
                        PenetapanKB.KotaKendaraan,
                        PenetapanKB.NamaRekeningOpsen,
                        PenetapanKB.TglSetoranOpsen,
                        (func.sum(PenetapanKB.JmlSetoranOpsen)+func.sum(PenetapanKB.JmlDendaOpsen)).label('JmlSetoranOpsen'),

                    )
                    .filter(PenetapanKB.UPTID.in_(uptid_list))
                    # .filter(
                    #     ~db.session.query(tblOpsen.ID)
                    #     .filter(tblOpsen.ID == PenetapanKB.ID)
                    #     .exists()
                    # )
                    .group_by(
                        PenetapanKB.HeaderID,
                        PenetapanKB.KotaKendaraan,
                        PenetapanKB.NamaRekeningOpsen,
                        PenetapanKB.TglSetoranOpsen
                    )
                )

                # FILTER_HeaderID
                subquery = select_query.subquery()
                aliased_query = aliased(subquery)
            elif checkadmin.IsIntegrasi == 1:
                select_query = (
                    db.session.query(
                        # func.row_number()
                        # .over(
                        #     order_by=(
                        #         PenetapanKB.KotaKendaraan,
                        #         PenetapanKB.TglSetoranOpsen,
                        #         PenetapanKB.NamaRekeningOpsen
                        #     )
                        # )
                        # .label('HeaderID'),
                        PenetapanKB.HeaderID,
                        PenetapanKB.KotaKendaraan,
                        PenetapanKB.NamaRekeningOpsen,
                        PenetapanKB.TglSetoranOpsen,
                        (func.sum(PenetapanKB.JmlSetoranOpsen) + func.sum(PenetapanKB.JmlDendaOpsen)).label(
                            'JmlSetoranOpsen'),

                    )
                    .filter(PenetapanKB.UPTID == wapuid,
                            # ~db.session.query(tblOpsen.ID)
                            # .filter(tblOpsen.ID == PenetapanKB.ID)
                            # .exists()
                            )
                    .group_by(
                        PenetapanKB.HeaderID,
                        PenetapanKB.KotaKendaraan,
                        PenetapanKB.NamaRekeningOpsen,
                        PenetapanKB.TglSetoranOpsen
                    )
                )

                # FILTER_HeaderID
                subquery = select_query.subquery()
                aliased_query = aliased(subquery)

            if args['HeaderID']:
                select_query = db.session.query(aliased_query).filter(
                    aliased_query.c.HeaderID == args['HeaderID']
                )

            # FILTER_TGL
            if args['filter_tgl']:
                select_query = select_query.filter(
                    (PenetapanKB.TglSetoranOpsen) == args['filter_tgl']
                )

            # FILTER_UPT
            if args['filter_upt']:
                select_query = select_query.filter(
                    (PenetapanKB.UPTID) == args['filter_upt']
                )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(PenetapanKB.NamaRekeningOpsen.ilike(search),
                        PenetapanKB.TglSetoranOpsen.ilike(search),
                        PenetapanKB.KotaKendaraan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(PenetapanKB, args['sort']).desc()
                else:
                    sort = getattr(PenetapanKB, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(PenetapanKB.TglSetoranOpsen,PenetapanKB.KotaKendaraan,
                                                     PenetapanKB.NamaRekeningOpsen.desc())

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


    class InstblOpsen(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('filter_tgl', type=str)
            parser.add_argument('filter_upt', type=str)

            args = parser.parse_args()
            uid = kwargs['claim']["UID"]

            wapuid = kwargs['claim']["WapuID"]
            groupid = kwargs['claim']["GroupId"]
            checkadmin = tblGroupUser.query.filter_by(
                GroupId=groupid
            ).first()
            if checkadmin.IsAdmin == 1:
                db.session.execute(
                    f"exec [INS_tblOpsen] @tgl='{args['filter_tgl']}', @wapuid='{args['filter_upt']}' "
                )
                db.session.commit()
            else:
                db.session.execute(
                    f"exec [INS_tblOpsen] @tgl='{args['filter_tgl']}', @wapuid={wapuid} "
                )
                db.session.commit()

    class InsSTS(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('filter_tgl', type=str)
            parser.add_argument('filter_upt', type=str)

            args = parser.parse_args()
            uid = kwargs['claim']["UID"]

            wapuid = kwargs['claim']["WapuID"]
            print(wapuid)
            groupid = kwargs['claim']["GroupId"]
            checkadmin = tblGroupUser.query.filter_by(
                GroupId=groupid
            ).first()
            if checkadmin.IsAdmin == 1:
                db.session.execute(
                    f"exec [INS_TBL_STS] @tgl='{args['filter_tgl']}', @wapuid='{args['filter_upt']}' "
                )
                db.session.commit()
            else:
                db.session.execute(
                    f"exec [INS_TBL_STS] @tgl='{args['filter_tgl']}', @wapuid={wapuid} "
                )
                db.session.commit()

    class PenetapanKBResourceID(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])

            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            penetapankb = PenetapanKB.query.get(id)
            if not penetapankb:
                return {'message': 'Data tidak ditemukan'}, 404
            result = {
                'ID': penetapankb.ID,
                'NoReg': penetapankb.NoReg,
                'Pemilik': penetapankb.Pemilik,
                'KodeRekening': penetapankb.KodeRekening,
                'NamaRekening': penetapankb.NamaRekening,
                'Pajak': float(penetapankb.Pajak or 0),
                'Denda': float(penetapankb.Denda or 0),
                'Wilayah': penetapankb.Wilayah,
                'KodeKendaraan': penetapankb.KodeKendaraan,
                'JmlSetoran': float(penetapankb.JmlSetoran or 0),
                'Keterangan': penetapankb.Keterangan,
                'TglBayar': penetapankb.TglBayar,  # Tanggal pembayaran (opsional, tambahkan jika tersedia)
                'Channel': penetapankb.Channel,  # Channel pembayaran (contoh: Online, ATM)
                'KodeRekeningOpsen': penetapankb.KodeRekeningOpsen,  # Kode opsen daerah
                'NamaRekeningOpsen': penetapankb.NamaRekeningOpsen,  # Nama rekening opsen
                'TglSetoranOpsen': penetapankb.TglSetoranOpsen,  # Tanggal setoran opsen
                'JmlSetoranOpsen': float(penetapankb.JmlSetoranOpsen or 0),  # Jumlah setoran opsen
                'JmlDendaOpsen': float(penetapankb.JmlDendaOpsen or 0),  # Jumlah denda opsen (opsional)
                'NTPD': penetapankb.NTPD,  # Nomor Transaksi Pajak Daerah
                'UserUpd': penetapankb.UserUpd,
                'DateUpd': penetapankb.DateUpd
            }
            return jsonify(result)

        def put(self, id, *args, **kwargs):
            penetapankb = PenetapanKB.query.get(id)
            if not penetapankb:
                return {'message': 'Data tidak ditemukan'}, 404
            args = parser.parse_args()

            penetapankb.NoReg = args['NoReg']
            penetapankb.Pemilik = args.get('Pemilik', penetapankb.Pemilik)
            penetapankb.KodeRekening = args.get('KodeRekening', penetapankb.KodeRekening)
            penetapankb.NamaRekening = args.get('NamaRekening', penetapankb.NamaRekening)
            penetapankb.Pajak = args.get('Pajak', penetapankb.Pajak)
            penetapankb.Denda = args.get('Denda', penetapankb.Denda)
            penetapankb.Wilayah = args.get('Wilayah', penetapankb.Wilayah)
            penetapankb.TglSetoranOpsen = args.get('TglSetoranOpsen', penetapankb.TglSetoranOpsen)
            penetapankb.JmlSetoran = args.get('JmlSetoran', penetapankb.JmlSetoran)
            penetapankb.Keterangan = args.get('Keterangan', penetapankb.Keterangan)
            penetapankb.UserUpd = args.get('UserUpd', penetapankb.UserUpd)
            penetapankb.DateUpd = args.get('DateUpd', penetapankb.DateUpd)
            db.session.commit()
            return {'message': 'Data berhasil diperbarui'}, 200

        def delete(self, id, *args, **kwargs):
            opsen = PenetapanKB.query.get(id)
            if not opsen:
                return {'message': 'Data tidak ditemukan'}, 404
            db.session.delete(opsen)
            db.session.commit()
            return {'message': 'Data berhasil dihapus'}, 200

    class PenetapanKBResourceNotSend(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
            parser.add_argument('search', type=str)

            args = parser.parse_args()
            penetapan_kb_alias = aliased(PenetapanKB)
            tbl_opsen_alias = aliased(tblOpsen)

            select_query = (
                db.session.query(
                    penetapan_kb_alias.ID,
                    penetapan_kb_alias.NoReg,
                    penetapan_kb_alias.NamaBadan,
                    penetapan_kb_alias.Pemilik,
                    penetapan_kb_alias.Wilayah,
                    func.coalesce(
                        penetapan_kb_alias.KotaKendaraan,
                        func.replace(penetapan_kb_alias.Wilayah, 'UPTD Pengelolaan Pendapatan Daerah', '')
                    ).label('KotaKendaraan'),
                    penetapan_kb_alias.KodeRekening,
                    penetapan_kb_alias.NamaRekening,
                    penetapan_kb_alias.MasaPajak,
                    penetapan_kb_alias.Pajak,
                    penetapan_kb_alias.Denda,
                    penetapan_kb_alias.JmlBayar,
                    penetapan_kb_alias.KodeBayar,
                    penetapan_kb_alias.TglBayar,
                    penetapan_kb_alias.Channel,
                    tbl_opsen_alias.NoSTS.label('NoSTS'),
                    penetapan_kb_alias.KodeRekeningOpsen,
                    penetapan_kb_alias.NamaRekeningOpsen,
                    penetapan_kb_alias.TglSetoranOpsen,
                    penetapan_kb_alias.JmlSetoranOpsen,
                    penetapan_kb_alias.JmlDendaOpsen,
                    penetapan_kb_alias.Keterangan,
                    penetapan_kb_alias.NTPD,
                    penetapan_kb_alias.UserUpd,
                    penetapan_kb_alias.DateUpd
                )
                .outerjoin(
                    tbl_opsen_alias,
                    and_(
                        func.ltrim(func.rtrim(tbl_opsen_alias.SetoranDari)) ==
                        func.ltrim(func.rtrim(penetapan_kb_alias.Wilayah)),
                        tbl_opsen_alias.TglSetoranOpsen == penetapan_kb_alias.TglBayar,
                        func.ltrim(func.rtrim(tbl_opsen_alias.Keterangan)) ==
                        func.ltrim(func.rtrim(penetapan_kb_alias.Keterangan)),
                        tbl_opsen_alias.NoSTS == tbl_opsen_alias.NoSTS,
                        penetapan_kb_alias.NoReg == tbl_opsen_alias.NoReg,
                        penetapan_kb_alias.KodeBayar == tbl_opsen_alias.KodeBayar,
                    ),
                )
            )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(penetapan_kb_alias.NoReg.ilike(search),
                        penetapan_kb_alias.Pemilik.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(penetapan_kb_alias, args['sort']).desc()
                else:
                    sort = getattr(penetapan_kb_alias, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(penetapan_kb_alias.NoReg)

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