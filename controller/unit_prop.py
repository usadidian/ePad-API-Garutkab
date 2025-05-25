import json

from flask import jsonify, request
from flask_restful import Resource

from config.helper import logger


def getUnitMapper(origin=None):
    result = {}
    try:
        id = origin.replace('http://', '').replace('https://', '') if origin else ''
        f = open('unit_mapper.json')
        # logger.info(f)
        data = json.load(f)
        # logger.info(data)
        f.close()
        empty = {}
        for i in data:
            if i['id'] == '':
                empty = i['attributes']
            if id == i['id']:
                result = i['attributes']
                break
        if not result:
            result = empty
        # logger.info(result)
        return result
    except Exception as e:
        logger.error(e)
        return result



class GetDomainProp(Resource):
    def post(self, *args, **kwargs):
        origin = request.origin
        # logger.info(origin)
        result = getUnitMapper(origin)
        # logger.info(result)
        return jsonify({'status_code': 1, 'message': 'OK', 'data': result})