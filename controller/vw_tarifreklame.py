from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination
from config.database import db


class vw_tarifreklame(db.Model, SerializerMixin):
    __tablename__ = 'vw_tarifreklame'
    LokasiID = db.Column(db.Integer, primary_key=True)
    NomorTitik = db.Column(db.Integer, nullable=False)
    NamaLokasi = db.Column(db.String, nullable=False)
    TipeLokasiID = db.Column(db.Integer, nullable=False)
    TipeKelas = db.Column(db.String, nullable=False)
    TarifPajak = db.Column(db.Numeric(12, 2), nullable=False)
    PeriodePajak = db.Column(db.String, nullable=False)
    Persentase = db.Column(db.Numeric(12, 2), nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)
    NamaKelas = db.Column( db.String, nullable=False )
    Keterangan = db.Column( db.String, nullable=False )
    JenisReklame = db.Column( db.String, nullable=False )


    class ListAll(Resource):
        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
            parser.add_argument('search', type=str)
            parser.add_argument('tipelokasiid', type=str)

            args = parser.parse_args()
            select_query = vw_tarifreklame.query


            # tipelokasiid
            if args['tipelokasiid']:
                select_query = select_query.filter(
                    vw_tarifreklame.TipeLokasiID == args['tipelokasiid']
                )
            result = []
            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_tarifreklame.NomorTitik.ilike(search),
                        vw_tarifreklame.NamaLokasi.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_tarifreklame, args['sort']).desc()
                else:
                    sort = getattr(vw_tarifreklame, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_tarifreklame.NomorTitik )

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            for row in query_execute.items:
                d = {}
                for key in row.keys():
                    if key == 'TarifPajak' or key == 'Persentase':
                        d[key] = str(getattr(row, key))
                    else:
                        d[key] = getattr(row, key)
                result.append(d)
            return success_reads_pagination(query_execute, result)

