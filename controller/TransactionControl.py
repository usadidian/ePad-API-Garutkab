from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_, distinct, func
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination
from config.database import db
from controller.tblUser import tblUser

class TransactionControl(db.Model, SerializerMixin):
    __tablename__ = 'TransactionControl'
    TransactionID = db.Column(db.Integer, primary_key=True)
    JenisPendapatanID = db.Column(db.String, nullable=False)
    NamaTransaksi = db.Column(db.String, nullable=True)
    YearTransaksi = db.Column(db.String, nullable=True)
    MonthTransaksi= db.Column(db.String, nullable=True)
    LastNum = db.Column(db.Integer, nullable=True)
    LastDate = db.Column(db.TIMESTAMP, nullable=True)
    ResetType = db.Column(db.String, nullable=True)

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
            select_query = TransactionControl.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(TransactionControl.YearTransaksi.ilike(search),
                        TransactionControl.MonthTransaksi.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(TransactionControl, args['sort']).desc()
                else:
                    sort = getattr(TransactionControl, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(TransactionControl.TransactionID)

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
            parser.add_argument('JenisPendapatanID', type=str)
            parser.add_argument('NamaTransaksi', type=str)
            parser.add_argument('YearTransaksi', type=str)
            parser.add_argument('MonthTransaksi', type=str)
            parser.add_argument('LastNum', type=str)
            parser.add_argument('LastDate', type=str)
            parser.add_argument('ResetType', type=str)

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            # select_query = session.query(distinct(func.date_part('YEAR', TransactionControl.YearTransaksi)))
            # result2 = select_query.first()[0]
            # yeartransaksi = result2
            #
            # select_query2 = session.query(distinct(func.date_part('MONTH', TransactionControl.MonthTransaksi)))
            # result3 = select_query2.first()[0]
            # monthtransaksi = result3

            add_record = TransactionControl(
                JenisPendapatanID=args['JenisPendapatanID'],
                NamaTransaksi=args['NamaTransaksi'],
                YearTransaksi=args['YearTransaksi'],
                MonthTransaksi=args['MonthTransaksi'],
                LastNum=args['LastNum'],
                LastDate=datetime.now(),
                ResetType=args['ResetType'],

            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = TransactionControl.query.filter_by(TransactionID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('JenisPendapatanID', type=str)
            parser.add_argument('NamaTransaksi', type=str)
            parser.add_argument('YearTransaksi', type=str)
            parser.add_argument('MonthTransaksi', type=str)
            parser.add_argument('LastNum', type=str)
            parser.add_argument('LastDate', type=str)
            parser.add_argument('ResetType', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = TransactionControl.query.filter_by(TransactionID=id).first()
                if select_query:
                    select_query.JenisPendapatanID = args['JenisPendapatanID']
                    select_query.NamaTransaksi = args['NamaTransaksi']
                    select_query.YearTransaksi = args['YearTransaksi']
                    select_query.MonthTransaksi = args['MonthTransaksi']
                    select_query.LastNum = args['LastNum']
                    select_query.LastDate = args['LastDate']
                    select_query.ResetType = args['ResetType']
                    db.session.commit()
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = TransactionControl.query.filter_by(TransactionID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})

