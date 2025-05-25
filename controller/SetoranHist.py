from datetime import datetime

from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination, success_read, failed_read, success_update, failed_update, \
    success_delete, failed_delete
from config.database import db
from controller.MsPegawai import MsPegawai
from controller.tblUser import tblUser


class SetoranHist(db.Model, SerializerMixin):
    __tablename__ = 'SetoranHist'
    SetoranHistID = db.Column(db.BigInteger, primary_key=True)
    NoKohir = db.Column(db.String, nullable=False)
    NoUrut = db.Column(db.Integer, nullable=False)
    SubKohir = db.Column(db.String, nullable=False)
    TglBayar = db.Column(db.TIMESTAMP, nullable=False)
    JmlBayar = db.Column(db.Numeric(12, 2), nullable=False)
    JmlBayarOpsen = db.Column(db.Numeric(12, 2), nullable=False)
    JmlBayarDenda = db.Column(db.Numeric(12, 2), nullable=True)
    Transaksi = db.Column(db.String, nullable=False)
    NoSSPD = db.Column(db.String, nullable=False)
    STS = db.Column( db.String, nullable=True )
    STSDenda = db.Column( db.String, nullable=True )
    NamaPenyetor = db.Column(db.String, nullable=True)

    # STS = db.Column(db.String, nullable=True)
    # STS = db.Column(db.String, nullable=True)

    Keterangan = db.Column(db.String, nullable=True)

    # NTPD = db.Column(db.String, nullable=True)
    # NTB = db.Column(db.String, nullable=True)
    # TglNTPD = db.Column(db.TIMESTAMP, nullable=False)

    BendID = db.Column(db.String, nullable=True)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    KodeStatus = db.Column(db.String, db.ForeignKey('MsJenisStatus.KodeStatus'), nullable=False)

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
            select_query = SetoranHist.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(SetoranHist.NoSSPD.ilike(search),
                        SetoranHist.TglBayar.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(SetoranHist, args['sort']).desc()
                else:
                    sort = getattr(SetoranHist, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(SetoranHist.NoSSPD)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)

        def post(self, apikey_decode=None, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('NoKohir', type=str)
            parser.add_argument('NoUrut', type=str)
            parser.add_argument('SubKohir', type=str)
            parser.add_argument('TglBayar', type=str)
            parser.add_argument('JmlBayar', type=str)
            parser.add_argument('JmlBayarDenda', type=str)
            parser.add_argument('Transaksi', type=str)
            parser.add_argument('NoSSPD', type=str)
            parser.add_argument('NamaPenyetor', type=str)

            # parser.add_argument('STS', type=str)
            # parser.add_argument('STSDenda', type=str)

            parser.add_argument('Keterangan', type=str)

            # parser.add_argument('NTPD', type=str)
            # parser.add_argument('NTB', type=str)
            # parser.add_argument('TglNTPD', type=str)

            parser.add_argument('BendID', type=str)
            parser.add_argument('KodeStatus', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            # PegawaiID = kwargs['claim']["PegawaiID"]
            #
            # select_query = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
            #     tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
            # result0 = select_query[0]
            # uptid = result0

            args = parser.parse_args()
            result1 = db.session.execute(
                f"exec [SP_SSPD]")
            result2 = []
            for row in result1:
                result2.append(row)
            nosspd = result2[0][0]

            select_query = db.session.execute(
                f"SELECT DISTINCT ISNULL(MAX(NoUrut),0) + 1 FROM SetoranHist WHERE SubKohir = '{args['SubKohir']}'")
            result3 = select_query.first()[0]
            nourut = result3

            result = []
            for row in result:
                result.append(row)

            add_record = SetoranHist(
                NoKohir=args['NoKohir'],
                NoUrut=nourut,
                SubKohir=args['SubKohir'],
                TglBayar=args['TglBayar'],
                JmlBayar=args['JmlBayar'],
                JmlBayarDenda=args['JmlBayarDenda'],
                Transaksi=args['Transaksi'],
                NoSSPD=nosspd,
                NamaPenyetor=args['NamaPenyetor'],
                Keterangan=args['Keterangan'],
                BendID=args['BendID'],
                KodeStatus=args['KodeStatus'],
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
                select_query = SetoranHist.query.filter_by(SetoranHistID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser = reqparse.RequestParser()
            parser.add_argument('SetoranHistID', type=str)
            parser.add_argument('NoKohir', type=str)
            parser.add_argument('NoUrut', type=str)
            parser.add_argument('SubKohir', type=str)
            parser.add_argument('TglBayar', type=str)
            parser.add_argument('JmlBayar', type=str)
            parser.add_argument('JmlBayarDenda', type=str)
            parser.add_argument('Transaksi', type=str)
            parser.add_argument('NoSSPD', type=str)
            parser.add_argument('NamaPenyetor', type=str)
            parser.add_argument('Keterangan', type=str)
            parser.add_argument('BendID', type=str)
            parser.add_argument('KodeStatus', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)


            uid = kwargs['claim']["UID"]
            args = parser.parse_args()
            try:
                select_query = SetoranHist.query.filter_by(SetoranHistID=id).first()
                if select_query:
                    select_query.NoKohir = args['NoKohir']
                    select_query.NoUrut = args['NoUrut']
                    select_query.SubKohir = args['SubKohir']
                    select_query.TglBayar = args['TglBayar']
                    select_query.JmlBayar = args['JmlBayar']
                    select_query.JmlBayarDenda = args['JmlBayarDenda']
                    select_query.Transaksi = args['Transaksi']
                    select_query.NoSSPD = args['NoSSPD']
                    select_query.NamaPenyetor = args['NamaPenyetor']
                    select_query.Keterangan = args['Keterangan']
                    select_query.BendID = args['BendID']
                    select_query.KodeStatus = args['KodeStatus']
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
                delete_record = SetoranHist.query.filter_by(SetoranHistID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})