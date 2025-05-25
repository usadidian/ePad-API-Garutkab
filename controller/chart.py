from datetime import datetime

from flask_restful import Resource, reqparse

from config.api_message import success_reads, failed_reads
from config.database import db
from config.helper import logger
from controller.tblGroupUser import tblGroupUser
from controller.tblUser import tblUser

class piutang(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        uid = kwargs['claim']["UID"]
        # result = []
        try:
            args = parser.parse_args()
            date = datetime.now()
            tahun = date.strftime("%Y")
            print(tahun)
            select_query = db.session.execute(
                f"exec WS_REPORT_PAD_PIUTANG_CHART @thn='{tahun}'"
            )

            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    if key == 'TARGET' or key == 'REALISASI' or key == 'KETETAPAN' or key == 'REALSKP' or key == 'CAPAIAN' or key == 'PIUTANG':
                        d[key] = str(getattr(row, key))
                    else:
                        d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)
        except Exception as e:
            logger.error( e )
            return failed_reads( result )