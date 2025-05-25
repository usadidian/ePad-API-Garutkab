from flask import jsonify
from flask_restful import Resource
from sqlalchemy_serializer import SerializerMixin

from config.database import db

class Endpoints(db.Model, SerializerMixin):
    # serialize_rules = ('-created_by', '-last_updated_by',)
    __tablename__ = 'endpoints'
    endpointsId = db.Column(db.Integer, primary_key=True)
    endpointsUrl = db.Column(db.String, nullable=False)
    endpointsName = db.Column(db.String, nullable=True)
