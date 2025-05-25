from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_, case
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.MsPegawai import MsPegawai
from controller.MsUPT import MsUPT
from controller.tblUser import tblUser
from controller.vw_bendahara import vw_bendahara


class MsBendahara(db.Model, SerializerMixin):
    __tablename__ = 'MsBendahara'
    BendaharaID = db.Column(db.String, primary_key=True)
    # PegawaiID = db.Column(db.String, nullable=False)s
    Rekening = db.Column(db.String, nullable=False)
    NamaRekening = db.Column(db.String, nullable=False)
    Status = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    PegawaiID = db.Column(db.String, db.ForeignKey('MsBendahara.PegawaiID'), nullable=False)


    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT BendaharaID AS Kode,Nama + ' - ' + (case when KodeUPT in (select distinct kode_badan from vw_header) "
                f"then (select distinct badan_singkat from vw_header) else UPT end) AS Nama FROM ((MsBendahara b LEFT JOIN "
                f"MsPegawai p ON b.PegawaiID = p.PegawaiID) LEFT JOIN MsUPT u ON u.UPTID = p.UPTID) WHERE b.[Status] = '1' "
                f"AND p.[Status] = '1'  ORDER BY Nama")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll5(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT BendaharaID,NIP,Nama AS Bendahara, "
                f"UPT, (Case when b.Status=1 then 'Aktif' else 'Non Aktif' end) as Status FROM ((MsBendahara b INNER JOIN "
                f"MsPegawai p ON b.PegawaiID = p.PegawaiID) INNER JOIN MsUPT u ON u.UPTID = p.UPTID)  "
                f"ORDER BY Nama")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
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

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            # print(UserId)
            # select_query = vw_bendahara.query
            select_query = db.session.query(
                vw_bendahara.BendaharaID, vw_bendahara.NIP, vw_bendahara.Nama, vw_bendahara.PegawaiID,
                vw_bendahara.UPTID, vw_bendahara.UPT,vw_bendahara.UserUpd, vw_bendahara.DateUpd,vw_bendahara.Status) \


            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_bendahara.BendaharaID.ilike(search),
                        vw_bendahara.PegawaiID.ilike(search),
                        vw_bendahara.Nama.ilike(search),
                        vw_bendahara.NIP.ilike(search))
                )

            ### SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_bendahara, args['sort']).desc()
                else:
                    sort = getattr(vw_bendahara, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_bendahara.Nama)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
                print( result )
            return success_reads_pagination( query_execute, result )


        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            # parser.add_argument('BendaharaID', type=str)
            parser.add_argument('PegawaiID', type=str)
            # parser.add_argument('BankID', type=str)
            # parser.add_argument('Rekening', type=str)
            # parser.add_argument('NamaRekening', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            select_query = db.session.execute(
                f"SELECT CAST(MAX(CAST(BendaharaID AS int) + 1) AS varchar(10)) AS NextID FROM MsBendahara")
            result2 = select_query.first()[0]
            bendaharaid = result2

            add_record = MsBendahara(
                BendaharaID=bendaharaid,
                PegawaiID=args['PegawaiID'],
                # BankID=args['BankID'],
                # Rekening=args['Rekening'],
                # NamaRekening=args['NamaRekening'],
                Status=1,
                UserUpd=uid,
                DateUpd=datetime.now(),

            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsBendahara.query.filter_by(BendaharaID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('BendaharaID', type=str)
            parser.add_argument('PegawaiID', type=str)
            # parser.add_argument('BankID', type=str)
            # parser.add_argument('Rekening', type=str)
            # parser.add_argument('NamaRekening', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            if args['Status'] == 'Aktif':
                status = 1
            if args['Status'] == 'Non Aktif':
                status = 0
            try:
                select_query = MsBendahara.query.filter_by( BendaharaID=id ).first()
                if select_query:
                    if args['BendaharaID']:
                        select_query.BendaharaID = args['BendaharaID']
                    if args['PegawaiID']:
                        select_query.PegawaiID = args['PegawaiID']
                    # select_query.BankID = args['BankID']
                    # select_query.Rekening = args['Rekening']
                    # select_query.NamaRekening = args['NamaRekening']
                    if args['Status']:
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
                delete_record = MsBendahara.query.filter_by(BendaharaID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})