from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import func

from config.api_message import success_reads, failed_reads, failed_create, success_create
from config.database import db
from config.helper import logger, toDict
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsWP import MsWP
from controller.MsWPData import MsWPData
from controller.MsWPOData import MsWPOData
from controller.Pembayaran import Pembayaran
from controller.tblUser import tblUser
from controller.tblUserWP import tblUserWP


def getListUsaha(userid, internal=False):
    result = []
    try:
        select_query = MsWPData.query.join(tblUserWP, tblUserWP.WPID == MsWPData.WPID) \
            .filter(tblUserWP.UserId == userid).all()
        if internal:
            return select_query

        for row in select_query:
            # newRow = toDict(row)
            newRow = {
                'ObyekBadanNo': row.ObyekBadanNo,
                'WPID': row.WPID,
                'NamaBadan': row.NamaBadan,
                'avatar': row.avatar,
                'AlamatBadan': row.AlamatBadan,
                'NamaPemilik': row.NamaPemilik,
                'subscriptions': getSubscription(row.ObyekBadanNo),
                'active': True
            }
            result.append(newRow)
        return result
    except Exception as e:
        logger.error(e)
        return result


def getUsaha(npwpd):
    result = []
    try:
        select_query = MsWPData.query.filter_by(ObyekBadanNo=npwpd).first()
        # if internal:
        #     return select_query

        # for row in select_query:
        #     newRow = toDict(row)
        #     # newRow = {
        #     #     'ObyekBadanNo': row.ObyekBadanNo,
        #     #     'NamaBadan': row.NamaBadan,
        #     #     'avatar': row.avatar,
        #     #     'AlamatBadan': row.AlamatBadan,
        #     #     'NamaPemilik': row.NamaPemilik,
        #     #     'subscriptions': getSubscription(row.ObyekBadanNo),
        #     #     'active': True
        #     # }
        #     result.append(newRow)
        return select_query
    except Exception as e:
        logger.error(e)
        return result


def getUsahaInquiry(npwpd):
    result = {}
    try:
        # if not (select_query := MsWPData.query.filter_by(ObyekBadanNo=npwpd).first()):
        #     return result
        # newRow = {
        #         'NamaBadan': select_query.NamaBadan,
        #         'avatar': select_query.avatar,
        #         'NamaPemilik': select_query.NamaPemilik,
        #     }
        # return newRow

        select_query = db.session.execute(
            f"SELECT nama_user, left(nama_user, charindex(' - ', nama_user)) AS ObyekBadanNo, "
            f"right(nama_user, len(nama_user) - charindex(' - ', nama_user) - 2) AS NamaBadan "
            f"from tblUser where code_group = 'WP'"
            f"AND left(nama_user, charindex(' - ', nama_user)) = '{npwpd}';").first()
        # print(select_query[2])
        if not select_query:
            return result
        newRow = {
                'NamaBadan': select_query[2],
                'avatar': "",
                'NamaPemilik': select_query[1],
            }
        return newRow
    except Exception as e:
        logger.error(e)
        return result


def getListUsahaAwait(userid, internal=False):
    result = []
    try:
        select_query = MsWPOData.query.filter(MsWPOData.UserUpd == f'{userid}').all()
        if internal:
            return select_query

        for row in select_query:
            # newRow = toDict(row)
            # print(toDict(row))
            newRow = {
                'NamaBadan': row.NamaBadan,
                'avatar': row.avatar,
                'AlamatBadan': row.AlamatBadan,
                'NamaPemilik': row.NamaPemilik,
                'DateUpd': row.DateUpd.strftime("%Y-%m-%d %H:%M"),
                'active': False,
            }
            result.append(newRow)
        return result
    except Exception as e:
        logger.error(e)
        return result


class GetListUsaha(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):

        result = []
        try:
            UserId = kwargs['claim']["UserId"]
            result = getListUsaha(UserId)
            resultAwait = getListUsahaAwait(UserId)
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result, 'data_await': resultAwait})
        except Exception as e:
            logger.error(e)
            return failed_reads(result)


class GetUsaha(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, npwpd, *args, **kwargs):
        try:
            UserId = kwargs['claim']["UserId"]
            # wpid = MsWPData.query.filter_by(ObyekBadanNo=npwpd).first().WPID
            # select_query = MsWPData.query.join(tblUserWP, tblUserWP.WPID == MsWPData.WPID) \
            #     .filter(tblUserWP.UserId == UserId, tblUserWP.WPID == wpid).first()
            select_query = getUsaha(npwpd)
            newRow = toDict(select_query)
            newRow['subscriptions'] = getSubscription(npwpd)
            # newRow = {
            #     'subscriptions': getSubscription(npwpd)
            # }
            return success_reads(newRow)
        except Exception as e:
            logger.error(e)
            return failed_reads({})


class GetUsahaLookup(Resource):
    method_decorators = {'post': [tblUser.auth_apikey]}

    def post(self, npwpd, *args, **kwargs):
        try:
            UserId = kwargs['claim']["UserId"]
            data = getUsahaInquiry(npwpd)
            return success_reads(data)
        except Exception as e:
            logger.error(e)
            return failed_reads({})


class AddUsahaFromOldWPO(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, npwpd, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('pass', type=str, required=True)
        args = parser.parse_args()
        result = {}
        try:
            password = args['pass']
            select_query = db.session.execute(
                f"SELECT nama_user, left(nama_user, charindex(' - ', nama_user)) AS ObyekBadanNo, "
                f"right(nama_user, len(nama_user) - charindex(' - ', nama_user) - 2) AS NamaBadan "
                f"from tblUser where code_group = 'WP'"
                f"AND left(nama_user, charindex(' - ', nama_user)) = '{npwpd}' "
                f"AND password = '{password}';"
            ).first()
            if not select_query:
                return result, 500
            data = {
                'NamaBadan': select_query.NamaBadan,
            }
            return success_create(data)
        except Exception as e:
            logger.error(e)
            return failed_create({})


def getSubscription(npwpd, internal=False):
    result = []
    try:
        wpid = MsWPData.query.filter_by(ObyekBadanNo=npwpd).first().WPID
        select_query = db.session.query(MsJenisPendapatan, MsWP).join(MsWP, MsWP.UsahaBadan == MsJenisPendapatan.JenisPendapatanID) \
            .filter(MsWP.WPID == wpid).order_by(MsJenisPendapatan.NamaJenisPendapatan).all()
        if internal:
            return select_query
        for row in select_query:
            newRow = {
                'NamaJenisPendapatan': row.MsJenisPendapatan.NamaJenisPendapatan,
                'KodeRekening': row.MsJenisPendapatan.KodeRekening,
                'img': row.MsJenisPendapatan.img,
                'icon': row.MsJenisPendapatan.icon,
                'OPDID': row.MsWP.OPDID,
                'JenisPendapatanID': row.MsJenisPendapatan.JenisPendapatanID,
                'OmzetBase': row.MsJenisPendapatan.OmzetBase,
                # 'LKecamatan': row.MsWP.LKecamatan,
                # 'LKelurahan': row.MsWP.LKelurahan,
                # 'LokasiID': row.MsWP.LokasiID
            }
            result.append(newRow)
        return result
    except Exception as e:
        logger.error(e)
        return None


class GetSubscription(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, npwpd, *args, **kwargs):
        result = []
        try:
            result = getSubscription(npwpd)
            if result:
                return success_reads(result)
            else:
                return failed_reads(result)
        except Exception as e:
            logger.error(e)
            return failed_reads(result)


class GetAllBill(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        result = []
        try:
            UserId = kwargs['claim']["UserId"]
            # get usaha by userid
            get_list_usaha = getListUsaha(UserId, True)
            list_of_subscription = []
            list_of_subscription_extra = []
            for row in get_list_usaha:
                # get objekbadanid by ObjekBadanNo
                subscriptions = getSubscription(row.ObyekBadanNo, True)
                for subs in subscriptions:
                    list_of_subscription.append(subs.MsWP.OPDID)
                    list_of_subscription_extra.append(
                        (subs.MsWP.OPDID, {
                            'img': subs.MsJenisPendapatan.img,
                            'icon': subs.MsJenisPendapatan.icon
                        })
                    )
            billData = Pembayaran.query.filter(Pembayaran.OPDID.in_(list_of_subscription)).all()
                # filter(Pembayaran.OPDID.in_(list_of_subscription),
                #        Pembayaran.StatusBayar != 'Lunas').all()

            for rowBill in billData:

                # print(tuple(list_of_subscription_extra)[rowBill.OPDID][1])
                newRow = toDict(rowBill)
                newRow['avatar'] = newRow['avatar'].strip() if newRow['avatar'] else ""
                newRow['img'] = dict(list_of_subscription_extra)[rowBill.OPDID]['img']
                newRow['icon'] = dict(list_of_subscription_extra)[rowBill.OPDID]['icon']
                # newRow = {
                #     'ObyekBadanNo': rowBill.ObyekBadanNo,
                #     'NamaBadan': rowBill.NamaBadan,
                #     'avatar': rowBill.avatar,
                #     'AlamatBadan': rowBill.AlamatBadan,
                #     'KohirID': rowBill.KohirID,
                #     'MasaAwal': rowBill.MasaAwal,
                #     'MasaAkhir': rowBill.MasaAkhir,
                #     'TglJatuhTempo': rowBill.TglJatuhTempo,
                #     'Kenaikan': rowBill.Kenaikan,
                #     'JmlKurangBayar': rowBill.JmlKurangBayar,
                #     'Denda': rowBill.Denda,
                #     'NamaJenisPendapatan': rowBill.NamaJenisPendapatan,
                #     'KodeRekening': rowBill.KodeRekening,
                #     'StatusBayar': rowBill.StatusBayar,
                #     'Pajak': rowBill.Pajak,
                #     'img': dict(list_of_subscription_extra)[rowBill.OPDID]['img'],
                #     'icon': dict(list_of_subscription_extra)[rowBill.OPDID]['icon']
                # }
                result.append(newRow)
            return success_reads(result)
        except Exception as e:
            logger.error(e)
            return failed_reads(result)