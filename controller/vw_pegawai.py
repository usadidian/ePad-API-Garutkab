from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_reads_pagination
from config.database import db
from controller.tblUser import tblUser


class vw_pegawai(db.Model, SerializerMixin):
    __tablename__ = 'vw_pegawai'
    Idpegawai = db.Column( db.Integer, primary_key=True, autoincrement=True, nullable=False )
    PegawaiID = db.Column(db.String, nullable=False)
    NIP = db.Column( db.String, nullable=False )
    Jabatan = db.Column( db.String, nullable=False )
    Nama = db.Column( db.String, nullable=False )
    Pangkat = db.Column( db.String, nullable=False )
    UPTID = db.Column( db.String, primary_key=True )
    KodeUPT = db.Column( db.String, nullable=False )
    UPT = db.Column( db.String, nullable=False )
    Status = db.Column( db.String, nullable=False )
    NamaStatus = db.Column( db.String, nullable=False )
    UserUpd = db.Column( db.String, nullable=False )
    DateUpd = db.Column( db.TIMESTAMP, nullable=False )


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
            select_query = vw_pegawai.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_pegawai.Nama.ilike(search),
                        vw_pegawai.NIP.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_pegawai, args['sort']).desc()
                else:
                    sort = getattr(vw_pegawai, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_pegawai.PegawaiID)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)