import re
from datetime import datetime
from sqlalchemy import func, literal
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
from config.helper import parser
from controller.PenetapanKB import PenetapanKB
from controller.tblGroupUser import tblGroupUser
from controller.tblOpsen import tblOpsen
from controller.tblUser import tblUser

# Mengatur Base dengan metadata khusus jika diperlukan
Base = declarative_base()


class PenetapanSamsat(db.Model, SerializerMixin):
    __tablename__ = 'PenetapanSamsat'

    ID = db.Column(db.Integer, primary_key=True)
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
        return {column.name: getattr(self, column.name) for column in self.__table__.columns if column.name != "ID"}

    # Resource CRUD
    class listAll(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int, default=1)
            parser.add_argument('length', type=int)  # Tidak ada default, agar bisa kosong
            args = parser.parse_args()

            wapuid = kwargs['claim']["WapuID"]
            groupid = kwargs['claim']["GroupId"]
            checkintegrasi = tblGroupUser.query.filter_by(
                GroupId=groupid
            ).first()
            print(checkintegrasi)
            result = []
            try:
                if checkintegrasi.IsIntegrasi == 1:
                    select_query = db.session.query(PenetapanSamsat).filter(PenetapanSamsat.UPTID == wapuid)
                    # Jika 'length' tidak diberikan, ambil semua data
                    if args['length']:
                        page = args['page']
                        length = args['length']
                        paginated_query = select_query.paginate(page=page, per_page=length, error_out=False)
                        json_data = [row.as_dict() for row in paginated_query.items]
                    else:
                        # Jika tidak ada pagination, ambil semua data
                        json_data = [row.as_dict() for row in select_query.all()]

                    return jsonify({
                        "status": "success",
                        "total": len(json_data),
                        "data": json_data
                    })
                elif checkintegrasi.IsAdmin == 1:
                    select_query = db.session.query(PenetapanSamsat)
                    # Jika 'length' tidak diberikan, ambil semua data
                    if args['length']:
                        page = args['page']
                        length = args['length']
                        paginated_query = select_query.paginate(page=page, per_page=length, error_out=False)
                        json_data = [row.as_dict() for row in paginated_query.items]
                    else:
                        # Jika tidak ada pagination, ambil semua data
                        json_data = [row.as_dict() for row in select_query.all()]

                    return jsonify({
                        "status": "success",
                        "total": len(json_data),
                        "data": json_data
                    })
            except Exception as e:
                print(e)
                return failed_reads(result)

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('data', type=list, location='json', required=True, help="Data tidak boleh kosong.")

            args = parser.parse_args()
            uid = kwargs['claim']["UID"]

            new_entries = []
            existing_entries = set()

            # Ambil semua kombinasi NoReg, KodeRekening, dan TglSetoranOpsen dari database untuk cek duplikasi
            existing_records = db.session.query(PenetapanKB.NoReg, PenetapanKB.KodeRekening,
                                                PenetapanKB.TglSetoranOpsen).all()
            existing_entries = {(record.NoReg, record.KodeRekening, record.TglSetoranOpsen) for record in
                                existing_records}

            for item in args['data']:
                # Konversi format tanggal jika tersedia
                tgl_bayar = datetime.strptime(item['TglBayar'], '%Y-%m-%d') if item.get('TglBayar') else None
                tgl_setoran_opsen = datetime.strptime(item['TglSetoranOpsen'], '%Y-%m-%d') if item.get(
                    'TglSetoranOpsen') else None

                # Cek apakah data sudah ada untuk menghindari duplikasi
                if (item['NoReg'], item['KodeRekening'], tgl_setoran_opsen) in existing_entries:
                    continue  # Lewati jika sudah ada

                new_entries.append(PenetapanKB(
                    NoReg=item['NoReg'],
                    KohirID=item['KohirID'],
                    Pemilik=item['Pemilik'],
                    Wilayah=item['Wilayah'],
                    KotaKendaraan=item['KotaKendaraan'],
                    KodeRekening=item['KodeRekening'],
                    NamaRekening=item['NamaRekening'],
                    MasaPajak=item['MasaPajak'],
                    Pajak=item['Pajak'],
                    Denda=item['Denda'],
                    TglBayar=tgl_bayar,
                    Channel=item['Channel'],
                    JmlBayar=item('JmlBayar', 0.0),
                    KodeBayar=item.get('KodeBayar', ''),
                    NoSTS=item.get('NoSTS', ''),
                    KodeRekeningOpsen=item.get('KodeRekeningOpsen'),
                    NamaRekeningOpsen=item.get('NamaRekeningOpsen'),
                    TglSetoranOpsen=tgl_setoran_opsen,
                    JmlSetoranOpsen=item.get('JmlSetoranOpsen'),
                    JmlDendaOpsen=item.get('JmlDendaOpsen'),
                    Keterangan=item.get('Keterangan'),
                    NTPD=item['NTPD'],
                    UserUpd=uid,
                    DateUpd=datetime.now()
                ))

            if new_entries:
                try:
                    db.session.add_all(new_entries)
                    db.session.commit()
                    return {'message': f"{len(new_entries)} data berhasil ditambahkan"}, 201
                except SQLAlchemyError as e:
                    db.session.rollback()
                    return {'message': f"Terjadi kesalahan saat menyimpan data: {str(e)}"}, 500
            else:
                return {'message': "Tidak ada data baru yang ditambahkan (data sudah ada di database)."}, 200


    class PenetapanSamsatResource(Resource):
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

            wapuid = kwargs['claim']["WapuID"]
            groupid = kwargs['claim']["GroupId"]
            checkadmin = tblGroupUser.query.filter_by(
                GroupId=groupid
            ).first()
            if checkadmin.IsAdmin == 1:
                select_query = (
                    db.session.query(
                        func.row_number()
                        .over(
                            order_by=(
                                PenetapanSamsat.KotaKendaraan,
                                PenetapanSamsat.TglSetoranOpsen,
                                PenetapanSamsat.NamaRekeningOpsen
                            )
                        )
                        .label('HeaderID'),
                        PenetapanSamsat.KotaKendaraan,
                        PenetapanSamsat.NamaRekeningOpsen,
                        PenetapanSamsat.TglSetoranOpsen,
                        (func.sum(PenetapanSamsat.JmlSetoranOpsen) + func.sum(PenetapanSamsat.JmlDendaOpsen)).label(
                            'JmlSetoranOpsen'),

                    )
                    .filter(
                        ~db.session.query(tblOpsen.ID)
                        .filter(tblOpsen.ID == PenetapanSamsat.ID)
                        .exists()
                    )
                    .group_by(
                        PenetapanSamsat.KotaKendaraan,
                        PenetapanSamsat.NamaRekeningOpsen,
                        PenetapanSamsat.TglSetoranOpsen
                    )
                )

                # FILTER_HeaderID
                subquery = select_query.subquery()
                aliased_query = aliased(subquery)
            else:
                select_query = (
                    db.session.query(
                        func.row_number()
                        .over(
                            order_by=(
                                PenetapanSamsat.KotaKendaraan,
                                PenetapanSamsat.TglSetoranOpsen,
                                PenetapanSamsat.NamaRekeningOpsen
                            )
                        )
                        .label('HeaderID'),
                        PenetapanSamsat.KotaKendaraan,
                        PenetapanSamsat.NamaRekeningOpsen,
                        PenetapanSamsat.TglSetoranOpsen,
                        (func.sum(PenetapanSamsat.JmlSetoranOpsen) + func.sum(PenetapanSamsat.JmlDendaOpsen)).label(
                            'JmlSetoranOpsen'),

                    )
                    .filter(PenetapanSamsat.UPTID == wapuid,
                            ~db.session.query(tblOpsen.ID)
                            .filter(tblOpsen.ID == PenetapanSamsat.ID)
                            .exists()
                            )
                    .group_by(
                        PenetapanSamsat.KotaKendaraan,
                        PenetapanSamsat.NamaRekeningOpsen,
                        PenetapanSamsat.TglSetoranOpsen
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
                    (PenetapanSamsat.TglSetoranOpsen) == args['filter_tgl']
                )

            # FILTER_UPT
            if args['filter_upt']:
                select_query = select_query.filter(
                    (PenetapanSamsat.UPTID) == args['filter_upt']
                )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(PenetapanSamsat.NamaRekeningOpsen.ilike(search),
                        PenetapanSamsat.TglSetoranOpsen.ilike(search),
                        PenetapanSamsat.KotaKendaraan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(PenetapanSamsat, args['sort']).desc()
                else:
                    sort = getattr(PenetapanSamsat, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(PenetapanSamsat.TglSetoranOpsen, PenetapanSamsat.KotaKendaraan,
                                                     PenetapanSamsat.NamaRekeningOpsen.desc())

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



    class PenetapanSamsatResourceID(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])

            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            penetapankb = PenetapanSamsat.query.get(id)
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
            penetapankb = PenetapanSamsat.query.get(id)
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
            opsen = PenetapanSamsat.query.get(id)
            if not opsen:
                return {'message': 'Data tidak ditemukan'}, 404
            db.session.delete(opsen)
            db.session.commit()
            return {'message': 'Data berhasil dihapus'}, 200

    class PenetapanSamsatResourceNotSend(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
            parser.add_argument('search', type=str)

            args = parser.parse_args()
            penetapan_kb_alias = aliased(PenetapanSamsat)
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