from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.tblUser import tblUser


class MsStrategisDtl(db.Model, SerializerMixin):
    __tablename__ = 'MsStrategisDtl'
    DetailID = db.Column(db.Integer, primary_key=True)
    StrategisID = db.Column(db.Integer, nullable=False)
    NamaStrategisDtl = db.Column(db.String, nullable=False)
    Nilai = db.Column(db.Numeric(12, 2), nullable=False)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    StrategisID = db.Column(db.String, db.ForeignKey('MsStrategisHdr.StrategisID'), nullable=False)


    class ListAll1(Resource):
        def get(self,  *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT DetailID ,h.StrategisID AS StrategisID1,NamaStrategisDtl + (case when h.StrategisID in ('6','7') then '' else ' "
                f"(Bobot ' + dbo.DESIMAL(Nilai) + (case when Persentase = 0 then '' else ' x ' + dbo.DESIMAL(Persentase) "
                f"+ '%' end) + ')' end) AS NamaStrategis FROM MsStrategisDtl d LEFT JOIN MsStrategisHdr h ON "
                f"d.StrategisID = h.StrategisID WHERE h.StrategisID = '1' ORDER BY DetailID")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll2(Resource):
        def get(self,  *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT DetailID ,h.StrategisID AS StrategisID2,NamaStrategisDtl + (case when h.StrategisID in ('6','7') then '' else ' "
                f"(Bobot ' + dbo.DESIMAL(Nilai) + (case when Persentase = 0 then '' else ' x ' + dbo.DESIMAL(Persentase) "
                f"+ '%' end) + ')' end) AS NamaStrategis FROM MsStrategisDtl d LEFT JOIN MsStrategisHdr h ON "
                f"d.StrategisID = h.StrategisID WHERE h.StrategisID = '2' ORDER BY DetailID")
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_reads(result)

    class ListAll3( Resource ):
        def get(self,  *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT DetailID ,h.StrategisID AS StrategisID3,NamaStrategisDtl + (case when h.StrategisID in ('6','7') then '' else ' "
                f"(Bobot ' + dbo.DESIMAL(Nilai) + (case when Persentase = 0 then '' else ' x ' + dbo.DESIMAL(Persentase) "
                f"+ '%' end) + ')' end) AS NamaStrategis FROM MsStrategisDtl d LEFT JOIN MsStrategisHdr h ON "
                f"d.StrategisID = h.StrategisID WHERE h.StrategisID = '3' ORDER BY DetailID" )
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads( result )

    class ListAll4( Resource ):
        def get(self,  *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT DetailID ,h.StrategisID AS StrategisID4,NamaStrategisDtl + (case when h.StrategisID in ('6','7') then '' else ' "
                f"(Rp. ' + dbo.DESIMAL(Nilai) + (case when Persentase = 0 then '' else ' x ' + dbo.DESIMAL(Persentase) "
                f"+ '%' end) + ')' end) AS NamaStrategis FROM MsStrategisDtl d LEFT JOIN MsStrategisHdr h ON "
                f"d.StrategisID = h.StrategisID WHERE h.StrategisID = '4' ORDER BY DetailID" )
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads( result )

    class ListAll5( Resource ):
        def get(self,  *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT DetailID ,h.StrategisID AS StrategisID5,NamaStrategisDtl + (case when h.StrategisID in ('6','7') then '' else ' "
                f"(Rp. ' + dbo.DESIMAL(Nilai) + (case when Persentase = 0 then '' else ' x ' + dbo.DESIMAL(Persentase) "
                f"+ '%' end) + ')' end) AS NamaStrategis FROM MsStrategisDtl d LEFT JOIN MsStrategisHdr h ON "
                f"d.StrategisID = h.StrategisID WHERE h.StrategisID = '5' AND substring(convert(varchar,DetailID),2,2) = '01' "
                f"ORDER BY DetailID" )
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads( result )

    class ListAll6( Resource ):
        def get(self,  *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT DetailID ,h.StrategisID AS StrategisID6,NamaStrategisDtl + (case when h.StrategisID in ('6','7') then '' else ' "
                f"(Rp. ' + dbo.DESIMAL(Nilai) + (case when Persentase = 0 then '' else ' x ' + dbo.DESIMAL(Persentase) "
                f"+ '%' end) + ')' end) AS NamaStrategis FROM MsStrategisDtl d LEFT JOIN MsStrategisHdr h ON "
                f"d.StrategisID = h.StrategisID WHERE h.StrategisID = '6' ORDER BY DetailID" )
            result = []
            for row in select_query:
                d = {}
                for key in row.keys():
                    d[key] = getattr( row, key )
                result.append( d )
            return success_reads( result )

    class ListAll7( Resource ):
        def get(self,  *args, **kwargs):
            select_query = db.session.execute(
                f"SELECT DetailID ,h.StrategisID AS StrategisID7,NamaStrategisDtl + (case when h.StrategisID in ('6','7') then '' else ' "
                f"(Rp. ' + dbo.DESIMAL(Nilai) + (case when Persentase = 0 then '' else ' x ' + dbo.DESIMAL(Persentase) "
                f"+ '%' end) + ')' end) AS NamaStrategis FROM MsStrategisDtl d LEFT JOIN MsStrategisHdr h ON "
                f"d.StrategisID = h.StrategisID WHERE h.StrategisID = '7' ORDER BY DetailID" )
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
            select_query = MsStrategisDtl.query

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsStrategisDtl.TarifPajak.ilike(search),
                        MsStrategisDtl.NamaStrategisDtl.ilike(search))
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsStrategisDtl, args['sort']).desc()
                else:
                    sort = getattr(MsStrategisDtl, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsStrategisDtl.DetailID)

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            result = []
            for row in query_execute.items:
                result.append(row.to_dict())
            return success_reads_pagination(query_execute, result)

        def post(self, *args, **kwargs):
            parser = reqparse.RequestParser()
            parser.add_argument('DetailID', type=str)
            parser.add_argument('StrategisID', type=str)
            # parser.add_argument('NamaKelas', type=str)
            parser.add_argument('NamaStrategisDtl', type=str)
            parser.add_argument('Nilai', type=str)

            parser.add_argument('UserUpd', type=str)
            parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]

            args = parser.parse_args()
            result = []
            for row in result:
                result.append(row)

            select_query = db.session.execute(
                f"exec [SP_DETAIL_STRATEGIS] '{args['StrategisID']}'")
            result = []
            for row in select_query:
                result.append(row)
            detailid = result[0][0]

            add_record = MsStrategisDtl(
                DetailID=detailid,
                StrategisID=args['StrategisID'],
                # NamaStrategisDtl=args['NamaKelas'],
                NamaStrategisDtl=args['NamaStrategisDtl'],
                Nilai=args['Nilai'],
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
                select_query = MsStrategisDtl.query.filter_by(DetailID=id).first()
                result = select_query.to_dict()
                return success_read(result)
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_read({})

        def put(self, id, *args, **kwargs):
            parser = reqparse.RequestParser()
            print(kwargs['claim'])
            # parser.add_argument('DetailID', type=str)
            # parser.add_argument('StrategisID', type=str)
            # parser.add_argument('NamaStrategisDtl', type=str)
            parser.add_argument('Nilai', type=str)
            # parser.add_argument('UserUpd', type=str)
            # parser.add_argument('DateUpd', type=str)

            uid = kwargs['claim']["UID"]
            args = parser.parse_args()
            try:
                select_query = MsStrategisDtl.query.filter_by(DetailID=id).first()
                if select_query:
                    if args['Nilai']:
                        # select_query.DetailID = args['DetailID']
                        # select_query.StrategisID = args['StrategisID']
                        # select_query.NamaStrategisDtl = args['NamaStrategisDtl']
                        select_query.Nilai = args['Nilai']
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
                delete_record = MsStrategisDtl.query.filter_by(DetailID=id)
                delete_record.delete()
                db.session.commit()
                return success_delete({})
            except Exception as e:
                db.session.rollback()
                print(e)
                return failed_delete({})

