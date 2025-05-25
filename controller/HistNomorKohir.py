from flask import jsonify
from flask_restful import Resource
from sqlalchemy_serializer import SerializerMixin

from config.database import db


class HistNomorKohir(db.Model, SerializerMixin):
    __tablename__ = 'HistNomorKohir'
    HistoryID = db.Column(db.Integer, primary_key=True)
    KohirID = db.Column(db.String, nullable=False)
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
    UserUpdHist = db.Column(db.String, nullable=False)
    DateUpdHist = db.Column(db.TIMESTAMP, nullable=False)
    SKHapus = db.Column(db.String, nullable=False)
    TglSKHapus = db.Column(db.TIMESTAMP, nullable=False)

    WPID = db.Column(db.Integer, db.ForeignKey('MsWPData.WPID'), nullable=False)


    class ListAll(Resource):
        #method_decorators = [users.auth_apikey_privilege]
        def get(self):
            select_query = HistNomorKohir.query.order_by(HistNomorKohir.KohirID).paginate(1, 10)
            #result = [row.to_dict() for row in select_query]
            #return jsonify({'status_code': 1, 'message': 'OK', 'data': result})
            result = []
            for row in select_query.items:
                result.append(row.to_dict())
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

