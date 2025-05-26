from datetime import datetime

import sqlalchemy
from flask import jsonify
from flask_cors import cross_origin
from flask_restful import Resource, reqparse, inputs
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from distutils.util import strtobool

from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.tblGroupUser import tblGroupUser
from controller.tblUrl import tblUrl


class tblRole(db.Model, SerializerMixin):

    __tablename__ = 'tblRole'
    RoleId = db.Column(db.Integer, primary_key=True)
    Get = db.Column(db.Boolean, default=False, server_default="false")
    Post = db.Column(db.Boolean, default=False, server_default="false")
    Put = db.Column(db.Boolean, default=False, server_default="false")
    Del = db.Column(db.Boolean, default=False, server_default="false")
    Upload = db.Column(db.Boolean, default=False, server_default="false")
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    GroupId = db.Column(db.Integer, db.ForeignKey('tblGroupUser.GroupId'), nullable=False)
    UrlId = db.Column(db.Integer, db.ForeignKey('tblUrl.UrlId'), nullable=False)

    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT * FROM TblRole order by RoleId")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll(Resource):


        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
            parser.add_argument('search', type=str)
            parser.add_argument('filter_groupid', type=str)

            args = parser.parse_args()
            select_query = db.session.query(
                tblRole.RoleId, tblUrl.UrlId, tblUrl.Url, tblGroupUser.GroupId, tblGroupUser.nama_group, tblRole.Get,tblRole.Post,
                tblRole.Put, tblRole.Del, tblRole.Upload)\
                .outerjoin(tblUrl, tblRole.UrlId == tblUrl.UrlId) \
                .outerjoin(tblGroupUser, tblRole.GroupId == tblGroupUser.GroupId)

            # FILTER_GROUP
            if args['filter_groupid']:
                select_query = select_query.filter(
                    tblRole.GroupId == args['filter_groupid']
                )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    tblUrl.Url.ilike(search)
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(tblRole, args['sort']).desc()
                else:
                    sort = getattr(tblRole, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(tblRole.RoleId)

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

        @cross_origin( supports_credentials=True )
        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            # parser.add_argument('RoleId', type=str)
            parser.add_argument('UrlId', type=str)
            parser.add_argument('GroupId', type=str)
            parser.add_argument('Get', type=str)
            parser.add_argument('Post', type=str)
            parser.add_argument('Put', type=str)
            parser.add_argument('Del', type=str)
            parser.add_argument('Upload', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            # uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)


            add_record = tblRole(
                UrlId=args['UrlId'],
                GroupId=args['GroupId'],
                Get=strtobool(args['Get']) if args['Get'] else False,
                Post=strtobool(args['Post']) if args['Post'] else False,
                Put=strtobool(args['Put']) if args['Put'] else False,
                Del=strtobool(args['Del']) if args['Del'] else False,
                Upload=strtobool(args['Upload']) if args['Upload'] else False,
                UserUpd='',
                DateUpd=datetime.now(),

            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):

        def get(self, id, *args, **kwargs):
            try:
                select_query = tblRole.query.filter_by(RoleId=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        @cross_origin( supports_credentials=True )
        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            # print(kwargs['claim'])
            parser = reqparse.RequestParser()
            # parser.add_argument('RoleId', type=str)
            parser.add_argument('UrlId', type=str)
            parser.add_argument('GroupId', type=str)
            parser.add_argument( "Get",  type=str )
            parser.add_argument( "Post",  type=str)
            parser.add_argument( "Put",  type=str)
            parser.add_argument( "Del",  type=str)
            parser.add_argument( "Upload", type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            # uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = tblRole.query.filter_by(RoleId=id).first()
                if select_query:
                    select_query.UrlId = args['UrlId']
                    select_query.GroupId = args['GroupId']
                    if args['Get']:
                        select_query.Get = strtobool(args['Get'])
                    if args['Post']:
                        select_query.Post = strtobool(args['Post'])
                    if args['Put']:
                        select_query.Put = strtobool(args['Put'])
                    if args['Del']:
                        select_query.Del = strtobool(args['Del'])
                    if args['Upload']:
                        select_query.Upload = strtobool(args['Upload'])
                    select_query.UserUpd = ""
                    select_query.DateUpd = datetime.now()
                    db.session.commit()
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = tblRole.query.filter_by(RoleId=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})