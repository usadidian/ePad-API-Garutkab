from flask import jsonify
from flask_restful import Resource
from sqlalchemy_serializer import SerializerMixin

from config.database import db
from controller.users import users


class test(db.Model, SerializerMixin):
    __tablename__ = 'MsBank'
    BankId = db.Column(db.String, primary_key=True)
    Bank = db.Column(db.String, nullable=False)


    class ListAll(Resource):
        #method_decorators = [users.auth_apikey_privilege]
        def get(self):
            select_query = test.query.all()
            result = [row.to_dict() for row in select_query]
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})
