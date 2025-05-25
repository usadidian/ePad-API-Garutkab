from datetime import datetime

from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads, failed_reads
from config.database import db
from controller.GeneralParameter import GeneralParameter
from controller.MsKawasan import MsKawasan
from controller.MsKecamatan import MsKecamatan
from controller.MsJenisJalan import MsJenisJalan
from controller.tblUser import tblUser


class MsJalan(db.Model, SerializerMixin):
    __tablename__ = 'MsJalan'
    JalanID = db.Column(db.Integer, primary_key=True)
    Jalan = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column( db.String, nullable=False )

    KecamatanID = db.Column( db.Integer, db.ForeignKey( 'MsKecamatan.KecamatanID' ), nullable=False )
    JenisJalanID = db.Column( db.String, db.ForeignKey( 'MsJenisJalan.JenisJalanID' ), nullable=False )
    KawasanID = db.Column(db.String, db.ForeignKey('MsKawasan.KawasanID'), nullable=False)



    class jalan(Resource):
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
            select_query = db.session.query(MsJalan.JalanID.label('jalanid'),
                                            MsJalan.Jalan.label('jalan'),
                                            MsJalan.KecamatanID.label('kecamatanid'))

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsJalan.JalanID.ilike(search),
                        MsJalan.Jalan.ilike(search),
                        MsJalan.KecamatanID.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsJalan, args['sort']).desc()
                else:
                    sort = getattr(MsJalan, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsJalan.JalanID)

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
        def get(self, *args, **kwargs):
            try:
                select_query = db.session.execute(
                    f"SELECT JenisJalanID + KawasanID + convert(varchar,JalanID) AS Kode,JalanID,"
                    f"right('000'+convert(varchar,JalanID),3) + ' - ' + Jalan + ', ' + Kecamatan AS Nama FROM MsJalan j "
                    f"LEFT JOIN MsKecamatan c ON j.KecamatanID = c.KecamatanID ORDER BY Jalan ")
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

    class ListAll3(Resource):
        def get(self, kecamatanid, *args, **kwargs):
            try:
                select_query = db.session.execute(
                    f"SELECT JalanID,  Jalan FROM MsJalan WHERE [Status]='1'  "
                    f"AND JenisJalanID = '{kecamatanid}'  ORDER BY Jalan")
                result = []
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr(row, key)
                    result.append(d)
                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_reads()

    class ListAll4(Resource):
        def get(self, *args, **kwargs):
            try:
                query = db.session.query(
                    GeneralParameter.ParamStrValue ).filter( GeneralParameter.ParamID == 'kotaid' )
                kotaid = query.first()[0]

                query_select = db.session.query(
                    MsKecamatan.KecamatanID ).filter( MsKecamatan.KotaID == {kotaid} )
                kecamatanid = query_select.first()[0]

                select_query = db.session.execute(
                    f"SELECT JalanID, Jalan FROM MsJalan WHERE KecamatanID ={kecamatanid} "
                    f"ORDER BY Jalan ")
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

    class ListAll5(Resource):
        def get(self, *args, **kwargs):
            try:
                query = db.session.query(
                    GeneralParameter.ParamStrValue ).filter( GeneralParameter.ParamID == 'kecamatanid' )
                kecamatanid = query.first()[0]

                select_query = db.session.execute(
                    f"SELECT Kode,Nama FROM( "
                    f"SELECT JalanID AS Kode,'KECAMATAN ' + Jalan AS Nama FROM MsJalan AS mk "
                    f"INNER JOIN vw_header AS vh ON vh.KecamatanID=mk.KecamatanID "
                    f"union "
                    f"SELECT 0 AS Kode,'LUAR KOTA CIMAHI' AS Nama)X "
                    f"ORDER BY NAMA")
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
            print(UserId)
            query = db.session.query(
                GeneralParameter.ParamStrValue ).filter( GeneralParameter.ParamID == 'kotaid' )
            kotaid = query.first()[0]

            query_select = db.session.query(
                MsKecamatan.KecamatanID ).filter( MsKecamatan.KotaID == kotaid )
            kecamatanid = query_select.first()[0]

            select_query = db.session.query(MsJalan.JalanID, MsJalan.Jalan, MsKecamatan.KecamatanID,
                                            MsJenisJalan.JenisJalanID, MsJenisJalan.JenisJalan,MsKawasan.KawasanID,
                                            MsKawasan.Kawasan, MsKecamatan.Kecamatan) \
                .outerjoin( MsKecamatan, MsJalan.KecamatanID == MsKecamatan.KecamatanID ) \
                .outerjoin(MsJenisJalan, MsJalan.JenisJalanID == MsJenisJalan.JenisJalanID) \
                .outerjoin( MsKawasan, MsJalan.KawasanID == MsKawasan.KawasanID ) \
                .filter(MsKecamatan.KotaID == kotaid)

            # kecamatanid
            if args['kecamatanid']:
                select_query = select_query.filter(
                    MsJalan.KecamatanID == args['kecamatanid']
                )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsJalan.JalanID.ilike(search),
                        MsJalan.Jalan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsJalan, args['sort']).desc()
                else:
                    sort = getattr(MsJalan, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsJalan.Jalan)

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
            parser.add_argument('KecamatanID', type=str)
            parser.add_argument('Jalan', type=str)
            parser.add_argument('JenisJalanID', type=str)
            parser.add_argument( 'KawasanID', type=str )

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            query = db.session.query(
                GeneralParameter.ParamStrValue ).filter( GeneralParameter.ParamID == 'kecamatanid' )
            kecamatanid = query.first()[0]

            result = []
            for row in result:
                result.append(row)

            select_query = db.session.execute(
                f"SELECT CAST(MAX(CAST(JalanID AS int) + 1) AS varchar(10)) AS NextID FROM MsJalan")
            result2 = select_query.first()[0]
            jalanid = result2

            add_record = MsJalan(
                JalanID=jalanid,
                Jalan=args['Jalan'],
                KecamatanID=args['KecamatanID'],
                JenisJalanID=args['JenisJalanID'],
                KawasanID=args['KawasanID'],
                UserUpd=uid,
                DateUpd=datetime.now(),

            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsJalan.query.filter_by(JalanID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            # parser.add_argument( 'JalanID', type=str )
            parser.add_argument('KecamatanID', type=str)
            parser.add_argument('Jalan', type=str)
            parser.add_argument('KawasanID', type=str)
            parser.add_argument('JenisJalanID', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = MsJalan.query.filter_by(JalanID=id).first()
                if select_query:
                    if args['KecamatanID']:
                        select_query.KecamatanID = args['KecamatanID']
                    if args['Jalan']:
                        select_query.Jalan = args['Jalan']
                    if args['KawasanID']:
                        select_query.KawasanID = args['KawasanID']
                    if args['JenisJalanID']:
                        select_query.JenisJalanID = args['JenisJalanID']
                    db.session.commit()
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsJalan.query.filter_by(JalanID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})
