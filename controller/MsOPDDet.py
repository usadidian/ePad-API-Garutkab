from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import func
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete
from config.database import db
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.tblUser import tblUser

class MsOPDDet(db.Model):
    __tablename__ = 'MsOPDDet'  # Nama tabel di database

    DetailD = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OPDID = db.Column(db.Integer, nullable=False)
    WPID = db.Column(db.Integer, nullable=False)
    OPDID = db.Column(db.Integer, nullable=False)
    NOP = db.Column(db.String)
    TglNOP = db.Column(db.DateTime)
    TglPendataan = db.Column(db.DateTime, nullable=True)
    UserUpd = db.Column(db.String(20), nullable=False)
    DateUpd = db.Column(db.DateTime, nullable=False)

    UsahaBadan = db.Column(db.String, db.ForeignKey('MsJenisPendapatan.JenisPendapatanID'), nullable=False)
    OPDID = db.Column(db.Integer, db.ForeignKey('MsOPD.OPDID'), nullable=False)

    def AddPendaftaranObjekPajakDetil(data):
        try:
            uid = data['uid']
            print(uid)
            result = []
            for row in result:
                result.append(row)

            opdid = data['OPDID']
            select_query = db.session.query(MsJenisPendapatan.KodeRekening).filter(
                MsJenisPendapatan.JenisPendapatanID == data['UsahaBadan']).first()

            if select_query:
                koderek = select_query[0]

                # Mengganti titik (.) dengan string kosong dan mengambil 6 karakter terakhir
                koderek_clean = koderek[-6:].replace('.', '')

                # Membuat OPDID menjadi 6 karakter dengan padding '0' di depannya
                opdid_padded = str(opdid).zfill(6)

                # Menggabungkan keduanya
                nop = koderek_clean + opdid_padded

                print(nop)  # Output hasilnya
            else:
                nop = None
                print("Kode Rekening tidak ditemukan")

            def generate_ObyekBadanID():
                max_id = db.session.query(func.max(MsOPDDet.OPDID)).scalar()
                return (max_id or 0) + 1

            add_record = MsOPDDet(
                UsahaBadan=data['UsahaBadan'],
                OPDID=opdid,
                WPID=opdid,
                OPDID=generate_ObyekBadanID(),
                NOP=nop,
                TglNOP=datetime.now().strftime('%Y-%m-%d') + ' 00:00:00.000',
                UserUpd=uid,
                DateUpd=datetime.now()
            )
            db.session.add(add_record)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False


    def UpdatePendaftaranObjekPajakDetil(data):
        try:
            uid = data['uid']
            print(uid)
            result = []
            # for row in result:
            #     result.append(row)
            select_query = MsOPDDet.query.filter_by(OPDID=data['OPDID']).first()
            if select_query:
                select_query.UsahaBadan=data['UsahaBadan']
                select_query.UserUpd=uid
                select_query.DateUpd = datetime.now()
                db.session.commit()
                return select_query
            else:
                return False
        except Exception as e:
            print(e)
            return False


    def DeletePendaftaranObjekPajakDetail(id):
        try:
            delete_record_detail = MsOPDDet.query.filter_by(OPDID=id)
            if delete_record_detail:
                delete_record_detail.delete()
                db.session.commit()
                return True
            else:
                db.session.rollback()
                return False
        except Exception as e:
            db.session.rollback()
            print(e)
            return False


    class ListAll(Resource):
        method_decorators = {'post': [tblUser.auth_apikey_privilege]}

        # def get(self, *args, **kwargs):
        #     select_query = MsOPDDet.query.order_by(MsOPDDet.OPDID).paginate(1, 10)
        #     result = []
        #     for row in select_query.items:
        #         result.append(row.to_dict())
        #     return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            # parser.add_argument('OPDID', type=str)
            parser.add_argument('UsahaBadan', type=str)
            parser.add_argument('TglPendataan', type=str)
            parser.add_argument('WPID', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            print(uid)

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            add_record = MsOPDDet(
                # OPDID=args['OPDID'],
                UsahaBadan=args['UsahaBadan'],
                TglPendataan=args['TglPendataan'],
                WPID=args['WPID'],
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
                select_query = MsOPDDet.query.filter_by(WPID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('UsahaBadan', type=str)
            parser.add_argument('TglPendataan', type=str)
            parser.add_argument('WPID', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            print(uid)

            args = parser.parse_args()
            try:
                select_query = MsOPDDet.query.filter_by(OPDID=id).first()
                if select_query:
                    select_query.UsahaBadan = f"{args['UsahaBadan']}"
                    select_query.TglPendataan = args['TglPendataan']
                    select_query.WPID = args['WPID']
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
                delete_record = MsOPDDet.query.filter_by(OPDID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})