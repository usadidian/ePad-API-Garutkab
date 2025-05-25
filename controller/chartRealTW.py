from datetime import datetime

from flask_restful import Resource, reqparse

from config.api_message import success_reads, failed_reads
from config.database import db
from config.helper import logger
from controller.tblGroupUser import tblGroupUser
from controller.tblUser import tblUser

class realTW(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        uid = kwargs['claim']["UID"]
        try:
            args = parser.parse_args()

            select_query = db.session.execute(
                f"WS_REPORT_PAD_PEMBAYARAN_TRIWULAN_CHART"
            )

            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    if key == 'TW1' or key == 'TW2' or key == 'TW3' or key == 'TW4':
                        d[key] = str(getattr(row, key))
                    else:
                        d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)
        except Exception as e:
            logger.error( e )
            return failed_reads( result )