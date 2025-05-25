import json

from flask_restful import Resource, reqparse
from sqlalchemy import desc
from sqlalchemy.sql.elements import or_

from config.api_message import success_reads, failed_reads
from config.database import db
from config.helper import toDict
from controller.MsWPData import MsWPData
from controller.tblUser import tblUser
from controller.vw_obyekbadan import vw_obyekbadan


class search(Resource):
    # method_decorators = {'get': [tblUser.auth_apikey]}

    def get(self, *args, **kwargs):
        # PARSING PARAMETER DARI REQUEST
        parser = reqparse.RequestParser()
        parser.add_argument('query', type=str)
        args = parser.parse_args()
        result = []
        try:
            select_query = MsWPData.query.with_entities(MsWPData.NamaBadan, MsWPData.ObyekBadanNo, MsWPData.avatar)

            if args['query'] and len(args['query']) > 0 and args['query'] != 'null':
                search = '%{0}%'.format(args['query'])
                select_query = select_query.filter(
                    or_(MsWPData.NamaBadan.ilike(search),
                        MsWPData.ObyekBadanNo.ilike(search)),
                )

                select_query = select_query.distinct().group_by(MsWPData.NamaBadan, MsWPData.ObyekBadanNo, MsWPData.avatar).order_by(desc(MsWPData.NamaBadan)).limit(5)
                result_wp = {
                    'type': "wp",
                    'typename': "Wajib Pajak atau Usaha",
                    'items': [],
                }
                for row in select_query:
                    fields = {
                        'name': row.__getattribute__('NamaBadan'),
                        'wpid': row.__getattribute__('ObyekBadanNo'),
                        'avatar': row.__getattribute__('avatar'),
                    }
                    # for field in [x for x in dir(row) if not x.startswith('_') and x != 'metadata']:
                    #     data = row.__getattribute__(field)
                    #     try:
                    #         json.dumps(data)
                    #         fields[field] = data
                    #     except TypeError:
                    #         print(fields)
                    result_wp['items'].append(fields)
                result.append(result_wp)
            return success_reads(result)
        except Exception as e:
            print(e)
            return failed_reads({})