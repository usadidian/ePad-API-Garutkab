from flask import jsonify
from flask_restful import Resource
from sqlalchemy_serializer import SerializerMixin

from config.database import db


class PenetapanReklameHdr(db.Model, SerializerMixin):
    __tablename__ = 'PenetapanReklameHdr'
    PenetapanID = db.Column(db.Integer, nullable=False)
    NoKohir = db.Column(db.String,  primary_key=True)
    KohirID = db.Column(db.String, nullable=False)
    TglPenetapan = db.Column(db.TIMESTAMP, nullable=False)
    TglJatuhTempo = db.Column(db.TIMESTAMP, nullable=False)
    MasaAwal = db.Column(db.TIMESTAMP, nullable=False)
    MasaAkhir = db.Column(db.TIMESTAMP, nullable=False)
    UrutTgl = db.Column(db.Integer, nullable=False)
    TotalPajak = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    Denda = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    Kenaikan = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    IsPaid = db.Column(db.String, nullable=False)
    TglBayar = db.Column(db.TIMESTAMP, nullable=True)
    JmlBayar =db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    TglKurangBayar = db.Column(db.TIMESTAMP, nullable=True)
    JmlKurangBayar = db.Column(db.Numeric(12, 2), nullable=True)
    JmlPeringatan = db.Column(db.Integer, nullable=True)
    UPTID = db.Column(db.String, nullable=False)
    Status = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    OPDID = db.Column(db.Integer, db.ForeignKey('MsOPD.OPDID'), nullable=False)
    KohirID = db.Column(db.String, db.ForeignKey('NomorKohir.KohirID'), nullable=False)
    KodeStatus = db.Column(db.String, db.ForeignKey('MsJenisStatus.KodeStatus'), nullable=False)

    class ListAll(Resource):
        #method_decorators = [users.auth_apikey_privilege]
        def get(self):
            select_query = PenetapanReklameHdr.query.order_by(PenetapanReklameHdr.NoKohir).paginate(1, 10)
            #result = [row.to_dict() for row in select_query]
            #return jsonify({'status_code': 1, 'message': 'OK', 'data': result})
            result = []
            for row in select_query.items:
                result.append(row.to_dict())
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

