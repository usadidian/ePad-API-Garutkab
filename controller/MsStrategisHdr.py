from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_, and_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.MsStrategisDtl import MsStrategisDtl
from controller.MsTipeLokasi import MsTipeLokasi
from controller.tblUser import tblUser
from controller.vw_nilaistrategis import vw_nilaistrategis


class MsStrategisHdr( db.Model, SerializerMixin ):
    __tablename__ = 'MsStrategisHdr'
    StrategisID = db.Column( db.Integer, primary_key=True )
    NamaStrategis = db.Column( db.String, nullable=False )
    Persentase = db.Column( db.String, nullable=False )

    class ListAll2( Resource ):
        def get(self, *args, **kwargs):


            select_query = db.session.execute(
                f"SELECT * FROM MsStrategisHdr ORDER BY StrategisID" )

            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    if key == 'Persentase':
                        d[key] = str( getattr( row, key ) )
                    else:
                        d[key] = getattr( row, key )
                result.append( d )
            return success_reads( result )

    class ListAll3( Resource ):
        method_decorators = {'get': [tblUser.auth_apikey_privilege]}

        # def get(self, tipelokasiid, *args, **kwargs):
        #     select_query = db.session.execute(
        #         f"SELECT DetailID,Nilai,NamaStrategis AS Wilayah,NamaStrategisDtl,Persentase FROM MsStrategisDtl h "
        #         f"LEFT JOIN MsStrategisHdr t ON h.StrategisID = t.StrategisID "
        #         f"LEFT JOIN MsTipeLokasi AS mtl ON h.NamaStrategisDtl=mtl.NamaKelas "
        #         f"WHERE mtl.TipeLokasiID={tipelokasiid} ORDER BY h.DetailID")
        #     result = []
        #     for row in select_query:
        #         d = {}
        #         for key in row.keys():
        #             if key == 'Persentase' or  key == 'Nilai':
        #                 d[key] = str(getattr(row, key))
        #             else:
        #                 d[key] = getattr(row, key)
        #         result.append(d)
        #     return success_reads(result)
        # def get(self, *args, **kwargs):
        #
        #     # PARSING PARAMETER DARI REQUEST
        #     parser = reqparse.RequestParser()
        #     parser.add_argument('page', type=int)
        #     parser.add_argument('length', type=int)
        #     parser.add_argument('sort', type=str)
        #     parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
        #     parser.add_argument('search', type=str)
        #     parser.add_argument('tipelokasiid', type=str)
        #
        #     args = parser.parse_args()
        #     select_query = db.session.query(
        #                                      MsStrategisDtl.DetailID, MsStrategisDtl.Nilai,MsStrategisHdr.StrategisID,
        #                                      MsStrategisHdr.NamaStrategis.label( 'Wilayah' ),
        #                                      MsStrategisDtl.NamaStrategisDtl, MsStrategisHdr.Persentase,
        #                                      MsTipeLokasi.TipeKelas, MsTipeLokasi.NamaKelas, MsTipeLokasi.TipeLokasiID
        #                                      ) \
        #         .outerjoin(MsStrategisDtl, MsStrategisHdr.StrategisID == MsStrategisDtl.StrategisID)\
        #         .outerjoin(MsTipeLokasi, MsStrategisDtl.NamaStrategisDtl == MsTipeLokasi.NamaKelas)\
        #     .filter(MsStrategisDtl.DetailID != None)
        #
        #
        #     # tipelokasiid
        #     if args['tipelokasiid']:
        #         select_query = select_query.filter(
        #             MsTipeLokasi.TipeLokasiID == args['tipelokasiid']
        #         )
        #     result = []
        #     # SEARCH
        #     if args['search'] and args['search'] != 'null':
        #         search = '%{0}%'.format(args['search'])
        #         select_query = select_query.filter(
        #             or_(MsStrategisHdr.NamaStrategis.ilike(search),
        #                 MsStrategisDtl.NamaStrategisDtl.ilike(search))
        #         )
        #
        #     # SORT
        #     if args['sort']:
        #         if args['sort_dir'] == "desc":
        #             sort = getattr( MsStrategisDtl, args['sort'] ).desc()
        #         else:
        #             sort = getattr(MsStrategisDtl, args['sort']).asc()
        #         select_query = select_query.order_by(sort)
        #     else:
        #         select_query = select_query.order_by  (MsStrategisDtl.DetailID)
        #
        #     # PAGINATION
        #     page = args['page'] if args['page'] else 1
        #     length = args['length'] if args['length'] else 10
        #     lengthLimit = length if length < 101 else 100
        #     query_execute = select_query.paginate(page, lengthLimit)
        #
        #     for row in query_execute.items:
        #         d = {}
        #         for key in row.keys():
        #             if key == 'Nilai' or key == 'Persentase':
        #                 d[key] = str(getattr(row, key))
        #             else:
        #                 d[key] = getattr(row, key)
        #         result.append(d)
        #     return success_reads_pagination(query_execute, result)

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
            parser.add_argument('search', type=str)
            parser.add_argument('tipelokasiid', type=str)

            args = parser.parse_args()
            select_query = db.session.query(
                                             vw_nilaistrategis.DetailID, vw_nilaistrategis.Nilai,vw_nilaistrategis.StrategisID,
                                             vw_nilaistrategis.NamaStrategis.label( 'Wilayah' ),
                                             vw_nilaistrategis.NamaStrategisDtl, vw_nilaistrategis.Persentase,
                                             vw_nilaistrategis.TipeKelas, vw_nilaistrategis.NamaKelas, vw_nilaistrategis.TipeLokasiID
                                             ) \
            .filter(vw_nilaistrategis.DetailID != None)


            # tipelokasiid
            if args['tipelokasiid']:
                select_query = select_query.filter(
                    vw_nilaistrategis.TipeLokasiID == args['tipelokasiid']
                )
            result = []
            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_nilaistrategis.NamaStrategis.ilike(search),
                        vw_nilaistrategis.NamaStrategisDtl.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr( vw_nilaistrategis, args['sort'] ).desc()
                else:
                    sort = getattr(vw_nilaistrategis, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by  (vw_nilaistrategis.DetailID)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            for row in query_execute.items:
                d = {}
                for key in row.keys():
                    if key == 'Nilai' or key == 'Persentase':
                        d[key] = str(getattr(row, key))
                    else:
                        d[key] = getattr(row, key)
                result.append(d)
            return success_reads_pagination(query_execute, result)

    class ListAll( Resource ):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument( 'page', type=int )
            parser.add_argument( 'length', type=int )
            parser.add_argument( 'sort', type=str )
            parser.add_argument( 'sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC' )
            parser.add_argument( 'search', type=str )

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            print( UserId )
            select_query = MsStrategisHdr.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format( args['search'] )
                select_query = select_query.filter(
                    or_( MsStrategisHdr.StrategisID.ilike( search ),
                         MsStrategisHdr.NamaStrategis.ilike( search ) )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr( MsStrategisHdr, args['sort'] ).desc()
                else:
                    sort = getattr( MsStrategisHdr, args['sort'] ).asc()
                select_query = select_query.order_by( sort )
            else:
                select_query = select_query.order_by( MsStrategisHdr.StrategisID )

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate( page, lengthLimit )

            result = []
            for row in query_execute.items:
                result.append( row.to_dict() )
            return success_reads_pagination( query_execute, result )

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            # parser.add_argument('StrategisID', type=str)
            parser.add_argument( 'NamaStrategis', type=str )
            parser.add_argument( 'Persentase', type=str )

            args = parser.parse_args()
            result = []
            for row in result:
                result.append( row )

            add_record = MsStrategisHdr(
                NamaStrategis=args['NamaStrategis'],
                Persentase=args['Persentase'],
            )
            db.session.add( add_record )
            db.session.commit()
            return jsonify( {'status_code': 1, 'message': 'OK', 'data': result} )

    class ListById( Resource ):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsStrategisHdr.query.filter_by( StrategisID=id ).first()
                result = select_query.to_dict()
                return success_read( result )
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_read( {} )

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print( kwargs['claim'] )
            # parser.add_argument('StrategisID', type=str)
            parser.add_argument( 'NamaStrategis', type=str )
            parser.add_argument( 'Persentase', type=str )

            args = parser.parse_args()
            try:
                select_query = MsStrategisHdr.query.filter_by( StrategisID=id ).first()
                if select_query:
                    # select_query.StrategisID = args['StrategisID']
                    select_query.NamaStrategis = args['NamaStrategis']
                    select_query.Persentase = args['Persentase']

                    db.session.commit()
                    return success_update( {'id': id} )
            except Exception as e:

                db.session.rollback()
                print( e )
                return failed_update( {} )

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsStrategisHdr.query.filter_by( StrategisID=id )
                delete_record.delete()
                db.session.commit()
                return success_delete( {} )
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_delete( {} )
