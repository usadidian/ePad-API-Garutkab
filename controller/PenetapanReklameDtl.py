from flask import jsonify
from flask_restful import Resource
from sqlalchemy_serializer import SerializerMixin
from config.database import db


class PenetapanReklameDtl(db.Model, SerializerMixin):
    __tablename__ = 'PenetapanReklameDtl'
    #NoKohir = db.Column(db.String, primary_key=True)
    NoUrut = db.Column(db.Integer, primary_key=True)
    JudulReklame = db.Column(db.String, nullable=False)
    JenisLokasi = db.Column(db.String, nullable=False)
    LokasiID = db.Column(db.Integer, nullable=False)
    AlamatPasang = db.Column(db.String, nullable=True)
    LuasReklame = db.Column(db.Integer, nullable=False)
    PanjangReklame = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    LebarReklame = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    SudutPandang = db.Column(db.Integer, nullable=False)
    JumlahReklame = db.Column(db.Integer, nullable=False)
    TarifPajak = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    LKecamatan = db.Column(db.String, nullable=True)
    LKelurahan = db.Column(db.String, nullable=True)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    NoKohir = db.Column(db.String, db.ForeignKey('PenetapanReklameHdr.NoKohir'), primary_key=True, nullable=False)

    class ListAll(Resource):
        #method_decorators = [users.auth_apikey_privilege]
        def get(self):

            # select_query = PenetapanReklameDtl.query.all()
            # result = [row.to_dict() for row in select_query]
            # return jsonify({'status_code': 1, 'message': 'OK', 'data': result})
            select_query = PenetapanReklameDtl.query.order_by(PenetapanReklameDtl.NoKohir).paginate(1, 10)
            result = []
            for row in select_query.items:
                result.append(row.to_dict())
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

