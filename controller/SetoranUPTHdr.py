from datetime import datetime
from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_reads_pagination, success_read, failed_read, success_update, failed_update, \
    success_delete, failed_delete
from config.database import db
from controller.tblUser import tblUser


class SetoranUPTHdr(db.Model, SerializerMixin):
    __tablename__ = 'SetoranUPTHdr'
    HeaderID = db.Column(db.Integer, primary_key=True)
    UPTID = db.Column(db.String, nullable=False)
    SetoranDari = db.Column(db.String, nullable=False)
    NoSTS = db.Column(db.String, nullable=False)
    STSKe = db.Column(db.Integer, nullable=False)
    TglSetoran = db.Column(db.TIMESTAMP, nullable=False)
    Keterangan = db.Column(db.String, nullable=False)
    StatusBayar = db.Column(db.String, nullable=True)
    Status = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    BendaharaID = db.Column(db.String, db.ForeignKey('MsBendahara.BendaharaID'), nullable=False)
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
            select_query = SetoranUPTHdr.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(SetoranUPTHdr.NoSTS.ilike(search),
                        SetoranUPTHdr.TglSetoran.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(SetoranUPTHdr, args['sort']).desc()
                else:
                    sort = getattr(SetoranUPTHdr, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(SetoranUPTHdr.NoSTS)

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
            # parser.add_argument('HeaderID', type=str)
            parser.add_argument('UPTID', type=str)
            parser.add_argument('SetoranDari', type=str)
            parser.add_argument('NoSTS', type=str)
            parser.add_argument('STSKe', type=str)
            parser.add_argument('TglSetoran', type=str)
            parser.add_argument('Keterangan', type=str)
            parser.add_argument('StatusBayar', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('BendaharaID', type=str)
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
            # result1 = db.session.execute(
            #     f"exec [SP_SSPD]")
            # result2 = []
            # for row in result1:
            #     result2.append(row)
            # nosspd = result2[0][0]

            select_query = db.session.execute(
                f"SELECT DISTINCT ISNULL(MAX(STSKe),0) + 1 FROM SetoranUPTHdr WHERE UPTID = '{args['UPTID']}' AND NoSTS ='{args['NoSTS']}'")
            result3 = select_query.first()[0]
            STSKe = result3

            result = []
            for row in result:
                result.append(row)

            add_record = SetoranUPTHdr(
                # HeaderID=args['HeaderID'],
                UPTID=args['UPTID'],
                SetoranDari=args['SetoranDari'],
                NoSTS=args['NoSTS'],
                STSKe=STSKe,
                TglSetoran=args['TglSetoran'],
                Keterangan=args['Keterangan'],
                StatusBayar=args['StatusBayar'],
                Status=args['Status'],
                BendaharaID=args['BendaharaID'],
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
                select_query = SetoranUPTHdr.query.filter_by(HeaderID=id).first()
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
            parser.add_argument('UPTID', type=str)
            parser.add_argument('SetoranDari', type=str)
            parser.add_argument('NoSTS', type=str)
            parser.add_argument('STSKe', type=str)
            parser.add_argument('TglSetoran', type=str)
            parser.add_argument('Keterangan', type=str)
            parser.add_argument('StatusBayar', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('BendaharaID', type=str)
            parser.add_argument('KodeStatus', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            args = parser.parse_args()
            try:
                select_query = SetoranUPTHdr.query.filter_by(HeaderID=id).first()
                if select_query:
                    select_query.UPTID = args['UPTID']
                    select_query.SetoranDari = args['SetoranDari']
                    select_query.NoSTS = args['NoSTS']
                    select_query.STSKe = args['STSKe']
                    select_query.TglSetoran = args['TglSetoran']
                    select_query.Keterangan = args['Keterangan']
                    select_query.StatusBayar = args['StatusBayar']
                    select_query.Status = args['Status']
                    select_query.BendaharaID = args['BendaharaID']
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
                delete_record = SetoranUPTHdr.query.filter_by(HeaderID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})