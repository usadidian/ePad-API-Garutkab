from datetime import datetime

from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import and_, case, func
from sqlalchemy import or_
from sqlalchemy.orm import aliased
from sqlalchemy_serializer import SerializerMixin

from config.api_message import failed_update
from config.api_message import success_read, failed_read, success_delete, failed_delete, \
    success_update, success_reads_pagination, failed_reads, success_reads
from config.database import db
from controller.GroupAttribute import GroupAttribute
from controller.Matangd import MATANGD
from controller.MsSatuanOmzet import MsSatuanOmzet
from controller.tblUser import tblUser


class MsJenisPendapatan(db.Model, SerializerMixin):
    __tablename__ = 'MsJenisPendapatan'
    JenisPendapatanID = db.Column(db.String, primary_key=True)
    NamaJenisPendapatan = db.Column(db.String, nullable=False)
    FlagJenisPendapatan = db.Column(db.String, nullable=False)
    FlagBendaBerharga = db.Column(db.String, nullable=False)
    ParentID = db.Column(db.String, nullable=False)
    PrefixNumber = db.Column(db.String, nullable=False)
    MasaPendapatan = db.Column(db.String, nullable=True)
    HariJatuhTempo = db.Column(db.Integer, nullable=True)
    OmzetBase = db.Column(db.String, nullable=True)
    OmzetProsentase = db.Column(db.Float, nullable=True)
    Status = db.Column(db.String, nullable=False)
    SelfAssessment = db.Column(db.Integer, nullable=True)
    RekeningDenda = db.Column(db.String, nullable=True)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)
    img = db.Column(db.String, nullable=False)
    icon = db.Column(db.String, nullable=False)

    KodeRekening = db.Column(db.String, db.ForeignKey('MsJenisPendapatan.KodeRekening'), nullable=False)
    # KodeRekening13 = db.Column( db.String, db.ForeignKey( 'MsJenisPendapatan.KodeRekening' ), nullable=False )
    GroupAttribute = db.Column(db.Integer, db.ForeignKey('GroupAttribute.GroupID'), nullable=False)
    OmzetID = db.Column(db.String, db.ForeignKey('MsSatuanOmzet.OmzetID'), nullable=False)

    class jenispajak( Resource ):
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

            result = []

            try:
                walet = '%{0}%'.format( 'Walet' )
                select_query = db.session.query(MsJenisPendapatan.JenisPendapatanID.label('jenispajakid'),
                                                MsJenisPendapatan.KodeRekening.label('koderekening'),
                                                MsJenisPendapatan.NamaJenisPendapatan.label('jenispajak')\
                                                ).filter(or_(*(and_(MsJenisPendapatan.SelfAssessment == 'Y',
                                                MsJenisPendapatan.ParentID <= 2, MsJenisPendapatan.ParentID != ''),
                                                MsJenisPendapatan.NamaJenisPendapatan == 'Sarang Burung Walet')))


                # SEARCH
                if args['search'] and args['search'] != 'null':
                    search = '%{0}%'.format( args['search'] )
                    select_query = select_query.filter(
                        or_(
                             MsJenisPendapatan.JenisPendapatanID.ilike( search ),
                             MsJenisPendapatan.NamaJenisPendapatan.ilike( search ) )
                    )

                # SORT
                if args['sort']:
                    if args['sort_dir'] == "desc":
                        sort = getattr( MsJenisPendapatan, args['sort'] ).desc()
                    else:
                        sort = getattr( MsJenisPendapatan, args['sort'] ).asc()
                    select_query = select_query.order_by( sort )
                else:
                    select_query = select_query.order_by( MsJenisPendapatan.KodeRekening )

                # PAGINATION
                page = args['page'] if args['page'] else 1
                length = args['length'] if args['length'] else 20
                lengthLimit = length if length < 101 else 100
                query_execute = select_query.paginate( page, lengthLimit )

                for row in query_execute.items:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr(row, key)
                    result.append(d)
                return success_reads_pagination(query_execute, result)
            except Exception as e:
                print( e )
                return failed_reads( result )

    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT DISTINCT mjp.JenisPendapatanID,mjp.KodeRekening,mjp.NamaJenisPendapatan, mjp.img, mjp.icon "
                f"FROM MsJenisPendapatan AS mjp WHERE mjp.[Status]='1' AND mjp.FlagBendaBerharga = 'N' " 
                f"AND mjp.JenisPendapatanID in (select distinct usahabadan from msobyekbadan where TglPenghapusan IS NULL)"
                f"AND mjp.NamaJenisPendapatan not like 'Pajak Bumi %' AND mjp.ParentID != '' " 
                f"ORDER BY mjp.KodeRekening")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll3(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT DISTINCT p.JenisPendapatanID AS Kode, p.KodeRekening, p.NamaJenisPendapatan AS Nama, "
                f"p.FlagJenisPendapatan FROM ((MsObyekBadan o LEFT JOIN MsJenisPendapatan j ON "
                f"o.UsahaBadan = j.JenisPendapatanID) LEFT JOIN MsJenisPendapatan p ON j.JenisPendapatanID = p.JenisPendapatanID) "
                f"WHERE  TglPenghapusan IS NULL AND SelfAssesment='N' ORDER BY p.KodeRekening")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll4(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT DISTINCT p.JenisPendapatanID, p.KodeRekening, p.NamaJenisPendapatan, "
                f"p.FlagJenisPendapatan FROM ((MsObyekBadan o LEFT JOIN MsJenisPendapatan j ON "
                f"o.UsahaBadan = j.JenisPendapatanID) LEFT JOIN MsJenisPendapatan p ON j.JenisPendapatanID = p.JenisPendapatanID) "
                f"WHERE  TglPenghapusan IS NULL AND SelfAssesment='Y' ORDER BY p.KodeRekening")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll5(Resource):
        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('WPID', type=str)
            args = parser.parse_args()
            print(args)
            wpid = args['WPID']

            if wpid is not None:
                # Gunakan parameter binding untuk keamanan
                select_query = db.session.execute(
                    "SELECT JenisPendapatanID, KodeRekening, NamaJenisPendapatan "
                    "FROM MsJenisPendapatan "
                    "WHERE [Status]='1' AND ParentID <> '' AND NamaJenisPendapatan NOT LIKE '%DENDA%' "
                    "AND NamaJenisPendapatan not like 'Pajak Bumi %' AND NamaJenisPendapatan not like '%Opsen%' "
                    "AND FlagBendaBerharga='N' AND JenisPendapatanID NOT IN (SELECT d.UsahaBadan FROM MsOPD d "
                    "WHERE d.WPID = :wpid) "
                    "ORDER BY KodeRekening",
                    {'wpid': wpid}
                )
            else:
                return {'error': 'WPID is required'}, 400

            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll50(Resource):
        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('kategori', type=str, choices=('true', 'false'), help='Diisi dengan true atau false')
            args = parser.parse_args()

            print("Nilai kategori yang diterima:", args['kategori'])

            # Query SQL dasar
            base_query = (
                "SELECT JenisPendapatanID, KodeRekening, NamaJenisPendapatan FROM MsJenisPendapatan "
                "WHERE [Status]='1' AND ParentID <> '' AND NamaJenisPendapatan NOT LIKE '%DENDA%' "
                "AND NamaJenisPendapatan NOT LIKE 'Pajak Bumi %' AND NamaJenisPendapatan NOT LIKE '%Opsen%' "
                "AND FlagBendaBerharga='N' "
            )

            # Tambahkan kondisi sesuai nilai `kategori`
            if args['kategori'] == 'true':
                base_query += "AND SelfAssessment = 'Y' "
            else:
                base_query += "AND SelfAssessment = 'N' "

            # Tambahkan urutan
            base_query += "ORDER BY KodeRekening"

            # Eksekusi query
            select_query = db.session.execute(base_query)
            result = []

            # Proses hasil query
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)

            return success_reads(result)

    class ListAll51(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT JenisPendapatanID, KodeRekening, NamaJenisPendapatan FROM MsJenisPendapatan "
                f"WHERE [Status]='1' AND ParentID <> '' AND NamaJenisPendapatan NOT LIKE '%DENDA%' "
                f"AND NamaJenisPendapatan not like 'Pajak Bumi %' AND NamaJenisPendapatan not like '%Opsen MBLB%' "
                f"AND FlagBendaBerharga='N'"
                f"ORDER BY KodeRekening")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll6(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT JenisPendapatanID, KodeRekening, NamaJenisPendapatan "
                f"FROM MsJenisPendapatan WHERE [Status] = '1' AND OmzetBase = 'Y' AND NamaJenisPendapatan like 'BPHTB%' "
                f"AND FlagBendaBerharga = 'N' ORDER BY NamaJenisPendapatan")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)


    class ListAll7(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT JenisPendapatanID AS JenisPendapatanIDDenda, KodeRekening AS KodeRekeningDenda, "
                f"NamaJenisPendapatan AS NamaJenisPendapatanDenda "
                f"FROM MsJenisPendapatan WHERE ParentID != '' AND FlagBendaBerharga = 'S' "
                f"AND ((left(ltrim(KodeRekening),6) = '4.1.4.') OR (left(ltrim(KodeRekening),7) = '4.1.04.')) ORDER BY KodeRekening")
            result = []
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
            parser.add_argument('filter_jenis', type=str)
            parser.add_argument('kategori', type=str, choices=('true', 'false'), help='diisi dengan true atau false')

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            print(UserId)

            result = []

            try:
                mjp = aliased( MsJenisPendapatan )
                mjp2 = aliased( MsJenisPendapatan )
                select_query = db.session.query(mjp.JenisPendapatanID, mjp.KodeRekening, mjp.NamaJenisPendapatan,
                                                mjp.HariJatuhTempo, MsSatuanOmzet.OmzetID, MsSatuanOmzet.SatuanOmzet,
                                                mjp.OmzetProsentase, mjp.MasaPendapatan, mjp.SelfAssessment,
                                                mjp.RekeningDenda, mjp.OmzetBase,
                                                mjp2.KodeRekening.label('KodeRekeningDenda'),
                                                mjp2.NamaJenisPendapatan.label('NamaJenisPendapatanDenda'),
                                                GroupAttribute.GroupID.label('GroupAttribute'), mjp.Status,
                                                case( [
                                                    (mjp.Status == '1', 'Aktif')], else_='Non Aktif' ).label(
                                                    'NamaStatus' )
                                                ) \
                    .outerjoin(mjp2, mjp.RekeningDenda == mjp2.JenisPendapatanID)\
                    .outerjoin(MsSatuanOmzet, mjp.OmzetID == MsSatuanOmzet.OmzetID) \
                    .outerjoin(GroupAttribute, mjp.GroupAttribute == GroupAttribute.GroupID)\
                    .filter(mjp.ParentID != '')
                # select_query = MsJenisPendapatan.query

                if args['filter_jenis']:
                    select_query = select_query.filter(
                        mjp.FlagBendaBerharga == args['filter_jenis']
                    )

                if args['kategori'] or args['kategori'] == "true":
                    select_query = select_query.filter(mjp.FlagBendaBerharga == 'S')
                else:
                    select_query = select_query.filter(mjp.FlagBendaBerharga == 'N')

                # SEARCH
                if args['search'] and args['search'] != 'null':
                    search = '%{0}%'.format( args['search'] )
                    select_query = select_query.filter(
                        or_( mjp.KodeRekening.ilike( search ),
                             mjp.NamaJenisPendapatan.ilike( search ) )
                    )

                # SORT
                if args['sort']:
                    if args['sort_dir'] == "desc":
                        sort = getattr( mjp, args['sort'] ).desc()
                    else:
                        sort = getattr( mjp, args['sort'] ).asc()
                    select_query = select_query.order_by( sort )
                else:
                    select_query = select_query.order_by( mjp.KodeRekening )

                # PAGINATION
                page = args['page'] if args['page'] else 1
                length = args['length'] if args['length'] else 10
                lengthLimit = length if length < 101 else 100
                query_execute = select_query.paginate( page, lengthLimit )

                result = []
                for row in query_execute.items:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr(row, key)
                    result.append(d)
                return success_reads_pagination(query_execute, result)
            except Exception as e:
                print(e)
                return failed_reads(result)

            #     # SEARCH
            #     if args['search'] and args['search'] != 'null':
            #         search = '%{0}%'.format(args['search'])
            #         select_query = select_query.filter(
            #             or_(MsJenisPendapatan.KodeRekening.ilike(search),
            #                 MsJenisPendapatan.NamaJenisPendapatan.ilike(search))
            #         )
            #
            #     # SORT
            #     if args['sort']:
            #         if args['sort_dir'] == "desc":
            #             sort = getattr(MsJenisPendapatan, args['sort']).desc()
            #         else:
            #             sort = getattr(MsJenisPendapatan, args['sort']).asc()
            #         select_query = select_query.order_by(sort)
            #     else:
            #         select_query = select_query.order_by(MsJenisPendapatan.KodeRekening)
            #
            #     # PAGINATION
            #     page = args['page'] if args['page'] else 1
            #     length = args['length'] if args['length'] else 10
            #     lengthLimit = length if length < 101 else 100
            #     query_execute = select_query.paginate(page, lengthLimit)
            #
            #     # print(query_execute.items)
            #     for row in query_execute.items:
            #         d = {}
            #         for key in row.keys():
            #             # print(key,  getattr(row, key))
            #             d[key] = getattr(row, key)
            #         result.append(d)
            #     return success_reads_pagination(query_execute, result)
            # except Exception as e:
            #     print(e)
            #     return failed_reads(result)



        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('JenisPendapatanID', type=str)
            # parser.add_argument('NamaJenisPendapatan', type=str)
            parser.add_argument( 'MTGKEY', type=str )
            # parser.add_argument('FlagJenisPendapatan', type=str)
            parser.add_argument('FlagBendaBerharga', type=str)
            parser.add_argument('ParentID', type=str)
            parser.add_argument('PrefixNumber', type=str)
            parser.add_argument('MasaPendapatan', type=str)
            # parser.add_argument('KodeRekening', type=str)
            # parser.add_argument( 'KDPER', type=str )
            parser.add_argument('HariJatuhTempo', type=str)
            parser.add_argument('GroupAttribute', type=str)
            parser.add_argument('OmzetBase', type=str)
            parser.add_argument('OmzetID', type=str)
            parser.add_argument('OmzetProsentase', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('SelfAssessment', type=str)
            parser.add_argument('RekeningDenda', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)
            parser.add_argument('kategori', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            select_query = db.session.execute(
                f"SELECT CAST(MAX(CAST(JenisPendapatanID AS int) + 1) AS varchar(10)) AS NextID FROM MsJenisPendapatan")
            result2 = select_query.first()[0]
            jenispendapatanid = result2

            select_query = MATANGD.query.filter_by( MTGKEY=args['MTGKEY'] ).first()
            koderekening = select_query.KDPER
            namajenispendapatan = select_query.NMPER

            select_query = db.session.execute(
                f"SELECT RIGHT('0'+CAST(ROW_NUMBER() OVER (PARTITION BY m.KDPER ORDER BY m.KDPER) AS VARCHAR(3)),3)"
                f"FROM MATANGD AS m WHERE m.KDPER= '{koderekening}'")
            result3 = select_query.first()[0]
            prefixnumber = result3

            select_query = db.session.execute(
                f"SELECT TYPE FROM MATANGD WHERE KDPER='{koderekening}' "
            )
            type = select_query.first()[0]

            # entry_exists = db.session.query(MsJenisPendapatan).filter(
            #     (MsJenisPendapatan.KodeRekening == koderekening)
            # ).first() is not None

            # koderekening ='4.1.01.14.00.'
            length = len(koderekening)
            left_length = length - 5
            parentid = ''
            entry_exists = db.session.query(MsJenisPendapatan).filter(
                MsJenisPendapatan.KodeRekening == func.left(koderekening, left_length)
            ).first()
            print(entry_exists)

            if entry_exists:
                select_query = db.session.execute(
                    f"SELECT ISNULL(mjp.JenisPendapatanID,'') FROM MsJenisPendapatan AS mjp "
                    f"WHERE mjp.KodeRekening= LEFT('{koderekening}', LEN('{koderekening}') - CHARINDEX('.', REVERSE('{koderekening}')) - 4)"
                )
                parentid = select_query.first()[0]
            kategori = args['kategori'].lower()
            prosentase = float(args['OmzetProsentase']) / 100

            add_record = MsJenisPendapatan(
                JenisPendapatanID=jenispendapatanid,
                NamaJenisPendapatan=namajenispendapatan,
                FlagJenisPendapatan='P',
                FlagBendaBerharga= 'S' if kategori == "true" else 'N',
                ParentID= parentid if parentid  else '',
                PrefixNumber=prefixnumber,
                MasaPendapatan=args['MasaPendapatan'],
                KodeRekening=koderekening,
                HariJatuhTempo=args['HariJatuhTempo'],
                GroupAttribute=args['GroupAttribute'],
                OmzetBase=args['OmzetBase'],
                OmzetID=args['OmzetID'],
                OmzetProsentase=prosentase if args['OmzetProsentase'] != 0 else 0,
                Status=args['Status'],
                SelfAssessment=args['SelfAssessment'],
                RekeningDenda=args['RekeningDenda'],
                UserUpd=uid,
                DateUpd=datetime.now()

            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsJenisPendapatan.query.filter_by(JenisPendapatanID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            # parser.add_argument('JenisPendapatanID', type=str)
            # parser.add_argument('NamaJenisPendapatan', type=str)
            # parser.add_argument('FlagJenisPendapatan', type=str)
            # parser.add_argument('FlagBendaBerharga', type=str)
            # parser.add_argument('ParentID', type=str)
            # parser.add_argument('PrefixNumber', type=str)
            parser.add_argument('MasaPendapatan', type=str)
            # parser.add_argument('KodeRekening', type=str)
            parser.add_argument('HariJatuhTempo', type=str)
            parser.add_argument('GroupAttribute', type=str)
            parser.add_argument('OmzetBase', type=str)
            parser.add_argument('OmzetID', type=str)
            parser.add_argument('OmzetProsentase', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('SelfAssessment', type=str)
            parser.add_argument('RekeningDenda', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            prosentase = float(args['OmzetProsentase'])/ 100

            try:
                select_query = MsJenisPendapatan.query.filter_by(JenisPendapatanID=id).first()
                if select_query:
                    # select_query.JenisPendapatanID = args['JenisPendapatanID']
                    # select_query.NamaJenisPendapatan = args['NamaJenisPendapatan']
                    # select_query.FlagJenisPendapatan = args['FlagJenisPendapatan']
                    # select_query.FlagBendaBerharga = args['FlagBendaBerharga']
                    # select_query.ParentID = args['ParentID']
                    # select_query.PrefixNumber = args['PrefixNumber']
                    if args['MasaPendapatan']:
                        select_query.MasaPendapatan = args['MasaPendapatan']
                    if args['HariJatuhTempo']:
                        select_query.HariJatuhTempo = args['HariJatuhTempo']
                    if args['GroupAttribute']:
                        select_query.GroupAttribute = args['GroupAttribute']
                    if args['OmzetBase']:
                        select_query.OmzetBase = args['OmzetBase']
                    if args['OmzetID']:
                        select_query.OmzetID = args['OmzetID']
                    if args['OmzetProsentase']:
                        select_query.OmzetProsentase = prosentase
                    if args['SelfAssessment']:
                        select_query.SelfAssessment = args['SelfAssessment']
                    if args['RekeningDenda']:
                     select_query.RekeningDenda = args['RekeningDenda']
                    if args['Status']:
                        select_query.Status = args['Status']
                    select_query.UserUpd = uid
                    select_query.DateUpd = datetime.now()
                    db.session.commit()
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsJenisPendapatan.query.filter_by(JenisPendapatanID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})



class MsJenisPendapatan13(db.Model, SerializerMixin):
    serialize_rules = ('-FlagBendaBerharga', '-Status')
    __tablename__ = 'MsJenisPendapatan13'
    JenisPendapatanID = db.Column(db.String, primary_key=True)
    NamaJenisPendapatan = db.Column(db.String, nullable=False)
    FlagBendaBerharga = db.Column(db.String, nullable=False)
    Status = db.Column(db.String, nullable=False)
    # ParentID = db.Column(db.String)
    ParentID = db.Column(db.String, db.ForeignKey('MsJenisPendapatan13.JenisPendapatanID'))
    KodeRekening = db.Column(db.String)
    childs = db.relationship('MsJenisPendapatan13')



    class ListAll(Resource):
        # method_decorators = {'get': [tblUser.auth_apikey_privilege]}
        def get(self, *args, **kwargs):
            try:
                select_query = MsJenisPendapatan13.query
                select_query = select_query.filter(
                    MsJenisPendapatan13.Status == "1",
                    MsJenisPendapatan13.ParentID == "",
                    MsJenisPendapatan13.FlagBendaBerharga == "N",
                    MsJenisPendapatan13.KodeRekening != "4.1.01.07.07.0001."
                )
                select_query = select_query.order_by(MsJenisPendapatan13.KodeRekening).all()
                result = []
                for row in select_query:
                    result.append(row.to_dict())
                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_read({})
