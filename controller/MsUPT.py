from datetime import datetime, timedelta
from functools import wraps

from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from sqlalchemy import or_, case
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads, failed_reads, success_create, failed_create
from config.database import db
from config.helper import toDict
from controller.GeneralParameter import GeneralParameter
from controller.tblGroupUser import tblGroupUser
from controller.tblUPTOpsen import tblUPTOpsen
from controller.tblUser import tblUser


class MsUPT( db.Model, SerializerMixin ):
    __tablename__ = 'MsUPT'
    UPTID = db.Column( db.String, primary_key=True )
    ParentID = db.Column( db.String, nullable=False )
    KodeUPT = db.Column( db.String, nullable=False )
    UPT = db.Column(db.String, nullable=False )
    AlamatUPT = db.Column( db.String, nullable=False )
    TelpUPT = db.Column( db.String, nullable=False )
    FaxUPT = db.Column( db.String, nullable=False )
    LevelUPT = db.Column( db.String, nullable=False )
    Status = db.Column( db.String, nullable=False )
    UserUpd = db.Column( db.String, nullable=False )
    DateUpd = db.Column( db.TIMESTAMP, nullable=False )
    KDUNIT = db.Column( db.String, nullable=False )
    kdurut = db.Column( db.String, nullable=False )

    class ListAll2(Resource):
        def get(self, *args, **kwargs):

            select_query = db.session.execute(
                f"SELECT UPTID, UPT FROM MsUPT u WHERE [Status]='1' AND LevelUPT=2 AND FaxUPT='Y'" )
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads( result )
            
            # select_query = MsUPT.query(MsUPT.UPTID, MsUPT.UPT).filter_by(Status=1, LevelUPT=3, FaxUPT='Y').order_by(MsUPT.UPT)
            # result = []
            # for row in select_query:
            #    result.append(toDict(row))
            # return success_reads(result)

    class ListAll3(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT UPTID AS Kode,'Pendapatan ' + (case when KodeUPT in (select kode_badan from vw_header) then "
                f"(select badan_singkat from vw_header) else UPT end) AS Nama FROM MsUPT u WHERE [Status]='1' "
                f"AND LevelUPT > 1 AND FaxUPT='Y'  ORDER BY Nama" )
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads(result)

    class ListAll4(Resource):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT Kode,Nama,KodeUPT FROM( "
                f"SELECT '0' AS Kode,(SELECT ' ' + badan_singkat FROM vw_header) AS Nama,'' AS KodeUPT union "
                f"SELECT UPTID AS Kode,UPT AS Nama,KodeUPT FROM MsUPT u WHERE [Status]='1'  AND LevelUPT > 1 AND KodeUPT  "
                f"<> (SELECT kode_badan FROM vw_header) AND UPTID NOT IN (select distinct UPTID from MsUPT where "
                f"LevelUPT=2 and UPT like '%camat%' and UPTID in (select distinct ParentID from MsUPT)) "
                f") x ORDER BY Nama" )
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads(result)

    class ListAll5(Resource):
        def get(self, *args, **kwargs):

            select_query = db.session.execute(
                f"SELECT KodeUPT, UPTID, UPT FROM MsUPT u WHERE [Status] = '1' AND LevelUPT = 2 order by KodeUPT" )
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads( result )

    class ListAll6(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege]}
        def get(self, *args, **kwargs):

            wapuid = kwargs['claim']["WapuID"]
            groupid = kwargs['claim']["GroupId"]
            checkadmin = tblGroupUser.query.filter_by(
                GroupId=groupid
            ).first()

            query1 = db.session.query(GeneralParameter.ParamStrValue).filter(
                GeneralParameter.ParamID == 'propid'
            ).first()
            kode_prov = str(query1[0]) if query1 else None

            query2 = db.session.query(tblUPTOpsen.UPTID).filter(
                tblUPTOpsen.KotaPropID.like(f"{kode_prov}%")
            ).all()
            uptid_list = [row[0] for row in query2] if query2 else []
            uptid_str = ','.join(f"'{id}'" for id in uptid_list)

            if checkadmin.IsAdmin == 1:
                select_query = db.session.execute(
                    f"SELECT DISTINCT su.WapuID,su.SetoranDari AS UPT FROM SetoranUPTHdr AS su  "
                    f"WHERE su.SetoranDari !='' AND su.SetoranDari !='-'  AND su.WapuID in({uptid_str})" )
            else:
                select_query = db.session.execute(
                    f"SELECT DISTINCT su.WapuID,su.SetoranDari AS UPT FROM SetoranUPTHdr AS su  "
                    f"WHERE su.SetoranDari !='' AND su.SetoranDari !='-' AND su.WapuID='{wapuid}' ")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads( result )

    class ListAll7(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege]}
        def get(self, *args, **kwargs):
            wapuid = kwargs['claim']["WapuID"]
            groupid = kwargs['claim']["GroupId"]
            checkadmin = tblGroupUser.query.filter_by(
                GroupId=groupid
            ).first()

            query1 = db.session.query(GeneralParameter.ParamStrValue).filter(
                GeneralParameter.ParamID == 'propid'
            ).first()
            kode_prov = str(query1[0]) if query1 else None

            query2 = db.session.query(tblUPTOpsen.UPTID).filter(
                tblUPTOpsen.KotaPropID.like(f"{kode_prov}%")
            ).all()
            uptid_list = [row[0] for row in query2] if query2 else []
            uptid_str = ','.join(f"'{id}'" for id in uptid_list)

            if checkadmin.IsAdmin == 1:
                select_query = db.session.execute(
                    f"SELECT * FROM tblUPTOpsen AS su WHERE su.UPTID IN({uptid_str}) "
                )
            else:
                select_query = db.session.execute(
                    f"SELECT * FROM tblUPTOpsen AS su WHERE su.UPTID= {wapuid}"
                )
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads( result )



    class ListAll8(Resource):
        def get(self, *args, **kwargs):

            select_query = db.session.execute(
                f"SELECT DISTINCT '' UPTID,su.KotaKendaraan AS UPT FROM tblOpsen AS su  "
            )
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads( result )


    class ListAll9(Resource):
        def auth_apikey_privilege(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                api_key = request.headers.get("APIKey")
                if not api_key:
                    return {"message": "Unauthorized, APIKey missing"}, 401
                return f(*args, **kwargs)

            return decorated_function
        method_decorators = {
            'get': [auth_apikey_privilege]
        }

        def get(self):
            print("Headers:", request.headers)
            print("Params:", request.args)

            api_key = request.headers.get('APIKey')
            print("APIKey diterima:", api_key)

            try:
                args = request.args
                nested = args.get("nested", type=int, default=0)
                kd_level = args.get("KdLevel", None)

                # Dummy user ID dari JWT (contoh)
                UserId = request.headers.get("UserId", "Guest")
                print("UserId:", UserId)

                print("KdLevel diterima di backend:", kd_level)
                parent_child = []  # ✅ Default agar tidak undefined
                result = []  # ✅ Pastikan result dideklarasikan sebelum digunakan

                # Query berdasarkan KdLevel
                if kd_level is not None:
                    if kd_level == '1':
                        parent_child = MsUPT.query.order_by(MsUPT.kdurut).all()
                    elif kd_level == '2':
                        parent_child = MsUPT.query.filter(MsUPT.LevelUPT <= 2).order_by(MsUPT.kdurut).all()
                    elif kd_level == '3':
                        parent_child = MsUPT.query.filter(MsUPT.LevelUPT <= 3).order_by(MsUPT.kdurut).all()

                for row in parent_child:
                    d = row.to_dict()

                    # ✅ Tambahkan NamaBadan
                    d['NamaBadan'] = d['UPT']

                    # ✅ Pastikan 'data' ada sebelum diakses
                    d['data'] = row.to_dict()
                    d['data']['NamaBadan'] = d['UPT']

                    last_digit = d['kdurut'].strip('.').split('.')[-1]
                    d['id'] = d['kdurut'].replace(".", "")
                    d['parent'] = d['id'][:-len(last_digit)]
                    d['id'] = int(d['id']) if d['id'] else None
                    d['parent'] = int(d['parent']) if d['parent'] else None
                    d['depth'] = int(d['LevelUPT'])

                    if nested == 1:
                        d['data'] = row.to_dict()
                        d['expanded'] = True if d['depth'] < 1 else False

                    result.append(d)  # ✅ Pastikan result sudah dideklarasikan

                # Jika nested == 1, ubah hasil ke dalam format tree
                if nested == 1:
                    def build_tree(elems):
                        set_relation = {}

                        def build_children(parent):
                            filter_result = [d for d in elems if d['id'] == parent]
                            cur_dict = filter_result[0] if filter_result else {}
                            if parent in set_relation.keys():
                                cur_dict["children"] = [build_children(child_id) for child_id in set_relation[parent]]
                                # ✅ Tambahkan NamaBadan ke setiap child dalam tree
                                cur_dict['NamaBadan'] = cur_dict.get('UPT', '')

                                # ✅ Pastikan 'data' ada sebelum diakses
                                if 'data' not in cur_dict:
                                    cur_dict['data'] = {}
                                cur_dict['data']['NamaBadan'] = cur_dict.get('UPT', '')

                                # ✅ Tambahkan NamaBadan di dalam setiap data children
                                if "children" in cur_dict:
                                    for child in cur_dict["children"]:
                                        if "data" not in child:
                                            child["data"] = {}
                                        child["data"]["NamaBadan"] = child.get("UPT", "")
                            return cur_dict

                        for item in elems:
                            child_id = item['id']
                            parent_id = item['parent']
                            set_relation.setdefault(parent_id, []).append(child_id)

                        root_id = 4  # Sesuaikan root ID
                        return build_children(root_id)

                    result = build_tree(result)  # ✅ Pastikan result dideklarasikan

                return success_reads(result)

            except Exception as e:
                print("Error:", str(e))
                return failed_reads(str(e))  # ✅ Gunakan string error agar bisa di-debug

    class ListAll(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument('filter_uptid', type=str)
            parser.add_argument('parentid', type=str)
            parser.add_argument('levelupt', type=str)
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC' )
            parser.add_argument('search', type=str)
            parser.add_argument('nested', type=int)
            parser.add_argument('KdLevel', type=str)

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            print(UserId)

            result = []
            try:
                print("KdLevel diterima di backend:", args['KdLevel'])

                parent_child = MsUPT.query.order_by(MsUPT.kdurut).all()

                for row in parent_child:
                    d = row.to_dict()
                    last_digit = d['kdurut'].strip('.').split('.')[-1]
                    d['id'] = d['kdurut'].replace(".", "")
                    d['parent'] = d['id'][:-len(last_digit)]
                    # d['parent'] = d['ParentID']
                    d['id'] = int(d['id']) if d['id'] else None

                    d['parent'] = int(d['parent']) if d['parent'] else None
                    d['depth'] = int(d['LevelUPT'])

                    if args['nested'] == 1:
                        # primeng tree table
                        d['data'] = row.to_dict()
                        d['expanded'] = True if d['depth'] < 1 else False
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

                        res = build_children(4)  # <--- root id
                        return res

                    result = build_tree(result)
                return success_reads(result)

            except Exception as e:
                print(e)
                return failed_reads(result)

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            # parser.add_argument('UPTID', type=str)
            parser.add_argument('ParentID', type=str)
            parser.add_argument('KodeUPT', type=str)
            parser.add_argument('UPT', type=str)
            parser.add_argument('AlamatUPT', type=str)
            parser.add_argument('TelpUPT', type=str)
            parser.add_argument('FaxUPT', type=str)
            parser.add_argument('LevelUPT', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)
            parser.add_argument('KDUNIT', type=str)

            uid = kwargs['claim']["UID"]

            try:
                args = parser.parse_args()
                result = []
                for row in result:
                    result.append( row )

                select_query = db.session.execute(
                    f"SELECT CAST(MAX(CAST(UPTID AS int) + 1) AS varchar(10)) AS NextID FROM MsUPT" )
                result2 = select_query.first()[0]
                uptid = result2

                add_record = MsUPT(
                    UPTID=uptid,
                    ParentID=args['ParentID'],
                    KodeUPT=args['KodeUPT'],
                    UPT=args['UPT'],
                    AlamatUPT=args['AlamatUPT'] if args['FaxUPT'] else '',
                    TelpUPT=args['TelpUPT'] if args['FaxUPT'] else '',
                    FaxUPT=args['FaxUPT'] if args['FaxUPT'] else '',
                    LevelUPT=args['LevelUPT'],
                    Status=1,
                    UserUpd=uid,
                    DateUpd=datetime.now(),
                    KDUNIT=args['KDUNIT']

                )
                db.session.add( add_record )
                db.session.commit()
                return success_create({'UPTID': add_record.UPTID,
                                       'ParentID': add_record.ParentID,
                                        'KodeUPT': add_record.KodeUPT,
                                        'UPT': add_record.UPT,
                                        'LevelUPT': add_record.LevelUPT
                                        })

            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_create({})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsUPT.query.filter_by(UPTID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            # parser.add_argument('UPTID', type=str)
            parser.add_argument('ParentID', type=str )
            parser.add_argument('KodeUPT', type=str )
            parser.add_argument('UPT', type=str )
            parser.add_argument('AlamatUPT', type=str )
            parser.add_argument('TelpUPT', type=str )
            parser.add_argument('FaxUPT', type=str )
            parser.add_argument('LevelUPT', type=str )
            parser.add_argument('GroupAttribute', type=str )
            parser.add_argument('Status', type=str )
            parser.add_argument('UserUpd', type=str )
            parser.add_argument('DateUpd', type=str )
            parser.add_argument('KDUNIT', type=str )

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            try:
                select_query = MsUPT.query.filter_by(UPTID=id).first()
                if select_query:
                    # select_query.UPTID = args['UPTID']
                    if args['ParentID'] :
                        select_query.ParentID = args['ParentID']
                    if args['KodeUPT']:
                        select_query.KodeUPT = args['KodeUPT']
                    if args['UPT']:
                        select_query.UPT = args['UPT']
                    if args['AlamatUPT']:
                        select_query.AlamatUPT = args['AlamatUPT']
                    if args['TelpUPT']:
                        select_query.TelpUPT = args['TelpUPT']
                    if args['FaxUPT']:
                        select_query.FaxUPT = args['FaxUPT']
                    if args['LevelUPT']:
                        select_query.LevelUPT = args['LevelUPT']
                    if args['Status']:
                        select_query.Status = args['Status']
                    select_query.UserUpd = uid
                    select_query.DateUpd = datetime.now()
                    if args['KDUNIT']:
                        select_query.KDUNIT = args['KDUNIT']
                    db.session.commit()
                    return success_create({'UPTID': select_query.UPTID,
                                           'ParentID': select_query.ParentID,
                                           'KodeUPT': select_query.KodeUPT,
                                           'UPT': select_query.UPT,
                                           'LevelUPT': select_query.LevelUPT
                                           })
            except Exception as e:

                db.session.rollback()
                print(e)
                return failed_update({})

        def delete(self, id, *args, **kwargs):
            try:
                delete_record = MsUPT.query.filter_by(UPTID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print( e )
                return failed_delete({})
