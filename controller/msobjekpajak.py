from config.database import db


class MsObjekPajak(db.Model):
    __tablename__ = 'msobjekpajak'  # Ini nama dari view di database
    __table_args__ = {'extend_existing': True}

    OPDID = db.Column(db.Integer, primary_key=True)
    OPDID = db.Column(db.Integer)
    ObyekBadanNo = db.Column(db.String)
    NamaBadan = db.Column(db.String)
    GrupUsahaID = db.Column(db.Integer)
    KlasifikasiID = db.Column(db.Integer)
    LokasiID = db.Column(db.Integer)
    SelfAssessment = db.Column(db.Boolean)
    AlamatBadan = db.Column(db.String)
    KotaBadan = db.Column(db.String)
    KecamatanBadan = db.Column(db.String)
    KelurahanBadan = db.Column(db.String)
    RWBadan = db.Column(db.Integer)
    RTBadan = db.Column(db.Integer)
    NoTelpBadan = db.Column(db.String)
    NoFaxBadan = db.Column(db.String)
    UsahaBadan = db.Column(db.Integer)
    TglPendataan = db.Column(db.DateTime)
    WPID = db.Column(db.Integer)
    WapuID = db.Column(db.Integer)
    UserUpd = db.Column(db.String)
    DateUpd = db.Column(db.DateTime)
    NamaPengelola = db.Column(db.String)
    AlamatPengelola = db.Column(db.String)
    KotaPengelola = db.Column(db.String)
    KecamatanPengelola = db.Column(db.String)
    KelurahanPengelola = db.Column(db.String)
    RWPengelola = db.Column(db.Integer)
    RTPengelola = db.Column(db.Integer)
    NoTelpPengelola = db.Column(db.String)
    NPWPPengelola = db.Column(db.String)
    NPWPUsaha = db.Column(db.String)
    avatar = db.Column(db.String)
    latlng = db.Column(db.String)
    NOP = db.Column(db.String)
    TglNOP = db.Column(db.DateTime)

    def __repr__(self):
        return f'<MsObjekPajak {self.NamaBadan}>'
