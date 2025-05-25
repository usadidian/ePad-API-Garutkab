from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads, failed_reads
from config.database import db
from controller.tblUser import tblUser


class MsMapOpsen(db.Model, SerializerMixin):
    __tablename__ = 'MsMapOpsen'
    id = db.Column(db.Integer, primary_key=True)
    JPID = db.Column(db.String, nullable=False)
    JPIDOpsen = db.Column(db.String, nullable=False)
   

