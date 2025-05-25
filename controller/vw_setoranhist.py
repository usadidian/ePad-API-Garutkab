from datetime import datetime, timedelta, date

from flask import request, jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import func, cast, Date, extract
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination
from config.database import db
from controller.vw_target import vw_target
from controller.vw_target import vw_target
from controller.tblUser import tblUser


class vw_setoranhist(db.Model, SerializerMixin):
    __bind_key__ = 'transaksi'
    __tablename__ = 'vw_setoranhist'
    ObyekBadanID = db.Column(db.Integer, primary_key=True)
    OBN = db.Column( db.String, nullable=True )
    ObyekBadanNo = db.Column( db.String, nullable=True )
    UsahaBadan = db.Column( db.String, nullable=True )
    NamaBadan = db.Column( db.String, nullable=True )
    TglJatuhTempo = db.Column( db.TIMESTAMP, nullable=False )
    StatusBayar = db.Column( db.String, nullable=False )
    NoKohir = db.Column( db.String, nullable=False )
    KohirID = db.Column( db.String, nullable=False )
    STS = db.Column( db.String, nullable=True )
    KodeBayar = db.Column( db.String, nullable=True )
    Dinas = db.Column( db.String, nullable=True )
    NTPD = db.Column(db.String, nullable=True)
    SKPOwner = db.Column(db.String, nullable=True)
    TglNTPD = db.Column(db.TIMESTAMP, nullable=False)
    NamaPemilik = db.Column( db.String, nullable=True )
    AlamatPemilik = db.Column( db.String, nullable=True )
    AlamatBadan = db.Column( db.String, nullable=True )
    MasaAwal = db.Column( db.TIMESTAMP, nullable=False )
    MasaAkhir = db.Column( db.TIMESTAMP, nullable=False )
    TglPenetapan = db.Column( db.TIMESTAMP, nullable=False )
    Pajak = db.Column( db.Numeric( precision=8, asdecimal=False, decimal_return_scale=None ), nullable=True )
    Denda = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    JmlBayar = db.Column( db.Numeric( precision=8, asdecimal=False, decimal_return_scale=None ), nullable=True )
    JmlKurangBayar = db.Column( db.Numeric( precision=8, asdecimal=False, decimal_return_scale=None ), nullable=True )
    JmlBayarDenda = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    HarusBayar = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    Kenaikan = db.Column( db.Numeric( precision=8, asdecimal=False, decimal_return_scale=None ), nullable=True )
    JenisPendapatanID = db.Column(db.String, nullable=True)
    NamaJenisPendapatan = db.Column(db.String, nullable=True)
    SetoranHistID = db.Column( db.Integer, nullable=True )
    NoSSPD = db.Column( db.String, nullable=False )
    TglBayar = db.Column( db.TIMESTAMP, nullable=True )
    KodeRekening = db.Column(db.String, nullable=True)
    Insidentil = db.Column( db.String, nullable=False )
    SelfAssesment = db.Column( db.String, nullable=False )
    OmzetBase = db.Column(db.String, nullable=False)
    UPTID = db.Column( db.String, nullable=True )
    UPT = db.Column( db.String, nullable=True )
    IsPaid = db.Column( db.String, nullable=True )
    JatuhTempo = db.Column( db.String, nullable=True )
    DateUpd = db.Column(db.TIMESTAMP, nullable=True)

