from datetime import datetime

from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, reqparse
from sqlalchemy import func, literal, or_
from sqlalchemy.orm import scoped_session
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_delete, failed_delete, failed_update, success_update, failed_read, success_read, \
    success_reads, failed_reads, failed_create, success_create, success_reads_pagination
from config.helper import parser, logger
from controller.MsPropinsi import MsPropinsi
from controller.tblUser import tblUser

db = SQLAlchemy()

class ApiUrl(db.Model, SerializerMixin):
    __tablename__ = 'ApiUrl'

    UrlId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Url = db.Column(db.String(100), nullable=True)
    Keterangan = db.Column(db.String(50), nullable=True)
    PropinsiID = db.Column(db.Integer, nullable=True)


    def __repr__(self):
        return f"<ApiUrl(UrlId={self.UrlId}, Url='{self.Url}', Keterangan='{self.Keterangan}', PropinsiID='{self.PropinsiID}')>"

    parser = reqparse.RequestParser()
    parser.add_argument('Url', type=str, required=False)
    parser.add_argument('Keterangan', type=str, required=False)
    parser.add_argument('PropinsiID', type=str, required=False)


class ApiUrlListResource(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

    # def get(self, *args, **kwargs):
    #     urls = ApiUrl.query.outerjoin(MsPropinsi.PropinsiID == ApiUrl.PropinsiID).all()
    #     data = [
    #         {
    #             'UrlId': url.UrlId,
    #             'Url': url.UrlId,
    #             'Keterangan': url.Keterangan,
    #             'PropinsiID': url.PropinsiID,
    #             'Propinsi': url.MsPropinsi.Kode +' - '+ url.MsPropinsi.Propinsi if url.propinsi else None
    #         }
    #         for url in urls
    #     ]
    #     return {'data': data}, 200
    def get(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('length', type=int)
        parser.add_argument('sort', type=str)
        parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
        parser.add_argument('search', type=str)

        args = parser.parse_args()
        try:

            select_query = db.session.query(ApiUrl.UrlId, ApiUrl.Url, ApiUrl.Keterangan,
                                            ApiUrl.PropinsiID, MsPropinsi.Kode,MsPropinsi.Propinsi,
                                            (MsPropinsi.Kode + literal(' - ') + MsPropinsi.Propinsi).label('NamaPropinsi')
                                            ) \
            .outerjoin(MsPropinsi, ApiUrl.PropinsiID == MsPropinsi.PropinsiID)\
                

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(ApiUrl.Url.ilike(search),
                        MsPropinsi.Kode.ilike(search),
                        MsPropinsi.Propinsi.ilike(search),
                        ApiUrl.Keterangan.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort'] == 'NamaPropinsi':
                    sort_column = (MsPropinsi.Kode + literal(' - ') + MsPropinsi.Propinsi)
                elif args['sort'] == 'Propinsi':
                    sort_column = MsPropinsi.Propinsi
                elif args['sort'] == 'Kode':
                    sort_column = MsPropinsi.Kode
                else:
                    sort_column = getattr(ApiUrl, args['sort'])

                if args['sort_dir'] == "desc":
                    sort = sort_column.desc()
                else:
                    sort = sort_column.asc()

                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(ApiUrl.PropinsiID)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads_pagination(query_execute, result)
        except Exception as e:
            logger.error(e)
            return failed_reads([])


    def post(self,*args, **kwargs):
        # args = parser.parse_args()
        parser = reqparse.RequestParser()
        # parser.add_argument('UPTID', type=str)
        parser.add_argument('Url', type=str)
        parser.add_argument('Keterangan', type=str)
        parser.add_argument('PropinsiID', type=str)

        try:
            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            new_url = ApiUrl(
                Url=args['Url'] if args['Url'] else '',
                Keterangan=args['Keterangan'] if args['Keterangan'] else '',
                PropinsiID=args['PropinsiID'] if args['PropinsiID'] else None
            )
            db.session.add(new_url)
            db.session.commit()

            data = {
                'UrlId': new_url.UrlId,
                'Url': new_url.Url,
                'Keterangan': new_url.Keterangan,
                'PropinsiID': new_url.PropinsiID
            }

            return success_create( {
                'message': 'Url created',
                'data': data
            })

        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_create({})

class ApiUrlResource(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                         'delete': [tblUser.auth_apikey_privilege]}

    def get(self, id, *args, **kwargs):
        try:
            select_query = ApiUrl.query.filter_by(UrlId=id).first()
            result = select_query.to_dict()
            return success_read(result)
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_read({})

    def put(self, id, *args, **kwargs):
        parser = reqparse.RequestParser()
        print(kwargs['claim'])
        parser.add_argument('Url', type=str)
        parser.add_argument('Keterangan', type=str)
        parser.add_argument('PropinsiID', type=str)

        args = parser.parse_args()
        try:
            select_query = ApiUrl.query.filter_by(UrlId=id).first()
            if select_query:
                if args['Url']:
                    select_query.Url = args['Url']
                if args['Keterangan']:
                    select_query.Keterangan = args['Keterangan']
                if args['PropinsiID']:
                    select_query.PropinsiID = args['PropinsiID']
                db.session.commit()
            return success_update({'id': id})
        except Exception as e:

            db.session.rollback()
            print(e)
            return failed_update({})

    def delete(self, id, *args, **kwargs):
        try:
            delete_record = ApiUrl.query.filter_by(UrlId=id)
            delete_record.delete()
            db.session.commit()
            return success_delete({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_delete({})

class ApiUrlLookup(Resource):
    def get(self,*args, **kwargs):
        data = ApiUrl.query.all()
        result = [
            {
                'UrlId': row.UrlId,
                'Url': row.Url,
                'Keterangan': row.Keterangan
            }
            for row in data
        ]
        return {'status_code': 1, 'message': 'OK', 'data': result}, 200