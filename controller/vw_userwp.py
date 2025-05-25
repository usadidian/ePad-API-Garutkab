from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.tblUser import tblUser


class vw_userwp(db.Model, SerializerMixin):
    __tablename__ = 'vw_userwp'
    UserId = db.Column(db.Integer, primary_key=True)
    UID = db.Column(db.String, nullable=False)
    Email = db.Column(db.Integer, nullable=False)
    WPID = db.Column(db.Integer, nullable=False)
    OPDID = db.Column( db.Integer, nullable=False )
    ObyekBadanNo = db.Column(db.String, nullable=False)
    NamaBadan = db.Column(db.String, nullable=False)
    AlamatBadan = db.Column(db.String, nullable=False)
    TglPengesahan = db.Column(db.DateTime, nullable=False)
    NamaJenisPendapatan = db.Column(db.String, nullable=False)
    # TglData = db.Column(db.TIMESTAMP, nullable=True)
    TglPenghapusan = db.Column(db.TIMESTAMP, nullable=True)
    JenisPendapatanID = db.Column(db.String, nullable=True)
    KodeRekening = db.Column(db.String, nullable=True)
    UsahaBadan = db.Column(db.String, nullable=True)
    # avatar = db.Column(db.String, nullable=True)
    # latlng = db.Column(db.String, nullable=True)
    # NIK = db.Column(db.String, nullable=True)
    # UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.String, nullable=False)

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
            parser.add_argument('uid', type=str)

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            print(UserId)
            select_query = vw_userwp.query

            # user
            if args['uid']:
                select_query = select_query.filter(
                    vw_userwp.UID == args['uid']
                )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_userwp.UID.ilike(search),
                        vw_userwp.Email.ilike(search),
                        vw_userwp.NamaBadan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_userwp, args['sort']).desc()
                else:
                    sort = getattr(vw_userwp, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_userwp.WPID)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)