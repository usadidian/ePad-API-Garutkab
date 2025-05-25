from datetime import datetime
import sqlalchemy
from flask import jsonify, request
from flask_restful import Resource, reqparse
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete
from config.database import db
from controller.tblUser import tblUser


class SetoranUPTDtl(db.Model, SerializerMixin):
    __tablename__ = 'SetoranUPTDtl'
    DetailID = db.Column(db.Integer, primary_key=True)
    NoReg = db.Column(db.String(50), nullable=False)
    id = db.Column(db.Integer, nullable=False)
    mapid = db.Column(db.Integer, nullable=False)
    JmlSetoran =  db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=True)
    Status= db.Column(db.String, nullable=False)
    NTB = db.Column(db.String, nullable=True)
    NTPD = db.Column(db.String, nullable=True)
    TglNTPD = db.Column(db.TIMESTAMP, nullable=True)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    HeaderID = db.Column(db.Integer, db.ForeignKey('SetoranUPTHdr.HeaderID'), nullable=False)
    JenisPendapatanID = db.Column(db.String, db.ForeignKey('MsJenisPendapatan.JenisPendapatanID'), nullable=False)

    class ListAll(Resource):
        method_decorators = {'post': [tblUser.auth_apikey_privilege]}

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('HeaderID', type=str)
            parser.add_argument('JenisPendapatanID', type=str)
            parser.add_argument('JmlSetoran', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('NTB', type=str)
            parser.add_argument('NTPD', type=str)
            parser.add_argument('TglNTPD', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            add_record = SetoranUPTDtl(
                HeaderID=args['HeaderID'],
                JenisPendapatanID=args['JenisPendapatanID'],
                JmlSetoran=args['JmlSetoran'],
                Status=args['Status'],
                NTB=sqlalchemy.sql.null(),
                NTPD=sqlalchemy.sql.null(),
                TglNTPD=sqlalchemy.sql.null(),
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
                select_query = SetoranUPTDtl.query.filter_by(DetailID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            parser.add_argument('HeaderID', type=str)
            parser.add_argument('JenisPendapatanID', type=str)
            parser.add_argument('JmlSetoran', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('NTB', type=str)
            parser.add_argument('NTPD', type=str)
            parser.add_argument('TglNTPD', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            args = parser.parse_args()
            try:
                select_query = SetoranUPTDtl.query.filter_by(DetailID=id, NTB=sqlalchemy.sql.null()).first()
                if select_query:
                    select_query.HeaderID = args['HeaderID']
                    select_query.JenisPendapatanID = args['JenisPendapatanID']
                    select_query.JmlSetoran = args['JmlSetoran']
                    select_query.Status = args['Status']
                    select_query.NTB = args['NTB']
                    select_query.NTPD = args['NTPD']
                    select_query.TglNTPD = args['TglNTPD']
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
                delete_record = SetoranUPTDtl.query.filter_by(DetailID=id, NTB=sqlalchemy.sql.null())
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})

