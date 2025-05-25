from flask import jsonify
from flask_restful import Resource
from sqlalchemy_serializer import SerializerMixin
from config.database import db

# READS
def success_reads(data):
    return jsonify({'status_code': 1, 'message': 'OK', 'data': data})

class MsSatuanOmzet(db.Model, SerializerMixin):
    __tablename__ = 'MsSatuanOmzet'
    OmzetID = db.Column(db.Integer, primary_key=True)
    SatuanOmzet = db.Column(db.String, nullable=False)
    TypeOmzet = db.Column(db.String, nullable=False)

    class ListAll(Resource):
        # method_decorators = [users.auth_apikey_privilege]
        def get(self):
            select_query = MsSatuanOmzet.query.order_by(MsSatuanOmzet.OmzetID).paginate(1, 10)
            # result = [row.to_dict() for row in select_query]
            # return jsonify({'status_code': 1, 'message': 'OK', 'data': result})
            result = []
            for row in select_query.items:
                result.append(row.to_dict())
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListAll2(Resource):
        def get(self):
            select_query = db.session.execute(
                f"SELECT mjp.JenisPendapatanID Kode, mjp.NamaJenisPendapatan Pendapatan, ga.GroupName "
                f"FROM MsJenisPendapatan AS mjp "
                f"INNER JOIN GroupAttribute AS ga ON ga.GroupID = mjp.GroupAttribute "
                f"INNER JOIN MsSatuanOmzet AS mso ON mso.OmzetID = mjp.OmzetID "
            )
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll3(Resource):
        def get(self):
            select_query = db.session.execute(
                f"SELECT OmzetID, SatuanOmzet FROM MsSatuanOmzet "
            )
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

