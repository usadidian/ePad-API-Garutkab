from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import outerjoin
from sqlalchemy.sql import case, func, or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads, failed_reads
from config.database import db
from config.helper import toDict
from controller.GeneralParameter import GeneralParameter
from controller.MsKecamatan import MsKecamatan
from controller.MsKelurahan import MsKelurahan
from controller.MsPropinsi import MsPropinsi
from controller.tblUser import tblUser


class MsKota(db.Model, SerializerMixin):
    __tablename__ = 'MsKota'
    KotaID = db.Column(db.Integer, primary_key=True)
    # PropinsiID = db.Column(db.Integer, nullable=False)
    Kota = db.Column(db.String, nullable=False)
    PropinsiID = db.Column( db.Integer, db.ForeignKey( 'MsPropinsi.PropinsiID' ), nullable=False )
    # Status = db.Column(db.String, nullable=False)
    # UserUpd = db.Column(db.String, nullable=False)
    # DateUpd = db.Column(db.String, nullable=False)

    # class ListAll2(Resource):
    #     method_decorators = {'get': [tblUser.auth_apikey_privilege]}
    #     def get(self, *args, **kwargs):
    #         try:
    #             select_query = MsKota.query.with_entities(
    #                 case([
    #                     (func.left(MsKota.Kota, 5) == 'Kota ', func.substring(MsKota.Kota, 6, 50) + ', Kota'),
    #                     (func.left(MsKota.Kota, 5) == 'Kabup ', func.substring(MsKota.Kota, 11, 50) + ', Kab'),
    #                     (func.left(MsKota.Kota, 6) == 'Kotama ', func.substring(MsKota.Kota, 11, 50) + ', Kotamadya'),
    #                 ], else_='').label("Kota"), MsKota.KotaID
    #             ).all()
    #             kotaids = GeneralParameter.query.filter_by(ParamID='kotaid').first()
    #             result = []
    #             for row in select_query:
    #                 if kotaids:
    #                     result.append({
    #                         'name': row.Kota,
    #                         'id': row.KotaID,
    #                         'selected': True if kotaids.ParamStrValue == row.KotaID else False
    #                     })
    #             return success_reads(result)
    #         except Exception as e:
    #             print(e)
    #             return failed_reads({})
    #
    #         # select_query = db.session.execute(
    #         #     f"SELECT KotaID, (case when left(kota,5) = 'Kota ' then substring(kota,6,50) + ', Kota' else "
    #         #     f"(case when left(kota,5) = 'Kabup' then substring(kota,11,50) + ', Kab' else "
    #         #     f"(case when left(kota,6) = 'Kotama' then substring(kota,11,50) + ', Kotamadya' else '' end) end) end) "
    #         #     f"AS Kota FROM MsKota "
    #         #     # f"WHERE KotaID IN (SELECT gp.ParamStrValue FROM GeneralParameter AS gp WHERE gp.ParamID='KotaId') "
    #         #     f"ORDER BY Kota")
    #         #
    #         # # kotaids = GeneralParameter.query.filter_by(ParamID='kotaid').first()
    #         # kotaids = db.session.execute(
    #         #     f"SELECT gp.ParamStrValue FROM GeneralParameter AS gp WHERE gp.ParamID='kotaid'"
    #         # )
    #         # result = []
    #         # for row in select_query:
    #         #     d = {}
    #         #     for key in row.keys():
    #         #         d[key] = getattr(row, key)
    #         #         if kotaids:
    #         #             if kotaids.ParamStrValue == getattr(row, key):
    #         #                 d['selected'] = True
    #         #             else:
    #         #                 d['selected'] = False
    #         #     result.append(d)
    #         #
    #         # return success_reads(result)

    class ListAll(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('search', type=str)
            parser.add_argument('uptid', type=str)
            args = parser.parse_args()

            try:
                result = []
                select_query = db.session.query(
                    MsKota, MsKecamatan)\
                    .join(MsKecamatan, MsKecamatan.KotaID == MsKota.KotaID) \
                    # .join(MsWPData, MsKecamatan.KotaID == MsWPData.KotaBadan)

                if args['search'] and len(args['search']) > 0:
                    search = "%{}%".format(args['search'])
                    select_query = select_query.filter(
                        or_(
                            MsKota.Kota.like( search ),
                            MsKecamatan.Kecamatan.like(search),
                        )
                    )

                if args['uptid'] and len(args['uptid']) > 0:
                    select_query = select_query.filter(
                        or_(
                            MsKecamatan.FaxKecamatan == args['uptid']
                        )
                    )
                    select_query = select_query.order_by(MsKota.Kota).all()
                else:
                    select_query = select_query.limit(30)
                for row in select_query:
                    kota_name = row.MsKota.Kota.replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                    result.append({
                        'name': kota_name
                                + ', Kec.' + row.MsKecamatan.Kecamatan,
                        'Kota': row.MsKota.Kota,
                        'Kecamatan': row.MsKecamatan.Kecamatan,
                        'KotaID': row.MsKota.KotaID,
                        'KecamatanID': row.MsKecamatan.KecamatanID,
                    })
                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_reads({})

    class ListAll2(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('search', type=str)
            parser.add_argument('uptid', type=str)
            args = parser.parse_args()

            try:
                result = []
                select_query = db.session.query(
                    MsKota, MsKecamatan, MsKelurahan
                ).join(MsKecamatan, MsKecamatan.KotaID == MsKota.KotaID) \
                    .join(MsKelurahan, MsKelurahan.KecamatanID == MsKecamatan.KecamatanID)

                if args['search'] and len(args['search']) > 0:
                    search = "%{}%".format(args['search'])
                    select_query = select_query.filter(
                        or_(
                            MsKota.Kota.like( search ),
                            MsKecamatan.Kecamatan.like(search),
                            MsKelurahan.Kelurahan.like(search),
                        )
                    )

                if args['uptid'] and len(args['uptid']) > 0:
                    select_query = select_query.filter(
                        or_(
                            MsKecamatan.FaxKecamatan == args['uptid']
                        )
                    )
                    select_query = select_query.order_by(MsKota.Kota).all()
                else:
                    select_query = select_query.limit(30)
                for row in select_query:
                    kota_name = (row.MsKota.Kota or '').replace("Kabupaten ", "Kab.").replace("Kotamadya ", "Kota")
                    kecamatan_name = row.MsKecamatan.Kecamatan or ''
                    kelurahan_name = row.MsKelurahan.Kelurahan or ''
                    kode_pos = row.MsKelurahan.KodePos if row.MsKelurahan.KodePos is not None else ''

                    result.append({
                        'name': f"{kota_name}, Kec.{kecamatan_name}, Kel.{kelurahan_name} - {kode_pos}",
                        'Kota': row.MsKota.Kota,
                        'Kecamatan': row.MsKecamatan.Kecamatan,
                        'Kelurahan': row.MsKelurahan.Kelurahan,
                        'KotaID': row.MsKota.KotaID,
                        'KecamatanID': row.MsKecamatan.KecamatanID,
                        'KelurahanID': row.MsKelurahan.KelurahanID
                    })

                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_reads({})


    class ListAll3( Resource ):
        method_decorators = {'get': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument( 'search', type=str )
            parser.add_argument( 'uptid', type=str )
            args = parser.parse_args()

            try:
                result = []
                query = db.session.query(
                    GeneralParameter.ParamStrValue).filter( GeneralParameter.ParamID == 'kotaid')
                kotaid = query.first()[0]

                print(kotaid)
                select_query = db.session.query(
                    MsKota, MsKecamatan, MsKelurahan
                ).join( MsKecamatan, MsKecamatan.KotaID == MsKota.KotaID ) \
                    .join( MsKelurahan, MsKelurahan.KecamatanID == MsKecamatan.KecamatanID ) \
                    .filter( MsKota.KotaID == kotaid, MsKelurahan.KecamatanID != None )

                if args['search'] and len( args['search'] ) > 0:
                    search = "%{}%".format( args['search'] )
                    select_query = select_query.filter(
                        or_(
                            MsKecamatan.Kecamatan.like( search ),
                            MsKelurahan.Kelurahan.like( search ),
                        )
                    )

                if args['uptid'] and len( args['uptid'] ) > 0:
                    select_query = select_query.filter(
                        or_(
                            MsKecamatan.FaxKecamatan == args['uptid']
                        )
                    )
                    select_query = select_query.order_by( MsKota.Kota ).all()
                else:
                    select_query = select_query.order_by( MsKota.Kota ).all()

                for row in select_query:
                    kota_name = row.MsKota.Kota.replace( "Kabupaten ", "Kab." ).replace( "Kotamadya ", "Kota" )
                    result.append( {
                        'name': kota_name
                                + ', Kec. ' + row.MsKecamatan.Kecamatan
                                + ', Kel. ' + row.MsKelurahan.Kelurahan
                                + " - " + row.MsKelurahan.KodePos if row.MsKelurahan.KodePos != None else '',
                        'Kecamatan': row.MsKecamatan.Kecamatan,
                        'Kelurahan': row.MsKelurahan.Kelurahan,
                        'KotaID': row.MsKota.KotaID,
                        'KecamatanID': row.MsKecamatan.KecamatanID,
                        'KelurahanID': row.MsKelurahan.KelurahanID,
                        'KodePos': row.MsKelurahan.KodePos
                    } )
                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_reads({})


    class ListAll4( Resource ):
        method_decorators = {'get': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument( 'search', type=str )
            parser.add_argument( 'uptid', type=str )
            args = parser.parse_args()

            try:
                result = []
                query = db.session.query(
                    GeneralParameter.ParamStrValue).filter( GeneralParameter.ParamID == 'propid')
                propid = query.first()[0]

                print(propid)
                select_query = db.session.query(
                    MsPropinsi, MsKota
                ).join( MsKota, MsKota.PropinsiID == MsPropinsi.PropinsiID ) \
                    .filter( MsPropinsi.PropinsiID == propid, MsKota.KotaID != None )

                if args['search'] and len( args['search'] ) > 0:
                    search = "%{}%".format( args['search'] )
                    select_query = select_query.filter(
                        or_(
                            MsPropinsi.Propinsi.like( search ),
                            MsKota.Kota.like( search ),
                        )
                    )

                for row in select_query:
                    prop_name = row.MsPropinsi.Propinsi
                    result.append( {
                        'name': prop_name
                                + ' ' + row.MsKota.Kota.replace( "Kabupaten ", "Kab." ).replace( "Kotamadya ", "Kota" )
                                if row.MsKota.Kota else "" ,
                        'PropinsiID': row.MsPropinsi.PropinsiID,
                        'KotaID': row.MsKota.KotaID,
                    } )
                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_reads({})

    class kota(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
            parser.add_argument('search', type=str)
            parser.add_argument( 'propinsiid', type=str )

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            print(UserId)

            select_query = db.session.query(MsKota.KotaID.label('kotaid'), MsKota.Kota.label('kota'),
                                            MsKota.PropinsiID.label('propinsiid'), MsPropinsi.Propinsi.label('propinsi'))\
            .outerjoin(MsPropinsi, MsKota.PropinsiID == MsPropinsi.PropinsiID)

            #propinsiid
            if args['propinsiid']:
                select_query = select_query.filter(
                    MsKota.PropinsiID == args['propinsiid']
                )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsKota.KotaID.ilike(search),
                        MsKota.Kota.ilike(search),
                        MsKota.PropinsiID.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsKota, args['sort']).desc()
                else:
                    sort = getattr(MsKota, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsKota.KotaID)

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

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('KotaID', type=str)
            parser.add_argument('PropinsiID', type=str)
            parser.add_argument('Kota', type=str)
            # parser.add_argument('Status', type=str)
            # parser.add_argument('UserUpd', type=str)
            # parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            select_query = db.session.execute(
                f"SELECT CAST(MAX(CAST(KotaID AS int) + 1) AS varchar(10)) AS NextID FROM MsKota")
            result2 = select_query.first()[0]
            kotaid = result2

            add_record = MsKota(

                KotaID=kotaid,
                PropinsiID=args['PropinsiID'],
                Kota=args['Kota'],
                # Status=args['Status'],
                # UserUpd=uid,
                # DateUpd=datetime.now(),

            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsKota.query.filter_by(KotaID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('KotaID', type=str)
            parser.add_argument('PropinsiID', type=str)
            parser.add_argument('Kota', type=str)
            # parser.add_argument('Status', type=str)
            # parser.add_argument('UserUpd', type=str)
            # parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = MsKota.query.filter_by(KotaID=id).first()
                if select_query:
                    select_query.KotaID = args['KotaID']
                    select_query.PropinsiID = args['PropinsiID']
                    select_query.Kota = args['Kota']
                    # select_query.Status = args['Status']
                    # select_query.UserUpd = uid
                    # select_query.DateUpd = datetime.now()
                    # db.session.commit()
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsKota.query.filter_by(KotaID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})