from datetime import datetime

from flask import jsonify, request
from flask_restful import Resource, reqparse
from sqlalchemy import or_, func, UniqueConstraint
from sqlalchemy_serializer import SerializerMixin

from config.api_message import success_reads_pagination, success_read, failed_read, \
    success_update, failed_update, success_delete, failed_delete, success_reads, success_create, failed_create
from config.database import db
from config.helper import logger
from controller.tblMenu import tblMenu
from controller.tblUrl import tblUrl
# from controller.tblUser import tblUser


class tblMenuDet(db.Model, SerializerMixin):

    __tablename__ = 'tblMenuDet'
    DetailId = db.Column(db.Integer, primary_key=True)
    UrlId = db.Column(db.Integer, nullable=True)
    MenuId = db.Column(db.Integer, nullable=True)

    __table_args__ = (UniqueConstraint('MenuId', 'UrlId', name='uq_MenuId_urlid'),)

    def to_dict(self):
        return {
            'DetailId': self.DetailId,
            'UrlId': self.UrlId,
            'MenuId': self.MenuId
        }
    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT DISTINCT DetailID, MenuId, UrlId FROM tblMenuDet")
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
                f"SELECT DetailId, d.MenuId, u.UrlId, u.Url FROM tblMenuDet d "
                f"LEFT JOIN tblUrl u ON u.UrlId=d.UrlId WHERE MenuId={menuid} order by DetailId")

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
            parent_child = tblMenuDet.query.order_by(tblMenuDet.DetailId).all()

            # for row in parent_child:
            #     d = row.to_dict()
            #     print(d)
            #     last_digit = d['DetailID'].strip('.').split('.')[-1]
            #     print(last_digit)
            #     d['id'] = d['DetailID'].replace(".", "")
            #     d['parent'] = d['id'][:-len(last_digit)]
            #     d['id'] = int(d['id']) if d['id'] else None
            #
            #     d['parent'] = int(d['parent']) if d['parent'] else None
            #     d['depth'] = int(d['MenuId'])
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
                if d['DetailID']:
                    last_digit = d['DetailID'].strip('.').split('.')[-1]
                    d['id'] = d['DetailID'].replace(".", "")  # Tetap sebagai string untuk pemeriksaan panjang
                    d['parent'] = int(d['id'][:-len(last_digit)]) if len(d['id']) > len(last_digit) else None

                else:
                    d['id'] = None
                    d['parent'] = None

                d['depth'] = int(d['MenuId'])

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
                db.session.query(tblMenuDet.DetailId, tblMenuDet.UrlId,
                                 tblUrl.Url,tblMenuDet.MenuId)
                .outerjoin(tblUrl, tblMenuDet.UrlId == tblMenu.UrlId)
                )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format( args['search'] )
                select_query = select_query.filter(
                    or_( tblMenuDet.DetailID.ilike( search ),
                         tblMenuDet.MenuId.ilike( search ),
                         tblMenuDet.Url.ilike(search))

                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr( tblMenuDet, args['sort'] ).desc()
                else:
                    sort = getattr( tblMenuDet, args['sort'] ).asc()
                select_query = select_query.order_by( sort )
            else:
                select_query = select_query.order_by( tblMenuDet.DetailID )

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
            parser.add_argument('MenuId', type=str, required=True)
            parser.add_argument('UrlId', type=int, action='append', location='json', required=True)

            args = parser.parse_args()
            result = []

            url_ids = args.get('UrlId', [])
            if not url_ids:
                logger.warning('UrlId list is empty or not provided')
                return {'error': 'UrlId list is empty or not provided'}, 400

            for arg in url_ids:
                if arg is None:
                    continue  # Skip if UrlId is None

                # Query tblUrl untuk setiap UrlId
                select_current_id = db.session.query(tblUrl).filter(tblUrl.UrlId == arg).first()
                if select_current_id is None:
                    logger.warning(f'UrlId {arg} tidak ditemukan di database.')
                    continue

                logger.info(f'UrlId ditemukan: {select_current_id.UrlId}')
                result.append(select_current_id.UrlId)

                # Tambahkan record ke tblMenuDet
                add_record = tblMenuDet(
                    MenuId=args['MenuId'],
                    UrlId=select_current_id.UrlId
                )
                db.session.add(add_record)  # Tambah record di sini untuk setiap UrlId yang valid

            # Commit hanya setelah semua record ditambahkan
            db.session.commit()

            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})
        # def post(self, *args, **kwargs):
        #     parser = reqparse.RequestParser()
        #     # parser.add_argument( 'DetailID', type=str )
        #     parser.add_argument( 'MenuId', type=str )
        #     parser.add_argument('UrlId', type=int, action='append', location='json', required=True)  # Ubah ke type=int
        #
        #     args = parser.parse_args()
        #     result = []
        #
        #     url_ids = args.get('UrlId', [])
        #     if not url_ids:
        #         logger.warning('UrlId list is empty or not provided')
        #         return {'error': 'UrlId list is empty or not provided'}, 400
        #
        #     for arg in url_ids:
        #         if arg is None:
        #             continue  # Skip if UrlId is None
        #
        #         # Query tblMenu for each MenuId
        #         select_current_id = db.session.query(tblUrl).filter(tblUrl.UrlId == arg).first()
        #         if select_current_id is None:
        #             logger.warning(f'UrlId {arg} tidak ditemukan di database.')
        #             continue
        #
        #         logger.info(select_current_id.UrlId)
        #         result.append(select_current_id.UrlId)
        #
        #     add_record = tblMenuDet(
        #         # DetailID=args['DetailID'],
        #         MenuId=args['MenuId'] if args['MenuId'] else None,
        #         UrlId=select_current_id.UrlId
        #
        #     )
        #     db.session.add( add_record )
        #     db.session.commit()
        #     return jsonify( {'status_code': 1, 'message': 'OK', 'data': result} )

    class AddUrl(Resource):

        def post(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('UrlId', action='append', required=True, nullable=False, location='json',
                                help="UrlId cannot be blank!")

            try:
                args = parser.parse_args()
                select_query = tblMenuDet.query.filter_by(DetailId=id).first()
                result = {'success': [], 'failed': []}
                if select_query:
                    data = {
                        'MenuId': select_query.MenuId,
                        'UrlId': select_query.UrlId,
                    }

                    if isinstance(args['UrlId'], list):
                        # Pastikan args['Url'] tidak None dan merupakan list
                        if args['Url'] is None or not isinstance(args['Url'], list):
                            args['Url'] = []  # Default ke list kosong jika tidak ada Url yang dikirim

                        for i, url_id in enumerate(args['UrlId']):
                            # Jika args['Url'] adalah list yang valid, ambil URL sesuai indeks, atau gunakan None
                            url = args['Url'][i] if i < len(args['Url']) else None
                            data['UrlId'] = url_id
                            data['Url'] = url

                            add_record_detail = tblMenuDet.AddMenuDetil(data)

                            if add_record_detail:
                                result['success'].append(add_record_detail.to_dict())  # Menyimpan objek
                            else:
                                result['failed'].append({'UrlId': url_id, 'Url': url})

                        db.session.commit()  # Commit setelah seluruh loop selesai


                    else:
                        # Kondisi single
                        data['UrlId'] = args['UrlId'][0] if isinstance(args['UrlId'], list) else args['UrlId']
                        data['Url'] = args['Url'][0] if isinstance(args['Url'], list) else args['Url']
                        add_record_detail = tblMenuDet.AddMenuDetil(data)

                        if add_record_detail:
                            result['success'].append(add_record_detail.to_dict())
                        else:
                            result['failed'].append({'UrlId': data['UrlId'], 'Url': data['Url']})

                        db.session.commit()

                    if result['success']:
                        return success_create({'DetailId': select_query.DetailId, 'success': result['success']})
                    else:
                        return failed_create({'failed': result['failed']})

            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_create({})

    def AddMenuDetil(data):
        try:
            # Cari data header berUrlId 'H' untuk mendapatkan DetailId sebagai ParentId
            header = db.session.query(tblMenuDet.DetailId).filter_by(DetailID=data['DetailID'], UrlId='H').first()

            if header:
                parentid = header.DetailId  # Gunakan DetailId dari Header sebagai ParentId
            else:
                # Jika Header tidak ditemukan, ambil data berUrlId 'D' terakhir
                last_d_entry = db.session.query(
                    tblMenuDet.DetailId,
                    tblMenuDet.DetailID,
                    tblMenuDet.ParentId
                ).filter(tblMenuDet.DetailID.like(f"{data['DetailID']}%"), tblMenuDet.UrlId == 'D').order_by(
                    tblMenuDet.DetailID.desc()).first()

                if last_d_entry:
                    parentid = last_d_entry.ParentId
                else:
                    raise ValueError(f"Tidak ada data berUrlId 'H' atau 'D' untuk DetailID {data['DetailID']}.")

            # Cari entri berUrlId 'D' terakhir yang sesuai dengan DetailID untuk melanjutkan DetailID
            last_entry = db.session.query(
                tblMenuDet.DetailId,
                tblMenuDet.DetailID
            ).filter(tblMenuDet.DetailID.like(f"{data['DetailID']}%"), tblMenuDet.UrlId == 'D').order_by(
                tblMenuDet.DetailID.desc()).first()

            # Tentukan nilai id_menu dan DetailID baru
            if last_entry:
                clean_id_menu = last_entry.DetailID.replace('.', '').strip()
                last_digit_str = clean_id_menu[-2:]
                if last_digit_str.isdigit():
                    last_digit = int(last_digit_str) + 1
                else:
                    raise ValueError(f"Unexpected id_menu format: {last_entry.id_menu}, cleaned: {clean_id_menu}")
                new_kode = f"{data['DetailID']}{str(last_digit).zfill(2)}."
            else:
                new_kode = f"{data['DetailID']}01."

            # Insert record baru berUrlId 'D'
            add_record = tblMenuDet(
                DetailID=new_kode,
                MenuId=data['MenuId'],
                UrlId=data['UrlId'],
            )
            db.session.add(add_record)
            return add_record  # Kembalikan objek add_record, bukan boolean

        except Exception as e:
            print(e)
            db.session.rollback()  # Rollback jika terjadi error
            return False

    # def post(self, *args, **kwargs):

    # try:
    #         parser = reqparse.RequestParser()
    #         parser.add_argument('DetailID', type=str)
    #         parser.add_argument('MenuId', type=str)
    #         parser.add_argument('UrlId', type=str)
    # 
    #         args = request.get_json()
    #         uid = kwargs['claim']["UID"]
    # 
    #         logger.info(args)
    # 
    #         for arg in args['UrlId']:
    #             # logger.info(arg)
    #             select_current_id = db.session.query(tblMenu).filter(tblMenu.UrlId == arg).first()
    #             # logger.info(select_current_id.UrlId)
    #             if select_current_id:
    #                 select_query = tblMenuDet.query.filter_by(UrlId=arg).first()
    #                 if select_query:
    #                     add_record = tblMenuDet(
    #                         UrlId=select_current_id.UrlId,
    #                         DetailID=select_query.DetailID,
    #                         MenuId=select_query.MenuId,
    #                         UrlId=select_query.UrlId,
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
                select_query = tblMenuDet.query.filter_by( DetailId=id ).first()
                result = select_query.to_dict()
                return success_read( result )
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_read( {} )

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            # print( kwargs['claim'] )
            parser.add_argument( 'DetailID', type=str )
            parser.add_argument( 'MenuId', type=str )
            parser.add_argument('UrlId', type=str)
            # parser.add_argument('UserUpd', type=str)
            # parser.add_argument('DateUpd', type=str)

            # uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = tblMenuDet.query.filter_by( DetailId=id ).first()
                if select_query:

                    if args['DetailID']:
                        select_query.Url = args['DetailID']
                    if args['MenuId']:
                        select_query.MenuId = args['MenuId']
                    if args['UrlId']:
                        select_query.MenuId = args['UrlId']
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
                delete_record = tblMenuDet.query.filter_by( DetailId=id )
                delete_record.delete()
                db.session.commit()
                return success_delete( {} )
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_delete( {} )