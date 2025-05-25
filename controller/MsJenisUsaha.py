from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_, case
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.tblUser import tblUser



class MsJenisUsaha(db.Model, SerializerMixin):
    __tablename__ = 'MsJenisUsaha'
    UsahaID = db.Column(db.Integer, primary_key=True)
    NamaUsaha = db.Column(db.String, nullable=False)
    TarifUsaha = db.Column(db.Numeric(12, 2), nullable=False)
    Persen = db.Column(db.Numeric(12, 2), nullable=False)
    Satuan = db.Column(db.String, nullable=False)
    Status = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    JenisPendapatanID = db.Column(db.String, db.ForeignKey('MsJenisPendapatan.JenisPendapatanID'), nullable=False)

    class ListAll2(Resource):
        def get(self, jenispendapatanid, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT UsahaID,NamaUsaha AS Usaha FROM MsJenisUsaha WHERE JenisPendapatanID = '{jenispendapatanid}' "
                f"AND [Status] = '1' ORDER BY Usaha")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    if key == 'TarifUsaha' or key == 'Persen':
                        d[key] = str(getattr(row, key))
                    else:
                        d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll2(Resource):
        def get(self, usahaid, jenispendapatanid, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT UsahaID,NamaUsaha AS Usaha FROM MsJenisUsaha WHERE JenisPendapatanID = '{jenispendapatanid}' "
                f"AND [Status] = '1' ORDER BY Usaha")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    if key == 'TarifUsaha' or key == 'Persen':
                        d[key] = str(getattr(row, key))
                    else:
                        d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'post': [tblUser.auth_apikey_privilege]}

        def get(self, *args, **kwargs):

            # PARSING PARAMETER DARI REQUEST
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan ASC atau DSC')
            parser.add_argument('search', type=str)
            parser.add_argument('jenis_perolehan', type=int)

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            print(UserId)
            select_query = db.session.query(MsJenisUsaha.UsahaID, MsJenisUsaha.JenisPendapatanID, MsJenisUsaha.NamaUsaha,
                                            MsJenisUsaha.TarifUsaha, MsJenisUsaha.Persen, MsJenisUsaha.Satuan,
                                            MsJenisUsaha.Status,
                                            case( [
                                                (MsJenisUsaha.Status == 1, 'Aktif')], else_='Non Aktif' ).label(
                                                'NamaStatus' )
                                            ).filter(MsJenisUsaha.JenisPendapatanID == '10')

            if args['jenis_perolehan'] and args['jenis_perolehan'] != 'null':
                select_query = select_query.filter_by(JenisPendapatanID=10).order_by(MsJenisUsaha.NamaUsaha).all()
                result = []
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr( row, key )
                    result.append( d )
                return success_reads( result )
            else:
                # SEARCH
                if args['search'] and args['search'] != 'null':
                    search = '%{0}%'.format(args['search'])
                    select_query = select_query.filter(
                        or_(MsJenisUsaha.TarifUsaha.ilike(search),
                            MsJenisUsaha.NamaUsaha.ilike(search))
                    )

                # SORT
                if args['sort']:
                    if args['sort_dir'] == "desc":
                        sort = getattr(MsJenisUsaha, args['sort']).desc()
                    else:
                        sort = getattr(MsJenisUsaha, args['sort']).asc()
                    select_query = select_query.order_by(sort)
                else:
                    select_query = select_query.order_by(MsJenisUsaha.NamaUsaha)

                # PAGINATION
                page = args['page'] if args['page'] else 1
                length = args['length'] if args['length'] else 10
                lengthLimit = length if length < 101 else 100
                query_execute = select_query.paginate(page, lengthLimit)

                result = []
                for row in query_execute.items:
                    d = {}
                    for key in row.keys():
                        if key == 'TarifUsaha':
                            d[key] = str( getattr( row, key ) )
                        else:
                            d[key] = getattr( row, key )
                    result.append( d )
                return success_reads_pagination( query_execute, result )

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            # parser.add_argument('UsahaID', type=str)
            parser.add_argument('JenisPendapatanID', type=str)
            parser.add_argument('NamaUsaha', type=str)
            parser.add_argument('TarifUsaha', type=str)
            parser.add_argument('Persen', type=str)
            parser.add_argument('Satuan', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            add_record = MsJenisUsaha(
                # UsahaID=args['UsahaID'],
                JenisPendapatanID=args['JenisPendapatanID'],
                NamaUsaha=args['NamaUsaha'],
                TarifUsaha=args['TarifUsaha'],
                Persen=args['Persen'],
                Satuan=args['Satuan'],
                Status=1,
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
                select_query = MsJenisUsaha.query.filter_by(UsahaID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            # parser.add_argument('UsahaID', type=str)
            parser.add_argument('JenisPendapatanID', type=str)
            parser.add_argument('NamaUsaha', type=str)
            parser.add_argument('TarifUsaha', type=str)
            parser.add_argument('Persen', type=str)
            parser.add_argument('Satuan', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            args = parser.parse_args()
            # if args['Status'] == 'Aktif':
            #     status = 1
            # if args['Status'] == 'Non Aktif':
            #     status = 0
            try:
                select_query = MsJenisUsaha.query.filter_by(UsahaID=id).first()
                if select_query:
                    # select_query.UsahaID = args['UsahaID']
                    select_query.JenisPendapatanID = args['JenisPendapatanID']
                    select_query.NamaUsaha = args['NamaUsaha']
                    select_query.TarifUsaha = args['TarifUsaha']
                    select_query.Persen = args['Persen']
                    select_query.Satuan = args['Satuan']
                    if args['Status']:
                        select_query.Status = args['Status']
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
                delete_record = MsJenisUsaha.query.filter_by(UsahaID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})