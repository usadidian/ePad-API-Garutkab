from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_, case
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.MsTipeLokasi import MsTipeLokasi
from controller.tblUser import tblUser
from controller.vw_tarifreklame import vw_tarifreklame


class MsTitikLokasiHdr(db.Model, SerializerMixin):
    __tablename__ = 'MsTitikLokasiHdr'
    LokasiID = db.Column(db.Integer, primary_key=True)
    NomorTitik = db.Column(db.Integer, nullable=False)
    NamaLokasi = db.Column(db.String, nullable=False)
    TipeLokasiID = db.Column(db.Integer, nullable=False)
    TipeKelas = db.Column(db.String, nullable=False)
    TarifPajak = db.Column(db.Numeric(12, 2), nullable=False)
    PeriodePajak = db.Column(db.String, nullable=False)
    Persentase = db.Column(db.Numeric(12, 2), nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)


    class ListAll2(Resource):
        def get(self, tipelokasiid, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT LokasiID,NamaLokasi + ' (Rp ' + dbo.DESIMAL(TarifPajak) + ')' + (case when Persentase = 0 "
                f"then '' else ' +' + dbo.DESIMAL(Persentase)+'%' end) AS NamaLokasi FROM MsTitikLokasiHdr "
                f"WHERE TipeLokasiID='{tipelokasiid}' ORDER BY NamaLokasi")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll3(Resource):
        def get(self, *args, **kwargs):
            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
            parser.add_argument('search', type=str)
            parser.add_argument('tipelokasiid', type=str)

            args = parser.parse_args()
            select_query = db.session.query(
                vw_tarifreklame.LokasiID, vw_tarifreklame.NomorTitik, vw_tarifreklame.NamaLokasi,
                vw_tarifreklame.TarifPajak, vw_tarifreklame.TipeKelas, vw_tarifreklame.Persentase,
                vw_tarifreklame.TipeLokasiID, vw_tarifreklame.NamaKelas, vw_tarifreklame.Keterangan,
                vw_tarifreklame.JenisReklame)

            # tipelokasiid
            if args['tipelokasiid']:
                select_query = select_query.filter(
                    MsTipeLokasi.TipeLokasiID == args['tipelokasiid']
                )
            result = []
            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_tarifreklame.NomorTitik.ilike(search),
                        vw_tarifreklame.NamaLokasi.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_tarifreklame, args['sort']).desc()
                else:
                    sort = getattr(vw_tarifreklame, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_tarifreklame.NomorTitik )

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            for row in query_execute.items:
                d = {}
                for key in row.keys():
                    if key == 'TarifPajak' or key == 'Persentase':
                        d[key] = str(getattr(row, key))
                    else:
                        d[key] = getattr(row, key)
                result.append(d)
            return success_reads_pagination(query_execute, result)

    class ListAll(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
            parser.add_argument('search', type=str)

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            print(UserId)
            select_query = MsTitikLokasiHdr.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsTitikLokasiHdr.LokasiID.ilike(search),
                        MsTitikLokasiHdr.NamaLokasi.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsTitikLokasiHdr, args['sort']).desc()
                else:
                    sort = getattr(MsTitikLokasiHdr, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsTipeLokasi.NamaKelas)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('NomorTitik', type=int)
            parser.add_argument('NamaLokasi', type=str)
            parser.add_argument('TipeLokasiID', type=int)
            parser.add_argument('TipeKelas', type=str)
            parser.add_argument('TarifPajak', type=str)
            parser.add_argument('Periode', type=str)
            parser.add_argument('Persentase', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            periode = 'hh' if args['Periode'] == 'Harian' else \
                      'ww' if args['Periode'] == 'Mingguan' else \
                      '2w' if args['Periode'] == '2 Mingguan' else \
                      'mm' if args['Periode'] == 'Bulanan' else \
                      '3m' if args['Periode'] == 'Triwulan' else \
                      'yy' if args['Periode'] == 'Tahunan' else\
                      'xx' if args['Periode'] == 'Non Waktu' else ''

            # select_query = db.session.execute(
            #     f"SELECT DISTINCT Keterangan + "
            #     f"'0'+CAST(CAST(ISNULL(RIGHT(MAX(mtlh.NomorTitik),2),'01') AS INT)+1 AS CHAR(2))  AS NomorTitik "
            #     f"FROM MsTipeLokasi tl LEFT JOIN MsTitikLokasiHdr AS mtlh ON mtlh.TipeLokasiID = tl.TipeLokasiID "
            #     f"where tl.TipeKelas ='{args['TipeKelas']}' GROUP BY tl.Keterangan")
            # nomortitik = select_query.first()[0]

            add_record = MsTitikLokasiHdr(
                # LokasiID=args['LokasiID'],
                NomorTitik=args['NomorTitik'],
                NamaLokasi=args['NamaLokasi'],
                TipeLokasiID=args['TipeLokasiID'],
                TipeKelas=args['TipeKelas'],
                TarifPajak=args['TarifPajak'],
                PeriodePajak=args['Periode'],
                Persentase=args['Persentase'],
                UserUpd=uid,
                DateUpd=datetime.now()
            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsTitikLokasiHdr.query.filter_by(LokasiID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            # parser.add_argument('LokasiID', type=str)
            parser.add_argument('NomorTitik', type=str)
            parser.add_argument('NamaLokasi', type=str)
            # parser.add_argument('TipeKelas', type=str)
            parser.add_argument('TarifPajak', type=str)
            parser.add_argument('Periode', type=str)
            parser.add_argument('Persentase', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            args = parser.parse_args()
            # result = []
            # for row in result:
            #     result.append(row)


            # Periode = 'hh' if args['Periode'] == 'Harian' else \
            #     'ww' if args['Periode'] == 'Mingguan' else \
            #         '2w' if args['Periode'] == '2 Mingguan' else \
            #             'mm' if args['Periode'] == 'Bulanan' else \
            #                 '3m' if args['Periode'] == 'Triwulan' else \
            #                     'yy' if args['Periode'] == 'Tahunan' else \
            #                         'xx' if args['Periode'] == 'Non Waktu' else ''
            Periode = ''
            if args['Periode'] == 'Harian':
                Periode = 'hh'
            if args['Periode'] == 'Mingguan':
                Periode = 'ww'
            if args['Periode'] == '2 Mingguan':
                Periode = '2w'
            if args['Periode'] == 'Bulanan':
                Periode = 'mm'
            if args['Periode'] == 'Tahunan':
                Periode = 'yy'
            if args['Periode'] == 'Non Waktu':
                Periode = 'xx'

            # print( Periode )

            try:
                select_query = MsTitikLokasiHdr.query.filter_by(LokasiID=id).first()
                if select_query:
                    # select_query.LokasiID = args['LokasiID']
                    if args['NomorTitik']:
                        select_query.NomorTitik = args['NomorTitik']
                    if args['NamaLokasi']:
                        select_query.NamaLokasi = args['NamaLokasi']
                    # select_query.TipeKelas = args['TipeKelas']
                    if args['TarifPajak']:
                        select_query.TarifPajak = args['TarifPajak']
                    # select_query.PeriodePajak = args['Periode'],
                    if args['Periode']:
                        select_query.PeriodePajak = Periode
                    if args['Persentase']:
                        select_query.Persentase = args['Persentase']
                    select_query.UserUpd = uid
                    select_query.DateUpd = datetime.now()

                    db.session.commit()
                    return success_update({'id': id})
                    # return jsonify( {'status_code': 1, 'message': 'OK', 'data': result} )
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsTitikLokasiHdr.query.filter_by(LokasiID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})