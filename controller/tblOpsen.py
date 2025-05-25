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
from controller.tblUPTOpsen import tblUPTOpsen
from controller.tblUser import tblUser

# Mengatur Base dengan metadata khusus jika diperlukan
Base = declarative_base()

class tblOpsen(db.Model, SerializerMixin):
    __tablename__ = 'tblOpsen'

    OpsenID = db.Column(db.Integer, primary_key=True)
    HeaderID = db.Column(db.Integer, nullable=True)
    ID = db.Column(db.Integer, nullable=True)
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

    def as_dict(self):
        """Mengonversi objek menjadi dictionary."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    # Parsers
    parse = reqparse.RequestParser()
    parser.add_argument('ID', type=str, required=True, help="ID tidak boleh kosong.")
    parser.add_argument('NoReg', type=str, required=True, help="NoReg tidak boleh kosong.")
    parser.add_argument('KohirID', type=str, required=True, help="KohirID tidak boleh kosong.")
    parser.add_argument('Pemilik', type=str, required=True, help="Nama Pemilik tidak boleh kosong.")
    parser.add_argument('Wilayah', type=str, required=True, help="Wilayah tidak boleh kosong.")
    parser.add_argument('KotaKendaraan', type=str, required=True, help="Kota Kendaraan tidak boleh kosong.")
    parser.add_argument('KodeRekening', type=str, required=True, help="Kode Rekening tidak boleh kosong.")
    parser.add_argument('NamaRekening', type=str, required=True, help="Nama Rekening tidak boleh kosong.")
    parser.add_argument('MasaPajak', type=str, required=True, help="MasaPajak tidak boleh kosong.")
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

    
    # Resource CRUD
    class OpsenListResource4(Resource):
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
            url = f"{baseUrlScheme}://{baseUrl}/opsen?HeaderID={headerid}"
            if baseUrlPort:
                url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/opsen?HeaderID={headerid}"

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
                        'Opsen ' + (SELECT TOP(1) pk.NamaRekening FROM PenetapanKB pk1 WHERE pk1.ID=pk.ID) AS Jenis,
                        '' AS TglJatuhTempo, 
                        'Lunas' AS StatPaid, 
                        pk.NoReg AS NoKohir, 
                        pk.NoReg AS OBN, 
                        pk.MasaPajak AS MP, 
                        pk.MasaPajak AS UrutMP, 
                        CAST(pk.JmlSetoranOpsen AS MONEY) AS JmlSetoran,                        
                        pk.KohirID AS KohirID, 
                        'STS' AS STS, 
                        pk.NoReg AS KID, 
                        KodeBayar AS SSPD, 
                        '' AS CekSTS, 
                        KotaKendaraan AS Wilayah,
                        pk.ID AS DetailID 
                        FROM tblOpsen pk  
                        LEFT JOIN MsJenisPendapatan AS mjp ON LTRIM(RTRIM(mjp.KodeRekening)) = LTRIM(RTRIM(pk.KodeRekeningOpsen))
                        WHERE HeaderID=:headerid AND TglSetoranOpsen = :tglopsen AND  KotaKendaraan = :kotakend AND NamaRekeningOpsen=:nmrekopsen
                        
                        UNION ALL
                        
                        SELECT :headerid AS HeaderID,
                        pk.NoReg AS ObyekBadanNo, 
                        pk.NamaBadan, 
                        pk.Pemilik AS NamaPemilik, 
                        (CASE WHEN pk.JmlDendaOpsen>0 AND mjp.NamaJenisPendapatan ='Opsen PKB' THEN '4.1.04.25.01.0001.' ELSE 
                        (CASE WHEN pk.JmlDendaOpsen>0 AND mjp.NamaJenisPendapatan ='Opsen BBN-KB' THEN '4.1.04.26.01.0001.'                                         END) END) AS KodeRekeningOpsen,
                        (CASE WHEN pk.JmlDendaOpsen>0 AND mjp.NamaJenisPendapatan ='Opsen PKB' THEN 'Denda Opsen' + (SELECT TOP(1) pk.NamaRekening FROM tblOpsen pk1 WHERE pk1.ID=pk.ID) ELSE 
                        (CASE WHEN pk.JmlDendaOpsen>0 AND mjp.NamaJenisPendapatan ='Opsen BBN-KB' THEN 'Denda Opsen' + (SELECT TOP(1) pk.NamaRekening FROM tblOpsen pk1 WHERE pk1.ID=pk.ID)                                         
                         END) END) AS Jenis,
                        '' AS TglJatuhTempo, 
                        'Lunas' AS StatPaid, 
                        pk.NoReg AS NoKohir, 
                        pk.NoReg AS OBN, 
                        pk.MasaPajak AS MP, 
                        pk.MasaPajak AS UrutMP, 
                        CAST(pk.JmlDendaOpsen AS MONEY) AS JmlSetoran,                        
                        pk.KohirID AS KohirID, 
                        'STS' AS STS, 
                        pk.NoReg AS KID, 
                        KodeBayar AS SSPD, 
                        '' AS CekSTS, 
                        KotaKendaraan AS Wilayah,
                        pk.ID AS DetailID 
                        FROM tblOpsen pk  
                        LEFT JOIN MsJenisPendapatan AS mjp ON LTRIM(RTRIM(mjp.KodeRekening)) = LTRIM(RTRIM(pk.KodeRekeningOpsen))
                        WHERE HeaderID=:headerid AND TglSetoranOpsen = :tglopsen AND  KotaKendaraan = :kotakend AND NamaRekeningOpsen=:nmrekopsen
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

    class OpsenListResource7(Resource):
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

            url = f"{baseUrlScheme}://{baseUrl}/opsen?HeaderID={headerid}"
            if baseUrlPort:
                url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/opsen?HeaderID={headerid}"

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
                        FROM tblOpsen pk  
                        LEFT JOIN MsJenisPendapatan AS mjp ON LTRIM(RTRIM(mjp.KodeRekening)) = LTRIM(RTRIM(pk.KodeRekeningOpsen))
                        WHERE HeaderID=:headerid AND TglSetoranOpsen = :tglopsen AND  KotaKendaraan = :kotakend AND NamaRekeningOpsen=:nmrekopsen
    
                        UNION ALL
    
                        SELECT :headerid AS HeaderID,
                        pk.NoReg AS ObyekBadanNo, 
                        pk.NamaBadan, 
                        pk.Pemilik AS NamaPemilik, 
                        (CASE WHEN pk.JmlDendaOpsen>0 AND mjp.NamaJenisPendapatan ='Opsen PKB' THEN '4.1.04.25.01.0001.' ELSE 
                        (CASE WHEN pk.JmlDendaOpsen>0 AND mjp.NamaJenisPendapatan ='Opsen BBN-KB' THEN '4.1.04.26.01.0001.'                                         END) END) AS KodeRekeningOpsen,
                        (CASE WHEN pk.JmlDendaOpsen>0 AND mjp.NamaJenisPendapatan ='Opsen PKB' THEN 'Denda ' + (SELECT TOP(1) pk.NamaRekening FROM tblOpsen pk1 WHERE pk1.ID=pk.ID) ELSE 
                        (CASE WHEN pk.JmlDendaOpsen>0 AND mjp.NamaJenisPendapatan ='Opsen BBN-KB' THEN 'Denda ' + (SELECT TOP(1) pk.NamaRekening FROM tblOpsen pk1 WHERE pk1.ID=pk.ID)                                         
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
                        FROM tblOpsen pk  
                        LEFT JOIN MsJenisPendapatan AS mjp ON LTRIM(RTRIM(mjp.KodeRekening)) = LTRIM(RTRIM(pk.KodeRekeningOpsen))
                        WHERE HeaderID=:headerid AND TglSetoranOpsen = :tglopsen AND  KotaKendaraan = :kotakend AND NamaRekeningOpsen=:nmrekopsen
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


    class OpsenListResource(Resource):
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
            uid = kwargs['claim']["UID"]
            groupid = kwargs['claim']["GroupId"]
            wapuid = kwargs['claim']["WapuID"]

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
                        #         tblOpsen.KotaKendaraan,
                        #         tblOpsen.TglSetoranOpsen,
                        #         tblOpsen.NamaRekeningOpsen
                        #     )
                        # )
                        # .label('HeaderID'),
                        tblOpsen.HeaderID,
                        tblOpsen.KotaKendaraan,
                        tblOpsen.NamaRekeningOpsen,
                        tblOpsen.TglSetoranOpsen,
                        (func.sum(tblOpsen.JmlSetoranOpsen)+func.sum(tblOpsen.JmlDendaOpsen)).label('JmlSetoranOpsen'),
                        )
                        .filter(tblOpsen.UPTID.in_(uptid_list))
                        .group_by(
                            tblOpsen.HeaderID,
                            tblOpsen.KotaKendaraan,
                            tblOpsen.NamaRekeningOpsen,
                            tblOpsen.TglSetoranOpsen
                        )
                    )

                subquery = select_query.subquery()
                aliased_query = aliased(subquery)
            else:
                select_query = (
                    db.session.query(
                        # func.row_number()
                        # .over(
                        #     order_by=(
                        #         tblOpsen.KotaKendaraan,
                        #         tblOpsen.TglSetoranOpsen,
                        #         tblOpsen.NamaRekeningOpsen
                        #     )
                        # )
                        # .label('HeaderID'),
                        tblOpsen.HeaderID,
                        tblOpsen.KotaKendaraan,
                        tblOpsen.NamaRekeningOpsen,
                        tblOpsen.TglSetoranOpsen,
                        (func.sum(tblOpsen.JmlSetoranOpsen) + func.sum(tblOpsen.JmlDendaOpsen)).label(
                            'JmlSetoranOpsen'),
                    )
                    .group_by(
                        tblOpsen.HeaderID,
                        tblOpsen.KotaKendaraan,
                        tblOpsen.NamaRekeningOpsen,
                        tblOpsen.TglSetoranOpsen
                    )
                ) \
                    .filter(tblOpsen.UPTID == wapuid)

                subquery = select_query.subquery()
                aliased_query = aliased(subquery)

            if args['HeaderID']:
                select_query = db.session.query(aliased_query).filter(
                    aliased_query.c.HeaderID == args['HeaderID']
                )

            # FILTER_TGL
            if args['filter_tgl']:
                select_query = select_query.filter(
                    (tblOpsen.TglSetoranOpsen) == args['filter_tgl']
                )

            # FILTER_UPT
            if args['filter_upt']:
                select_query = select_query.filter(
                    (tblOpsen.UPTID) == args['filter_upt']
                )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(tblOpsen.NoReg.ilike(search),
                        tblOpsen.Pemilik.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(tblOpsen, args['sort']).desc()
                else:
                    sort = getattr(tblOpsen, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(tblOpsen.TglSetoranOpsen,tblOpsen.KotaKendaraan,
                                                     tblOpsen.NamaRekeningOpsen.desc())

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


        def post(self, *args, **kwargs):
            uid = kwargs['claim']["UID"]

            try:
                # Ambil data dari request body dalam format JSON
                data = request.get_json()

                if not isinstance(data, list):  # Periksa apakah data berbentuk array (list)
                    return {'message': 'Data harus berupa array.'}, 400

                new_opsen_list = []

                for item in data:
                    # Validasi setiap item (gunakan validasi yang mirip dengan reqparse)
                    if not all(key in item for key in ('NoReg', 'Pemilik', 'Wilayah', 'KotaKendaraan',
                                                       'KodeRekening', 'NamaRekening', 'MasaPajak',
                                                       'Pajak', 'Channel', 'NTPD')):
                        return {'message': f"Data tidak valid: {item}"}, 400

                    # Cek apakah data dengan kombinasi yang sama sudah ada
                    existing_opsen = tblOpsen.query.filter_by(
                        NoReg=item['NoReg'],
                        KodeRekening=item['KodeRekening'],
                        TglSetoranOpsen=item.get('TglSetoranOpsen'),
                        MasaPajak=item['MasaPajak']
                    ).first()

                    if existing_opsen:
                        return {
                            'message': f"Data dengan kombinasi NoReg '{item['NoReg']}', "
                                       f"KodeRekening '{item['KodeRekening']}', "
                                       f"dan TglSetoranOpsen '{item.get('TglSetoranOpsen')}' sudah ada."
                        }, 400

                    for item in data:
                        try:
                            # Validasi field wajib
                            if not item.get('NoReg'):
                                return {'message': 'NoReg tidak boleh kosong.'}, 400
                            if not item.get('KotaKendaraan'):
                                return {'message': 'KotaKendaraan tidak boleh kosong.'}, 400

                            # Parsing tanggal
                            TglBayar = datetime.strptime(item['TglBayar'], '%Y-%m-%d %H:%M:%S.%f') if item.get(
                                'TglBayar') else None
                            TglSetoranOpsen = datetime.strptime(item['TglSetoranOpsen'],
                                                                '%Y-%m-%d %H:%M:%S.%f') if item.get(
                                'TglSetoranOpsen') else None

                            # Parsing angka
                            Pajak = float(item['Pajak']) if item.get('Pajak') else None
                            JmlSetoranOpsen = float(item['JmlSetoranOpsen']) if item.get('JmlSetoranOpsen') else None
                            JmlDendaOpsen = float(item['JmlDendaOpsen']) if item.get('JmlDendaOpsen') else None

                            # Parsing string kosong
                            Channel = item.get('Channel') or None
                            NTPD = item.get('NTPD') or None

                            # Buat objek baru
                            new_opsen = tblOpsen(
                                ID=item['ID'],
                                NoReg=item['NoReg'],
                                NamaBadan=item.get('NamaBadan'),
                                Pemilik=item.get('Pemilik'),
                                Wilayah=item.get('Wilayah'),
                                KotaKendaraan=item['KotaKendaraan'],
                                KodeRekening=item.get('KodeRekening'),
                                NamaRekening=item.get('NamaRekening'),
                                MasaPajak=item.get('MasaPajak'),
                                Pajak=Pajak,
                                Denda=args['Denda'],
                                JmlBayar=item.get('JmlBayar'),
                                KodeBayar=item.get('KodeBayar'),
                                TglBayar=TglBayar,
                                Channel=Channel,
                                NoSTS=item.get('NoSTS', ''),
                                KodeRekeningOpsen=item.get('KodeRekeningOpsen'),
                                NamaRekeningOpsen=item.get('NamaRekeningOpsen'),
                                TglSetoranOpsen=TglSetoranOpsen,
                                JmlSetoranOpsen=JmlSetoranOpsen,
                                JmlDendaOpsen=JmlDendaOpsen,
                                Keterangan=item.get('Keterangan'),
                                NTPD=NTPD,
                                UserUpd=uid,
                                DateUpd=datetime.now()
                            )
                            new_opsen_list.append(new_opsen)
                        except Exception as e:
                            return {'message': f"Kesalahan pada item {item}: {str(e)}"}, 400

                    # Simpan ke database
                    db.session.bulk_save_objects(new_opsen_list)
                    db.session.commit()

                return {'message': f"{len(new_opsen_list)} data berhasil ditambahkan"}, 201
            except SQLAlchemyError as e:
                db.session.rollback()
                return {'message': f"Terjadi kesalahan saat menyimpan data: {str(e)}"}, 500
            except Exception as e:
                return {'message': f"Terjadi kesalahan: {str(e)}"}, 500

    ###############################################################################
    class opsenlist(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get (self, *args, **kwargs):

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

            # Query data dari tabel tblOpsen
            select_query = db.session.query(tblOpsen)

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

        #####################################################################################

    class OpsenResource(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}
        def get (self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])

            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            wapuid = kwargs['claim']["WapuID"]
            opsen = tblOpsen.query.get(OpsenID=id).filter(tblOpsen.UPTID==wapuid)
            if not opsen:
                return {'message': 'Data tidak ditemukan'}, 404
            result = {
                'OpsenID': opsen.OpsenID,
                'NoReg': opsen.NoReg,
                'Pemilik': opsen.Pemilik,
                'KodeRekening': opsen.KodeRekening,
                'NamaRekening': opsen.NamaRekening,
                'Pajak': float(opsen.Pajak or 0),
                'Denda': float(opsen.Denda or 0),
                'Wilayah': opsen.Wilayah,
                'KotaKendaraan': opsen.KotaKendaraan,
                'Keterangan': opsen.Keterangan,
                'TglBayar': opsen.TglBayar,  # Tanggal pembayaran (opsional, tambahkan jika tersedia)
                'Channel': opsen.Channel,  # Channel pembayaran (contoh: Online, ATM)
                'KodeRekeningOpsen': opsen.KodeRekeningOpsen,  # Kode opsen daerah
                'NamaRekeningOpsen': opsen.NamaRekeningOpsen,  # Nama rekening opsen
                'TglSetoranOpsen': opsen.TglSetoranOpsen,  # Tanggal setoran opsen
                'JmlSetoranOpsen': float(opsen.JmlSetoranOpsen or 0),  # Jumlah setoran opsen
                'JmlDendaOpsen': float(opsen.JmlDendaOpsen or 0),  # Jumlah denda opsen (opsional)
                'NTPD': opsen.NTPD,  # Nomor Transaksi Pajak Daerah
                'UserUpd': opsen.UserUpd,
                'DateUpd': opsen.DateUpd
            }
            return jsonify(result)

        def put(self, id, *args, **kwargs):
            opsen = tblOpsen.query.get(OpsenID=id)
            if not opsen:
                return {'message': 'Data tidak ditemukan'}, 404
            args = parser.parse_args()

            opsen.NoReg = args['NoReg']
            opsen.Pemilik = args.get('Pemilik', opsen.Pemilik)
            opsen.KodeRekening = args.get('KodeRekening', opsen.KodeRekening)
            opsen.NamaRekening = args.get('NamaRekening', opsen.NamaRekening)
            opsen.Pajak = args.get('Pajak', opsen.Pajak)
            opsen.Denda = args.get('Denda', opsen.Denda)
            opsen.Wilayah = args.get('Wilayah', opsen.Wilayah)
            opsen.TglSetoranOpsen = args.get('TglSetoranOpsen', opsen.TglSetoranOpsen)
            opsen.JmlSetoran = args.get('JmlSetoran', opsen.JmlSetoran)
            opsen.Keterangan = args.get('Keterangan', opsen.Keterangan)
            opsen.UserUpd = args.get('UserUpd', opsen.UserUpd)
            opsen.DateUpd = args.get('DateUpd', opsen.DateUpd)
            db.session.commit()
            return {'message': 'Data berhasil diperbarui'}, 200

        def delete(self, id, *args, **kwargs):
            opsen = tblOpsen.query.get(OpsenID=id)
            if not opsen:
                return {'message': 'Data tidak ditemukan'}, 404
            db.session.delete(opsen)
            db.session.commit()
            return {'message': 'Data berhasil dihapus'}, 200


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