from flask_restful import Resource

from config.api_message import success_reads, failed_reads
from config.database import db
from config.helper import logger
from controller.tblGroupUser import tblGroupUser
from controller.tblUser import tblUser


class DataAkhir(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}
    def get(self, *args, **kwargs):
        result = []
        try:
            groupid = kwargs['claim']["GroupId"]
            checkadmin = tblGroupUser.query.filter_by(
                        GroupId=groupid
                    ).first()
            # print(checkadmin)
            if checkadmin.IsAdmin == 1 or checkadmin.IsExecutive == 1:
                select_query = db.session.execute(
                    f"exec SP_DATA_AKHIR @user='ADM'"
                )
                result = []
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr( row, key )
                    result.append( d )
                return success_reads( result )
        except Exception as e:
            logger.error( e )
            return failed_reads( result )