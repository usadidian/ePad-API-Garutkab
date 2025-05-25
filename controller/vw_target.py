from datetime import datetime

from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, failed_reads, success_create
from config.database import db
from controller.tblUser import tblUser


class vw_target(db.Model, SerializerMixin):
    __bind_key__ = 'transaksi'
    __tablename__ = 'vw_target'
    TargetID = db.Column(db.Integer, primary_key=True)
    JenisPendapatanID = db.Column(db.String, nullable=False)
    KodeRekening = db.Column(db.String, nullable=False)
    NamaJenisPendapatan = db.Column(db.String, nullable=False)
    TahunPendapatan = db.Column(db.String, nullable=False)
    TargetPendapatan= db.Column(db.Numeric(precision=16, asdecimal=False, decimal_return_scale=None), nullable=True)
    DateUpd = db.Column(db.TIMESTAMP, nullable=True)

