from flask import jsonify
from flask_restful import Resource
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads
from config.database import db


class MsLokasiKhusus(db.Model, SerializerMixin):
    __tablename__ = 'MsLokasiKhusus'
    LokasiID = db.Column(db.String, primary_key=True)
    Lokasi = db.Column(db.String, nullable=False)
    Insidentil= db.Column(db.String, nullable=False)
    Laporan = db.Column(db.String, nullable=False)

    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT LokasiID AS KhususID, Lokasi AS Khusus FROM MsLokasiKhusus WHERE Insidentil = 'N' "
                f"ORDER BY LokasiID ")
            result=[]
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll(Resource):
        #method_decorators = [users.auth_apikey_privilege]
        def get(self):
            select_query = MsLokasiKhusus.query.order_by(MsLokasiKhusus.LokasiID).paginate(1, 10)
            #result = [row.to_dict() for row in select_query]
            #return jsonify({'status_code': 1, 'message': 'OK', 'data': result})
            result = []
            for row in select_query.items:
                result.append(row.to_dict())
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})
