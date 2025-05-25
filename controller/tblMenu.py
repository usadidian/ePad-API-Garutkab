from datetime import datetime

from flask import jsonify, request
from flask_restful import Resource, reqparse
from sqlalchemy import or_, func, UniqueConstraint
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination, success_read, failed_read, \
    success_update, failed_update, success_delete, failed_delete, success_reads, success_create, failed_create
from config.database import db
from config.helper import logger
from controller.tblUrl import tblUrl


class tblMenu(db.Model, SerializerMixin):

    __tablename__ = 'tblMenu'
    MenuId = db.Column(db.Integer, primary_key=True)
    Kode = db.Column(db.String, nullable=True)
    ParentId = db.Column(db.Integer, nullable=True)
    Menu = db.Column(db.String, nullable=True)
    Tipe = db.Column(db.String, nullable=True)
    UrlId = db.Column(db.Integer, db.ForeignKey('tblUrl.UrlId'), nullable=True)
    KdLevel = db.Column(db.Integer, nullable=True)

    __table_args__ = (UniqueConstraint('ParentId', 'UrlId', name='uq_parentid_urlid'),)

    def to_dict(self):
        return {
            'MenuId': self.MenuId,
            'Kode': self.Kode,
            'ParentId': self.ParentId,
            'Menu': self.Menu,
            'Tipe': self.Tipe,
            'UrlId': self.UrlId,
            'KdLevel': self.KdLevel
        }
    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT DISTINCT Kode, Menu, Tipe FROM tblMenu")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll3(Resource):
        def get(self,  menuid,*args, **kwargs):
            select_query = db.session.execute(
                f"SELECT MenuId, Kode, Menu, Tipe FROM tblMenuDet WHERE MenuId={menuid} order by MenuId")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)
    

    class ListAll4(Resource):
        def get(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('nested', type=int)
            args = parser.parse_args()

            # PARSING PARAMETER DARI REQUEST
            # UserId = kwargs['claim']["UserId"]
            result = []
            parent_child = tblMenu.query.order_by(tblMenu.MenuId).all()

            # for row in parent_child:
            #     d = row.to_dict()
            #     print(d)
            #     last_digit = d['Kode'].strip('.').split('.')[-1]
            #     print(last_digit)
            #     d['id'] = d['Kode'].replace(".", "")
            #     d['parent'] = d['id'][:-len(last_digit)]
            #     d['id'] = int(d['id']) if d['id'] else None
            #
            #     d['parent'] = int(d['parent']) if d['parent'] else None
            #     d['depth'] = int(d['KdLevel'])
            #
            #     if args['nested'] == 1:
            #         #primeng tree table
            #         d['data'] = row.to_dict()
            #         # d['expanded'] = True if d['depth'] <= 3 else False
            #         d['expanded'] = True if d['depth'] <= 2 else False
            #     result.append(d)

            if not parent_child:
                return {"message": "No menu items found"}, 404
            for row in parent_child:
                d = row.to_dict()

                # Mengambil last_digit dan membangun id dan parent
                if d['Kode']:
                    last_digit = d['Kode'].strip('.').split('.')[-1]
                    d['id'] = d['Kode'].replace(".", "")  # Tetap sebagai string untuk pemeriksaan panjang
                    d['parent'] = int(d['id'][:-len(last_digit)]) if len(d['id']) > len(last_digit) else None

                else:
                    d['id'] = None
                    d['parent'] = None

                d['depth'] = int(d['KdLevel'])

                if args['nested'] == 1:
                    d['data'] = row.to_dict()
                    d['expanded'] = True if d['depth'] <= 1 else False

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

                    res = build_children(1) #<--- root id
                    return res
                result = build_tree(result)
            return success_reads(result)

    class ListAll( Resource ):
        # method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument( 'page', type=int )
            parser.add_argument( 'length', type=int )
            parser.add_argument( 'sort', type=str )
            parser.add_argument( 'sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC' )
            parser.add_argument( 'search', type=str )

            args = parser.parse_args()
            # UserId = kwargs['claim']["UserId"]
            # print( UserId )
            select_query = (
                db.session.query(tblMenu.MenuId, tblMenu.Kode, tblMenu.Menu, tblUrl.Url, tblMenu.UrlId,
                                 tblMenu.Tipe, tblMenu.KdLevel)
                .outerjoin(tblUrl, tblMenu.UrlId == tblUrl.UrlId)
                ).filter(tblMenu.ParentId != None)

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format( args['search'] )
                select_query = select_query.filter(
                    or_( tblMenu.Kode.ilike( search ),
                         tblMenu.Menu.ilike( search ) )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr( tblMenu, args['sort'] ).desc()
                else:
                    sort = getattr( tblMenu, args['sort'] ).asc()
                select_query = select_query.order_by( sort )
            else:
                select_query = select_query.order_by( tblMenu.Kode )

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
            parser.add_argument( 'Kode', type=str )
            parser.add_argument( 'Menu', type=str )
            parser.add_argument('Tipe', type=str)
            parser.add_argument( 'UrlId', type=str )

            args = parser.parse_args()
            result = []
            for row in result:
                result.append( row )

            result = db.session.query(
                func.replace(func.rtrim(tblMenu.Kode), '.', '')
            ).filter(tblMenu.Kode == args['Kode']).all()

            id = [row[0] for row in result]

            add_record = tblMenu(
                Kode=args['Kode'],
                Menu=args['Menu'] if args['Menu'] else '-',
                Tipe=args['Tipe'] if args['Tipe'] else 'D',
                KdLevel=args['Tipe'] if args['Tipe'] else '',
                UrlId=args['UrlId'],

            )
            db.session.add( add_record )
            db.session.commit()
            return jsonify( {'status_code': 1, 'message': 'OK', 'data': result} )

    # class AddUrl(Resource):
    #     method_decorators = {'post': [tblUser.auth_apikey_privilege]}
    #
    #     def post(self, id, *args, **kwargs):
    #         parser = reqparse.RequestParser()
    #         parser.add_argument('UrlId', action='append', required=True, nullable=False,
    #                             help="UrlId cannot be blank!")
    #         parser.add_argument('Url', action='append', required=False, nullable=False,
    #                             help="Url cannot be blank!")
    #
    #         try:
    #             args = parser.parse_args()
    #             select_query = tblMenu.query.filter_by(MenuId=id).first()
    #             result = {'success': [], 'failed': []}
    #             if select_query:
    #                 data = {
    #                     'Kode': select_query.Kode,
    #                     'Menu': select_query.Menu,
    #                     'Tipe': select_query.Tipe,
    #                 }
    #
    #                 if isinstance(args['UrlId'], list):
    #                     # Pastikan args['Url'] tidak None dan merupakan list
    #                     if args['Url'] is None or not isinstance(args['Url'], list):
    #                         args['Url'] = []  # Default ke list kosong jika tidak ada Url yang dikirim
    #
    #                     for i, url_id in enumerate(args['UrlId']):
    #                         # Jika args['Url'] adalah list yang valid, ambil URL sesuai indeks, atau gunakan None
    #                         url = args['Url'][i] if i < len(args['Url']) else None
    #                         data['UrlId'] = url_id
    #                         data['Url'] = url
    #
    #                         add_record_detail = tblMenu.AddMenuDetil(data)
    #
    #                         if add_record_detail:
    #                             result['success'].append(add_record_detail.to_dict())  # Menyimpan objek
    #                         else:
    #                             result['failed'].append({'UrlId': url_id, 'Url': url})
    #
    #                     db.session.commit()  # Commit setelah seluruh loop selesai
    #
    #
    #                 else:
    #                     # Kondisi single
    #                     data['UrlId'] = args['UrlId'][0] if isinstance(args['UrlId'], list) else args['UrlId']
    #                     data['Url'] = args['Url'][0] if isinstance(args['Url'], list) else args['Url']
    #                     add_record_detail = tblMenu.AddMenuDetil(data)
    #
    #                     if add_record_detail:
    #                         result['success'].append(add_record_detail.to_dict())
    #                     else:
    #                         result['failed'].append({'UrlId': data['UrlId'], 'Url': data['Url']})
    #
    #                     db.session.commit()
    #
    #                 if result['success']:
    #                     return success_create({'MenuId': select_query.MenuId, 'success': result['success']})
    #                 else:
    #                     return failed_create({'failed': result['failed']})
    #
    #         except Exception as e:
    #             db.session.rollback()
    #             print(e)
    #             return failed_create({})
    #
    # def AddMenuDetil(data):
    #     try:
    #         # Cari data header bertipe 'H' untuk mendapatkan MenuId sebagai ParentId
    #         header = db.session.query(tblMenu.MenuId).filter_by(Kode=data['Kode'], Tipe='H').first()
    #
    #         if header:
    #             parentid = header.MenuId  # Gunakan MenuId dari Header sebagai ParentId
    #         else:
    #             # Jika Header tidak ditemukan, ambil data bertipe 'D' terakhir
    #             last_d_entry = db.session.query(
    #                 tblMenu.MenuId,
    #                 tblMenu.Kode,
    #                 tblMenu.ParentId
    #             ).filter(tblMenu.Kode.like(f"{data['Kode']}%"), tblMenu.Tipe == 'D').order_by(
    #                 tblMenu.Kode.desc()).first()
    #
    #             if last_d_entry:
    #                 parentid = last_d_entry.ParentId
    #             else:
    #                 raise ValueError(f"Tidak ada data bertipe 'H' atau 'D' untuk Kode {data['Kode']}.")
    #
    #         # Cari entri bertipe 'D' terakhir yang sesuai dengan Kode untuk melanjutkan Kode
    #         last_entry = db.session.query(
    #             tblMenu.MenuId,
    #             tblMenu.Kode
    #         ).filter(tblMenu.Kode.like(f"{data['Kode']}%"), tblMenu.Tipe == 'D').order_by(
    #             tblMenu.Kode.desc()).first()
    #
    #         # Tentukan nilai id_menu dan Kode baru
    #         if last_entry:
    #             clean_id_menu = last_entry.Kode.replace('.', '').strip()
    #             last_digit_str = clean_id_menu[-2:]
    #             if last_digit_str.isdigit():
    #                 last_digit = int(last_digit_str) + 1
    #             else:
    #                 raise ValueError(f"Unexpected id_menu format: {last_entry.id_menu}, cleaned: {clean_id_menu}")
    #             new_kode = f"{data['Kode']}{str(last_digit).zfill(2)}."
    #         else:
    #             new_kode = f"{data['Kode']}01."
    #
    #         # Insert record baru bertipe 'D'
    #         add_record = tblMenu(
    #             Kode=new_kode,
    #             ParentId=parentid,  # ParentId diambil dari Header atau dari D sebelumnya
    #             Menu=data['Menu'],
    #             Tipe='D',
    #             KdLevel=5,
    #             UrlId=data['UrlId'],
    #         )
    #         db.session.add(add_record)
    #         return add_record  # Kembalikan objek add_record, bukan boolean
    #
    #     except Exception as e:
    #         print(e)
    #         db.session.rollback()  # Rollback jika terjadi error
    #         return False

    # def post(self, *args, **kwargs):

    # try:
    #         parser = reqparse.RequestParser()
    #         parser.add_argument('Kode', type=str)
    #         parser.add_argument('Menu', type=str)
    #         parser.add_argument('Tipe', type=str)
    # 
    #         args = request.get_json()
    #         uid = kwargs['claim']["UID"]
    # 
    #         logger.info(args)
    # 
    #         for arg in args['UrlId']:
    #             # logger.info(arg)
    #             select_current_id = db.session.query(tblUrl).filter(tblUrl.UrlId == arg).first()
    #             # logger.info(select_current_id.UrlId)
    #             if select_current_id:
    #                 select_query = tblMenu.query.filter_by(UrlId=arg).first()
    #                 if select_query:
    #                     add_record = tblMenu(
    #                         UrlId=select_current_id.UrlId,
    #                         Kode=select_query.Kode,
    #                         Menu=select_query.Menu,
    #                         Tipe=select_query.Tipe,
    #                     )
    #                     db.session.add(add_record)
    #                     db.session.flush()
    # 
    #         db.session.commit()
    #         return success_create({})
    # 
    #     except Exception as e:
    #         db.session.rollback()
    #         logger.error(e)
    #         return failed_create({})

    class ListById( Resource ):
        # method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
        #                      'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = tblMenu.query.filter_by( MenuId=id ).first()
                result = select_query.to_dict()
                return success_read( result )
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_read( {} )

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            # print( kwargs['claim'] )
            parser.add_argument( 'Kode', type=str )
            parser.add_argument( 'Menu', type=str )
            parser.add_argument('Tipe', type=str)
            # parser.add_argument('UserUpd', type=str)
            # parser.add_argument('DateUpd', type=str)

            # uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = tblMenu.query.filter_by( MenuId=id ).first()
                if select_query:

                    if args['Kode']:
                        select_query.Url = args['Kode']
                    if args['Menu']:
                        select_query.Menu = args['Menu']
                    if args['Tipe']:
                        select_query.Menu = args['Tipe']
                    # select_query.UserUpd = uid
                    select_query.DateUpd = datetime.now()
                    db.session.commit()
                    return success_update( {'id': id} )
            except Exception as e:

                db.session.rollback()
                print( e )
                return failed_update( {} )

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = tblMenu.query.filter_by( MenuId=id )
                delete_record.delete()
                db.session.commit()
                return success_delete( {} )
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_delete( {} )