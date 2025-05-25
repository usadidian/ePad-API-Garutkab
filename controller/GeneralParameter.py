from datetime import datetime
from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import or_, case, func
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination
from config.database import db
from controller.tblUser import tblUser


class GeneralParameter(db.Model, SerializerMixin):
    __tablename__ = 'GeneralParameter'
    ParamID = db.Column(db.String, primary_key=True)
    NoUrut = db.Column(db.Integer, nullable=False)
    ParamName = db.Column(db.String, nullable=False)
    ParamStrValue= db.Column(db.String, nullable=False)
    ParamNumValue = db.Column(db.Numeric(12, 2), nullable=False)
    ParamUnit = db.Column(db.String, nullable=False)
    IsUpdateable = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

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

            paramnumvalue = GeneralParameter.query.with_entities(GeneralParameter.ParamStrValue).first()
            print(paramnumvalue)
            select_query = db.session.query(
                GeneralParameter.ParamID, GeneralParameter.NoUrut, GeneralParameter.ParamName,
                # GeneralParameter.ParamStrValue, GeneralParameter.ParamNumValue,
                case( [
                (GeneralParameter.ParamNumValue != None, func.dbo.DESIMAL(GeneralParameter.ParamNumValue))],
                else_=GeneralParameter.ParamStrValue ).label( 'ParamStrValue' ) )\
            .filter(GeneralParameter.IsUpdateable == 'Y')

            # select_query = GeneralParameter.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(GeneralParameter.NoUrut.ilike(search),
                        GeneralParameter.ParamName.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(GeneralParameter, args['sort']).desc()
                else:
                    sort = getattr(GeneralParameter, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(GeneralParameter.NoUrut)

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
            parser.add_argument('ParamID', type=str)
            parser.add_argument('ParentID', type=str)
            parser.add_argument('NoUrut', type=str)
            parser.add_argument('ParamName', type=str)
            parser.add_argument('ParamStrValue', type=str)
            parser.add_argument('ParamUnit', type=str)
            parser.add_argument('IsUpdateable', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            select_query = db.session.execute(
                f"SELECT MAX(NoUrut) + 1 AS NextID FROM GeneralParameter")
            result2 = select_query.first()[0]
            nourut = result2

            add_record = GeneralParameter(
                ParamID=args['ParamID'],
                NoUrut=nourut,
                ParamName=args['ParamName'],
                ParamStrValue=args['ParamStrValue'],
                ParamUnit=args['ParamUnit'],
                IsUpdateable=args['IsUpdateable'],
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
                select_query = GeneralParameter.query.filter_by(NoUrut=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('ParamID', type=str)
            parser.add_argument('NoUrut', type=str)
            parser.add_argument('ParamName', type=str)
            parser.add_argument('ParamStrValue', type=str)
            parser.add_argument('ParamUnit', type=str)
            parser.add_argument('IsUpdateable', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = GeneralParameter.query.filter_by(NoUrut=id).first()
                if select_query:
                    if args['ParamID']:
                        select_query.ParamID = args['ParamID']
                    if args['NoUrut']:
                        select_query.NoUrut = args['NoUrut']
                    if args['ParamName']:
                        select_query.ParamName = args['ParamName']
                    if args['ParamStrValue']:
                        # if select_query.ParamNumValue == 0:
                        select_query.ParamStrValue = args['ParamStrValue']
                        # else:
                        select_query.ParamNumValue = float(args['ParamStrValue'])
                    if args['ParamUnit']:
                        select_query.ParamUnit = args['ParamUnit']
                    if args['IsUpdateable']:
                        select_query.IsUpdateable = args['IsUpdateable']

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
                delete_record = GeneralParameter.query.filter_by(NoUrut=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})

