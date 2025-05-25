from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads, failed_reads
from config.database import db
from controller.GeneralParameter import GeneralParameter
from controller.MsUPT import MsUPT
from controller.tblUser import tblUser


class MsKawasan( db.Model, SerializerMixin ):
    __tablename__ = 'MsKawasan'
    KawasanID = db.Column( db.String, primary_key=True )
    Kawasan = db.Column( db.String, nullable=False )

    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            try:
                select_query = db.session.execute(
                    f"SELECT KawasanID, Kawasan FROM MsKawasan ORDER BY Kawasan ")
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

    class ListAll( Resource ):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument( 'page', type=int )
            parser.add_argument( 'length', type=int )
            parser.add_argument( 'sort', type=str )
            parser.add_argument( 'sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC' )
            parser.add_argument( 'search', type=str )

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            print( UserId )
            select_query = db.session.query( MsKawasan.KawasanID, MsKawasan.Kawasan )

                # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format( args['search'] )
                select_query = select_query.filter(
                    or_( MsKawasan.KawasanID.ilike( search ),
                         MsKawasan.Kawasan.ilike( search ) )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr( MsKawasan, args['sort'] ).desc()
                else:
                    sort = getattr( MsKawasan, args['sort'] ).asc()
                select_query = select_query.order_by( sort )
            else:
                select_query = select_query.order_by( MsKawasan.KawasanID )

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate( page, lengthLimit )

            result = []
            for row in query_execute.items:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads_pagination( query_execute, result )

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument( 'KawasanID', type=str )
            parser.add_argument( 'Kawasan', type=str )

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append( row )

            select_query = db.session.execute(
                f"SELECT CAST(MAX(CAST(KawasanID AS int) + 1) AS varchar(10)) AS NextID FROM MsKawasan" )
            result2 = select_query.first()[0]
            KawasanID = result2

            add_record = MsKawasan(
                KawasanID=KawasanID,
                Kawasan=args['Kawasan'],
            )
            db.session.add( add_record )
            db.session.commit()
            return jsonify( {'status_code': 1, 'message': 'OK', 'data': result} )

    class ListById( Resource ):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsKawasan.query.filter_by( KawasanID=id ).first()
                result = select_query.to_dict()
                return success_read( result )
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_read( {} )

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print( kwargs['claim'] )
            parser.add_argument( 'KawasanID', type=str )
            parser.add_argument( 'Kawasan', type=str )
            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = MsKawasan.query.filter_by( KawasanID=id ).first()
                if select_query:
                    if args['KawasanID']:
                        select_query.KawasanID = args['KawasanID']
                    if args['Kawasan']:
                        select_query.Kawasan = args['Kawasan']
                    db.session.commit()
                    return success_update( {'id': id} )
            except Exception as e:

                db.session.rollback()
                print( e )
                return failed_update( {} )

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsKawasan.query.filter_by( KawasanID=id )
                delete_record.delete()
                db.session.commit()
                return success_delete( {} )
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_delete( {} )