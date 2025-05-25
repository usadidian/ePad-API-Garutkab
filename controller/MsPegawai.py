from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_, case
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.GeneralParameter import GeneralParameter
from controller.MsUPT import MsUPT
from controller.tblUser import tblUser
from controller.vw_pegawai import vw_pegawai


class MsPegawai(db.Model, SerializerMixin):
    __tablename__ = 'MsPegawai'
    Idpegawai = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    PegawaiID = db.Column(db.String, primary_key=True)
    NIP = db.Column(db.String, nullable=False)
    Jabatan = db.Column(db.String, nullable=False)
    Nama= db.Column(db.String, nullable=False)
    Pangkat= db.Column(db.String, nullable=False)
    Status = db.Column(db.String, nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    UPTID = db.Column(db.String, db.ForeignKey('MsPegawai.UPTID'), nullable=False)

    class ListAll2(Resource):
        def get(self, *args, **kwargs):
            # select_query = db.session.execute(
            #     f"SELECT PegawaiID AS PetugasID, Nama AS Petugas FROM MsPegawai WHERE [Status]='1' AND UPTID = "
            #     f"(SELECT mu.UPTID FROM MsUPT AS mu WHERE mu.KDUNIT IN(SELECT gp.ParamStrValue "
            #     f"FROM GeneralParameter AS gp WHERE gp.ParamID='satker_sipkd') AND RIGHT(mu.KodeUPT,3)='01.') "
            #     f"ORDER BY Petugas ")

            parser = reqparse.RequestParser()
            parser.add_argument('search', type=str)
            parser.add_argument('length', type=str)
            args = parser.parse_args()
            kd_unit_global = db.session.query(GeneralParameter.ParamStrValue).filter(GeneralParameter.ParamID == 'satker_sipkd').scalar()
            subquery2 = db.session.query(MsUPT.UPTID).filter(MsUPT.KodeUPT.endswith('05.'), MsUPT.KDUNIT == kd_unit_global).scalar()
            select_query = db.session.query(MsPegawai.PegawaiID.label("PetugasID"), MsPegawai.Nama.label("Petugas"), MsPegawai.NIP, MsPegawai.Nama)\
                .filter(MsPegawai.Status == '1', MsPegawai.UPTID == subquery2)
            if args['search'] and len(args['search']) > 0:
                search = "%{}%".format(args['search'])
                select_query = select_query.filter(MsPegawai.Nama.like(search))
            select_query = select_query.order_by(MsPegawai.Nama).limit(args['length'] or 5)
            result = []
            if select_query:
                for row in select_query:
                    d = {}
                    for key in row.keys():
                        d[key] = getattr(row, key)
                    result.append(d)
            return success_reads(result)

    class ListAll3(Resource):
        def get(self, uptid, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT PegawaiID AS PetugasID, Nama AS Petugas FROM MsPegawai WHERE [Status]='1' AND UPTID = '{uptid}'"
                f"ORDER BY Petugas ")
            result=[]
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll4(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege]}

        def get(self, uptid, *args, **kwargs):
            PegawaiID = kwargs['claim']["PegawaiID"]
            select_query = db.session.query(MsPegawai.UPTID).join(tblUser).filter(
                tblUser.PegawaiID == PegawaiID, MsPegawai.PegawaiID == PegawaiID).first()
            result = select_query[0]
            uptid = result
            select_query = db.session.execute(
                f"SELECT PegawaiID AS PetugasID, Nama AS Petugas FROM MsPegawai WHERE [Status]='1' AND UPTID = '{uptid}'"
                f"ORDER BY Petugas ")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll5( Resource ):
        def get(self, *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT mp.PegawaiID, mp.Nama FROM MsPegawai mp LEFT JOIN MsBendahara mb on mb.PegawaiID=mp.PegawaiID "
                f"WHERE mp.[Status]='1' AND mb.PegawaiID IS NULL ORDER BY mp.PegawaiID " )
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads( result )

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

            args = parser.parse_args()
            UserId = kwargs['claim']["UserId"]
            print(UserId)
            select_query = db.session.query(vw_pegawai.Idpegawai, vw_pegawai.PegawaiID, vw_pegawai.Nama, vw_pegawai.NIP,
                                            vw_pegawai.Jabatan, vw_pegawai.Pangkat, vw_pegawai.UPTID,
                                            vw_pegawai.UPT, vw_pegawai.Status, vw_pegawai.Status, vw_pegawai.NamaStatus)



            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(vw_pegawai.Nama.ilike(search),
                        vw_pegawai.NIP.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(vw_pegawai, args['sort']).desc()
                else:
                    sort = getattr(vw_pegawai, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(vw_pegawai.PegawaiID)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads_pagination( query_execute, result )

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('PegawaiID', type=str)
            parser.add_argument('NIP', type=str)
            parser.add_argument('Jabatan', type=str)
            parser.add_argument('Nama', type=str)
            parser.add_argument('Pangkat', type=str)
            parser.add_argument('UPTID', type=str)
            parser.add_argument('Status', type=str)
            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            select_query = db.session.execute(
                f"SELECT CAST(MAX(CAST(PegawaiID AS int) + 1) AS varchar(10)) AS NextID FROM MsPegawai")
            result2 = select_query.first()[0]
            pegawaiid = result2

            select_query = db.session.execute(
                f"SELECT mu.UPTID FROM MsUPT AS mu WHERE mu.KDUNIT IN(SELECT gp.ParamStrValue "
                f"FROM GeneralParameter AS gp WHERE gp.ParamID='satker_sipkd') AND RIGHT(mu.KodeUPT,3)='05.'" )
            result = select_query.first()[0]
            uptid = result

            add_record = MsPegawai(

                PegawaiID=pegawaiid,
                NIP=args['NIP'] if args['NIP'] else '-',
                Jabatan=args['Jabatan'] if args['Jabatan'] else '-',
                Nama=args['Nama'],
                Pangkat=args['Pangkat'] if args['Pangkat'] else '-',
                UPTID=args['UPTID'] if args['UPTID'] else uptid,
                Status=1,
                UserUpd=uid,
                DateUpd=datetime.now(),

            )
            db.session.add(add_record)
            db.session.commit()
            return jsonify({'status_code': 1, 'message': 'OK', 'data': result})

    class ListById(Resource):
        method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
                             'delete': [tblUser.auth_apikey_privilege]}

        def get(self, id, *args, **kwargs):
            try:
                select_query = MsPegawai.query.filter_by(Idpegawai=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            # parser.add_argument('PegawaiID', type=str)
            parser.add_argument('NIP', type=str)
            parser.add_argument('Jabatan', type=str)
            parser.add_argument('Nama', type=str)
            parser.add_argument('Pangkat', type=str)
            parser.add_argument('UPTID', type=str)
            parser.add_argument('Status', type=str)
            # parser.add_argument('UserUpd', type=str)
            # parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            # if args['Status'] == 'Aktif':
            #     status = 1
            # if args['Status'] == 'Non Aktif':
            #     status = 0
            try:
                select_query = MsPegawai.query.filter_by(Idpegawai=id).first()
                if select_query:

                    if args['NIP']:
                        select_query.NIP = args['NIP']
                    if args['Jabatan']:
                        select_query.Jabatan = args['Jabatan']
                    if args['Nama']:
                        select_query.Nama = args['Nama']
                    if args['Pangkat']:
                        select_query.Pangkat = args['Pangkat']
                    if args['UPTID']:
                        select_query.UPTID = args['UPTID']
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
                delete_record = MsPegawai.query.filter_by(Idpegawai=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})