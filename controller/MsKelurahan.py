from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.GeneralParameter import GeneralParameter
from controller.MsKecamatan import MsKecamatan
from controller.tblUser import tblUser


class MsKelurahan(db.Model, SerializerMixin):
    __tablename__ = 'MsKelurahan'
    KelurahanID = db.Column(db.Integer, primary_key=True)
    Kelurahan = db.Column(db.String, nullable=False)
    AlamatKelurahan= db.Column(db.String, nullable=False)
    TelpKelurahan = db.Column(db.String, nullable=False)
    FaxKelurahan = db.Column(db.String, nullable=False)
    KodePos = db.Column(db.String, nullable=False)

    KecamatanID = db.Column(db.Integer, db.ForeignKey('MsKecamatan.KecamatanID'), nullable=False)

    class kelurahan(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
            parser.add_argument('search', type=str)
            parser.add_argument( 'kecamatanid', type=str )

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            print(UserId)
            select_query = db.session.query(MsKelurahan.KelurahanID.label('kelurahanid'),
                                            MsKelurahan.Kelurahan.label('kelurahan'),
                                            MsKelurahan.KodePos.label('kodepos'),
                                            MsKelurahan.KecamatanID.label('kecamatanid'))

            # kecamatanid
            if args['kecamatanid']:
                select_query = select_query.filter(
                    MsKelurahan.KecamatanID == args['kecamatanid']
                )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsKelurahan.KelurahanID.ilike(search),
                        MsKelurahan.Kelurahan.ilike(search),
                        MsKelurahan.KecamatanID.ilike( search ),
                        MsKelurahan.KodePos.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsKelurahan, args['sort']).desc()
                else:
                    sort = getattr(MsKelurahan, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsKelurahan.KelurahanID)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 5
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads_pagination( query_execute, result )


    class ListAll2(Resource):
        def get(self, kecamatanid, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('KecamatanID', type=str)
            select_query = db.session.execute(
                f"SELECT KelurahanID, Kelurahan FROM MsKelurahan WHERE [Status]='1' AND KecamatanID ='{kecamatanid}' "
                f"ORDER BY Kelurahan")
            result=[]
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

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
            parser.add_argument( 'kecamatanid', type=str )

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]

            query = db.session.query(
                GeneralParameter.ParamStrValue ).filter( GeneralParameter.ParamID == 'kotaid' )
            kotaid = query.first()[0]

            print(UserId)
            select_query = db.session.query(MsKelurahan.KelurahanID, MsKelurahan.Kelurahan, MsKelurahan.KodePos,
                                            MsKelurahan.KecamatanID)\
            .join(MsKecamatan, MsKelurahan.KecamatanID == MsKecamatan.KecamatanID)\
            .filter(MsKecamatan.KotaID == kotaid)

            # kecamatanid
            if args['kecamatanid']:
                select_query = select_query.filter(
                    MsKelurahan.KecamatanID == args['kecamatanid']
                )
            result = []
            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsKelurahan.KelurahanID.ilike(search),
                        MsKelurahan.Kelurahan.ilike(search),
                        MsKelurahan.KodePos.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsKelurahan, args['sort']).desc()
                else:
                    sort = getattr(MsKelurahan, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsKelurahan.KelurahanID)

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
            # parser.add_argument('KelurahanID', type=str)
            parser.add_argument('KecamatanID', type=str)
            parser.add_argument('Kelurahan', type=str)
            parser.add_argument('AlamatKelurahan', type=str)
            parser.add_argument('TelpKelurahan', type=str)
            parser.add_argument('FaxKelurahan', type=str)
            parser.add_argument('KodePos', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            select_query = db.session.execute(
                f"SELECT CAST(MAX(CAST(KelurahanID AS int) + 1) AS varchar(10)) AS NextID FROM MsKelurahan")
            result2 = select_query.first()[0]
            kelurahanid = result2

            add_record = MsKelurahan(
                # KelurahanID=kelurahanid,
                KecamatanID=args['KecamatanID'],
                Kelurahan=args['Kelurahan'],
                AlamatKelurahan=args['AlamatKelurahan'] if args['AlamatKelurahan'] else '',
                TelpKelurahan=args['TelpKelurahan'] if args['TelpKelurahan'] else '',
                FaxKelurahan=args['FaxKelurahan'] if args['FaxKelurahan'] else '',
                KodePos=args['KodePos'],

            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsKelurahan.query.filter_by(KelurahanID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            # parser.add_argument('KelurahanID', type=str)
            parser.add_argument('KecamatanID', type=str)
            parser.add_argument('Kelurahan', type=str)
            parser.add_argument('AlamatKelurahan', type=str)
            parser.add_argument('TelpKelurahan', type=str)
            parser.add_argument('FaxKelurahan', type=str)
            parser.add_argument('KodePos', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = MsKelurahan.query.filter_by(KelurahanID=id).first()
                if select_query:
                    select_query.KecamatanID = args['KecamatanID']
                    select_query.Kelurahan = args['Kelurahan']
                    select_query.AlamatKelurahan = args['AlamatKelurahan'] if args['AlamatKelurahan'] else None
                    select_query.TelpKelurahan = args['TelpKelurahan'] if args['TelpKelurahan'] else None
                    select_query.FaxKelurahan = args['FaxKelurahan'] if args['FaxKelurahan'] else None
                    select_query.KodePos = args['KodePos']
                    db.session.commit()
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsKelurahan.query.filter_by(KelurahanID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})