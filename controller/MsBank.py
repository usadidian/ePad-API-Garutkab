from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads, failed_reads
from config.database import db
from controller.tblUser import tblUser


class MsBank(db.Model, SerializerMixin):
    __tablename__ = 'MsBank'
    BankID = db.Column(db.String, primary_key=True)
    Bank = db.Column(db.String, nullable=False)
    AkronimBank = db.Column(db.String, nullable=False)
    CabangBank = db.Column(db.String, nullable=False)
    AlamatBank = db.Column(db.String, nullable=False)
    TelpBank = db.Column(db.String, nullable=False)
    Status = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    class ListAll2( Resource ):
        def get(self, *args, **kwargs):
            try:
                select_query = db.session.execute(
                    f"SELECT BankID, Bank + ' - ' + CabangBank AS NamaBank, Bank FROM MsBank "
                    f"WHERE [Status]='1' ORDER BY NamaBank " )
                result = []
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr( row, key )
                    result.append( d )
                return success_reads( result )
            except Exception as e:
                print( e )
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

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            print(UserId)
            select_query = MsBank.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsBank.Bank.ilike(search),
                        MsBank.AkronimBank.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsBank, args['sort']).desc()
                else:
                    sort = getattr(MsBank, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsBank.BankID)

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
            parser.add_argument('BankID', type=str)
            parser.add_argument('Bank', type=str)
            parser.add_argument('AkronimBank', type=str)
            parser.add_argument('CabangBank', type=str)
            parser.add_argument('AlamatBank', type=str)
            parser.add_argument('TelpBank', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            select_query = db.session.execute(
                f"DECLARE @NoUrut INT,@BankID CHAR(2)"
                f"SET @NoUrut=ISNULL((SELECT DISTINCT MAX(CAST(mb.BankID AS INT)+1)  FROM MsBank AS mb),0)"
                f"SET @BankID = (select SUBSTRING('00' + CAST(@NoUrut as varchar), LEN(@NoUrut)+1 , 2))"
                f"SELECT @BankID AS bankid")
            result2 = select_query.first()[0]
            bankid = result2

            add_record = MsBank(
                BankID=bankid,
                Bank=args['Bank'],
                AkronimBank=args['AkronimBank'],
                CabangBank=args['CabangBank'],
                AlamatBank=args['AlamatBank'],
                TelpBank=args['TelpBank'],
                Status=args['Status'],
                UserUpd=uid,
                DateUpd=datetime.now(),

            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})
    class ListAll5(Resource):
        # method_decorators = {'get': [tblUser.auth_apikey_privilege], }

        def get(self,  *args, **kwargs):
            try:
                select_query = MsBank.query.all()
                result=[]
                for row in select_query:
                    result.append(row.to_dict())
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsBank.query.filter_by(BankID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('BankID', type=str)
            parser.add_argument('Bank', type=str)
            parser.add_argument('AkronimBank', type=str)
            parser.add_argument('CabangBank', type=str)
            parser.add_argument('AlamatBank', type=str)
            parser.add_argument('TelpBank', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = MsBank.query.filter_by(BankID=id).first()
                if select_query:
                    select_query.BankID = args['BankID']
                    select_query.Bank = args['Bank']
                    select_query.AkronimBank = args['AkronimBank']
                    select_query.CabangBank = args['CabangBank']
                    select_query.AlamatBank = args['AlamatBank']
                    select_query.TelpBank = args['TelpBank']
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
                delete_record = MsBank.query.filter_by(BankID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})