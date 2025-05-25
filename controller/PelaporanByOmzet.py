from config.database import db


class PelaporanByOmzet(db.Model):
    __tablename__ = 'PelaporanByOmzet'

    PelaporanID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SPT = db.Column(db.String(8), nullable=False)
    OPDID = db.Column(db.Integer, nullable=False)
    NamaBadan = db.Column(db.String)
    WapuID = db.Column(db.Integer, nullable=True)
    TglPelaporan = db.Column(db.DateTime, nullable=False)
    MasaAwal = db.Column(db.DateTime, nullable=False)
    MasaAkhir = db.Column(db.DateTime, nullable=False)
    SetoranHistID = db.Column(db.Integer, nullable=True)
    TarifPajak = db.Column(db.Numeric(18, 2), nullable=False)
    TarifPajakOpsen = db.Column(db.Numeric(18, 2), nullable=True)
    JmlBayar = db.Column(db.Numeric(18, 2), nullable=True)
    UPTID = db.Column(db.String(5), nullable=False)
    UserUpd = db.Column(db.String(20), nullable=False)
    DateUpd = db.Column(db.DateTime, nullable=False)
    DocLapor = db.Column(db.String, nullable=True)