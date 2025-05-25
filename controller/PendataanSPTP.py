from datetime import datetime
from flask_restful import Resource, reqparse
from sqlalchemy import case
from sqlalchemy import or_
from config.api_message import success_reads_pagination, failed_reads, success_reads, failed_create, success_create, \
    success_update, failed_update, success_delete, failed_delete
from config.database import db
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.PendataanByOmzet import PendataanByOmzet
from controller.PendataanByOmzetDtl import PendataanByOmzetDtl
from controller.PenetapanByOmzet import PenetapanByOmzet
from controller.tblUser import tblUser
from controller.vw_obyekbadan import vw_obyekbadan


class PendataanSPTP2(Resource):
    def get(self, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT OBN,OPDID,ObyekBadanNo,NamaBadan,NamaJenisPendapatan AS Jenis,TglSah,"
            f"(CASE WHEN MasaPendapatan='B' THEN 'Bulanan' ELSE '' END) AS Masa,(CASE WHEN TglData IS NULL "
            f"THEN 'Baru' ELSE 'Terdata' END) AS [Status],Kecamatan FROM vw_obyekbadan WHERE  SelfAssesment = 'Y' "
            f"AND TglHapus IS NULL AND  OPDID IN (select distinct OPDID from MsObyekBadan "
            f"where Insidentil = 'N')  ORDER BY OBN")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


class PendataanSPTP3(Resource):
    def get(self, opdid, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT OPDID,ObyekBadanNo, NamaBadan,NamaPemilik,AlamatBadan, Kota,Kecamatan,Kelurahan, "
            f"vw.KodeRekening, KodePos,UsahaBadan, vw.NamaJenisPendapatan AS Sub,ISNULL(GroupAttribute,0) "
            f"AS GroupAttribute,vw.OmzetBase,vw.OmzetID,vw.MasaPendapatan FROM vw_obyekbadan vw "
            f"LEFT JOIN MsJenisPendapatan jp ON vw.UsahaBadan = jp.JenisPendapatanID WHERE OPDID='{opdid}'")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)


class PendataanSPTPOmzet(Resource):
    def get(self, opdid, *args, **kwargs):
        select_query = db.session.execute(
            f"SELECT x.UPTID,x.SPT,x.MasaAwal,x.MasaAkhir,TglPendataan,pbod.DetailID,v.AlamatPemilik,v.KodeRekening,"
            f"v.NamaJenisPendapatan,(CASE WHEN TglPenetapan IS NULL "
            f"THEN 'Terdata' ELSE 'SPTP' END) AS Validasi, 0 AS Jumlah,'' AS Lokasi,x.TarifPajak AS Pajak FROM "
            f"((PendataanByOmzet x LEFT JOIN PenetapanByOmzet p ON x.OPDID = p.OPDID AND x.MasaAwal = "
            f"p.MasaAwal AND x.MasaAkhir = p.MasaAkhir AND x.UrutTgl = p.UrutTgl) LEFT JOIN vw_obyekbadan v ON "
            f"x.OPDID = v.OPDID) LEFT JOIN PendataanByOmzetDtl AS pbod ON pbod.PendataanID=x.PendataanID "
            f"WHERE x.OPDID = '{opdid}' ORDER BY x.MasaAwal DESC")
        result = []
        for row in select_query:
            d = {}
            for key in row.keys():
                if key == 'Pajak':
                    d[key] = str(getattr(row, key))
                else:
                    d[key] = getattr(row, key)
            result.append(d)
        return success_reads(result)

class AddPendataanSPTP(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('SPT', type=str)
        parser.add_argument('OPDID', type=str)
        parser.add_argument('TglPendataan', type=str)
        parser.add_argument('MasaAwal', type=str)
        parser.add_argument('MasaAkhir', type=str)
        parser.add_argument('UrutTgl', type=str)
        parser.add_argument('JmlOmzetAwal', type=str)
        parser.add_argument('TarifPajak', type=str)
        parser.add_argument('UPTID', type=str)
        parser.add_argument('Status', type=str)
        parser.add_argument('LKecamatan', type=str)
        parser.add_argument('LKelurahan', type=str)
        parser.add_argument('UserUpd', type=str)
        parser.add_argument('DateUpd', type=str)

        parser.add_argument('PendataanID', type=str)
        parser.add_argument('UsahaID', type=str)
        parser.add_argument('Luas', type=str)

        uid = kwargs['claim']["UID"]

        try:
            args = parser.parse_args()
            result = db.session.execute(
                f"exec [SP_SPT] '{args['TglPendataan']}'")
            result2 = []
            for row in result:
                result2.append(row)
                # print(row[0])
            spt = result2[0][0]

            select_query = db.session.execute(
                f"SELECT DISTINCT isnull(max(UrutTgl) + 1,1) FROM PendataanByOmzet "
                f"WHERE OPDID = '{args['OPDID']}' AND MasaAwal='{args['MasaAwal']}' AND MasaAkhir='{args['MasaAkhir']}'")
            result3 = select_query.first()[0]
            uruttgl = result3

            jmlomzetawal = args['JmlOmzetAwal']
            opdid = args['OPDID']
            tglpendataan = args['TglPendataan']

            if jmlomzetawal != 0:
                add_record = PendataanByOmzet(
                    SPT=spt,
                    OPDID=opdid,
                    TglPendataan=tglpendataan,
                    MasaAwal=args['MasaAwal'],
                    MasaAkhir=args['MasaAkhir'],
                    UrutTgl=uruttgl,
                    JmlOmzetAwal=jmlomzetawal,
                    TarifPajak=args['TarifPajak'],
                    UPTID=args['UPTID'],
                    Status=1,
                    LKecamatan=args['LKecamatan'],
                    LKelurahan=args['LKelurahan'],
                    UserUpd=uid,
                    DateUpd=datetime.now()
                )
                db.session.add(add_record)
                db.session.commit()
                if add_record:
                    select_query = db.session.execute(
                        f"UPDATE MsWP SET TglPendataan = '{tglpendataan}' WHERE OPDID = {opdid} "
                        f"AND TglPendataan IS NULL")
                    data = {
                        'uid': uid,
                        'PendataanID': add_record.PendataanID,
                        'SPT': add_record.SPT,
                        'LKecamatan': add_record.LKecamatan,
                        'LKelurahan': add_record.LKelurahan,
                        'UsahaID': args['UsahaID'],
                        'Luas': add_record.JmlOmzetAwal,

                    }
                    add_record_detail = PendataanByOmzetDtl.AddPPendataanDetil(data)
                    if add_record_detail:
                        return success_create({'SPT': add_record.SPT,
                                               'UPTID': add_record.UPTID,
                                               'OPDID': add_record.OPDID,
                                               'TarifPajak': add_record.TarifPajak})
            else:
                db.session.rollback()
                return failed_create({})

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_create({})


class UpdatePendataanSPTP(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}
    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        print(kwargs['claim'])
        parser.add_argument('SPT', type=str)
        parser.add_argument('OPDID', type=str)
        parser.add_argument('TglPendataan', type=str)
        parser.add_argument('MasaAwal', type=str)
        parser.add_argument('MasaAkhir', type=str)
        parser.add_argument('UrutTgl', type=str)
        parser.add_argument('JmlOmzetAwal', type=str)
        parser.add_argument('TarifPajak', type=str)
        parser.add_argument('UPTID', type=str)
        parser.add_argument('Status', type=str)
        parser.add_argument('LKecamatan', type=str)
        parser.add_argument('LKelurahan', type=str)
        parser.add_argument('UserUpd', type=str)
        parser.add_argument('DateUpd', type=str)

        parser.add_argument('PendataanID', type=str)
        parser.add_argument('UsahaID', type=str)
        parser.add_argument('Luas', type=str)
        parser.add_argument('NoUrut', type=str)
        parser.add_argument('DetailID', type=int)

        args = parser.parse_args()
        uid = kwargs['claim']["UID"]
        try:
            select_query = PendataanByOmzet.query.filter_by(SPT=id).first()
            if select_query:
                if args['OPDID']:
                    select_query.OPDID = f"{args['OPDID']}"
                if args['TglPendataan']:
                    select_query.TglPendataan = args['TglPendataan']
                if args['MasaAwal']:
                    select_query.MasaAwal = args['MasaAwal']
                if args['MasaAkhir']:
                    select_query.MasaAkhir = args['MasaAkhir']
                if args['UrutTgl']:
                    select_query.UrutTgl = args['UrutTgl']
                if args['JmlOmzetAwal']:
                    select_query.JmlOmzetAwal = args['JmlOmzetAwal']
                if args['TarifPajak']:
                    select_query.TarifPajak = args['TarifPajak']
                if args['UPTID']:
                    select_query.UPTID = args['UPTID']
                if args['Status']:
                    select_query.Status = args['Status']
                if args['LKecamatan']:
                    select_query.LKecamatan = args['LKecamatan']
                if args['LKelurahan']:
                    select_query.LKelurahan = args['LKelurahan']
                select_query.UserUpd = uid
                select_query.DateUpd = datetime.now()
                db.session.commit()
                print('sukses update ke header')
                if select_query.SPT:
                    data = {
                        'uid': uid,
                        'PendataanID': select_query.PendataanID,
                        'SPT': select_query.SPT,
                        'LKecamatan': select_query.LKecamatan,
                        'LKelurahan': select_query.LKelurahan,
                        'UsahaID': args['UsahaID'],
                        'Luas': select_query.JmlOmzetAwal,
                        'NoUrut': args['NoUrut'],
                        'DetailID': args['DetailID']
                    }
                    update_record_detail = PendataanByOmzetDtl.UpdatePendataanDetail(data)
                    if update_record_detail:
                        return success_update({'SPT': select_query.SPT,
                                               'UPTID': select_query.UPTID,
                                               'OPDID': select_query.OPDID,
                                               'TarifPajak': select_query.TarifPajak})
                    else:
                        db.session.rollback()
                        return failed_update({})
                else:
                    db.session.rollback()
                    return failed_update({})
            else:
                return failed_update({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_update({})


class DeletePendataanSPTP(Resource):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege]}

    def delete(self, id, *args, **kwargs):
        try:
            delete_record_detail = PendataanByOmzetDtl.query.filter_by(DetailID=id)
            if delete_record_detail:
                spt = delete_record_detail.first().SPT
                check_detail = PendataanByOmzetDtl.query.filter_by(SPT=spt).all()
                print(len(check_detail))
                if len(check_detail) == 1:
                    delete_record_detail.delete()
                    check_header = PendataanByOmzet.query.filter_by(SPT=spt)
                    opdid = check_header.first().OPDID
                    select_query = db.session.execute(
                        f"UPDATE MsWP SET TglPendataan = NULL WHERE OPDID = {opdid}")
                    check_header.delete()
                    db.session.commit()
                    if check_header:
                        return success_delete({})
                    else:
                        db.session.rollback()
                        return failed_delete({})
                else:
                    delete_record_detail.delete()
                    db.session.commit()
                    return success_delete({})
            else:
                db.session.rollback()
                return failed_delete({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_delete({})

#######################################################################
#######################################################################

class PendataanSPTP(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):

        # PARSING PARAMETER DARI REQUEST
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('length', type=int)
        parser.add_argument('sort', type=str)
        parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
        parser.add_argument('search', type=str)
        parser.add_argument('search_jenis', type=str)

        args = parser.parse_args()
        UserId = kwargs['claim']["UserId"]

        result = []
        try:
            select_query = db.session.query(vw_obyekbadan.OBN, vw_obyekbadan.OPDID,
                                            vw_obyekbadan.ObyekBadanNo, vw_obyekbadan.NamaBadan,
                                            vw_obyekbadan.NamaJenisPendapatan,
                                            vw_obyekbadan.TglSah,
                                            case([(vw_obyekbadan.MasaPendapatan == 'B', 'Bulanan')]
                                                 ,
                                                 else_=''
                                                 ).label('Masa'),
                                            case([(vw_obyekbadan.TglData == None, 'Baru')]
                                                 ,
                                                 else_='Terdata'
                                                 ).label('Status'),
                                            vw_obyekbadan.Kecamatan) \
                .filter(
                vw_obyekbadan.TglHapus == None, vw_obyekbadan.SelfAssesment == 'Y', vw_obyekbadan.Insidentil == 'N'
            )

            # SEARCH_JENIS
            if args['search_jenis']:
                select_query = select_query.filter(
                    MsJenisPendapatan.JenisPendapatanID == args['search_jenis']
                )

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
                    sort = getattr(vw_obyekbadan, args['sort']).desc()
                else:
                    sort = getattr(vw_obyekbadan, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_obyekbadan.ObyekBadanNo)

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


class PendataanSPTPOmset(Resource):
    # method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, opdid, *args, **kwargs):

        # PARSING PARAMETER DARI REQUEST
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('length', type=int)
        parser.add_argument('sort', type=str)
        parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
        parser.add_argument('search', type=str)
        parser.add_argument('search_jenis', type=str)

        args = parser.parse_args()
        # UserId = kwargs['claim']["UserId"]

        result = []
        try:
            select_query = db.session.query(PendataanByOmzet.UPTID, PendataanByOmzet.MasaAwal,
                                            PendataanByOmzet.MasaAkhir, PendataanByOmzet.TglPendataan,
                                            case([(PenetapanByOmzet.TglPenetapan == None, 'Terdata')]
                                                 ,
                                                 else_='SPTP'
                                                 ).label('Validasi'),
                                            PendataanByOmzet.TarifPajak) \
                .join(PenetapanByOmzet, (PenetapanByOmzet.OPDID == PendataanByOmzet.OPDID) &
                      (PenetapanByOmzet.MasaAwal == PendataanByOmzet.MasaAwal) &
                      (PenetapanByOmzet.MasaAkhir == PendataanByOmzet.MasaAkhir) &
                      (PenetapanByOmzet.UrutTgl == PendataanByOmzet.UrutTgl), isouter=True) \
                .join(vw_obyekbadan, vw_obyekbadan.OPDID == PendataanByOmzet.OPDID) \
                .filter(
                PendataanByOmzet.OPDID == opdid
            )

            # # SEARCH_JENIS
            # if args['search_jenis']:
            #     select_query = select_query.filter(
            #         MsJenisPendapatan.JenisPendapatanID == args['search_jenis']
            #     )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_obyekbadan.NamaBadan.ilike(search),
                        vw_obyekbadan.ObyekBadanNo.ilike(search),
                        vw_obyekbadan.TglPendataan.ilike(search)
                        )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_obyekbadan, args['sort']).desc()
                else:
                    sort = getattr(vw_obyekbadan, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_obyekbadan.ObyekBadanNo)

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
                d['Jumlah'] = 0
                d['Lokasi'] = ''
            return success_reads_pagination(query_execute, result)
        except Exception as e:
            print(e)
            return failed_reads(result)