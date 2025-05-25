from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, failed_reads
from config.database import db


class tblGroupUser(db.Model, SerializerMixin):
    __tablename__ = 'tblGroupUser'
    GroupId = db.Column(db.Integer, primary_key=True)
    code_group = db.Column(db.String, nullable=False)
    nama_group = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    level_group = db.Column(db.String, nullable=True)
    IsAdmin = db.Column(db.Integer, nullable=True)
    IsWP = db.Column(db.Integer, nullable=True)
    IsPendaftaran = db.Column(db.Integer, nullable=True)
    IsPendataan = db.Column(db.Integer, nullable=True)
    IsPenetapan = db.Column(db.Integer, nullable=True)
    IsPembayaran = db.Column(db.Integer, nullable=True)
    IsPenyetoran = db.Column(db.Integer, nullable=True)
    IsExecutive = db.Column(db.Integer, nullable=True)
    IsIntegrasi = db.Column(db.Integer, nullable=True)
    UserUpd = db.Column(db.String, nullable=True)
    DateUpd = db.Column(db.TIMESTAMP, nullable=True)

    def to_dict(self):
        return {
            'GroupId': self.GroupId,
            'code_group': self.code_group,
            'nama_group': self.nama_group,
            'description': self.description,
            'level_group': self.level_group,
            'IsAdmin': self.IsAdmin,
            'IsWP': self.IsWP,
            'IsPendaftaran': self.IsPendaftaran,
            'IsPendataan': self.IsPendataan,
            'IsPenetapan': self.IsPenetapan,
            'IsPembayaran': self.IsPembayaran,
            'IsPenyetoran': self.IsPenyetoran,
            'IsExecutive': self.IsExecutive,
            'IsIntegrasi': self.IsExecutive,
            'UserUpd': self.UserUpd,
            'DateUpd': self.DateUpd.strftime('%Y-%m-%d %H:%M:%S') if self.DateUpd else None
        }
    # users = db.relationship("tblUser", backref="groups", lazy="dynamic")