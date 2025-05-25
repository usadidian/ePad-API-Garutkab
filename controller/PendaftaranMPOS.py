import os
from datetime import datetime
from multiprocessing import Process

import sqlalchemy
from flask import request
from flask_restful import reqparse, Resource

from config.api_message import failed_create, success_create
from config.database import db
from config.helper import logger
from controller.MsWP import MsWP
from controller.MsWPData import MsWPData
from controller.task.task_bridge import GoToTaskUploadWPAvatar
from controller.tblUser import tblUser
from controller.vw_obyekbadan import vw_obyekbadan


class pendaftaran(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def post(self, *args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument( 'namabadan', required=True, nullable=False,
                             help="Harus diisi" )
        parser.add_argument( 'jenispajakid', required=True, nullable=False,
                             help="Harus diisi" )
        parser.add_argument( 'telpbadan', type=str )
        parser.add_argument( 'alamatbadan', type=str )
        parser.add_argument( 'kotabadan', type=str, required=True, help="Harus diisi" )
        parser.add_argument( 'kecamatanbadan', required=True, nullable=False,
                             help="Harus diisi" )
        parser.add_argument( 'kelurahanbadan', required=True, nullable=False,
                             help="Harus diisi" )
        parser.add_argument( 'namapemilik', type=str, required=True, help="Harus diisi" )
        parser.add_argument( 'telppemilik', type=str )
        parser.add_argument( 'alamatpemilik', type=str )
        parser.add_argument( 'kotapemilik', type=str, required=True, help="Harus diisi" )
        parser.add_argument( 'kecamatanpemilik', type=str, required=True, help="Harus diisi" )
        parser.add_argument( 'kelurahanpemilik', type=str, required=True, help="Harus diisi" )
        parser.add_argument( 'avatar', type=str )
        parser.add_argument( 'latlng', type=str )
        parser.add_argument( 'nik', type=str )
        args = parser.parse_args()
        try:

            uid = kwargs['claim']["UID"]
            result = db.session.execute(
                f"exec [SP_NPWPD] '{args['kecamatanbadan']}','{args['kelurahanbadan']}','{datetime.now().strftime('%Y-%m-%d')}'" )

            result2 = []
            for row in result:
                result2.append( row )
            ObyekBadanNo = result2[0][0].replace( ' ', '' )
            NoPengesahan = result2[0][1]

            if ObyekBadanNo and NoPengesahan:
                add_record = MsWPData(
                    NamaBadan=args['namabadan'] if args['namabadan'] else '',
                    GrupUsahaID='',
                    KlasifikasiID='',
                    LokasiID='',
                    AlamatBadan=args['alamatbadan'] if args['alamatbadan'] else '',
                    KotaBadan=args['kotabadan'] if args['kotabadan'] else '',
                    KecamatanBadan=args['kecamatanbadan'] if args['kecamatanbadan'] else '',
                    KelurahanBadan=args['kelurahanbadan'] if args['kelurahanbadan'] else '',
                    RWBadan='',
                    RTBadan='',
                    NoTelpBadan=args['telpbadan'] if args['telpbadan'] else '',
                    NoFaxBadan='',
                    NamaPemilik=args['namapemilik'] if args['namapemilik'] else '',
                    JabatanPemilik='',
                    AlamatPemilik=args['alamatpemilik'] if args['alamatpemilik'] else '',
                    KotaPemilik=args['kotapemilik'] if args['kotapemilik'] else '',
                    KecamatanPemilik=args['kecamatanpemilik'] if args['kecamatanpemilik'] else '',
                    KelurahanPemilik=args['kelurahanpemilik'] if args['kelurahanpemilik'] else '',
                    RWPemilik='',
                    RTPemilik='',
                    NoTelpPemilik=args['telppemilik'] if args['telppemilik'] else '',
                    NoFaxPemilik='',
                    TglPendaftaran=datetime.now().strftime('%Y-%m-%d'),
                    TglPengesahan=datetime.now().strftime('%Y-%m-%d'),
                    NoPengesahan=NoPengesahan,
                    TglPenghapusan=sqlalchemy.sql.null(),
                    PetugasPendaftar='09',
                    Insidentil='N',
                    UserUpd=uid,
                    DateUpd=datetime.now(),
                    ObyekBadanNo=ObyekBadanNo,
                    latlng='',
                    NIK=''
                )
                db.session.add( add_record )
                db.session.commit()
                print( 'sukses insert ke header' )
                if add_record:
                    data = {
                        'uid': uid,
                        'UsahaBadan': args['jenispajakid'],
                        'WPID': add_record.WPID
                    }
                    add_record_detail = MsWP.AddPendaftaranDetil( data )

                    # ////INCLUDE IMG
                    files_img = request.files
                    if files_img:
                        if not os.path.exists( f'./static/uploads/avatar_wp_temp' ):
                            os.makedirs( f'./static/uploads/avatar_wp_temp' )
                        folder_temp = f'./static/uploads/avatar_wp_temp'

                        # add item img and upload
                        filenames = []

                        for img_row in files_img.items():
                            img_row_ok = img_row[1]
                            if img_row_ok.filename == '':
                                logger.info( 'file image dengan nama avatar wajib disertakan' )
                            if img_row_ok:
                                new_filename = f"{add_record.WPID}.png"
                                img_row_ok.save( os.path.join( folder_temp, new_filename ) )
                                filenames.append( new_filename )
                        filenames_str = ','.join( [str( elem ) for elem in filenames] )
                        # logger.info(filenames_str)
                        if filenames_str != '':
                            thread = Process( target=GoToTaskUploadWPAvatar,
                                              args=(
                                              folder_temp, filenames_str, add_record.WPID, kwargs['claim']['UserId'], False, request.origin) )
                            thread.daemon = True
                            thread.start()

                    if add_record_detail:
                        select_query = db.session.query( vw_obyekbadan.NamaJenisPendapatan ).filter(
                            vw_obyekbadan.JenisPendapatanID == data['UsahaBadan'] )
                        jenispajak = select_query.first()[0]
                        return success_create( {'namabadan': add_record.NamaBadan, 'npwpd': add_record.ObyekBadanNo, 'jenispajak': jenispajak})
                else:
                    db.session.rollback()
                    return failed_create( {} )
            else:
                db.session.rollback()
                return failed_create( {} )
        except Exception as e:
            db.session.rollback()
            print( e )
            return failed_create( {} )