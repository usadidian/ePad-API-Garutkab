from datetime import datetime
import sqlalchemy
from flask import jsonify, request
from flask_restful import Resource, reqparse
from sqlalchemy_serializer import SerializerMixin
from config.api_message import failed_delete, success_delete, failed_update, success_update, failed_read, success_read
from config.database import db
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsMapOpsen import MsMapOpsen
from controller.MsTarifLokasi import MsTarifLokasi
from controller.tblUser import tblUser


class PendataanByOmzetDtl(db.Model, SerializerMixin):
    __tablename__ = 'PendataanByOmzetDtl'
    DetailID = db.Column(db.Integer, autoincrement=True, primary_key=True)
    SPT = db.Column(db.String, nullable=False)
    NoUrut = db.Column(db.Integer, nullable=False)
    NoKohir = db.Column(db.String, nullable=False)
    Lokasi = db.Column(db.String, nullable=False)
    Luas = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    UsahaID = db.Column(db.Integer, nullable=False)
    TarifPajak = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    TarifPajakOpsen = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    Status = db.Column(db.String, nullable=False)
    LKecamatan = db.Column(db.String, nullable=True)
    LKelurahan = db.Column(db.String, nullable=True)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    PendataanID = db.Column(db.Integer, db.ForeignKey('PendataanByOmzet.PendataanID'), primary_key=True, nullable=False)

    def AddPPendataanDetil(data):
        try:
            uid = data['uid']
            print(uid)
            spt = data['SPT']
            select_query = db.session.execute(
                f"SELECT DISTINCT isnull(max(NoUrut) + 1,1) FROM PendataanByOmzetDtl "
                f"WHERE SPT = '{spt}' ")
            nourut = select_query.first()[0]
            usahaid = data['UsahaID']
            omzet = data['Luas']
            opdid =data['OPDID']
            select_query = db.session.query(MsTarifLokasi.TarifPajak).filter(
                MsTarifLokasi.LokasiID == usahaid)
            trfpajak = select_query.first()[0] if select_query else None
            if not trfpajak:
                return False

            tarifpajak = float(omzet) * float(trfpajak)

            select_query = db.session.execute(
                f"SELECT TOP 1 ISNULL(JenispendapatanID,'') FROM vw_obyekbadan "
                f"WHERE OPDID = '{opdid}' ")
            jpid = select_query.first()[0]
            print(jpid)

            select_query = db.session.execute(
                f"SELECT TOP 1 ISNULL(NamaJenisPendapatan,'') FROM MsJenisPendapatan "
                f"WHERE JenisPendapatanID = '{jpid}' ")
            nmjpid = select_query.first()[0]
            print(jpid)
            tarifpajakopsen = 0
            mblb = None
            if nmjpid == 'Mineral Bukan Logam dan Batuan':

                select_query = db.session.query(MsMapOpsen.JPIDOpsen).filter(
                    MsMapOpsen.JPID == jpid)
                jpidopsen = select_query.first()[0]

                select_query = db.session.query(MsJenisPendapatan.NamaJenisPendapatan).filter(
                    MsJenisPendapatan.JenisPendapatanID == jpidopsen)
                result = select_query.first()
                mblb = result[0] if result else None

                if mblb is not None:
                    select_query = db.session.query(MsTarifLokasi.LokasiID).filter(
                        MsTarifLokasi.JenisPendapatanID == jpidopsen)
                    lokasiidopsen = select_query.first()[0]

                    select_query = db.session.query(MsTarifLokasi.TarifPajak).filter(
                        MsTarifLokasi.LokasiID == lokasiidopsen)
                    trfpajakopsen = select_query.first()[0] if select_query else None

                    tarifpajakopsen = float(tarifpajak) * float(trfpajakopsen)

            result = []
            for row in result:
                result.append(row)

            add_record = PendataanByOmzetDtl(
                PendataanID=data['PendataanID'],
                SPT=spt,
                NoUrut=nourut,
                NoKohir=sqlalchemy.sql.null(),
                Lokasi=sqlalchemy.sql.null(),
                Luas=omzet,
                UsahaID=usahaid,
                TarifPajak=tarifpajak,
                TarifPajakOpsen=tarifpajakopsen if tarifpajakopsen else 0,
                Status=1,
                LKecamatan=data['LKecamatan'],
                LKelurahan=data['LKelurahan'],
                UserUpd=uid,
                DateUpd=datetime.now()
            )
            db.session.add(add_record)
            db.session.commit()
            print(f"UPDATE PendataanByOmzet SET TarifPajak={float(tarifpajak)} WHERE SPT = '{spt}'")
            if add_record.DetailID:
                db.session.execute(
                    f"UPDATE PendataanByOmzet SET TarifPajak={tarifpajak} WHERE SPT = '{spt}'")
                db.session.commit()
                if mblb:
                    db.session.execute(
                    f"UPDATE PendataanByOmzet SET TarifPajakOpsen = {tarifpajakopsen} WHERE SPT = '{spt}'")
                    db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def UpdatePendataanDetail(data):
        try:
            uid = data['uid']
            print(uid)
            spt = data['SPT']
            nourut = int(data['NoUrut'])
            usahaid = int(data['UsahaID'])
            omzet = float(data['Luas'])
            select_query = db.session.query(MsTarifLokasi.TarifPajak).filter(
                MsTarifLokasi.LokasiID == usahaid)
            trfpajak = select_query.first()[0]
            print(trfpajak)
            tarifpajak = float(omzet) * float(trfpajak)

            result = []
            for row in result:
                result.append(row)

            select_query = PendataanByOmzetDtl.query.filter_by(DetailID=data['DetailID']).first()
            if select_query:
                if data['PendataanID']:
                    select_query.PendataanID = data['PendataanID']
                if spt:
                    select_query.SPT = spt
                if nourut:
                    select_query.NoUrut = nourut
                if data['LKecamatan']:
                    select_query.LKecamatan = data['LKecamatan']
                if data['LKelurahan']:
                    select_query.LKelurahan = data['LKelurahan']
                if data['UsahaID']:
                    select_query.UsahaID = data['UsahaID']
                if omzet:
                    select_query.Luas = omzet
                if tarifpajak:
                    select_query.TarifPajak = tarifpajak
                select_query.UserUpd = uid
                select_query.DateUpd = datetime.now()
                db.session.commit()
                select_query = db.session.execute(
                    f"UPDATE PendataanByOmzet SET TarifPajak=(SELECT SUM(TarifPajak) FROM PendataanByOmzetDtl WHERE SPT = {spt}) "
                    f"WHERE SPT = {spt}")

                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False


    def UpdateParent(data):
        try:
            nokohir = data['NoKohir']
            spt = data['SPT']
            nourut = data['UrutTgl']

            query = db.session.query(PendataanByOmzetDtl.DetailID).filter(
                PendataanByOmzetDtl.SPT == spt, PendataanByOmzetDtl.NoUrut == nourut).first()
            result = query[0]
            detailid = result

            select_query = PendataanByOmzetDtl.query.filter_by(DetailID=detailid).first()
            if select_query:
                if data['NoKohir']:
                    select_query.NoKohir = nokohir
                db.session.commit()
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def DeleteParent(data):
        try:
            nokohir = data['NoKohir']
            spt = data['SPT']
            nourut = data['UrutTgl']
            query = db.session.query(PendataanByOmzetDtl.DetailID).filter(
                PendataanByOmzetDtl.SPT == spt, PendataanByOmzetDtl.NoUrut == nourut).first()
            result = query[0]
            detailid = result
            select_query = PendataanByOmzetDtl.query.filter_by(DetailID=detailid).first()
            if select_query:
                if nokohir:
                    select_query.NoKohir = sqlalchemy.null
                db.session.commit()
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    class ListAll(Resource):
        method_decorators = {'post': [tblUser.auth_apikey_privilege]}

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('PendataanID', type=str)
            parser.add_argument('SPT', type=str)
            parser.add_argument('NoUrut', type=int)
            parser.add_argument('NoKohir', type=str)
            parser.add_argument('Lokasi', type=str)
            parser.add_argument('Luas', type=str)
            parser.add_argument('UsahaID', type=int)
            parser.add_argument('TarifPajak', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('LKecamatan', type=str)
            parser.add_argument('LKelurahan', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            nourut = int('1')
            usahaid = int(request.form['UsahaID'])
            omzet = float(request.form['Luas'])
            select_query = db.session.query(MsTarifLokasi.TarifPajak).filter(
                MsTarifLokasi.LokasiID == usahaid)  # .first()
            trfpajak = select_query.first()[0]
            print(trfpajak)
            tarifpajak = float(omzet) * float(trfpajak)

            select_query = db.session.execute(
                f"UPDATE PendataanByOmzet SET TarifPajak=tarifpajak, JmlOmzetAwal=omzet"
                f"WHERE SPT = '{args['SPT']}'")
            result3 = select_query.first()[0]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            add_record = PendataanByOmzetDtl(
                PendataanID=args['PendataanID'],
                SPT=args['SPT'],
                NoUrut=nourut,
                NoKohir=sqlalchemy.sql.null(),
                Lokasi=sqlalchemy.sql.null(),
                Luas=omzet,
                UsahaID=usahaid,
                TarifPajak=tarifpajak,
                Status=args['Status'],
                LKecamatan=args['LKecamatan'],
                LKelurahan=args['LKelurahan'],
                UserUpd=uid,
                DateUpd=datetime.now()
            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = PendataanByOmzetDtl.query.filter_by(SPT=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('SPT', type=str)
            parser.add_argument('NoUrut', type=str)
            parser.add_argument('NoKohir', type=str)
            parser.add_argument('Lokasi', type=str)
            parser.add_argument('Luas', type=str)
            parser.add_argument('UsahaID', type=str)
            parser.add_argument('TarifPajak', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('LKecamatan', type=str)
            parser.add_argument('LKelurahan', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            nourut = int('1')
            usahaid = int(request.form['UsahaID'])
            omzet = float(request.form['Luas'])
            select_query = db.session.query(MsTarifLokasi.TarifPajak).filter(
                MsTarifLokasi.LokasiID == usahaid)
            trfpajak = select_query.first()[0]
            print(trfpajak)
            tarifpajak = float(omzet) * float(trfpajak)

            spt = request.form['SPT']
            select_query = db.session.execute(
                f"UPDATE PendataanByOmzet SET TarifPajak= {tarifpajak}, JmlOmzetAwal= {omzet} "
                f"WHERE SPT= '{spt}'")

            args = parser.parse_args()
            try:
                select_query = PendataanByOmzetDtl.query.filter_by(SPT=id).first()
                if select_query:
                    select_query.SPT = args['SPT']
                    select_query.NoUrut = nourut
                    select_query.NoKohir = args['NoKohir']
                    select_query.Lokasi = args['Lokasi']
                    select_query.Luas = omzet
                    select_query.UsahaID = usahaid
                    select_query.TarifPajak = tarifpajak
                    select_query.Status = args['Status']
                    select_query.LKecamatan = args['LKecamatan']
                    select_query.LKelurahan = args['LKelurahan']
                    select_query.UserUpd = uid
                    select_query.DateUpd = datetime.now()
                    db.session.commit()
                    return success_update({'id': id})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = PendataanByOmzetDtl.query.filter_by(SPT=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})