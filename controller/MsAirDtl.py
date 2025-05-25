from datetime import datetime

from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads, failed_reads
from config.database import db
from controller.MsAirHdr import MsAirHdr
from controller.tblUser import tblUser


class MsAirDtl(db.Model, SerializerMixin):
    __tablename__ = 'MsAirDtl'
    ATID = db.Column(db.Integer, primary_key=True)
    ATUrut = db.Column(db.String, nullable=False)
    Nama = db.Column( db.String, nullable=False )
    Nilai = db.Column(db.Numeric(12, 2), nullable=False)
    Status = db.Column( db.String, nullable=False )
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column( db.String, nullable=False )

    ATGrup = db.Column( db.Integer, db.ForeignKey( 'MsAirHdr.ATGrup' ), nullable=False )


    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            try:
                select_query = db.session.execute(
                    f"SELECT ATID,Nama + (case when nilai=0 then '' else ' (' + convert(varchar,nilai) + ')' end) "
                    f"AS Nama FROM MsAirDtl WHERE ATGrup = '61' AND [Status] = '1' ORDER BY ATUrut ")

                result=[]
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr(row, key)
                    result.append(d)
                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_reads()

    class ListAll3(Resource):
        def get(self, *args, **kwargs):
            try:
                select_query = db.session.execute(
                    f"SELECT ATID, Nama FROM MsAirDtl WHERE ATGrup = '91' AND [Status] = '1' ORDER BY ATUrut ")

                result=[]
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr(row, key)
                    result.append(d)
                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_reads()

    class ListAll4(Resource):
        def get(self, *args, **kwargs):
            try:
                select_query = db.session.execute(
                    f"SELECT ATID ,Nama + (case when nilai=0 then '' else ' (' + convert(varchar,nilai) + ')' end) "
                    f"AS Nama FROM MsAirDtl WHERE ATGrup = '81' AND [Status] = '1' ORDER BY ATUrut  ")
                result=[]
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr(row, key)
                    result.append(d)
                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_reads()

    class ListAll5(Resource):
        def get(self, *args, **kwargs):
            try:
                select_query = db.session.execute(
                    f"SELECT ATID,Nama + (case when nilai=0 then '' else ' (' + convert(varchar,nilai) + ')' end) "
                    f"AS Nama FROM MsAirDtl WHERE ATGrup = '71' AND [Status] = '1' ORDER BY ATUrut ")
                result=[]
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr(row, key)
                    result.append(d)
                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_reads()


    class ListAll6(Resource):
        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument( 'ATUrut', type=int )
            parser.add_argument( 'A81', type=int )
            parser.add_argument( 'A71', type=int )
            parser.add_argument( 'ATGrup', type=str )
            args = parser.parse_args()

            try:
                select_query = db.session.execute(
                    f"SELECT (select Nilai from MsAirDtl where ATUrut={args['ATUrut']} and ATGrup=91) AS f1,(select Nilai from MsAirDtl "
                    f"where ATUrut={args['ATUrut']}  and ATGrup=92) AS f2,(select Nilai from MsAirDtl where ATUrut={args['ATUrut']}  and ATGrup=93) AS f3,"
                    f"(select Nilai from MsAirDtl where ATUrut={args['ATUrut']} and ATGrup=94) AS f4, (select Nilai from MsAirDtl "
                    f"where ATUrut={args['ATUrut']} and ATGrup=95) AS f5,(select Nilai from MsAirDtl where ATID='8001') AS psnsda,"
                    f"(select Nilai from MsAirDtl where ATID='8002') AS psnutk,(select Nilai from MsAirDtl where ATID={args['A81']}) "
                    f"AS kompsda, (select Nilai from MsAirDtl where ATID = {args['A71']})) AS denda ")
                result=[]
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr(row, key)
                    result.append(d)
                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_reads()

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
            parser.add_argument( 'ATUrut', type=str )

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            print(UserId)

            select_query = db.session.query(MsAirDtl.ATID, MsAirDtl.ATGrup, MsAirDtl.ATUrut,
                                            MsAirDtl.Nama, MsAirDtl.Nilai) \
                .outerjoin( MsAirHdr, MsAirDtl.ATGrup == MsAirHdr.ATGrup ) \


            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsAirDtl.ATID.ilike(search),
                        MsAirDtl.ATGrup.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsAirDtl, args['sort']).desc()
                else:
                    sort = getattr(MsAirDtl, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsAirDtl.ATGrup)

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
            return success_reads_pagination( query_execute, result )

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('ATUrut', type=str)
            parser.add_argument('ATGrup', type=str)
            parser.add_argument('Nama', type=str)
            parser.add_argument( 'Nilai', type=str )
            parser.add_argument( 'Status', type=str )
            parser.add_argument( 'UserUpd', type=str )
            parser.add_argument( 'DateUpd', type=str )

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()


            result = []
            for row in result:
                result.append(row)

            select_query = db.session.execute(
                f"SELECT CAST(MAX(CAST(ATID AS int) + 1) AS varchar(10)) AS NextID FROM MsAirDtl")
            result2 = select_query.first()[0]
            ATID = result2

            add_record = MsAirDtl(
                ATID=ATID,
                ATGrup=args['ATGrup'],
                ATUrut=args['ATUrut'],
                Nama=args['Nama'],
                Nilai=args['Nilai'],
                Status=args['Status'],
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
                select_query = MsAirDtl.query.filter_by(ATID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            # parser.add_argument( 'ATID', type=str )
            parser.add_argument('ATUrut', type=str)
            parser.add_argument('ATGrup', type=str)
            parser.add_argument('Nilai', type=str)
            parser.add_argument('Nama', type=str)
            parser.add_argument( 'Status', type=str )
            parser.add_argument( 'UserUpd', type=str )
            parser.add_argument( 'DateUpd', type=str )

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = MsAirDtl.query.filter_by(ATID=id).first()
                if select_query:
                    if args['ATUrut']:
                        select_query.ATUrut = args['ATUrut']
                    if args['ATGrup']:
                        select_query.ATGrup = args['ATGrup']
                    if args['Nilai']:
                        select_query.Nilai = args['Nilai']
                    if args['Nama']:
                        select_query.Nama = args['Nama']
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
                delete_record = MsAirDtl.query.filter_by(ATID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})
