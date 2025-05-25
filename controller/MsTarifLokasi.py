from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_, case
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.tblUser import tblUser
from controller.vw_jenistarif import vw_jenistarif


class tarifpajak(Resource):
    def get(self, jenispendapatanid, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT LokasiID AS KodeTarif,NamaLokasi + ' ' + dbo.DESIMAL(TarifPajak * 100) + '%' AS NamaTarif,TarifPajak FROM MsTarifLokasi"
            f" WHERE JenisPendapatanID = '{jenispendapatanid}' AND [Status] = '1' ORDER BY NamaTarif")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                if key == 'value':
                    d[key] = str(getattr(row, key))
                else:
                    d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)

class MsTarifLokasi(db.Model, SerializerMixin):
    __tablename__ = 'MsTarifLokasi'
    LokasiID = db.Column(db.Integer, primary_key=True)
    NamaLokasi = db.Column(db.String, nullable=False)
    PeriodePajak = db.Column(db.String, nullable=False)
    TarifPajak = db.Column(db.Numeric(12, 2), nullable=False)
    Satuan = db.Column(db.String, nullable=False)
    Target = db.Column(db.String, nullable=False)
    Status = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    JenisPendapatanID = db.Column(db.String, db.ForeignKey('MsJenisPendapatan.JenisPendapatanID'), nullable=False)

    class ListAll2(Resource):
        def get(self, jenispendapatanid, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT LokasiID AS Kode,NamaLokasi + ' ' + dbo.DESIMAL(TarifPajak * 100) + '%' AS Nama,TarifPajak AS value FROM MsTarifLokasi"
                f" WHERE JenisPendapatanID = '{jenispendapatanid}' AND [Status] = '1' ORDER BY Nama")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    if key == 'value':
                        d[key] = str(getattr(row, key))
                    else:
                        d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

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
            parser.add_argument( 'jenispendapatanid', type=str )

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            print(UserId)
            # select_query = db.session.query(
            #     MsTarifLokasi.LokasiID, MsTarifLokasi.JenisPendapatanID, MsJenisPendapatan.KodeRekening,
            #     MsJenisPendapatan.NamaJenisPendapatan, MsTarifLokasi.NamaLokasi, MsTarifLokasi.TarifPajak,
            #     (MsJenisPendapatan.KodeRekening+' '+MsJenisPendapatan.NamaJenisPendapatan).label('Nama'),
            #     MsTarifLokasi.Target, MsTarifLokasi.Satuan, MsTarifLokasi.Status,
            #     MsTarifLokasi.UserUpd, MsTarifLokasi.DateUpd,
            #     case( [
            #         (MsTarifLokasi.Status == 1, 'Aktif')], else_='Non Aktif' ).label( 'Status' ),
            #     case( [
            #         (MsTarifLokasi.PeriodePajak == 'dd', 'Harian'),
            #         (MsTarifLokasi.PeriodePajak == 'ww', 'Mingguan'),
            #         (MsTarifLokasi.PeriodePajak == 'mm', 'Bulanan'),
            #         (MsTarifLokasi.PeriodePajak == 'yy', 'Tahunan'),
            #         (MsTarifLokasi.PeriodePajak == '2w', '2 Mingguan'),
            #     ], else_='Non Waktu' ).label( 'Periode' ) ) \
            #     .outerjoin( MsJenisPendapatan, MsTarifLokasi.JenisPendapatanID == MsJenisPendapatan.JenisPendapatanID ) \

            select_query = db.session.query(
                vw_jenistarif.LokasiID, vw_jenistarif.JenisPendapatanID, vw_jenistarif.KodeRekening,
                vw_jenistarif.NamaJenisPendapatan, vw_jenistarif.NamaLokasi, vw_jenistarif.TarifPajak,
                (vw_jenistarif.Nama), vw_jenistarif.Target, vw_jenistarif.Satuan, vw_jenistarif.Status,
                vw_jenistarif.UserUpd, vw_jenistarif.DateUpd,vw_jenistarif.Periode)

            # tipelokasiid
            if args['jenispendapatanid']:
                select_query = select_query.filter(
                    vw_jenistarif.JenisPendapatanID == args['jenispendapatanid']
                )
            result = []
            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_jenistarif.TarifPajak.ilike(search),
                        vw_jenistarif.NamaLokasi.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_jenistarif, args['sort']).desc()
                else:
                    sort = getattr(vw_jenistarif, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_jenistarif.KodeRekening)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            for row in query_execute.items:
                d = {}
                for key in row.keys():
                    if key == 'TarifPajak' :
                        d[key] = str( getattr( row, key ) )
                    else:
                        d[key] = getattr( row, key )
                result.append( d )
            return success_reads_pagination( query_execute, result )

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            # parser.add_argument('LokasiID', type=str)
            parser.add_argument('JenisPendapatanID', type=str)
            parser.add_argument('NamaLokasi', type=str)
            parser.add_argument('Periode', type=str)
            parser.add_argument('TarifPajak', type=str)
            parser.add_argument('Satuan', type=str)
            # parser.add_argument('Target', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)
            Periode = ''
            if args['Periode'] == 'Harian':
                Periode = 'hh'
            if args['Periode'] == 'Mingguan':
                Periode= 'ww'
            if args['Periode'] == '2 Mingguan':
                Periode= '2w'
            if args['Periode'] == 'Bulanan':
                Periode= 'mm'
            if args['Periode'] == 'Tahunan':
                Periode= 'yy'
            if args['Periode'] == 'Non Waktu':
                Periode= 'xx'

            satuan = ''
            if args['Satuan'] == None or args['Satuan'] == '':
                satuan = '-'
            else:
                satuan = args['Satuan']

            add_record = MsTarifLokasi(
                # LokasiID=args['LokasiID'],
                JenisPendapatanID=args['JenisPendapatanID'],
                NamaLokasi=args['NamaLokasi'],
                PeriodePajak=Periode,
                TarifPajak=args['TarifPajak'],
                Satuan=satuan,
                Target='P',
                Status='1',
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
                select_query = MsTarifLokasi.query.filter_by(LokasiID=id).first()
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
            # parser.add_argument('JenisPendapatanID', type=str)
            parser.add_argument('NamaLokasi', type=str)
            parser.add_argument('Periode', type=str)
            parser.add_argument('TarifPajak', type=str)
            parser.add_argument('Satuan', type=str)
            # parser.add_argument('Target', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            args = parser.parse_args()
            Periode = ''
            if args['Periode'] == 'Harian':
                Periode = 'hh'
            if args['Periode'] == 'Mingguan':
                Periode= 'ww'
            if args['Periode'] == '2 Mingguan':
                Periode= '2w'
            if args['Periode'] == 'Bulanan':
                Periode= 'mm'
            if args['Periode'] == 'Tahunan':
                Periode= 'yy'
            if args['Periode'] == 'Non Waktu':
                Periode= 'xx'
            print(Periode)
            satuan = ''
            if args['Satuan'] == None or args['Satuan'] == '':
                satuan = '-'
            else:
                satuan = args['Satuan']
            status = 1
            if args['Status'] == 'Aktif':
                status = 1
            if args['Status'] == 'Non Aktif':
                status = 0

            try:
                select_query = MsTarifLokasi.query.filter_by(LokasiID=id).first()
                if select_query:
                    # select_query.LokasiID = args['LokasiID']
                    # if args['JenisPendapatanID']:
                    #     select_query.JenisPendapatanID = args['JenisPendapatanID']
                    if args['NamaLokasi']:
                        select_query.NamaLokasi = args['NamaLokasi']
                    if args['Periode']:
                        select_query.PeriodePajak = Periode
                    if args['TarifPajak']:
                        select_query.TarifPajak = args['TarifPajak']
                    if args['Satuan']:
                        select_query.Satuan = satuan
                    select_query.Target = 'P'
                    select_query.Status = status
                    select_query.UserUpd = uid
                    select_query.DateUpd = datetime.now()

                    db.session.commit()
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsTarifLokasi.query.filter_by(LokasiID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})
