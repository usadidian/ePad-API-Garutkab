from datetime import datetime
from sqlalchemy_serializer import SerializerMixin
from config.database import db
from config.helper import logger
from controller.MsStrategisDtl import MsStrategisDtl
from controller.MsStrategisHdr import MsStrategisHdr
from controller.MsTitikLokasiHdr import MsTitikLokasiHdr
from controller.PendataanReklameHdr import PendataanReklameHdr


class PendataanReklameDtl(db.Model, SerializerMixin):
    __tablename__ = 'PendataanReklameDtl'
    DetailID = db.Column(db.Integer, autoincrement=True, primary_key=True)
    SPT = db.Column(db.String, nullable=False)
    NoUrut = db.Column(db.Integer, nullable=False)
    JudulReklame= db.Column(db.String, nullable=False)
    JenisLokasi = db.Column(db.String, nullable=False)
    LokasiID = db.Column(db.Integer, nullable=False)
    AlamatPasang = db.Column(db.String, nullable=True)
    # LuasReklame = db.Column(db.Integer, nullable=False)
    PanjangReklame = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=False)
    LebarReklame = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=False)
    TinggiReklame = db.Column( db.Numeric( precision=8, asdecimal=False, decimal_return_scale=None ), nullable=False )
    SudutPandang = db.Column(db.Integer, nullable=False)
    JumlahReklame = db.Column(db.Integer, nullable=False)
    TarifPajak = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None), nullable=False)
    LKecamatan = db.Column(db.String, nullable=True)
    LKelurahan = db.Column(db.String, nullable=True)
    UserUpd = db.Column(db.String, nullable=False)
    DateUpd = db.Column(db.TIMESTAMP, nullable=False)

    PendataanID = db.Column(db.Integer, db.ForeignKey('PendataanReklameHdr.PendataanID'), primary_key=True, nullable=False)

    def AddPPendataanDetil(data):
        try:
            uid = data['uid']
            print(uid)
            spt = data['SPT']
            select_query = db.session.execute(
                f"SELECT DISTINCT isnull(max(NoUrut) + 1,1) AS NextUrut FROM PendataanReklameDtl "
                f"WHERE SPT = '{spt}'")
            result2 = select_query.first()[0]
            nourut = result2
            kawasan = data['kawasan']
            lokasi = data['lokasi']
            dateupdate = datetime.now()

            result = []
            for row in result:
                result.append(row)

            add_record = PendataanReklameDtl(
                PendataanID=data['PendataanID'],
                SPT=spt,
                NoUrut=nourut,
                JudulReklame=data['JudulReklame'],
                JenisLokasi='T',
                LokasiID=data['LokasiID'],
                AlamatPasang=data['AlamatPasang'],
                TinggiReklame=data['TinggiReklame'],
                PanjangReklame=data['PanjangReklame'],
                LebarReklame=data['LebarReklame'],
                SudutPandang=data['SudutPandang'],
                JumlahReklame=data['JumlahReklame'],
                TarifPajak=data['TarifPajak'],
                LKecamatan=data['LKecamatan'],
                LKelurahan=data['LKelurahan'],
                UserUpd=uid,
                DateUpd=dateupdate
            )
            db.session.add(add_record)
            db.session.commit()
            db.session.execute(
                f"UPDATE PendataanReklameHdr SET TotalPajak=(select sum(TarifPajak) from PendataanReklameDtl where SPT='{spt}') "
                f"WHERE SPT = '{spt}'")
            db.session.commit()
            db.session.execute(
                f"INSERT INTO PendataanNSL (SPT,NoUrut,DetailID,UserUpd,DateUpd) VALUES ('{spt}','{nourut}','{kawasan}','{uid}','{dateupdate.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}')")
            db.session.commit()
            db.session.execute(
                f"INSERT INTO PendataanNSL (SPT,NoUrut,DetailID,UserUpd,DateUpd) VALUES "
                f"('{spt}',{nourut},{lokasi},'{uid}','{dateupdate.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}')")
            db.session.commit()
            return True
        except Exception as e:
            logger.error(e)
            return False
        
    
    def UpdatePendataanDetail(data):
        try:
            uid = data['uid']
            print(uid)
            spt = data['SPT']
            nourut = data['NoUrut']

            result = []
            for row in result:
                result.append(row)

            select_query = PendataanReklameDtl.query.filter_by(DetailID=data['DetailID']).first()
            if select_query:
                if data['PendataanID']:
                    select_query.PendataanID = data['PendataanID']
                if spt:
                    select_query.SPT = spt
                if nourut:
                    select_query.NoUrut = nourut
                if data['JudulReklame']:
                    select_query.JudulReklame = data['JudulReklame']
                if data['LokasiID']:
                    select_query.LokasiID = data['LokasiID']
                if data['AlamatPasang']:
                    select_query.AlamatPasang = data['AlamatPasang']
                if data['TinggiReklame']:
                    select_query.PanjangReklame = data['TinggiReklame']
                if data['PanjangReklame']:
                    select_query.PanjangReklame = data['PanjangReklame']
                if data['LebarReklame']:
                    select_query.LebarReklame = data['LebarReklame']
                if data['SudutPandang']:
                    select_query.SudutPandang = data['SudutPandang']
                if data['JumlahReklame']:
                    select_query.JumlahReklame = data['JumlahReklame']
                if data['LKecamatan']:
                    select_query.LKecamatan = data['LKecamatan']
                if data['LKelurahan']:
                    select_query.LKelurahan = data['LKelurahan']
                if data['LuasReklame']:
                    select_query.LuasReklame = data['LuasReklame']
                if data['TarifPajak']:
                    select_query.TarifPajak = data['TarifPajak']

                select_query.UserUpd = uid
                select_query.DateUpd = datetime.now()
                db.session.commit()

                db.session.execute(
                    f"UPDATE PendataanReklameHdr SET TotalPajak=(select sum(TarifPajak) from PendataanReklameDtl where SPT='{spt}') "
                    f"WHERE SPT = '{spt}'")
                db.session.commit()
                return True
            else:
                return False
        except Exception as e:
            logger.error(e)
            return False

    # def AddPPendataanDetil(data):
    #     try:
    #         uid = data['uid']
    #         print(uid)
    #         spt = data['SPT']
    #         select_query = db.session.execute(
    #             f"SELECT DISTINCT isnull(max(NoUrut) + 1,1) AS NextUrut FROM PendataanReklameDtl "
    #             f"WHERE SPT = '{spt}'")
    #         result2 = select_query.first()[0]
    #         nourut = result2
    #
    #         panjang = data['PanjangReklame']
    #         lebar = data['LebarReklame']
    #         luas = int(panjang) * int(lebar)
    #
    #         sudutpandang = data['SudutPandang']
    #         jumlahreklame = data['JumlahReklame']
    #
    #         select_query = db.session.query(PendataanReklameHdr.MasaAwal).filter(
    #             PendataanReklameHdr.SPT == spt)
    #         masaawal = select_query.first()[0]
    #
    #         select_query = db.session.query(PendataanReklameHdr.MasaAkhir).filter(
    #             PendataanReklameHdr.SPT == spt)
    #         masaakhir = select_query.first()[0]
    #
    #         select_query = db.session.query(MsTitikLokasiHdr.LokasiID).filter(
    #             MsTitikLokasiHdr.LokasiID == data['LokasiID'])
    #         lokasiid = select_query.first()[0]
    #
    #         select_query = db.session.query(MsStrategisDtl.DetailID).join(MsStrategisHdr).filter(
    #             MsStrategisHdr.StrategisID == data['StrategisID1'])
    #         kawasan = select_query.first()[0]
    #
    #         select_query2 = db.session.query(MsStrategisDtl.DetailID).join(MsStrategisHdr).filter(
    #             MsStrategisHdr.StrategisID == data['StrategisID2'])
    #         lokasi = select_query2.first()[0]
    #
    #         select_query = db.session.execute(
    #             f"exec [SP_WPO_HITREKLA] '{masaawal}','{masaakhir}','{panjang}',"
    #             f"'{lebar}','{sudutpandang}','{jumlahreklame}',"
    #             f"'{kawasan}','{lokasi}','{lokasiid}'")
    #         result3 = select_query.first()[0]
    #         tarifpajak = float(result3)
    #
    #         result = []
    #         for row in result:
    #             result.append(row)
    #
    #         add_record = PendataanReklameDtl(
    #             SPT=spt,
    #             NoUrut=nourut,
    #             JudulReklame=data['JudulReklame'],
    #             JenisLokasi='T',
    #             LokasiID=data['LokasiID'],
    #             AlamatPasang=data['AlamatPasang'],
    #             LuasReklame=luas,
    #             PanjangReklame=data['PanjangReklame'],
    #             LebarReklame=data['LebarReklame'],
    #             SudutPandang=data['SudutPandang'],
    #             JumlahReklame=data['JumlahReklame'],
    #             TarifPajak=tarifpajak,
    #             LKecamatan=data['LKecamatan'],
    #             LKelurahan=data['LKelurahan'],
    #             UserUpd=uid,
    #             DateUpd=datetime.now()
    #         )
    #         db.session.add(add_record)
    #         db.session.commit()
    #         select_query = db.session.execute(
    #             f"UPDATE PendataanReklameHdr SET TotalPajak=(select sum(TarifPajak) from PendataanReklameDtl where SPT='{spt}') "
    #             f"WHERE SPT = '{spt}'")
    #         return True
    #     except Exception as e:
    #         print(e)
    #         return False

 ##################################################################################

    # class ListAll(Resource):
    #     method_decorators = {'post': [tblUser.auth_apikey_privilege]}
    #
    #     def post(self, *args, **kwargs):
    #         parser = reqparse.RequestParser()
    #         parser.add_argument('SPT', type=str)
    #         parser.add_argument('NoUrut', type=int)
    #         parser.add_argument('JudulReklame', type=str)
    #         parser.add_argument('JenisLokasi', type=str)
    #         parser.add_argument('LokasiID', type=str)
    #         parser.add_argument('AlamatPasang', type=str)
    #         parser.add_argument('LuasReklame', type=int)
    #         parser.add_argument('PanjangReklame', type=str)
    #         parser.add_argument('LebarReklame', type=str)
    #         parser.add_argument('SudutPandang', type=str)
    #         parser.add_argument('JumlahReklame', type=int)
    #         parser.add_argument('TarifPajak', type=str)
    #         parser.add_argument('LKecamatan', type=str)
    #         parser.add_argument('LKelurahan', type=str)
    #         parser.add_argument('UserUpd', type=str)
    #         parser.add_argument('DateUpd', type=str)
    #
    #         parser.add_argument('TipeLokasiID', type=str)
    #         parser.add_argument('StrategisID1', type=int)
    #         parser.add_argument('StrategisID2', type=int)
    #         parser.add_argument('DetailID1', type=int)
    #         parser.add_argument('DetailID2', type=int)
    #
    #         uid = kwargs['claim']["UID"]
    #
    #         args = parser.parse_args()
    #
    #         select_query = db.session.execute(
    #             f"SELECT DISTINCT isnull(max(NoUrut) + 1,1) AS NextUrut FROM PendataanReklameDtl "
    #             f"WHERE SPT = '{args['SPT']}'")
    #         result2 = select_query.first()[0]
    #         nourut = result2
    #
    #         panjang = float(request.form['PanjangReklame'])
    #         lebar = float(request.form['LebarReklame'])
    #         luas = int(panjang) * int(lebar)
    #
    #         select_query = db.session.query(PendataanReklameHdr.MasaAwal).filter(
    #             PendataanReklameHdr.SPT == args['SPT'])
    #         masaawal = select_query.first()[0]
    #
    #         select_query = db.session.query(PendataanReklameHdr.MasaAkhir).filter(
    #             PendataanReklameHdr.SPT == args['SPT'])
    #         masaakhir = select_query.first()[0]
    #
    #         select_query = db.session.query(MsTipeLokasi.TipeLokasiID).filter(
    #             MsTipeLokasi.TipeLokasiID == args['TipeLokasiID'])
    #         tipelokasiid = select_query.first()[0]
    #
    #         select_query = db.session.query(MsTitikLokasiHdr.LokasiID).filter(
    #             MsTitikLokasiHdr.LokasiID == args['LokasiID'])
    #         lokasiid = select_query.first()[0]
    #
    #         select_query = db.session.query(MsStrategisDtl.DetailID).join(MsStrategisHdr).filter(
    #             MsStrategisHdr.StrategisID == args['StrategisID1'])
    #         kawasan = select_query.first()[0]
    #
    #         select_query2 = db.session.query(MsStrategisDtl.DetailID).join(MsStrategisHdr).filter(
    #             MsStrategisHdr.StrategisID == args['StrategisID2'])
    #         lokasi = select_query2.first()[0]
    #
    #         select_query = db.session.execute(
    #             f"exec [SP_WPO_HITREKLA] '{masaawal}','{masaakhir}','{args['PanjangReklame']}',"
    #             f"'{args['LebarReklame']}','{args['SudutPandang']}','{args['JumlahReklame']}',"
    #             f"'{kawasan}','{lokasi}','{lokasiid}'")
    #         result3 = select_query.first()[0]
    #         tarifpajak = float(result3)
    #
    #         result = []
    #         for row in result:
    #             result.append(row)
    #
    #         add_record = PendataanReklameDtl(
    #             SPT=args['SPT'],
    #             NoUrut=nourut,
    #             JudulReklame=args['JudulReklame'],
    #             JenisLokasi='T',
    #             LokasiID=lokasiid,
    #             AlamatPasang=args['AlamatPasang'],
    #             LuasReklame=luas,
    #             PanjangReklame=panjang,
    #             LebarReklame=lebar,
    #             SudutPandang=int(request.form['SudutPandang']),
    #             JumlahReklame=int(request.form['JumlahReklame']),
    #             TarifPajak=tarifpajak,
    #             LKecamatan=args['LKecamatan'],
    #             LKelurahan=args['LKelurahan'],
    #             UserUpd=uid,
    #             DateUpd=datetime.now()
    #         )
    #         db.session.add(add_record)
    #         db.session.commit()
    #         return jsonify({'status_code': 1, 'message': 'OK', 'data': result})
    #
    # class ListById(Resource):
    #     method_decorators = {'get': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege],
    #                          'delete': [tblUser.auth_apikey_privilege]}
    #
    #     def get(self, id, *args, **kwargs):
    #         try:
    #             select_query = PendataanReklameDtl.query.filter_by(DetailID=id).first()
    #             result = select_query.to_dict()
    #             return success_read(result)
    #         except Exception as e:
    #             db.session.rollback()
    #             print(e)
    #             return failed_read({})
    #
    #     def put(self, id, *args, **kwargs):
    #         parser = reqparse.RequestParser()
    #         print(kwargs['claim'])
    #         parser.add_argument('SPT', type=str)
    #         parser.add_argument('NoUrut', type=int)
    #         parser.add_argument('JenisLokasi', type=str)
    #         parser.add_argument('LokasiID', type=str)
    #         parser.add_argument('AlamatPasang', type=str)
    #         parser.add_argument('LuasReklame', type=int)
    #         parser.add_argument('PanjangReklame', type=str)
    #         parser.add_argument('LebarReklame', type=str)
    #         parser.add_argument('SudutPandang', type=str)
    #         parser.add_argument('JumlahReklame', type=int)
    #         parser.add_argument('TarifPajak', type=str)
    #         parser.add_argument('LKecamatan', type=str)
    #         parser.add_argument('LKelurahan', type=str)
    #         parser.add_argument('UserUpd', type=str)
    #         parser.add_argument('DateUpd', type=str)
    #
    #         uid = kwargs['claim']["UID"]
    #
    #
    #         args = parser.parse_args()
    #         try:
    #             select_query = PendataanReklameDtl.query.filter_by(DetailID=id).first()
    #             if select_query:
    #                 select_query.SPT = args['SPT']
    #                 select_query.NoUrut = args['NoUrut']
    #                 select_query.JenisLokasi = args['JenisLokasi']
    #                 select_query.LokasiID = args['LokasiID']
    #                 select_query.AlamatPasang = args['AlamatPasang']
    #                 select_query.LuasReklame = args['LuasReklame']
    #                 select_query.PanjangReklame = args['PanjangReklame']
    #                 select_query.LebarReklame = args['LebarReklame']
    #                 select_query.SudutPandang = args['SudutPandang']
    #                 select_query.JumlahReklame = args['JumlahReklame']
    #                 select_query.TarifPajak = args['TarifPajak']
    #                 select_query.LKecamatan = args['LKecamatan']
    #                 select_query.LKelurahan = args['LKelurahan']
    #                 select_query.UserUpd = uid
    #                 select_query.DateUpd = datetime.now()
    #                 db.session.commit()
    #                 return success_update({'id': id})
    #         except Exception as e:
    #             db.session.rollback()
    #             print(e)
    #             return failed_update({})
    #
    #     def delete(self, id, *args, **kwargs):
    #         try:
    #             delete_record = PendataanReklameDtl.query.filter_by(DetailID=id)
    #             delete_record.delete()
    #             db.session.commit()
    #             return success_delete({})
    #         except Exception as e:
    #             db.session.rollback()
    #             print(e)
    #             return failed_delete({})