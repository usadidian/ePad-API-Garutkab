from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination
from config.database import db
from controller.tblUser import tblUser

class vw_pendataanskp(db.Model, SerializerMixin):
    __tablename__ = 'vw_pendataanskp'
    OPDID = db.Column(db.Integer, primary_key=True)
    OBN = db.Column(db.String, nullable=False)
    WPID = db.Column(db.Integer, nullable=False)
    WapuID = db.Column(db.Integer, nullable=False)
    WajibPungut = db.Column(db.String, nullable=True)
    ObyekBadanNo = db.Column(db.String, nullable=True)
    KodeRekening = db.Column(db.String, nullable=True)
    JenisPendapatanID = db.Column(db.String, nullable=True)
    NamaJenisPendapatan = db.Column(db.String, nullable=True)
    MasaPendapatan = db.Column(db.String, nullable=True)
    NamaBadan = db.Column(db.String, nullable=True)
    AlamatBadan = db.Column(db.String, nullable=True)
    NamaPemilik = db.Column(db.String, nullable=False)
    Status = db.Column(db.String, nullable=False)
    SelfAssesment = db.Column(db.String, nullable=False)
    TglPengesahan = db.Column(db.TIMESTAMP, nullable=False)
    TglData = db.Column(db.TIMESTAMP, nullable=False)
    TglHapus = db.Column(db.TIMESTAMP, nullable=False)
    KegSatker = db.Column(db.TIMESTAMP, nullable=False)
    Insidentil = db.Column(db.String, nullable=False)
    KecamatanID = db.Column(db.Integer, nullable=True)
    Kecamatan = db.Column(db.String, nullable=False)
    FaxKecamatan = db.Column(db.String, nullable=False)
    KelurahanID = db.Column(db.Integer, nullable=True)
    Kelurahan = db.Column(db.String, nullable=False)
    avatar = db.Column(db.String, nullable=False)
    # UserUpd = db.Column(db.String, nullable=False)
    # DateUpd = db.Column(db.TIMESTAMP, nullable=False)


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
            select_query = vw_pendataanskp.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_pendataanskp.PendataanID.ilike(search),
                        vw_pendataanskp.TglPendataan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_pendataanskp, args['sort']).desc()
                else:
                    sort = getattr(vw_pendataanskp, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_pendataanskp.TglData.desc())

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)