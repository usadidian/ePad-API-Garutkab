from datetime import datetime
from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy.sql.elements import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_reads_pagination, success_update, success_read, failed_read, failed_update, \
    success_delete, failed_delete
from config.database import db
from controller.MsPegawai import MsPegawai
from controller.tblUser import tblUser


class PendataanReklameHdr(db.Model, SerializerMixin):
    __tablename__ = 'PendataanReklameHdr'
    PendataanID = db.Column(db.Integer, primary_key=True)
    SPT = db.Column(db.String, nullable=False)
    TglPendataan = db.Column(db.TIMESTAMP, nullable=False)
    MasaAwal = db.Column(db.TIMESTAMP, nullable=False)
    MasaAkhir = db.Column(db.TIMESTAMP, nullable=False)
    UrutTgl = db.Column(db.Integer, nullable=False)
    TotalPajak = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    UPTID = db.Column(db.String, nullable=False)
    Status = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    OPDID = db.Column(db.Integer, db.ForeignKey('MsOPD.OPDID'), nullable=False)

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
            select_query = PendataanReklameHdr.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(PendataanReklameHdr.OPDID.ilike(search),
                        PendataanReklameHdr.TglPendataan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(PendataanReklameHdr, args['sort']).desc()
                else:
                    sort = getattr(PendataanReklameHdr, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(PendataanReklameHdr.SPT)

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
            parser.add_argument('SPT', type=str)
            parser.add_argument('OPDID', type=str)
            parser.add_argument('TglPendataan', type=str)
            parser.add_argument('MasaAwal', type=str)
            parser.add_argument('MasaAkhir', type=str)
            parser.add_argument('UrutTgl', type=str)
            parser.add_argument('TotalPajak', type=str)
            parser.add_argument('UPTID', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            PegawaiID = kwargs['claim']["PegawaiID"]

            select_query = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
                tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
            result = select_query[0]
            uptid = result

            args = parser.parse_args()
            result = db.session.execute(
                f"exec [SP_SPT] '{args['TglPendataan']}'")

            result2 = []
            for row in result:
                result2.append(row)
                # print(row[0])
            spt = result2[0][0]

            select_query = db.session.execute(
                f"SELECT DISTINCT isnull(max(UrutTgl) + 1,1) FROM PendataanReklameHdr "
                f"WHERE OPDID = '{args['OPDID']}' AND MasaAwal='{args['MasaAwal']}' AND MasaAkhir='{args['MasaAkhir']}'")
            result3 = select_query.first()[0]
            uruttgl = result3

            add_record = PendataanReklameHdr(
                SPT=spt,
                OPDID=args['OPDID'],
                TglPendataan=args['TglPendataan'],
                MasaAwal=args['MasaAwal'],
                MasaAkhir=args['MasaAkhir'],
                UrutTgl=uruttgl,
                TotalPajak=args['TotalPajak'],
                UPTID=uptid,
                Status=args['Status'],
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
                select_query = PendataanReklameHdr.query.filter_by(SPT=id).first()
                result = select_query.to_dict()
                return success_read(result)

            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('SPT', type=str)
            parser.add_argument('OPDID', type=str)
            parser.add_argument('TglPendataan', type=str)
            parser.add_argument('MasaAwal', type=str)
            parser.add_argument('MasaAkhir', type=str)
            parser.add_argument('UrutTgl', type=str)
            parser.add_argument('TotalPajak', type=str)
            parser.add_argument('UPTID', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = PendataanReklameHdr.query.filter_by(SPT=id).first()
                if select_query:
                    select_query.OPDID = args['OPDID']
                    select_query.TglPendataan = args['TglPendataan']
                    select_query.MasaAwal = args['MasaAwal']
                    select_query.MasaAkhir = args['MasaAkhir']
                    select_query.UrutTgl = args['UrutTgl']
                    select_query.TotalPajak = args['TotalPajak']
                    select_query.UPTID = args['UPTID']
                    select_query.Status = args['Status']
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
                delete_record = PendataanReklameHdr.query.filter_by(SPT=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})
