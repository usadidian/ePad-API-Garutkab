from datetime import datetime

from flask_restful import Resource, reqparse

from config.api_message import success_reads, failed_reads
from config.database import db
from config.helper import logger
from controller.tblGroupUser import tblGroupUser
from controller.tblUser import tblUser

class realbulan(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        uid = kwargs['claim']["UID"]
        try:
            args = parser.parse_args()

            select_query = db.session.execute(
                f"exec WS_REPORT_PAD_PEMBAYARAN_BULAN_CHART"
            )

            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    if key == 'JAN' or key == 'FEB' or key == 'MAR' or key == 'APR' or key == 'MEI' or key == 'JUN' \
                    or key == 'JUL' or key == 'AGT' or key == 'SEPT' or key == 'OKT' or key == 'NOV' or key == 'DES':
                        d[key] = str(getattr(row, key))
                    else:
                        d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)
        except Exception as e:
            logger.error( e )
            return failed_reads( result )