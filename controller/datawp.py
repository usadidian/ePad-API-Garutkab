from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import or_, func
from config.api_message import success_reads_pagination, failed_reads
from config.database import db
from config.helper import logger
from controller.MsJenisPendapatan import MsJenisPendapatan
from controller.MsWP import MsWP
from controller.MsWPData import MsWPData
from controller.tblUser import tblUser
from controller.MsWPData import MsWPData


def getSubscription(npwpd):
    result = []
    try:
        select_query = db.session.query(MsJenisPendapatan, MsWP).join(MsWP, MsWP.UsahaBadan == MsJenisPendapatan.JenisPendapatanID) \
            .join( MsWPData, MsWPData.WPID == MsWP.WPID ) \
            .filter(MsWPData.ObyekBadanNo == npwpd,
                    MsWPData.TglPenghapusan == None, MsJenisPendapatan.SelfAssessment == 'Y', MsJenisPendapatan.ParentID <= 2,
                    MsWPData.Insidentil == 'N', MsJenisPendapatan.ParentID != ''
                    ).order_by(MsJenisPendapatan.NamaJenisPendapatan).all()
        for row in select_query:
            newRow = {
                'jenispajak': row.MsJenisPendapatan.NamaJenisPendapatan,
                # 'kdrek': row.MsJenisPendapatan.KodeRekening,
                # 'img': row.MsJenisPendapatan.img,
                # 'icon': row.MsJenisPendapatan.icon,
                'opdid': row.MsWP.OPDID,
                'jenispajakid': row.MsJenisPendapatan.JenisPendapatanID,
                # 'omzetbase': row.MsJenisPendapatan.OmzetBase,
            }
            result.append(newRow)
        return result
    except Exception as e:
        logger.error(e)
        return None


class datawp(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):

        # PARSING PARAMETER DARI REQUEST
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('length', type=int)
        parser.add_argument('sort', type=str)
        parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
        parser.add_argument('search', type=str)
        args = parser.parse_args()

        group_code = kwargs['claim']['code_group']
        if group_code != 'MPOS':
            return jsonify({'message': 'OK'})

        result = []
        try:
            select_query = db.session.query(
                                            MsWPData.ObyekBadanNo.label('npwpd'), MsWPData.NamaBadan.label('namabadan'),
                                            MsWPData.AlamatBadan.label('alamatbadan'), MsWPData.TglPengesahan.label('tglpengesahan'),
                                            MsWPData.KecamatanBadan.label('kecamatanbadan'),
                                            MsWPData.KelurahanBadan.label('kelurahanbadan'),
                                            MsWPData.NIK.label('nik'), MsWPData.WPID.label('wpid'),
                                            MsWPData.TglPendaftaran.label('tglpendaftaran'),
                                            ) \

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(MsWPData.NamaBadan.ilike(search),
                        MsWPData.NIK.ilike(search),
                        MsWPData.ObyekBadanNo.ilike(search),
                        func.replace(func.replace(func.replace(MsWPData.ObyekBadanNo,
                        '.', ''), '-', ''), ' ', '').ilike(search)
                        , MsWPData.WPID.ilike( search ),
                        )
                )


            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(MsWPData, args['sort']).desc()
                else:
                    sort = getattr(MsWPData, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(MsWPData.DateUpd.desc())

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)

            # for row in query_execute.items:
            #     d = {}
            #     npwpd = None
            #     for key in row.keys():
            #         d[key] = getattr(row, key)
            #         if key == 'npwpd':
            #             npwpd = getattr(row, key)
            #         d['jenispajak'] = getSubscription(npwpd)
            #     result.append(d)
            # return success_reads_pagination(query_execute, result)

            for row in query_execute.items:
                d = {}
                npwpd = None
                for key in row.keys():
                    d[key] = getattr(row, key)
                    if key == 'npwpd':
                        npwpd = getattr(row, key)
                    d['jenispajak'] = getSubscription(npwpd)
                result.append(d)

            if len(result) == 0:
            # if result == None:
                return jsonify({'message': 'data tidak ditemukan atau wajib pajak belum terdaftar'})
            else:
                return success_reads_pagination(query_execute, result)
        except Exception as e:
            print(e)
            return failed_reads(result)
