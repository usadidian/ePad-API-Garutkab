from asyncio.windows_events import NULL

from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads, failed_reads, success_reads_pagination
from config.database import db
from config.helper import toDict
from controller.MsJenisPungut import MsJenisPungut
from controller.MsKecamatan import MsKecamatan
from controller.MsKelurahan import MsKelurahan
from controller.MsPegawai import MsPegawai
from controller.tblUser import tblUser


class vw_obyekbadanwapu(db.Model, SerializerMixin):
    __tablename__ = 'vw_obyekbadanwapu'
    WapuID = db.Column(db.Integer, primary_key=True)
    JenisPungutID = db.Column(db.Integer, nullable=True)
    Kode = db.Column(db.String, nullable=True)
    JenisPungut = db.Column(db.String, nullable=False)
    ObyekBadanNo = db.Column(db.String, nullable=True)
    NamaBadan = db.Column(db.String, nullable=False)
    AlamatBadan = db.Column(db.String, nullable=False)
    NoTelpBadan = db.Column(db.String, nullable=False)
    KotaBadan = db.Column(db.Integer, nullable=False)
    Kota = db.Column(db.String, nullable=False)
    KecamatanBadan = db.Column(db.Integer, nullable=False)
    Kecamatan = db.Column(db.String, nullable=False)
    KelurahanBadan = db.Column(db.Integer, nullable=True)
    Kelurahan = db.Column(db.String, nullable=False)
    TglPendaftaran = db.Column(db.TIMESTAMP, nullable=False)
    TglPenghapusan = db.Column(db.TIMESTAMP, nullable=True, default=NULL)
    PetugasPendaftar = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)
    avatar = db.Column(db.String, nullable=True)
    latlng = db.Column(db.String, nullable=True)
    NIK = db.Column(db.String, nullable=True)



    class ListAll(Resource):
        method_decorators = {'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
            parser.add_argument('search', type=str)
            args = parser.parse_args()
            result = []
            try:
                select_query = vw_obyekbadanwapu.query

                # SEARCH
                if args['search'] and args['search'] != 'null':
                    search = '%{0}%'.format(args['search'])
                    select_query = select_query.filter(
                        or_(vw_obyekbadanwapu.NamaBadan.ilike(search),
                            vw_obyekbadanwapu.ObyekBadanNo.ilike(search)),
                    )

                # SORT
                if args['sort']:
                    if args['sort_dir'] == "desc":
                        sort = getattr(vw_obyekbadanwapu, args['sort']).desc()
                    else:
                        sort = getattr(vw_obyekbadanwapu, args['sort']).asc()
                    select_query = select_query.order_by(sort)
                else:
                    select_query = select_query.order_by(vw_obyekbadanwapu.WapuID, vw_obyekbadanwapu.NamaBadan.desc())

                # PAGINATION
                page = args['page'] if args['page'] else 1
                length = args['length'] if args['length'] else 10
                lengthLimit = length if length < 101 else 100
                query_execute = select_query.paginate(page, lengthLimit)

                # print(query_execute.items)
                for row in query_execute.items:
                    d = {}
                    for key in row.keys():
                        # print(key,  getattr(row, key))
                        d[key] = getattr(row, key)
                    result.append(d)
                return success_reads_pagination(query_execute, result)
            except Exception as e:
                print(e)
                return failed_reads(result)