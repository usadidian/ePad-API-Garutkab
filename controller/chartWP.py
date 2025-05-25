from datetime import datetime

from flask_restful import Resource, reqparse

from config.api_message import success_reads, failed_reads
from config.database import db
from config.helper import logger
from controller.tblGroupUser import tblGroupUser
from controller.tblUser import tblUser

class realWP(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        uid = kwargs['claim']["UID"]
        parser.add_argument( 'npwpd', type=str )
        try:
            args = parser.parse_args()
            npwpd = args['npwpd']

            select_query = db.session.execute(
                f"WS_GET_PAD_CHARTWPALL_VENDOR @NPWPD='{npwpd}'"
            )

            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    if key == 'Pembayaran':
                        d[key] = str(getattr(row, key))
                    else:
                        d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)
        except Exception as e:
            logger.error( e )
            return failed_reads( result )