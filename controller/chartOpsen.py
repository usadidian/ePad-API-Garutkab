import locale

from flask import request
from flask_restful import Resource, reqparse

from config.api_message import success_reads, failed_reads
from config.database import db
from config.helper import logger
from controller.tblGroupUser import tblGroupUser
from controller.tblUPTOpsen import tblUPTOpsen
from controller.tblUser import tblUser
from sqlalchemy.orm import scoped_session


class realopsen(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('tahun', type=lambda x: int(x) if x and x.isnumeric() else None)
        parser.add_argument('bulan', type=lambda x: int(x) if x and x.isnumeric() else None)
        parser.add_argument('wilayah', type=str)
        parser.add_argument('tgl_setoran', type=str)

        args = parser.parse_args()
        session = scoped_session(db.session)  # Gunakan scoped_session
        try:
            tahun = args.get('tahun')
            bulan = args.get('bulan')
            wilayah = args.get('wilayah')
            tgl_setoran = args.get('tgl_setoran')

            wapuid = kwargs['claim']["WapuID"]
            upt_id = session.query(tblUPTOpsen).filter_by(UPT=wilayah).first()  # Gunakan session

            uptid = wapuid if wapuid else (upt_id.UPTID if upt_id else None)

            query = """
                      EXEC WS_REPORT_REALISASI_OPSEN 
                      @tahun=:tahun, @uptid=:uptid, @bulan=:bulan, @tgl_setoran=:tgl_setoran
                  """
            params = {
                "tahun": tahun,
                "uptid": uptid,
                "bulan": bulan,
                "tgl_setoran": tgl_setoran
            }

            select_query = session.execute(query, params)  # Gunakan session

            result = []
            for row in select_query:
                d = {key: getattr(row, key) for key in row.keys()}
                if 'Jumlah' in d:
                    d['Jumlah'] = f"Rp {float(d['Jumlah']):,.0f}".replace(",", ".")  # Format ke Rupiah
                result.append(d)

            return success_reads(result)
        except Exception as e:
            logger.error(e)
            return failed_reads([])
        finally:
            session.close()  # Pastikan session selalu ditutup