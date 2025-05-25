from flask_sqlalchemy import SQLAlchemy

# Inisialisasi SQLAlchemy
db = SQLAlchemy()


class tblUPTOpsen(db.Model):
    __tablename__ = 'tblUPTOpsen'

    UPTID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UPT = db.Column(db.String(50), nullable=True)
    KotaPropID = db.Column(db.String(5), nullable=True)

    def __repr__(self):
        return f"<tblUPTOpsen UPTID={self.UPTID} UPT='{self.UPT} KotaPropID='{self.KotaPropID}'>"
