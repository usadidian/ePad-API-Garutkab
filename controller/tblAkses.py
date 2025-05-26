from datetime import datetime

from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination, success_read, failed_read, \
    success_update, failed_update, success_delete, failed_delete, success_reads
from config.database import db
from config.helper import logger
from controller.tblGroupUser import tblGroupUser
from controller.tblMenu import tblMenu


# from controller.tblUser import tblUser


class tblAkses(db.Model, SerializerMixin):
    __tablename__ = 'tblAkses'
    AksesId = db.Column(db.Integer, primary_key=True)
    GroupId = db.Column(db.Integer, db.ForeignKey('tblGroupUser.GroupId'), nullable=False)
    MenuId = db.Column(db.Integer, db.ForeignKey('tblMenu.MenuId'), nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)
    Get = db.Column(db.Boolean, default=False, server_default="false")
    Post = db.Column(db.Boolean, default=False, server_default="false")
    Put = db.Column(db.Boolean, default=False, server_default="false")
    Del = db.Column(db.Boolean, default=False, server_default="false")
    Upload = db.Column(db.Boolean, default=False, server_default="false")
    # Relationships
    group = relationship('tblGroupUser', backref='akses')
    menu = relationship('tblMenu', backref='akses')



    class tblAkses4(Resource):
        def get(self, groupid, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT u.GroupId, s.nama_group, j.Kode,j.Menu, u.AksesId "
                f"FROM ((tblAkses u LEFT JOIN tblMenu j ON u.MenuId = j.MenuId) "
                f"LEFT JOIN tblGroupUser AS s ON u.GroupId = s.GroupId) WHERE s.GroupId= '{groupid}' "
            )
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT AksesId, GroupId FROM tblAkses order by AksesId")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll3(Resource):
        def get(self, *args, **kwargs):
            kode = kwargs.get('Kode')  # Pastikan parameter dikirim dengan benar

            # Pastikan bahwa kode bukan None dan bertipe string
            if kode is None or not isinstance(kode, str):
                return {"message": "Kode is required and should be a string."}, 400

            # Print nilai kode untuk debugging
            print(f"Kode: {kode}")

            # Jalankan subquery untuk memeriksa AksesId yang sudah ada di tblMenu dengan kode tertentu
            subquery_result = db.session.execute(
                f"""
                SELECT AksesId 
                FROM tblMenu 
                WHERE Kode = :kode
                """, {'kode': kode}).fetchall()

            # Print hasil subquery untuk debugging
            print(f"Subquery Result: {subquery_result}")

            # Filter AksesId yang tidak ada di tblMenu untuk kode tertentu
            select_query = db.session.execute(
                f"""
                SELECT AksesId, GroupId, MenuId 
                FROM tblAkses 
                WHERE AksesId NOT IN (
                    SELECT AksesId FROM tblMenu WHERE Kode = :kode
                )
                ORDER BY AksesId
                """, {'kode': kode})

            result = []
            for row in select_query:
                d = {key: getattr(row, key) for key in row.keys()}
                result.append(d)

            return success_reads(result)
    
    class ListAll4(Resource):
        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('GroupId', type=str)
            parser.add_argument('nested', type=int)
            args = parser.parse_args()

            result = []
            groupId = args['GroupId']
            parent_child = (tblMenu.query
                            .outerjoin(tblAkses, tblMenu.MenuId == tblAkses.MenuId)
                            # .filter(tblMenu.MenuId.not_in(
                            #         tblAkses.query.with_entities(tblAkses.MenuId)
                            #         .filter(tblAkses.GroupId == groupId)
                                    #     )
                                    # )
                            .order_by(tblMenu.Kode).all())
            # print(parent_child)
            for row in parent_child:
                d = row.to_dict()
                # print(d)
                last_digit = d['Kode'].strip('.').split('.')[-1]
                d['id'] = d['Kode'].replace(".", "")
                d['parent'] = d['id'][:-len(last_digit)]
                d['id'] = int(d['id']) if d['id'] else None

                d['parent'] = int(d['parent']) if d['parent'] else None
                d['depth'] = int(d['KdLevel'])

                if args['nested'] == 1:
                    # d['data'] = getattr( row, key )
                    d['data'] = row.to_dict()
                    # d['expanded'] = True if d['depth'] < 3 else False
                    d['cheked'] = True if d['depth'] == 5 else False
                    d['expanded'] = True if d['depth'] <= 4 else False
                result.append(d)
            #
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

                    res = build_children(1) #<--- root id
                    return res
                result = build_tree(result)
            return success_reads(result)

    class ListAll( Resource ):

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int, required=True, help="Page is required")
            parser.add_argument('length', type=int, required=True, help="Length is required")
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help="diisi dengan ASC atau DESC")
            parser.add_argument('search', type=str)

            args = parser.parse_args()
            # UserId = kwargs['claim']["UserId"]
            # print( UserId )
            print("Received Params:", args)  # Debugging Parameter

            # Jika page atau length tidak ada, return error
            if not args["page"] or not args["length"]:
                return {"message": "Page dan Length harus diisi"}, 400

            select_query = db.session.query( tblGroupUser.GroupId,tblGroupUser.code_group,
                                             tblGroupUser.nama_group)


            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format( args['search'] )
                select_query = select_query.filter(
                    or_( tblGroupUser.nama_group.ilike( search ),
                         tblGroupUser.code_group.ilike( search ) )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr( tblGroupUser, args['sort'] ).desc()
                else:
                    sort = getattr( tblGroupUser, args['sort'] ).asc()
                select_query = select_query.order_by( sort )
            else:
                select_query = select_query.order_by( tblGroupUser.code_group )

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate( page, lengthLimit )

            result = []
            for row in query_execute.items:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads_pagination( query_execute, result )


        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('GroupId', type=str)
            parser.add_argument('MenuId', type=list, location='json')  # Pastikan `MenuId` diterima sebagai list
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            # uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []

            menu_ids = args.get('MenuId', [])
            if not menu_ids:
                logger.warning('MenuId list is empty or not provided')
                return {'error': 'MenuId list is empty or not provided'}, 400

            for arg in menu_ids:
                if arg is None:
                    continue  # Skip if MenuId is None

                # Query tblMenu for each MenuId
                select_current_id = db.session.query(tblMenu).filter(tblMenu.MenuId == arg).first()
                if select_current_id is None:
                    logger.warning(f'MenuId {arg} tidak ditemukan di database.')
                    continue

                logger.info(select_current_id.MenuId)

                # Insert into tblAkses if Tipe is 'D'
                if select_current_id.Tipe == 'D':
                    add_record = tblAkses(
                        GroupId=args['GroupId'],
                        MenuId=select_current_id.MenuId,
                        UserUpd='admin',
                        DateUpd=datetime.now(),
                    )
                    db.session.add(add_record)

            # Commit all changes after loop
            db.session.commit()

            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById( Resource ):
        # method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
        #                      'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = tblAkses.query.filter_by( AksesId=id ).first()
                result = select_query.to_dict()
                return success_read( result )
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_read( {} )

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument( 'GroupId', type=str )
            parser.add_argument( 'MenuId', type=str )

            args = parser.parse_args()
            try:
                select_query = tblAkses.query.filter_by( AksesId=id ).first()
                if select_query:

                    if args['GroupId']:
                        select_query.GroupId = args['GroupId']
                    if args['MenuId']:
                        select_query.MenuId = args['MenuId']
                    select_query.UserUpd = 'admin'
                    select_query.DateUpd = datetime.now()
                    db.session.commit()
                    return success_update( {'id': id} )
            except Exception as e:

                db.session.rollback()
                print( e )
                return failed_update( {} )

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = tblAkses.query.filter_by( AksesId=id )
                delete_record.delete()
                db.session.commit()
                return success_delete( {} )
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_delete( {} )
