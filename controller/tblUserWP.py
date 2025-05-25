from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination, failed_reads, success_reads
from config.database import db
from config.helper import logger, toDict
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsWP import MsWP
from controller.MsWPData import MsWPData
from controller.tblUser import tblUser
from controller.vw_userwp import vw_userwp
from controller.vw_userwp import vw_userwp


class tblUserWP(db.Model, SerializerMixin):
    __tablename__ = 'tblUserWP'
    UserId = db.Column(db.Integer, primary_key=True)
    UID = db.Column(db.String, nullable=False)
    WPID = db.Column(db.Integer, nullable=False)

    class ListAll(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            # parser = reqparse.RequestParser()
            # parser.add_argument('uid', type=str)

            # args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            result = []
            try:
                select_query = db.session.query(vw_userwp, vw_userwp.UID, vw_userwp.WPID, vw_userwp.ObyekBadanNo,
                                                vw_userwp.NamaBadan,
                                                vw_userwp.AlamatBadan, vw_userwp.Email, vw_userwp.TglPengesahan,
                                                vw_userwp.KodeRekening,
                                                vw_userwp.NamaJenisPendapatan)\
                    .filter(vw_userwp.UserId == UserId).first()
                    # .order_by(vw_userwp.DateUpd.desc()).all()


                if select_query:
                    data = toDict(select_query.vw_userwp)
                    select_obyekpajak = vw_userwp.query.filter_by(UserId=UserId).all()
                    ob = []
                    for row in select_obyekpajak:
                        ob.append({'KodeRekening': row.KodeRekening,
                                   'NamaJenisPendapatan': row.NamaJenisPendapatan}
                                  )
                    data.update({'ObyekPajak': ob})
                    return success_reads(data)
                else:
                    logger.error
                    return success_reads({})

            #     for row in select_query:
            #         d = {}
            #         for key in row.keys():
            #             d[key] = getattr(row, key)
            #         result.append(d)
            #     return success_reads(result)
            #
            # except Exception as e:
            #     print(e)
            #     return failed_reads(result)

            #     for row in select_query:
            #         d = {}
            #         for key in row.keys():
            #             d[key] = getattr(row, key)
            #         result.append(d)
            #     return success_reads(select_query, result)
            except Exception as e:
                logger.error(e)
                return failed_reads(result)