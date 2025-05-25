import parser
from datetime import datetime
from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads, success_create, failed_update, success_delete, failed_delete, \
    failed_create, success_reads_pagination
from config.database import db
from config.helper import toDict
from controller.tblUser import tblUser


class MsKlasifikasiUsaha:
    pass


class MsKlasifikasiUsaha(db.Model, SerializerMixin):
    __tablename__ = 'MsKlasifikasiUsaha'
    IdKlasifikasi = db.Column(db.Integer, primary_key=True)
    KlasifikasiID = db.Column(db.String)
    JenisUsaha = db.Column(db.String, nullable=False)
    KlasUsaha = db.Column(db.String, nullable=False)

    class ListAll2( Resource ):
        method_decorators = [tblUser.auth_apikey_privilege]

        def get(self, *args, **kwargs):
            select_query = MsKlasifikasiUsaha.query.order_by(MsKlasifikasiUsaha.KlasifikasiID).all()
            result = []
            for row in select_query:
                result.append( row.to_dict() )
            return success_reads( result )


    class ListAll(Resource):
        method_decorators = [tblUser.auth_apikey_privilege]

        def get(self, *args, **kwargs):
            select_query = db.session.query(
                MsKlasifikasiUsaha.IdKlasifikasi, MsKlasifikasiUsaha.KlasifikasiID,
                (MsKlasifikasiUsaha.JenisUsaha + ' - ' + MsKlasifikasiUsaha.KlasUsaha).label('JenisUsaha')
            )
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads( result )

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('KlasifikasiID', type=str)
            parser.add_argument('JenisUsaha', type=str)
            parser.add_argument('KlasUsaha', type=str)
            try:
                args = parser.parse_args()
                result = []
                for row in result:
                    result.append(row)

                add_record = MsKlasifikasiUsaha(
                    KlasifikasiID=args['KlasifikasiID'],
                    JenisUsaha=args['JenisUsaha'],
                    KlasUsaha=args['KlasUsaha']

                )
                db.session.add(add_record)
                db.session.commit()
                return success_create({'IdKlasifikasi': add_record.IdKlasifikasi,
                                       'KlasifikasiID': add_record.KlasifikasiID,
                                       'JenisUsaha': add_record.JenisUsaha,
                                       'KlasUsaha': add_record.KlasUsaha
                                       })

            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_create({})


    class ListById(Resource):
        method_decorators = [tblUser.auth_apikey_privilege]

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            # print(kwargs['claim'])
            parser.add_argument('KlasifikasiID', type=str)
            parser.add_argument('JenisUsaha', type=str)
            parser.add_argument('KlasUsaha', type=str)

            # uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = MsKlasifikasiUsaha.query.filter_by(IdKlasifikasi=id).first()
                if select_query:

                    if args['KlasifikasiID']:
                        select_query.KlasifikasiID = args['KlasifikasiID']
                    if args['JenisUsaha']:
                        select_query.JenisUsaha = args['JenisUsaha']
                    if args['KlasUsaha']:
                        select_query.KlasUsaha = args['KlasUsaha']

                    # select_query.UserUpd = uid
                    select_query.DateUpd = datetime.now()

                    db.session.commit()
                    return success_create({'IdKlasifikasi': select_query.IdKlasifikasi,
                                           'KlasifikasiID': select_query.KlasifikasiID,
                                           'JenisUsaha': select_query.JenisUsaha,
                                           'KlasUsaha': select_query.KlasUsaha
                                           })
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsKlasifikasiUsaha.query.filter_by(IdKlasifikasi=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})
