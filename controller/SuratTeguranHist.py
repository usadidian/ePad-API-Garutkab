from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_create, failed_create, failed_reads, success_reads
from config.database import db
from config.helper import logger
from controller.vw_suratteguranhist import vw_suratteguranhist
from controller.tblUser import tblUser


class SuratTeguranHist(db.Model, SerializerMixin):
    __tablename__ = 'SuratTeguranHist'
    SuratID = db.Column(db.Integer, primary_key=True)
    KohirID = db.Column(db.String, nullable=False)
    NoUrut = db.Column(db.Integer, nullable=False)
    NoSurat = db.Column(db.String, nullable=False)
    TglSurat = db.Column(db.TIMESTAMP, nullable=False)
    Status = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    class ListAll(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
            parser.add_argument('search', type=str)
            parser.add_argument('kohirid', type=str )
            parser.add_argument('filter_jenis', type=str)
            parser.add_argument('kategori', type=str)
            parser.add_argument('nonwp', type=str)

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]

            result = []
            try:
                select_query = db.session.query(
                                                vw_suratteguranhist.SuratID,
                                                # vw_suratteguranhist.NoUrut,
                                                vw_suratteguranhist.NoSurat,
                                                vw_suratteguranhist.TglSurat,
                                                # vw_suratteguranhist.Status,
                                                vw_suratteguranhist.KohirID,
                                                vw_suratteguranhist.SelfAssessment,
                                                vw_suratteguranhist.Insidentil,
                                                vw_suratteguranhist.OBN,
                                                vw_suratteguranhist.ObyekBadanNo,
                                                vw_suratteguranhist.NamaBadan,
                                                vw_suratteguranhist.NamaPemilik,
                                                vw_suratteguranhist.AlamatBadan,
                                                vw_suratteguranhist.AlamatPemilik,
                                                vw_suratteguranhist.Kota,
                                                vw_suratteguranhist.Kecamatan,
                                                vw_suratteguranhist.Kelurahan,
                                                vw_suratteguranhist.MasaAwal,
                                                vw_suratteguranhist.MasaAkhir,
                                                vw_suratteguranhist.TglPenetapan,
                                                vw_suratteguranhist.JatuhTempo,
                                                vw_suratteguranhist.TglJatuhTempo,
                                                vw_suratteguranhist.JmlTeguran,
                                                vw_suratteguranhist.UPTID,
                                                vw_suratteguranhist.UPT,
                                                vw_suratteguranhist.DateUpd,
                                                vw_suratteguranhist.JenisPendapatanID,
                                                vw_suratteguranhist.NamaJenisPendapatan,
                                                vw_suratteguranhist.avatar
                                                ).distinct()

                # FILTER_ID
                if args['kohirid']:
                    select_query = select_query.filter(
                        vw_suratteguranhist.KohirID == args['kohirid']
                    )

                # filter_jenis
                if args['filter_jenis']:
                    select_query = select_query.filter(
                        vw_suratteguranhist.JenisPendapatanID == args['filter_jenis']
                    )

                # kategori
                if args['kategori'] or args['kategori'] == "true":
                    select_query = select_query.filter( vw_suratteguranhist.SelfAssessment == 'Y' )
                else:
                    select_query = select_query.filter( vw_suratteguranhist.SelfAssessment == 'N' )

                # nonwp
                if args['nonwp'] or args['nonwp'] == "true":
                    select_query = select_query.filter( vw_suratteguranhist.Insidentil == 'Y' )
                else:
                    select_query = select_query.filter( vw_suratteguranhist.Insidentil == 'N' )

                # SEARCH
                if args['search'] and args['search'] != 'null':
                    search = '%{0}%'.format(args['search'])
                    select_query = select_query.filter(
                        or_(vw_suratteguranhist.SuratID.ilike(search),
                            vw_suratteguranhist.KohirID.ilike( search ),
                            vw_suratteguranhist.NamaBadan.ilike(search),
                            vw_suratteguranhist.ObyekBadanNo.ilike(search),
                            vw_suratteguranhist.JmlTeguran.ilike(search),
                            vw_suratteguranhist.NamaPemilik.ilike(search),
                            vw_suratteguranhist.NoSurat.ilike( search )
                            )
                    )

                # SORT
                if args['sort']:
                    if args['sort_dir'] == "desc":
                        sort = getattr(vw_suratteguranhist, args['sort']).desc()
                    else:
                        sort = getattr(vw_suratteguranhist, args['sort']).asc()
                    select_query = select_query.order_by(sort)
                else:
                    select_query = select_query.order_by(vw_suratteguranhist.TglPenetapan.desc())

                # PAGINATION
                page = args['page'] if args['page'] else 1
                length = args['length'] if args['length'] else 10
                lengthLimit = length if length < 101 else 100
                query_execute = select_query.distinct().paginate(page, lengthLimit)

                for row in query_execute.items:
                    d = {}
                    for key in row.keys():
                        d[key] = str(getattr(row, key))
                    result.append(d)
                return success_reads_pagination(query_execute, result)
            except Exception as e:
                logger.error(e)
                return failed_reads(result)

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('SuratID', type=str)
            parser.add_argument('KohirID', type=str)
            parser.add_argument('NoUrut', type=str)
            parser.add_argument('NoSurat', type=str)
            parser.add_argument('TglSurat', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            try:
                args = parser.parse_args()
                select_query = db.session.execute(
                    f"SELECT DISTINCT ISNULL(MAX(NoUrut),0) + 1 FROM SuratTeguranHist WHERE KohirID = '{args['KohirID']}'")
                result3 = select_query.first()[0]
                nourut = result3

                add_record = SuratTeguranHist(
                    KohirID=args['KohirID'],
                    NoUrut=nourut,
                    NoSurat=args['NoSurat'],
                    TglSurat=args['TglSurat'],
                    Status=1,
                    UserUpd=uid,
                    DateUpd=datetime.now()
                )
                db.session.add(add_record)
                db.session.commit()
                if add_record.TglSurat:
                    return success_create({'KohirID': add_record.KohirID,
                                           'NoUrut': add_record.NoUrut,
                                           'NoSurat': add_record.NoSurat,
                                           'UserUpd': add_record.UserUpd,
                                           'DateUpd': add_record.DateUpd})

            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_create({})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = SuratTeguranHist.query.filter_by(SuratID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('KohirID', type=str)
            parser.add_argument('NoUrut', type=str)
            parser.add_argument('NoSurat', type=str)
            parser.add_argument('TglSurat', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            args = parser.parse_args()
            uid = kwargs['claim']["UID"]
            try:
                select_query = SuratTeguranHist.query.filter_by(SuratID=id).first()
                if select_query:
                    if args['KohirID']:
                        select_query.KohirID = args['KohirID']
                    if args['NoUrut']:
                        select_query.NoUrut = args['NoUrut']
                    if args['NoSurat']:
                        select_query.NoSurat = args['NoSurat']
                    if args['TglSurat']:
                        select_query.TglSurat = args['TglSurat']
                    if args['Status']:
                        select_query.Status = args['Status']
                    select_query.UserUpd = uid
                    select_query.DateUpd = datetime.now()
                    db.session.commit()
                    return success_update({'KohirID': select_query.KohirID,
                                           'NoUrut': select_query.NoUrut,
                                           'NoSurat': select_query.NoSurat,
                                           'UserUpd': select_query.UserUpd,
                                           'DateUpd': select_query.DateUpd})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})


        def delete(self, id, *args, **kwargs):
            try:
                delete_record = SuratTeguranHist.query.filter_by(SuratID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})


    class ListAll2(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument( 'KohirID', type=str )

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]

            result = []
            try:
                select_query = db.session.query(
                                                vw_suratteguranhist.SuratID,
                                                vw_suratteguranhist.KohirID,
                                                vw_suratteguranhist.ObyekBadanNo,
                                                vw_suratteguranhist.NamaBadan,
                                                vw_suratteguranhist.NamaPemilik,
                                                vw_suratteguranhist.TglJatuhTempo,
                                                vw_suratteguranhist.NoUrut,
                                                vw_suratteguranhist.NoSurat,
                                                vw_suratteguranhist.TglSurat,
                                                vw_suratteguranhist.Status,
                                                vw_suratteguranhist.avatar
                                                )\
                .filter(
                    vw_suratteguranhist.KohirID == args['KohirID']
                ).distinct()
                print("Total rows fetched:", select_query.count())

                result = []
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr(row, key)
                    if d['SuratID'] > 0:
                        result.append(d)
                return success_reads(result)
            except Exception as e:
                logger.error( e )
                return failed_reads( result )



    class ListAll3(Resource):
        def get(self, kohirid, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT KohirID, NamaBadan, AlamatBadan, NamaPemilik, AlamatPemilik FROM vw_suratteguranhist WHERE KohirID='{kohirid}' ")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll4( Resource ):
        method_decorators = {'get': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument( 'SuratID', type=str )

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]

            result = []
            try:
                select_query = db.session.query(
                    vw_suratteguranhist.SuratID,
                    vw_suratteguranhist.KohirID,
                    vw_suratteguranhist.ObyekBadanNo,
                    vw_suratteguranhist.NamaBadan,
                    vw_suratteguranhist.NamaPemilik,
                    vw_suratteguranhist.NoUrut,
                    vw_suratteguranhist.NoSurat,
                    vw_suratteguranhist.TglSurat,
                    vw_suratteguranhist.Status,
                    vw_suratteguranhist.avatar
                ) \
                    .filter(
                    vw_suratteguranhist.SuratID == args['SuratID']
                ).distinct()

                result = []
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr( row, key )
                    if d['SuratID'] > 0:
                        result.append( d )
                return success_reads( result )
            except Exception as e:
                logger.error( e )
                return failed_reads( result )