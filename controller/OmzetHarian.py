from datetime import datetime, timedelta
import json

from _decimal import Decimal
from flask import jsonify, Flask
from flask_restful import Resource, reqparse, Api
from sqlalchemy import case, text, and_, desc
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination, failed_reads, success_reads, failed_create, success_create, \
    success_update, failed_update, success_delete, failed_delete, failed_read, success_read
from config.database import db
from config.helper import logger
from controller.GeneralParameter import GeneralParameter
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsMapOpsen import MsMapOpsen
from controller.MsTarifLokasi import MsTarifLokasi
from controller.PendataanByOmzet import PendataanByOmzet
from controller.PendataanByOmzetDtl import PendataanByOmzetDtl
from controller.PendataanSKP import AddPendataanSKP
from controller.PenetapanByOmzet import PenetapanByOmzet
from controller.tblUser import tblUser
from controller.vw_obyekbadan import vw_obyekbadan
from sqlalchemy import create_engine, update, select, exists


class OmzetHarian(db.Model, SerializerMixin):

    __tablename__ = 'OmzetHarian'
    OmzetHarianID = db.Column(db.Integer, primary_key=True)
    OPDID = db.Column(db.Integer,unique=True, nullable=False)
    TglOmzet = db.Column( db.TIMESTAMP,unique=True, nullable=False)
    JmlOmzet = db.Column( db.Numeric( precision=8, asdecimal=False, decimal_return_scale=None ), nullable=True )
    UserUpd = db.Column( db.String, nullable=False )
    DateUpd = db.Column( db.TIMESTAMP, nullable=False )
    

    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT OPDID, TglOmzet, JmlOmzet FROM OmzetHarian order by OPDID")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll( Resource ):
        # method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument( 'page', type=int )
            parser.add_argument( 'length', type=int )
            parser.add_argument( 'sort', type=str )
            parser.add_argument( 'sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC' )
            parser.add_argument( 'search', type=str )

            args = parser.parse_args()
            # UserId = kwargs['claim']["UserId"]
            # print( UserId )
            select_query = db.session.query( OmzetHarian.OPDID, vw_obyekbadan.NamaBadan, OmzetHarian.TglOmzet, OmzetHarian.JmlOmzet)\
            .outerjoin(vw_obyekbadan, OmzetHarian.OPDID == vw_obyekbadan.OPDID)

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format( args['search'] )
                select_query = select_query.filter(
                    or_( OmzetHarian.TglOmzet.ilike( search ),
                         OmzetHarian.JmlOmzet.ilike( search ) )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr( OmzetHarian, args['sort'] ).desc()
                else:
                    sort = getattr( OmzetHarian, args['sort'] ).asc()
                select_query = select_query.order_by( sort )
            else:
                select_query = select_query.order_by( OmzetHarian.OPDID )

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate( page, lengthLimit )

            result = []
            for row in query_execute.items:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads_pagination( query_execute, result )

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument( 'OPDID', type=str )
            parser.add_argument( 'TglOmzet', type=str )
            parser.add_argument( 'TglOmzet', type=str )

            # uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append( row )

            add_record = OmzetHarian(

                OPDID=args['OPDID'],
                TglOmzet=datetime.now(),
                JmlOmzet=args['JmlOmzet'] if args['JmlOmzet'] else '-',


            )
            db.session.add( add_record )
            db.session.commit()
            return jsonify( {'status_code': 1, 'message': 'OK', 'data': result} )

    class ListById( Resource ):
        # method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
        #                      'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = OmzetHarian.query.filter_by( OPDID=id ).first()
                result = select_query.to_dict()
                return success_read( result )
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_read( {} )

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            # print( kwargs['claim'] )
            parser.add_argument( 'OPDID', type=str )
            parser.add_argument( 'JmlOmzet', type=str )
            parser.add_argument('TglOmzet', type=str)

            # uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = OmzetHarian.query.filter_by( OPDID=id ).first()
                if select_query:

                    if args['OPDID']:
                        select_query.JmlOmzet = args['OPDID']
                    if args['JmlOmzet']:
                        select_query.JmlOmzet = args['JmlOmzet']
                    select_query.TglOmzet = datetime.now()
                    db.session.commit()
                    return success_update( {'id': id} )
            except Exception as e:

                db.session.rollback()
                print( e )
                return failed_update( {} )

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = OmzetHarian.query.filter_by( OPDID=id )
                delete_record.delete()
                db.session.commit()
                return success_delete( {} )
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_delete( {} )

class OmzetHarianSKP(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):

        # PARSING PARAMETER DARI REQUEST
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('length', type=int)
        parser.add_argument('sort', type=str)
        parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
        parser.add_argument('search', type=str)
        parser.add_argument('filter_jenis', type=str)
        parser.add_argument('filter_uptid', type=str)
        parser.add_argument('filter_kecamatanid', type=str)
        parser.add_argument('filter_kelurahanid', type=str)
        parser.add_argument('kategori', type=str, choices=('true', 'false'), help='diisi dengan true atau false')
        parser.add_argument('nonwp', type=str, choices=('true', 'false'), help='diisi dengan true atau false')

        args = parser.parse_args()
        UserId = kwargs['claim']["UserId"]
        IsWP = kwargs['claim']["IsWP"]

        result = []
        try:
            select_query = db.session.query(vw_obyekbadan.WPID, vw_obyekbadan.OBN, vw_obyekbadan.OPDID,
                                            vw_obyekbadan.ObyekBadanNo, vw_obyekbadan.NamaBadan,
                                            vw_obyekbadan.NamaPemilik,
                                            vw_obyekbadan.KodeRekening, vw_obyekbadan.JenisPendapatanID,
                                            vw_obyekbadan.NamaJenisPendapatan,vw_obyekbadan.TglPendaftaran,
                                            vw_obyekbadan.TglPengesahan, vw_obyekbadan.AlamatBadan,
                                            case([(vw_obyekbadan.MasaPendapatan == 'B', 'Bulanan')]
                                                 ,
                                                 else_=''
                                                 ).label('Masa'),
                                            case([(vw_obyekbadan.TglData == None, 'Baru')]
                                                 ,
                                                 else_='Terdata'
                                                 ).label('Status'),
                                            vw_obyekbadan.KecamatanID, vw_obyekbadan.Kecamatan,
                                            vw_obyekbadan.FaxKecamatan,
                                            vw_obyekbadan.KelurahanID, vw_obyekbadan.Kelurahan,
                                            vw_obyekbadan.Insidentil, vw_obyekbadan.DateUpd,
                                            vw_obyekbadan.SelfAssesment, vw_obyekbadan.avatar
                                            ) \
                .filter(
                vw_obyekbadan.TglHapus == None,  vw_obyekbadan.Insidentil == 'N'
                ,vw_obyekbadan.SelfAssesment == 'Y'
            )

            # FILTER_UPT
            if args['filter_uptid']:
                select_query = select_query.filter(
                    vw_obyekbadan.FaxKecamatan == args['filter_uptid']
                )

            # FILTER_KECAMATAN
            if args['filter_kecamatanid']:
                select_query = select_query.filter(
                    vw_obyekbadan.KecamatanID == args['filter_kecamatanid']
                )

            # FILTER_KELURAHAN
            if args['filter_kelurahanid']:
                select_query = select_query.filter(
                    vw_obyekbadan.KelurahanID == args['filter_kelurahanid']
                )

            # FILTER_JENIS
            if args['filter_jenis']:
                select_query = select_query.filter(
                    vw_obyekbadan.JenisPendapatanID == args['filter_jenis']
                )

            # kategori
            if IsWP != 1:
                if args['kategori'] or args['kategori'] == "true":
                    select_query = select_query.filter(vw_obyekbadan.SelfAssesment == 'Y')
                else:
                    select_query = select_query.filter(vw_obyekbadan.SelfAssesment == 'N')

            # nonwp
            if args['nonwp'] or args['nonwp'] == "true":
                select_query = select_query.filter(vw_obyekbadan.Insidentil == 'Y')
            else:
                select_query = select_query.filter(vw_obyekbadan.Insidentil == 'N')

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_obyekbadan.NamaBadan.ilike(search),
                        vw_obyekbadan.ObyekBadanNo.ilike(search),
                        vw_obyekbadan.TglData.ilike(search)
                        )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    if args['sort'] == "Status":
                        sort = getattr(vw_obyekbadan, 'TglData').desc()
                    elif args['sort'] == "Masa":
                        sort = getattr(vw_obyekbadan, 'MasaPendapatan').desc()
                    else:
                        sort = getattr(vw_obyekbadan, args['sort']).desc()
                else:
                    if args['sort'] == "Status":
                        sort = getattr(vw_obyekbadan, 'TglData').asc()
                    elif args['sort'] == "Masa":
                        sort = getattr(vw_obyekbadan, 'MasaPendapatan').asc()
                    else:
                        sort = getattr(vw_obyekbadan, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_obyekbadan.TglData.desc(), vw_obyekbadan.DateUpd.desc())

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

class OmzetHarianSKPOmzet(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    def get(self, opdid, *args, **kwargs):

        # PARSING PARAMETER DARI REQUEST
        parser = reqparse.RequestParser()
        parser.add_argument( 'page', type=int )
        parser.add_argument( 'length', type=int )
        parser.add_argument( 'sort', type=str )
        parser.add_argument( 'sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC' )
        parser.add_argument( 'search', type=str )
        parser.add_argument( 'JenisPendapatanID', type=str )
        args = parser.parse_args()

        select_query = db.session.query(OmzetHarian.OPDID, vw_obyekbadan.NamaBadan, OmzetHarian.TglOmzet, OmzetHarian.JmlOmzet)\
                        .outerjoin(vw_obyekbadan, OmzetHarian.OPDID == vw_obyekbadan.OPDID) \
                        .filter(
                        OmzetHarian.OPDID == opdid
        )

        # SEARCH
        if args['search'] and args['search'] != 'null':
            search = '%{0}%'.format( args['search'] )
            select_query = select_query.filter(
                or_( OmzetHarian.TglOmzet.ilike( search ),
                     OmzetHarian.JmlOmzet.ilike( search ) )
            )

        # SORT
        if args['sort']:
            if args['sort_dir'] == "desc":
                sort = getattr( OmzetHarian, args['sort'] ).desc()
            else:
                sort = getattr( OmzetHarian, args['sort'] ).asc()
            select_query = select_query.order_by( sort )
        else:
            select_query = select_query.order_by(desc(OmzetHarian.TglOmzet ))

        # PAGINATION
        page = args['page'] if args['page'] else 1
        length = args['length'] if args['length'] else 10
        lengthLimit = length if length < 101 else 100
        query_execute = select_query.paginate( page, lengthLimit )

        result = []
        for row in query_execute.items:
            d = {}
            for key in row.keys():
                d[key] = getattr( row, key )
            result.append( d )
        return success_reads_pagination( query_execute, result )

# class OmzetHarianSKPOmzet(Resource):
#     def get(self, opdid, *args, **kwargs):
#         parser = reqparse.RequestParser()
#         parser.add_argument('JenisPendapatanID', type=str)
#         args = parser.parse_args()
#         check_jenis = MsJenisPendapatan.query.filter_by(
#             JenisPendapatanID=args['JenisPendapatanID']
#         ).first()
#         # untuk selain reklame
#         if check_jenis.SelfAssessment == 'Y' and 'reklame' not in check_jenis.NamaJenisPendapatan.lower():
#             select_query = db.session.execute(
#                 f"SELECT DISTINCT x.UPTID,x.SPT,x.MasaAwal,x.MasaAkhir,TglPendataan,pbod.DetailID,v.AlamatPemilik,v.KodeRekening,"
#                 f"v.NamaJenisPendapatan,v.NamaBadan,v.ObyekBadanNo,v.NamaPemilik,(CASE WHEN TglPenetapan IS NULL "
#                 f"THEN 'Terdata' ELSE 'SPTP' END) AS Penetapan, 0 AS Jumlah,'' AS Lokasi,x.TarifPajak AS Pajak FROM "
#                 f"PendataanByOmzet x LEFT JOIN PenetapanByOmzet p ON x.OPDID = p.OPDID AND x.MasaAwal = "
#                 f"p.MasaAwal AND x.MasaAkhir = p.MasaAkhir AND x.UrutTgl = p.UrutTgl LEFT JOIN vw_obyekbadan v ON "
#                 f"x.OPDID = v.OPDID LEFT JOIN PendataanByOmzetDtl AS pbod ON pbod.PendataanID=x.PendataanID "
#                 f"WHERE x.OPDID = '{opdid}' AND (pbod.DetailID != '' or pbod.DetailID != NULL) ORDER BY x.MasaAwal DESC")
#         elif check_jenis.SelfAssessment == 'N' and 'reklame' not in check_jenis.NamaJenisPendapatan.lower():
#             select_query = db.session.execute(
#                 f"SELECT DISTINCT x.UPTID,x.SPT,x.MasaAwal,x.MasaAkhir,TglPendataan,pbod.DetailID,v.AlamatPemilik,v.KodeRekening,"
#                 f"v.NamaJenisPendapatan,v.NamaBadan,v.ObyekBadanNo,v.NamaPemilik,(CASE WHEN TglPenetapan IS NULL "
#                 f"THEN 'Terdata' ELSE 'SKP' END) AS Penetapan, 0 AS Jumlah,'' AS Lokasi,x.TarifPajak AS Pajak FROM "
#                 f"PendataanByOmzet x LEFT JOIN PenetapanByOmzet p ON x.OPDID = p.OPDID AND x.MasaAwal = "
#                 f"p.MasaAwal AND x.MasaAkhir = p.MasaAkhir AND x.UrutTgl = p.UrutTgl LEFT JOIN vw_obyekbadan v ON "
#                 f"x.OPDID = v.OPDID LEFT JOIN PendataanByOmzetDtl AS pbod ON pbod.PendataanID=x.PendataanID "
#                 f"WHERE x.OPDID = '{opdid}' AND (pbod.DetailID != '' or pbod.DetailID != NULL) ORDER BY x.MasaAwal DESC" )
#         result = []
#         for row in select_query:
#             d = {}
#             for key in row.keys():
#                 if key == 'Pajak':
#                     d[key] = str(getattr(row, key))
#                 else:
#                     d[key] = getattr(row, key)
#             result.append(d)
#         return success_reads(result)


app = Flask(__name__)
api = Api(app)
class AddOmzetHarianSKP(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('OPDID', type=str)
        parser.add_argument('TglOmzetHarian', type=str)
        parser.add_argument('JumlahOmzetHarian', type=str)
        try:
            uid = kwargs['claim']["UID"]
            args = parser.parse_args()

            jmlomzetharian = str(args['JumlahOmzetHarian'])
            opdid = args['OPDID']
            tglomzetharian = args['TglOmzetHarian']

            if jmlomzetharian != 0:
                add_record = OmzetHarian(
                    OPDID=opdid,
                    TglOmzet=tglomzetharian,
                    JmlOmzet=jmlomzetharian,
                    UserUpd=uid,
                    DateUpd=datetime.now()
                )

                db.session.add(add_record)
                db.session.commit()
                if add_record.OmzetHarianID:

                    select_query = db.session.execute(
                        f"SELECT TOP 1 ISNULL(JenispendapatanID,'') FROM vw_obyekbadan "
                        f"WHERE OPDID = '{opdid}' ")
                    jpid = select_query.first()[0]
                    print(jpid)

                    select_query = db.session.execute(
                        f"SELECT top 1 isnull(LokasiID,'') FROM MsTarifLokasi "
                        f"WHERE JenisPendapatanID = '{jpid}' ")
                    lokasiid = select_query.first()[0]
                    print(lokasiid)

                    today = datetime.today()
                    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    end_of_month = (start_of_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(
                        days=1)
                    end_of_month = end_of_month.replace(hour=0, minute=0, second=0, microsecond=0)

                    pendataan_data = {
                        'OPDID': opdid,
                        'WapuID': 1,
                        'TglPendataan': tglomzetharian,
                        'MasaAwal': start_of_month.isoformat(),
                        'MasaAkhir': end_of_month.isoformat(),
                        'JumlahOmzetAwal': jmlomzetharian,
                        'TarifPajak': jmlomzetharian,
                        'LokasiID': lokasiid
                    }

                    entry_exists = db.session.query(PendataanByOmzet).filter(
                        (PendataanByOmzet.OPDID == opdid) &
                        (PendataanByOmzet.MasaAwal == start_of_month) &
                        (PendataanByOmzet.MasaAkhir == end_of_month)
                    ).first() is not None

                    if entry_exists:
                        # Update the entry
                        select_query = db.session.execute(
                            text(
                                "SELECT ISNULL((JmlOmzetAwal), 0) AS JmlOmzetAwal FROM PendataanByOmzet AS pbo "
                                "WHERE pbo.OPDID = :opdid AND pbo.MasaAwal = :start_of_month AND pbo.MasaAkhir = :end_of_month"
                            ),
                            {
                                'opdid': str(opdid),  # Pastikan ini adalah string
                                'start_of_month': str(start_of_month),  # Pastikan ini adalah string
                                'end_of_month': str(end_of_month)  # Pastikan ini adalah string
                            }
                        )
                        jmlomzetawal = str(select_query.first()[0])
                        print(jmlomzetawal)

                        select_query = db.session.execute(
                            f"SELECT TOP 1 ISNULL(JenispendapatanID,'') FROM vw_obyekbadan "
                            f"WHERE OPDID = '{opdid}' ")
                        jpid = select_query.first()[0]
                        print(jpid)

                        select_query = db.session.execute(
                            f"SELECT top 1 isnull(LokasiID,'') FROM MsTarifLokasi "
                            f"WHERE JenisPendapatanID = '{jpid}' ")
                        lokasiid = select_query.first()[0]
                        print(lokasiid)

                        usahaid = lokasiid
                        omzet = Decimal(jmlomzetharian) + Decimal(jmlomzetawal)
                        select_query = db.session.query(MsTarifLokasi.TarifPajak).filter(
                            MsTarifLokasi.LokasiID == usahaid)
                        trfpajak = select_query.first()[0] if select_query else None
                        if not trfpajak:
                            return False

                        tarifpajak = float(omzet) * float(trfpajak)

                        select_query = db.session.query(MsMapOpsen.JPIDOpsen).filter(
                            MsMapOpsen.JPID == jpid)
                        jpidopsen = select_query.first()[0]

                        select_query = db.session.query(MsJenisPendapatan.NamaJenisPendapatan).filter(
                            MsJenisPendapatan.JenisPendapatanID == jpidopsen)
                        result = select_query.first()
                        mblb = result[0] if result else None

                        if mblb is not None:
                            select_query = db.session.query(MsTarifLokasi.LokasiID).filter(
                                MsTarifLokasi.JenisPendapatanID == jpidopsen)
                            lokasiidopsen = select_query.first()[0]

                            select_query = db.session.query(MsTarifLokasi.TarifPajak).filter(
                                MsTarifLokasi.LokasiID == lokasiidopsen)
                            trfpajakopsen = select_query.first()[0] if select_query else None

                            tarifpajakopsen = float(tarifpajak) * float(trfpajakopsen)

                            db.session.query(PendataanByOmzet).filter(
                                (PendataanByOmzet.OPDID == opdid) &
                                (PendataanByOmzet.MasaAwal == start_of_month) &
                                (PendataanByOmzet.MasaAkhir == end_of_month)
                            ).update({
                                PendataanByOmzet.TglPendataan: tglomzetharian,
                                PendataanByOmzet.TarifPajak: tarifpajak,
                                PendataanByOmzet.TarifPajakOpsen: tarifpajakopsen,
                                PendataanByOmzet.JmlOmzetAwal: omzet
                            })
                            entry = db.session.query(PendataanByOmzet).filter(
                                (PendataanByOmzet.OPDID == opdid) &
                                (PendataanByOmzet.MasaAwal == start_of_month) &
                                (PendataanByOmzet.MasaAkhir == end_of_month)
                            ).first()

                            # Pastikan entry tidak None sebelum mengakses atributnya
                            if entry.SPT and entry.PendataanID:
                                db.session.query(PendataanByOmzetDtl).filter(
                                    (PendataanByOmzetDtl.SPT == entry.SPT) &
                                    (PendataanByOmzetDtl.PendataanID == entry.PendataanID)
                                ).update({
                                    PendataanByOmzetDtl.TarifPajak: tarifpajak,
                                    PendataanByOmzetDtl.TarifPajakOpsen: tarifpajakopsen,
                                    PendataanByOmzetDtl.Luas: omzet
                                })
                            db.session.commit()

                            skp_exists = db.session.query(PenetapanByOmzet).filter(
                                (PenetapanByOmzet.OPDID == opdid) &
                                (PenetapanByOmzet.MasaAwal == start_of_month) &
                                (PenetapanByOmzet.MasaAkhir == end_of_month) &
                                (PenetapanByOmzet.IsPaid == 'N')
                            ).first() is not None

                            if skp_exists:
                                db.session.query(PenetapanByOmzet).filter(
                                    (PenetapanByOmzet.OPDID == opdid) &
                                    (PenetapanByOmzet.MasaAwal == start_of_month) &
                                    (PenetapanByOmzet.MasaAkhir == end_of_month)
                                ).update({
                                    PenetapanByOmzet.TglPenetapan: tglomzetharian,
                                    PenetapanByOmzet.TarifPajak: tarifpajak,
                                    PenetapanByOmzet.TarifPajakOpsen: tarifpajakopsen,
                                    PenetapanByOmzet.JmlOmzetAwal: omzet
                                })
                            db.session.commit()
                            return success_create({
                                'OPDID': opdid,
                                'JmlOmzetAwal': omzet,
                                'TarifPajak': tarifpajak
                            })
                        else:
                            db.session.query(PendataanByOmzet).filter(
                                (PendataanByOmzet.OPDID == opdid) &
                                (PendataanByOmzet.MasaAwal == start_of_month) &
                                (PendataanByOmzet.MasaAkhir == end_of_month)
                            ).update({
                                PendataanByOmzet.TglPendataan: tglomzetharian,
                                PendataanByOmzet.TarifPajak: tarifpajak,
                                PendataanByOmzet.JmlOmzetAwal: omzet
                            })
                            entry = db.session.query(PendataanByOmzet).filter(
                                (PendataanByOmzet.OPDID == opdid) &
                                (PendataanByOmzet.MasaAwal == start_of_month) &
                                (PendataanByOmzet.MasaAkhir == end_of_month)
                            ).first()

                            # Pastikan entry tidak None sebelum mengakses atributnya
                            if entry.SPT and entry.PendataanID:
                                db.session.query(PendataanByOmzetDtl).filter(
                                    (PendataanByOmzetDtl.SPT == entry.SPT) &
                                    (PendataanByOmzetDtl.PendataanID == entry.PendataanID)
                                ).update({
                                    PendataanByOmzetDtl.TarifPajak: tarifpajak,
                                    PendataanByOmzetDtl.Luas: omzet
                                })
                            db.session.commit()

                            skp_exists = db.session.query(PenetapanByOmzet).filter(
                                (PenetapanByOmzet.OPDID == opdid) &
                                (PenetapanByOmzet.MasaAwal == start_of_month) &
                                (PenetapanByOmzet.MasaAkhir == end_of_month) &
                                (PenetapanByOmzet.IsPaid == 'N')
                            ).first() is not None

                            if skp_exists:
                                db.session.query(PenetapanByOmzet).filter(
                                    (PenetapanByOmzet.OPDID == opdid) &
                                    (PenetapanByOmzet.MasaAwal == start_of_month) &
                                    (PenetapanByOmzet.MasaAkhir == end_of_month)
                                ).update({
                                    PenetapanByOmzet.TglPenetapan: tglomzetharian,
                                    PenetapanByOmzet.TarifPajak: tarifpajak,
                                    PenetapanByOmzet.JmlOmzetAwal: omzet
                                })
                            db.session.commit()
                            return success_create({
                                'OPDID': opdid,
                                'JmlOmzetAwal': omzet,
                                'TarifPajak': tarifpajak
                            })

                    else:
                        add_pendataan_skp = AddPendataanSKP()
                        if not add_pendataan_skp:
                            db.session.rollback()
                            return failed_create({})

                        with app.test_request_context('/add_pendataan_skp', method='POST', data=json.dumps(pendataan_data), content_type='application/json'):
                            response = add_pendataan_skp.post(*args, **kwargs)
                            response_data = response.get_json()  # Extract the JSON content from the response
                            print(response_data)

                return success_create({
                    'OPDID': add_record.OPDID,
                    'TglOmzetHarian': add_record.TglOmzet,
                    'JmlOmzetHarian': add_record.JmlOmzet,
                    'OmzetHarianResult': response_data
                })
            else:
                logger.error('gagal insert pendataan ke db')
                db.session.rollback()
                return failed_create({})

        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return failed_create({})

api.add_resource(AddOmzetHarianSKP, '/add_omzet_harian_skp')

if __name__ == '__main__':
    app.run(debug=True)
