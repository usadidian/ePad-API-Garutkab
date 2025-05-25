from flask_restful import reqparse, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination, success_read, failed_read
from controller.tblUser import tblUser

db = SQLAlchemy()


class GeoData(db.Model, SerializerMixin):
    __tablename__ = 'GEODATA'

    id = db.Column(db.String(255), primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    geometry = db.Column(db.Text, nullable=True)
    level = db.Column(db.SmallInteger, nullable=True)
    type = db.Column(db.String(1), nullable=True)

    class ListAll(Resource):
        # GET method
        @tblUser.auth_apikey_privilege  # Dekorator diterapkan ke method `get`
        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
            parser.add_argument('search', type=str)

            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            select_query = (
                db.session.query(
                    GeoData.id,
                    GeoData.name,
                    GeoData.geometry,
                    GeoData.level,
                    GeoData.type
                )
            )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(GeoData.name.ilike(search),
                        GeoData.geometry.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(GeoData, args['sort']).desc()
                else:
                    sort = getattr(GeoData, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(GeoData.name)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads_pagination(query_execute, result)

    class ListById(Resource):
        # GET method
        @tblUser.auth_apikey_privilege  # Dekorator diterapkan ke method `get`
        def get(self, id, *args, **kwargs):
            try:
                select_query = GeoData.query.filter_by(id=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})
