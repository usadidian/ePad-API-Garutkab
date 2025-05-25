from flask import jsonify
from flask_restful import Resource
from sqlalchemy_serializer import SerializerMixin
from config.database import db


class GroupAttribute(db.Model, SerializerMixin):
    __tablename__ = 'GroupAttribute'
    GroupID = db.Column(db.Integer, primary_key=True)
    GroupName = db.Column(db.String, nullable=False)
    GroupDesc= db.Column(db.String, nullable=False)
    IsTarif = db.Column(db.String, nullable=False)


    class ListAll(Resource):
        #method_decorators = [users.auth_apikey_privilege]
        def get(self):
            select_query = GroupAttribute.query.order_by(GroupAttribute.GroupID).paginate(1, 10)
            #result = [row.to_dict() for row in select_query]
            #return jsonify({'status_code': 1, 'message': 'OK', 'data': result})
            result = []
            for row in select_query.items:
                result.append(row.to_dict())
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})
