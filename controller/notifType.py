from flask import jsonify
from flask_restful import Resource
from sqlalchemy_serializer import SerializerMixin
from datetime import timedelta, datetime
from config.database import db


class NotifType(db.Model, SerializerMixin):
    # serialize_rules = ()
    __tablename__ = 'notifType'
    notifTypeId = db.Column(db.Integer, primary_key=True)
    notifTypeName = db.Column(db.String, nullable=True)
    notifTypeIcon = db.Column(db.String, nullable=True)
    notifTypeImg = db.Column(db.String, nullable=True)
    notifTypeTitle = db.Column(db.String, nullable=True)
    notifTypeBody = db.Column(db.String, nullable=True)
