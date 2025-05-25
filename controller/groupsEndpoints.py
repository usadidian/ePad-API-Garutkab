from flask import jsonify
from flask_restful import Resource
from sqlalchemy_serializer import SerializerMixin

from config.database import db
from controller.endpoints import Endpoints
from controller.groups import groups


class GroupsEndpoints(db.Model, SerializerMixin):
    # serialize_rules = ('-created_by', '-last_updated_by',)
    __tablename__ = 'groupsEndpoints'
    groupsEndpointsId = db.Column(db.Integer, primary_key=True)
    endpointsId = db.Column(db.Integer, db.ForeignKey('Endpoints.endpointsId'), nullable=False)
    groupsId = db.Column(db.Integer, db.ForeignKey('groups.groupsId'), nullable=False)
    groupsEndpointsGet = db.Column(db.Boolean, nullable=True)
    groupsEndpointsPost = db.Column(db.Boolean, nullable=True)
    groupsEndpointsPut = db.Column(db.Boolean, nullable=True)
    groupsEndpointsDel = db.Column(db.Boolean, nullable=True)

