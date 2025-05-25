from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask_restful import Resource
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

class ApiPemda(db.Model, SerializerMixin):
    __tablename__ = 'ApiPemda'

    ApiPemdaId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    KodePemda = db.Column(db.String(10), nullable=True)
    UrlId = db.Column(db.Integer, db.ForeignKey('ApiUrl.UrlId'), unique=True, nullable=True)

    # Relasi One-to-One ke ApiUrl
    url = db.relationship('ApiUrl', back_populates='pemda')

    def __repr__(self):
        return f"<ApiPemda(ApiPemdaId={self.ApiPemdaId}, KodePemda='{self.KodePemda}', UrlId={self.UrlId})>"


class ApiPemdaList(Resource):
    def get(self):
        data = ApiPemda.query.all()
        result = []
        for item in data:
            result.append({
                'ApiPemdaId': item.ApiPemdaId,
                'KodePemda': item.KodePemda,
                'UrlId': item.UrlId,
                'Url': item.url.Url if item.url else None,
                'Keterangan': item.url.Keterangan if item.url else None
            })
        return {'status_code': 1, 'message': 'OK', 'data': result}, 200

    def post(self):
        json_data = request.get_json()
        kode_pemda = json_data.get('KodePemda')
        url_id = json_data.get('UrlId')

        new_pemda = ApiPemda(KodePemda=kode_pemda, UrlId=url_id)
        db.session.add(new_pemda)
        db.session.commit()

        return {'status_code': 1, 'message': 'ApiPemda created'}, 201


class ApiPemdaDetail(Resource):
    def get(self, id):
        pemda = ApiPemda.query.get_or_404(id)
        return {
            'ApiPemdaId': pemda.ApiPemdaId,
            'KodePemda': pemda.KodePemda,
            'UrlId': pemda.UrlId,
            'Url': pemda.url.Url if pemda.url else None,
            'Keterangan': pemda.url.Keterangan if pemda.url else None
        }, 200

    def put(self, id):
        pemda = ApiPemda.query.get_or_404(id)
        json_data = request.get_json()
        pemda.KodePemda = json_data.get('KodePemda', pemda.KodePemda)
        pemda.UrlId = json_data.get('UrlId', pemda.UrlId)
        db.session.commit()
        return {'status_code': 1, 'message': 'ApiPemda updated'}, 200

    def delete(self, id):
        pemda = ApiPemda.query.get_or_404(id)
        db.session.delete(pemda)
        db.session.commit()
        return {'status_code': 1, 'message': 'ApiPemda deleted'}, 200

class ApiPemdaLookup(Resource):
    def get(self):
        data = ApiPemda.query.all()
        result = [
            {
                'ApiPemdaId': row.ApiPemdaId,
                'KodePemda': row.KodePemda,
                'UrlId': row.UrlId
            }
            for row in data
        ]
        return {'status_code': 1, 'message': 'OK', 'data': result}, 200