import numbers
from datetime import datetime, timedelta

from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_, Numeric
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, failed_reads, success_create
from config.database import db
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsUPT import MsUPT
from controller.tblUser import tblUser


class MsTargetPendapatan(db.Model, SerializerMixin):
    __tablename__ = 'MsTargetPendapatan'
    TargetID = db.Column(db.Integer, primary_key=True)
    TahunPendapatan = db.Column(db.String, nullable=False)
    Periode = db.Column(db.Integer, nullable=False)
    TargetPendapatan= db.Column(db.Numeric(precision=16, asdecimal=False, decimal_return_scale=None), nullable=True)
    Status = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    JenisPendapatanID = db.Column(db.String, db.ForeignKey('MsJenisPendapatan.JenisPendapatanID'), nullable=False)
    UPTID = db.Column(db.String, db.ForeignKey('MsUPT.UPTID'), nullable=False)

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
            parser.add_argument( 'filter_uptid', type=str )
            parser.add_argument( 'filter_jenis', type=str )
            parser.add_argument( 'tahun_pendapatan', type=str )
            parser.add_argument( 'Periode', type=str )

            args = parser.parse_args()
            result = []
            try:
                UserId = kwargs['claim']["UserId"]
                print(UserId)
                select_query = db.session.query( MsTargetPendapatan.Periode, MsTargetPendapatan.JenisPendapatanID,
                                                 MsJenisPendapatan.NamaJenisPendapatan, MsJenisPendapatan.KodeRekening,
                                                 MsTargetPendapatan.TahunPendapatan, MsTargetPendapatan.TargetPendapatan,
                                                 MsUPT.UPTID, MsUPT.KDUNIT, MsUPT.UPT
                                                 , MsTargetPendapatan.TargetID
                                                 ) \
                    .outerjoin(MsJenisPendapatan, MsTargetPendapatan.JenisPendapatanID == MsJenisPendapatan.JenisPendapatanID)\
                    .outerjoin(MsUPT, MsTargetPendapatan.UPTID == MsUPT.UPTID)\
                    .filter(
                    MsJenisPendapatan.Status == '1',  MsTargetPendapatan.Status == '1',
                    MsTargetPendapatan.TahunPendapatan == args['tahun_pendapatan']
                )\
                    .distinct()

                # FILTER_UPT
                if args['filter_uptid']:
                    select_query = select_query.filter(
                        MsTargetPendapatan.UPTID == args['filter_uptid']
                    )

                # FILTER_JENIS
                if args['filter_jenis']:
                    select_query = select_query.filter(
                        MsTargetPendapatan.JenisPendapatanID == args['filter_jenis']
                    )

                # TAHUN_PENDAPATAN
                if args['tahun_pendapatan']:
                    select_query = select_query.filter(
                        MsTargetPendapatan.TahunPendapatan == args['tahun_pendapatan']
                    )

                # PERIODE
                if args['Periode']:
                    select_query = select_query.filter(
                        MsTargetPendapatan.Periode == args['Periode']
                    )

                # SEARCH
                if args['search'] and args['search'] != 'null':
                    search = '%{0}%'.format(args['search'])
                    select_query = select_query.filter(
                        or_(MsTargetPendapatan.TargetPendapatan.ilike(search),
                            MsTargetPendapatan.UPTID.ilike(search))
                    )

                # SORT
                if args['sort']:
                    if args['sort_dir'] == "desc":
                        sort = getattr(MsTargetPendapatan, args['sort']).desc()
                    else:
                        sort = getattr(MsTargetPendapatan, args['sort']).asc()
                    select_query = select_query.order_by(sort)
                else:
                    select_query = select_query.order_by(MsTargetPendapatan.TargetID)

                # PAGINATION
                page = args['page'] if args['page'] else 1
                length = args['length'] if args['length'] else 10
                lengthLimit = length if length < 101 else 100
                query_execute = select_query.paginate(page, lengthLimit)

                for row in query_execute.items:
                    d = {}
                    for key in row.keys():
                        if key == 'TargetPendapatan':
                            d[key] = str( getattr( row, key ) )
                        else:
                            d[key] = getattr( row, key )
                    result.append( d )
                return success_reads_pagination( query_execute, result )

            except Exception as e:
                print( e )
                return failed_reads( result )

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('JenisPendapatanID', type=str)
            parser.add_argument('TahunPendapatan', type=str)
            parser.add_argument('UPTID', type=str)
            parser.add_argument('TargetPendapatan', type=str)
            parser.add_argument( 'Periode', type=int )

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            add_record = MsTargetPendapatan(
                JenisPendapatanID=args['JenisPendapatanID'],
                TahunPendapatan=args['TahunPendapatan'],
                UPTID=args['UPTID'],
                TargetPendapatan=args['TargetPendapatan'],
                Periode=int(args['Periode']),
                Status=1,
                UserUpd=uid,
                DateUpd=datetime.now(),
            )
            db.session.add(add_record)
            db.session.commit()
            return success_create({'JenisPendapatanID': add_record.JenisPendapatanID,
                            'TahunPendapatan' : add_record.TahunPendapatan,
                            'UPTID' : add_record.UPTID,
                            'Periode' : add_record.Periode
                            })


    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsTargetPendapatan.query.filter_by(TargetID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('TargetPendapatan', type=str)


            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = MsTargetPendapatan.query.filter_by(TargetID=id).first()
                if select_query:
                    if args['TargetPendapatan']:
                        select_query.TargetPendapatan = args['TargetPendapatan']
                        select_query.UserUpd = uid
                        select_query.DateUpd = datetime.now()
                        db.session.commit()
                        return success_update({'JenisPendapatanID': select_query.JenisPendapatanID,
                                                'TahunPendapatan' : select_query.TahunPendapatan,
                                                'UPTID' : select_query.UPTID,
                                                'Periode' : select_query.Periode,
                                                'TargetPendapatan' : args['TargetPendapatan']
                                                })
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsTargetPendapatan.query.filter_by(TargetID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})