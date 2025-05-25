from collections import defaultdict
from datetime import datetime, timedelta

import sqlalchemy
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_, Integer, cast, func, null
from sqlalchemy.orm import aliased
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from config.helper import toDict
from controller.tblUser import tblUser



class MATANGD(db.Model, SerializerMixin):
    __tablename__ = 'MATANGD'
    MTGKEY = db.Column(db.Integer, primary_key=True, autoincrement=True)
    KDPER = db.Column(db.String, primary_key=True)
    NMPER = db.Column(db.String, nullable=False)
    MTGLEVEL= db.Column(db.String, nullable=False)
    KDKHUSUS = db.Column(db.String, nullable=False)
    TYPE = db.Column(db.String, nullable=False)

    class ListAll2( Resource ):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT DISTINCT mjp.JenisPendapatanID, m.MTGKEY,m.KDPER ,m.NMPER, m.KDPER+' '+m.NMPER AS NamaJenisPendapatan, m.MTGLEVEL, m.TYPE "
                f"FROM MATANGD AS m LEFT JOIN MsJenisPendapatan AS mjp ON LTRIM(RTRIM(mjp.KodeRekening))=LTRIM(RTRIM(m.KDPER))"
                f"WHERE m.MTGLEVEL >'5' AND  m.KDPER BETWEEN '4.1.01.06.' AND '4.1.01.17.' OR (m.NMPER LIKE'%OPSEN%' AND m.MTGLEVEL >='5') AND mjp.KodeRekening IS NULL "
                f"ORDER BY m.KDPER")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads( result )


    class ListAll(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        # def get(self, *args, **kwargs):
        #
        #     # PARSING PARAMETER DARI REQUEST
        #     parser = reqparse.RequestParser()
        #     parser.add_argument('page', type=int)
        #     parser.add_argument('length', type=int)
        #     parser.add_argument('sort', type=str)
        #     parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
        #     parser.add_argument('search', type=str)
        #
        #     args = parser.parse_args()
        #     UserId = kwargs['claim']["UserId"]
        #     print(UserId)
        #     select_query = MATANGD.query
        #
        #     # SEARCH
        #     if args['search'] and args['search'] != 'null':
        #         search = '%{0}%'.format(args['search'])
        #         select_query = select_query.filter(
        #             or_(MATANGD.KDPER.ilike(search),
        #                 MATANGD.NMPER.ilike(search))
        #         )
        #
        #     # SORT
        #     if args['sort']:
        #         if args['sort_dir'] == "desc":
        #             sort = getattr(MATANGD, args['sort']).desc()
        #         else:
        #             sort = getattr(MATANGD, args['sort']).asc()
        #         select_query = select_query.order_by(sort)
        #     else:
        #         select_query = select_query.order_by(MATANGD.KDPER)
        #
        #     # PAGINATION
        #     page = args['page'] if args['page'] else 1
        #     length = args['length'] if args['length'] else 10
        #     lengthLimit = length if length < 101 else 100
        #     query_execute = select_query.paginate(page, lengthLimit)
        #
        #     result = []
        #     for row in query_execute.items:
        #         result.append(row.to_dict())
        #     return success_reads_pagination(query_execute, result)



        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('nested', type=int)
            args = parser.parse_args()

            # PARSING PARAMETER DARI REQUEST
            UserId = kwargs['claim']["UserId"]
            result = []
            parent_child = MATANGD.query.order_by(MATANGD.KDPER).all()

            for row in parent_child:
                d = row.to_dict()
                last_digit = d['KDPER'].strip('.').split('.')[-1]
                d['id'] = d['KDPER'].replace(".", "")
                d['parent'] = d['id'][:-len(last_digit)]
                d['id'] = int(d['id']) if d['id'] else None

                d['parent'] = int(d['parent']) if d['parent'] else None
                d['depth'] = int(d['MTGLEVEL'])

                if args['nested'] == 1:
                    #primeng tree table
                    d['data'] = row.to_dict()
                    d['expanded'] = True if d['depth'] < 3 else False
                result.append(d)

            if args['nested'] == 1:
                def build_tree(elems):
                    set_relation = {}

                    def build_children(parent):
                        filter_result = [d for d in elems if d['id'] == parent]
                        cur_dict = filter_result[0] if filter_result else {}
                        if parent in set_relation.keys():
                            cur_dict["children"] = [build_children(child_id) for child_id in set_relation[parent]]
                        return cur_dict

                    for item in elems:
                        child_id = item['id']
                        parent_id = item['parent']
                        set_relation.setdefault(parent_id, []).append(child_id)

                    res = build_children(4) #<--- root id
                    return res
                result = build_tree(result)
            return success_reads(result)

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            # parser.add_argument('MTGKEY', type=str)
            parser.add_argument('KDPER', type=str)
            parser.add_argument('NMPER', type=str)
            parser.add_argument('MTGLEVEL', type=str)
            parser.add_argument('KDKHUSUS', type=str)
            parser.add_argument('TYPE', type=str)

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            add_record = MATANGD(
                # MTGKEY=args['MTGKEY'],
                KDPER=args['KDPER'],
                NMPER=args['NMPER'],
                MTGLEVEL=args['MTGLEVEL'],
                KDKHUSUS=args['KDKHUSUS'],
                TYPE=args['TYPE']
            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MATANGD.query.filter_by(MTGKEY=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            # parser.add_argument('MTGKEY', type=str)
            parser.add_argument('KDPER', type=str)
            parser.add_argument('NMPER', type=str)
            parser.add_argument('MTGLEVEL', type=str)
            parser.add_argument('TYPE', type=str)

            args = parser.parse_args()
            try:
                select_query = MATANGD.query.filter_by(MTGKEY=id).first()
                if select_query:
                    # select_query.MTGKEY = args['MTGKEY']
                    select_query.KDPER = args['KDPER']
                    select_query.NMPER = args['NMPER']
                    select_query.MTGLEVEL = args['MTGLEVEL']
                    select_query.TYPE = args['TYPE']
                    db.session.commit()
                    return success_update({'id': id})
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MATANGD.query.filter_by(MTGKEY=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})