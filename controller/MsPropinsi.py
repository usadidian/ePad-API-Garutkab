from flask_restful import Resource, reqparse
from sqlalchemy.sql import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination, failed_reads, success_reads
from config.database import db
from controller.tblUser import tblUser


class MsPropinsi(db.Model, SerializerMixin):
    __tablename__ = 'MsPropinsi'
    PropinsiID = db.Column(db.Integer, primary_key=True)
    Propinsi = db.Column(db.String, nullable=False)
    Kode = db.Column( db.String, nullable=True )

    class propinsi(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument( 'page', type=int )
            parser.add_argument( 'length', type=int )
            parser.add_argument( 'sort', type=str )
            parser.add_argument( 'sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC' )
            parser.add_argument( 'search', type=str )

            args = parser.parse_args()
            try:
                result = []
                select_query = db.session.query(
                    MsPropinsi.PropinsiID.label('propinsiid'), MsPropinsi.Propinsi.label('propinsi')
                )

                if args['search'] and len(args['search']) > 0:
                    search = "%{}%".format(args['search'])
                    select_query = select_query.filter(
                        or_(
                            MsPropinsi.Propinsi.like(search),
                            MsPropinsi.PropinsiID.like(search),
                        )
                    )

                # SORT
                if args['sort']:
                    if args['sort_dir'] == "desc":
                        sort = getattr( MsPropinsi, args['sort'] ).desc()
                    else:
                        sort = getattr( MsPropinsi, args['sort'] ).asc()
                    select_query = select_query.order_by( sort )
                else:
                    select_query = select_query.order_by( MsPropinsi.PropinsiID )

                # PAGINATION
                page = args['page'] if args['page'] else 1
                length = args['length'] if args['length'] else 5
                lengthLimit = length if length < 101 else 100
                query_execute = select_query.paginate( page, lengthLimit )

                result = []
                for row in query_execute.items:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr( row, key )
                    result.append( d )
                return success_reads_pagination( query_execute, result )
            except Exception as e:
                print(e)
                return failed_reads({})

    class lookupPropinsi( Resource ):
        def get(self, *args, **kwargs):
            try:
                select_query = db.session.execute(
                    f"SELECT PropinsiID,Kode,Propinsi, LTRIM(RTRIM(Kode)) + ' - ' + Propinsi AS NamaPropinsi FROM MsPropinsi "
                    f"WHERE [Status]='1' ORDER BY PropinsiID " )
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