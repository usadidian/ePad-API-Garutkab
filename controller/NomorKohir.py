from flask import jsonify
from flask_restful import Resource
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_delete, failed_delete
from config.database import db


class NomorKohir(db.Model, SerializerMixin):
    __tablename__ = 'NomorKohir'
    KohirID = db.Column(db.String, primary_key=True)
    #OPDID = db.Column(db.Integer, nullable=False)
    MasaAwal = db.Column(db.TIMESTAMP, nullable=False)
    MasaAkhir = db.Column(db.TIMESTAMP, nullable=False)
    TglPenetapan = db.Column(db.TIMESTAMP, nullable=False)
    Penagih = db.Column(db.String, nullable=True)
    #WPID = db.Column(db.Integer, nullable=True)
    TglKurangBayar = db.Column(db.TIMESTAMP, nullable=True)
    KohirKet = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    WPID = db.Column(db.Integer, db.ForeignKey('MsWPData.WPID'), nullable=False)

    def DeleteParent(data):
        try:
            kohirid = data['KohirID']
            print(kohirid)
            delete_record = NomorKohir.query.filter_by(KohirID=kohirid).first()
            delete_record.delete()
            db.session.commit()
            return success_delete({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_delete({})

    class ListAll(Resource):
        #method_decorators = [users.auth_apikey_privilege]
        def get(self):
            select_query = NomorKohir.query.order_by(NomorKohir.KohirID).paginate(1, 10)
            #result = [row.to_dict() for row in select_query]
            #return jsonify({'status_code': 1, 'message': 'OK', 'data': result})
            result = []
            for row in select_query.items:
                result.append(row.to_dict())
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

