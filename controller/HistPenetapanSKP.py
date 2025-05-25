from datetime import datetime

from flask_restful import Resource, reqparse
from sqlalchemy import case
from sqlalchemy import or_
from config.api_message import success_reads_pagination, failed_reads, success_update, failed_update
from config.database import db
from config.helper import logger
from controller.HistNomorKohir import HistNomorKohir
from controller.HistPenetapanByOmzet import HistPenetapanByOmzet
from controller.HistPenetapanReklameHdr import HistPenetapanReklameHdr
from controller.MsPegawai import MsPegawai
from controller.tblGroupUser import tblGroupUser
from controller.tblUser import tblUser
from controller.vw_hist_penetapan import vw_hist_penetapan


class HistPenetapanSKP(Resource):
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
        parser.add_argument( 'kategori', type=str, choices=('true', 'false'), help='diisi dengan true atau false' )
        parser.add_argument( 'nonwp', type=str, choices=('true', 'false'), help='diisi dengan true atau false' )

        args = parser.parse_args()
        UserId = kwargs['claim']["UserId"]
        # uptid=''
        groupid = kwargs['claim']["GroupId"]

        result = []
        try:

            select_query = db.session.query(vw_hist_penetapan.HistoryID, vw_hist_penetapan.OBN, vw_hist_penetapan.UPTID,
                                            vw_hist_penetapan.OPDID, vw_hist_penetapan.ObyekBadanNo,
                                            vw_hist_penetapan.TglJatuhTempo,
                                            vw_hist_penetapan.NamaBadan, vw_hist_penetapan.KohirID,
                                            vw_hist_penetapan.NamaBadan,
                                            vw_hist_penetapan.NamaPemilik,
                                            vw_hist_penetapan.AlamatBadan, vw_hist_penetapan.KodeRekening,
                                            vw_hist_penetapan.MasaAwal, vw_hist_penetapan.MasaAkhir,
                                            vw_hist_penetapan.NamaJenisPendapatan, vw_hist_penetapan.JenisPendapatanID,
                                            vw_hist_penetapan.Pajak, vw_hist_penetapan.Denda,
                                            vw_hist_penetapan.TglPenetapan, vw_hist_penetapan.Insidentil,
                                            vw_hist_penetapan.UPT,
                                            vw_hist_penetapan.Kenaikan, vw_hist_penetapan.TglKurangBayar,
                                            vw_hist_penetapan.DateUpd, vw_hist_penetapan.SelfAssesment,
                                            vw_hist_penetapan.StatusBayar, vw_hist_penetapan.OmzetBase,
                                            vw_hist_penetapan.UrutTgl, vw_hist_penetapan.NoSKHapus, vw_hist_penetapan.TglSKHapus,
                                            vw_hist_penetapan.UserUpdHist,vw_hist_penetapan.DateUpdHist, vw_hist_penetapan.avatar,
                                            case([(vw_hist_penetapan.SelfAssesment == 'Y', 'SPTP')],
                                                 else_='SKP'
                                                 ).label('Kategori')
                                            )
            checkadmin = tblGroupUser.query.filter_by(
                GroupId=groupid
            ).first()

            checkwp = tblGroupUser.query.filter_by(
                GroupId=groupid
            ).first()

            if checkadmin.IsAdmin != 1 and checkwp.IsWP != 1:
                PegawaiID = kwargs['claim']["PegawaiID"]
                uptid = ''
                if PegawaiID:
                    select_query_uptid = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
                        tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
                    result = select_query_uptid[0]
                    uptid = result
                    print(uptid)
                select_query = select_query.filter(
                    vw_hist_penetapan.SKPOwner == uptid
                )

            if checkwp.IsWP == 1:
                ObyekBadanNo = kwargs['claim']["ObyekBadanNo"]
                select_query = select_query.filter(
                    vw_hist_penetapan.ObyekBadanNo == ObyekBadanNo
                )

            # kategori
            if  args['kategori'] == "true":
                select_query = select_query.filter( vw_hist_penetapan.SelfAssesment == 'Y' )
            else:
                select_query = select_query.filter( vw_hist_penetapan.SelfAssesment == 'N' )

            # nonwp
            if  args['nonwp'] == "true":
                select_query = select_query.filter( vw_hist_penetapan.Insidentil == 'Y' )
            else:
                select_query = select_query.filter( vw_hist_penetapan.Insidentil == 'N' )

            # filter_jenis
            if args['filter_jenis']:
                select_query = select_query.filter(
                    vw_hist_penetapan.JenisPendapatanID == args['filter_jenis']
                )


            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_hist_penetapan.NamaBadan.ilike(search),
                        vw_hist_penetapan.ObyekBadanNo.ilike(search),
                        vw_hist_penetapan.NamaPemilik.ilike(search)
                        )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_hist_penetapan, args['sort']).desc()
                else:
                    sort = getattr(vw_hist_penetapan, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_hist_penetapan.DateUpdHist.desc())

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            # result = []
            # for row in query_execute.items:
            #     result.append(row.to_dict())
            # return success_reads_pagination(query_execute, result)

            for row in query_execute.items:
                d = {}
                for key in row.keys():
                    d[key] = str(getattr(row, key))
                result.append(d)
            return success_reads_pagination(query_execute, result)
        except Exception as e:
            logger.error(e)
            return failed_reads(result)

class UpdateHistPenetapanSKP(Resource):
    method_decorators = {'put': [tblUser.auth_apikey_privilege]}

    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        print(kwargs['claim'])
        parser.add_argument('OmzetBase', type=str)
        parser.add_argument('NoSKHapus', type=str)
        parser.add_argument('TglSKHapus', type=str)


        args = parser.parse_args()
        uid = kwargs['claim']["UID"]
        try:
            if args['OmzetBase'] == 'Y':
                select_query = HistPenetapanByOmzet.query.filter_by(HistoryID=id).first()
            else:
                select_query = HistPenetapanReklameHdr.query.filter_by(HistoryID=id).first()
            if select_query:
                if args['NoSKHapus']:
                    select_query.UserUpdHist = uid
                    select_query.DateUpdHist = datetime.now()
                if args['TglSKHapus']:
                    select_query.UserUpdHist = uid
                    select_query.DateUpdHist = datetime.now()
                db.session.commit()

            if select_query.KohirID:
                kohirid = select_query.KohirID
                query = HistNomorKohir.query.filter_by(KohirID=kohirid).first()
                if query:
                    if args['NoSKHapus']:
                        query.SKHapus = args['NoSKHapus']
                    if args['TglSKHapus']:
                        query.TglSKHapus = args['TglSKHapus']
                    query.UserUpdHist = uid
                    query.DateUpdHist = datetime.now()
                    db.session.commit()
            return success_update({'KohirID': select_query.KohirID,
                                   'UPTID': select_query.UPTID,
                                   'NoSKHapus': query.SKHapus,
                                   'TglSKHapus': query.TglSKHapus,
                                   'UserUpdHist': select_query.UserUpdHist})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_update({})


