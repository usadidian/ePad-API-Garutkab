from datetime import datetime

from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination, success_read, failed_read, \
    success_update, failed_update, success_delete, failed_delete, success_reads
from config.database import db


class tblUrl(db.Model, SerializerMixin):

    __tablename__ = 'tblUrl'
    UrlId = db.Column(db.Integer, primary_key=True)
    Url = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT u.UrlId, u.Url, u.description FROM TblUrl u "
                f"LEFT JOIN tblMenuDet m ON m.UrlId=u.UrlId "
                f"WHERE u.UrlId NOT IN(SELECT d.UrlId FROM tblMenuDet d )"
                f"order by u.UrlId")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll3(Resource):
        def get(self, *args, **kwargs):
            # Menggunakan RequestParser untuk mengambil 'MenuId' dari parameter query
            parser = reqparse.RequestParser()
            parser.add_argument('MenuId', type=str, required=False, help="MenuId is required and should be a string.")
            parsed_args = parser.parse_args()

            # Ambil MenuId dari parsed_args
            idmenu = parsed_args.get('MenuId')

            if not idmenu:
                return {"message": "MenuId is required and should be a string."}, 400

            print(f"MenuId: {idmenu}")

            # Eksekusi subquery
            subquery_result = db.session.execute(
                """
                SELECT UrlId
                FROM tblMenuDet
                WHERE MenuId = :idmenu
                """, {'idmenu': idmenu}).fetchall()

            print(f"Subquery Result: {subquery_result}")

            # Eksekusi main query
            select_query = db.session.execute(
                """
                SELECT UrlId, Url, description
                FROM TblUrl
                WHERE UrlId NOT IN (
                    SELECT UrlId FROM tblMenuDet WHERE MenuId = :idmenu
                )
                ORDER BY UrlId
                """, {'idmenu': idmenu})

            result = []
            for row in select_query:
                d = {key: getattr(row, key) for key in row.keys()}
                result.append(d)

            return success_reads(result)

    class ListAll( Resource ):
        # method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument( 'page', type=int )
            parser.add_argument( 'length', type=int )
            parser.add_argument( 'sort', type=str )
            parser.add_argument( 'sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC' )
            parser.add_argument( 'search', type=str )

            args = parser.parse_args()
            # UserId = kwargs['claim']["UserId"]
            # print( UserId )
            select_query = db.session.query( tblUrl.UrlId, tblUrl.Url, tblUrl.description)

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format( args['search'] )
                select_query = select_query.filter(
                    or_( tblUrl.Url.ilike( search ),
                         tblUrl.description.ilike( search ) )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr( tblUrl, args['sort'] ).desc()
                else:
                    sort = getattr( tblUrl, args['sort'] ).asc()
                select_query = select_query.order_by( sort )
            else:
                select_query = select_query.order_by( tblUrl.UrlId )

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
            parser.add_argument( 'Url', type=str )
            parser.add_argument( 'description', type=str )
            parser.add_argument( 'UserUpd', type=str )
            parser.add_argument( 'DateUpd', type=str )

            # uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append( row )

            add_record = tblUrl(

                Url=args['Url'],
                description=args['description'] if args['description'] else '-',
                UserUpd='',
                DateUpd=datetime.now(),

            )
            db.session.add( add_record )
            db.session.commit()
            return jsonify( {'status_code': 1, 'message': 'OK', 'data': result} )

    class ListById( Resource ):
        # method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
        #                      'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = tblUrl.query.filter_by( UrlId=id ).first()
                result = select_query.to_dict()
                return success_read( result )
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_read( {} )

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            # print( kwargs['claim'] )
            parser.add_argument( 'Url', type=str )
            parser.add_argument( 'description', type=str )
            # parser.add_argument('UserUpd', type=str)
            # parser.add_argument('DateUpd', type=str)

            # uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = tblUrl.query.filter_by( UrlId=id ).first()
                if select_query:

                    if args['Url']:
                        select_query.Url = args['Url']
                    if args['description']:
                        select_query.description = args['description']
                    # select_query.UserUpd = uid
                    select_query.DateUpd = datetime.now()
                    db.session.commit()
                    return success_update( {'id': id} )
            except Exception as e:

                db.session.rollback()
                print( e )
                return failed_update( {} )

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = tblUrl.query.filter_by( UrlId=id )
                delete_record.delete()
                db.session.commit()
                return success_delete( {} )
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_delete( {} )