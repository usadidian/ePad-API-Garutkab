
from flask_restful import Resource, reqparse
from sqlalchemy import func

from sqlalchemy.orm import aliased
from sqlalchemy_serializer import SerializerMixin

from config.api_message import failed_read, success_reads
from config.database import db


class MATANGD13(db.Model, SerializerMixin):
    __tablename__ = 'MATANGD13'
    MTGKEY = db.Column(db.String, primary_key=True)
    KDPER = db.Column(db.String, nullable=False)
    NMPER = db.Column(db.String, nullable=False)
    MTGLEVEL = db.Column(db.String, nullable=False)
    MAT_MTGKEY = db.Column(db.String, db.ForeignKey('MATANGD13.MTGKEY'), nullable=False)
    childs = db.relationship('MATANGD13')

    class ListAll(Resource):
        # method_decorators = {'get': [tblUser.auth_apikey_privilege]}
        def get(self, *args, **kwargs):
            try:
                parser = reqparse.RequestParser()
                parser.add_argument('parent_kode', type=str, help='diisi dengan kode rekening parent, contoh 4.1.1.')
                args = parser.parse_args()
                # level = [44, 45]
                # level = db.session.query(func.min(MATANGD13.MTGLEVEL)).scalar()
                select_query = MATANGD13.query

                if args['parent_kode'] and args['parent_kode'] != 'null':
                    select_query = select_query.filter(
                        MATANGD13.KDPER == args['parent_kode']
                    )
                    # select_query = select_query.filter(MATANGD13.MTGLEVEL.in_(level))
                select_query = select_query.order_by(MATANGD13.KDPER).all()
                result = []
                for row in select_query[0].childs:
                    result.append(row.to_dict())
                return success_reads(result)
            except Exception as e:
                print(e)
                return failed_read({})