from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()


class vw_pelaporanomzet(db.Model):
    __tablename__ = 'vw_pelaporanomzet'
    __table_args__ = {'extend_existing': True}  # Prevent duplicate table creation
    PelaporanID = db.Column(db.Integer, primary_key=True)
    WapuID = db.Column(db.Integer)
    UPTID = db.Column(db.Integer)
    SPT = db.Column(db.String(50))
    MasaAwal = db.Column(db.DateTime)
    MasaAkhir = db.Column(db.DateTime)
    DetailID = db.Column(db.Integer)
    AlamatPemilik = db.Column(db.String)
    KodeRekening = db.Column(db.String(50))
    NamaJenisPendapatan = db.Column(db.String)
    NamaBadan = db.Column(db.String)
    AlamatBadan = db.Column(db.String)
    ObyekBadanNo = db.Column(db.String(50))
    NamaPemilik = db.Column(db.String)
    JOA = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    Penetapan = db.Column(db.String(50))
    Pajak = db.Column(db.Float)
    SetoranHistID = db.Column(db.Integer)
    TglBayar = db.Column(db.DateTime)
    JmlBayar = db.Column(db.Float)
    TglPelaporan = db.Column(db.DateTime, default=func.now())
    Denda = db.Column(db.Float)
    OPDID = db.Column(db.Integer)
    DocLapor = db.Column(db.String)
    NamaFile = db.Column(db.String)

    def __repr__(self):
        return f"<vw_pelaporanomzet(UPTID={self.UPTID}, Penetapan={self.Penetapan})>"
