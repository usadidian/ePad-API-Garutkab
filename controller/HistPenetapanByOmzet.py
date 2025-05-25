from datetime import datetime

import sqlalchemy
from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy.sql.elements import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination, success_read, failed_read, success_update, failed_update, \
    success_delete, failed_delete
from config.database import db
from controller.MsPegawai import MsPegawai
from controller.PendataanByOmzet import PendataanByOmzet
from controller.tblUser import tblUser


class HistPenetapanByOmzet(db.Model, SerializerMixin):
    __tablename__ = 'HistPenetapanByOmzet'
    HistoryID = db.Column(db.Integer, primary_key=True)
    NoKohir = db.Column(db.String, nullable=False)
    KohirID = db.Column(db.String, nullable=False)
    OPDID = db.Column(db.Integer, nullable=False)
    TglPenetapan= db.Column(db.TIMESTAMP, nullable=False)
    TglJatuhTempo = db.Column(db.TIMESTAMP, nullable=False)
    MasaAwal = db.Column(db.TIMESTAMP, nullable=False)
    MasaAkhir = db.Column(db.TIMESTAMP, nullable=False)
    UrutTgl = db.Column(db.Integer, nullable=False)
    JmlOmzetAwal = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    TarifPajak = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    Denda = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    Kenaikan = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    IsPaid = db.Column(db.String, nullable=False)
    TglBayar = db.Column(db.TIMESTAMP, nullable=True)
    JmlBayar = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    TglKurangBayar = db.Column(db.TIMESTAMP, nullable=True)
    JmlKurangBayar = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    JmlPeringatan = db.Column(db.Integer, nullable=True)
    UPTID = db.Column(db.String, nullable=False)
    Status = db.Column(db.String, nullable=False)
    LKecamatan = db.Column(db.String, nullable=True)
    LKelurahan = db.Column(db.String, nullable=True)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)
    UserUpdHist = db.Column(db.String, nullable=False)
    DateUpdHist = db.Column(db.TIMESTAMP, nullable=False)


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
            select_query = HistPenetapanByOmzet.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(HistPenetapanByOmzet.KohirID.ilike(search),
                        HistPenetapanByOmzet.TglPenetapan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(HistPenetapanByOmzet, args['sort']).desc()
                else:
                    sort = getattr(HistPenetapanByOmzet, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(HistPenetapanByOmzet.KohirID)

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
            parser.add_argument('LKecamatan', type=str)
            parser.add_argument('LKelurahan', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            PegawaiID = kwargs['claim']["PegawaiID"]

            select_query = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
                tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
            result0 = select_query[0]
            uptid = result0

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

            result = []
            for row in result:
                result.append(row)

            add_record = HistPenetapanByOmzet(
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
                IsPaid=args['IsPaid'],
                TglBayar=sqlalchemy.sql.null(),
                JmlBayar=sqlalchemy.sql.null(),
                TglKurangBayar=sqlalchemy.sql.null(),
                JmlKurangBayar=sqlalchemy.sql.null(),
                JmlPeringatan=sqlalchemy.sql.null(),
                UPTID=uptid,
                Status=args['Status'],
                LKecamatan=args['LKecamatan'],
                LKelurahan=args['LKelurahan'],
                UserUpd=uid,
                DateUpd=datetime.now(),
                UserUpdHist = uid,
                DateUpdHist = datetime.now()
            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = HistPenetapanByOmzet.query.filter_by(KohirID=id).first()
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
            parser.add_argument('LKecamatan', type=str)
            parser.add_argument('LKelurahan', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            args = parser.parse_args()
            try:
                select_query = HistPenetapanByOmzet.query.filter_by(KohirID=id).first()
                if select_query:
                    select_query.NoKohir = args['NoKohir']
                    select_query.KohirID = args['KohirID']
                    select_query.OPDID = args['OPDID']
                    select_query.TglPenetapan = args['TglPenetapan']
                    select_query.TglJatuhTempo = args['TglJatuhTempo']
                    select_query.MasaAwal = args['MasaAwal']
                    select_query.MasaAkhir = args['MasaAkhir']
                    select_query.UrutTgl = args['UrutTgl']
                    select_query.JmlOmzetAwal = args['JmlOmzetAwal']
                    select_query.TarifPajak = args['TarifPajak']
                    select_query.Denda = args['Denda']
                    select_query.Kenaikan = args['Kenaikan']
                    select_query.IsPaid = args['IsPaid']
                    select_query.JmlBayar = args['JmlBayar']
                    select_query.TglKurangBayar = args['TglKurangBayar']
                    select_query.JmlKurangBayar = args['JmlKurangBayar']
                    select_query.JmlPeringatan = args['JmlPeringatan']
                    select_query.UPTID = args['UPTID']
                    select_query.Status = args['Status']
                    select_query.LKecamatan = args['LKecamatan']
                    select_query.LKelurahan = args['LKelurahan']
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
                delete_record = HistPenetapanByOmzet.query.filter_by(KohirID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})

