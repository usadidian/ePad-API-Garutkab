from flask import jsonify
from flask_restful import Resource
from sqlalchemy_serializer import SerializerMixin

from config.database import db


class units(db.Model, SerializerMixin):
    serialize_rules = ('-unitsId',)
    __tablename__ = 'units'
    unitsId = db.Column(db.Integer, primary_key=True)
    unitsName = db.Column(db.String, nullable=False)
    unitsLogo = db.Column(db.String, nullable=True)
    unitsSignature1Title = db.Column(db.String, nullable=True)
    unitsSignature1Img = db.Column(db.String, nullable=True)
    unitsSignature1Name = db.Column(db.String, nullable=True)
    unitsSignature1Code = db.Column(db.String, nullable=True)
