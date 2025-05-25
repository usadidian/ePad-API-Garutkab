from flask_restful import Api

from controller import users, groups, chartOpsen
from controller.ApiUrl import ApiUrlLookup, ApiUrlListResource, ApiUrlResource
from controller.MsPropinsi import MsPropinsi
from controller.MsWPOData import MsWPOData
from controller.MsWapu import MsWapu
from controller.Pelaporan import PelaporanOmzet, PelaporanOmzetDet, AddPelaporanOmzet, DeletePelaporanOmzet
from controller.PendaftaranObjekPajak import AddPendaftaranObjekPajak, UpdatePendaftaranObjekPajak, \
    DeletePendaftaranObjekPajak, AddPendaftaranObjekPajakRekening, PenonaktifanOPDEdit, PenonaktifanOPD, \
    UpdatePenonaktifanOPD, AktivasiOPD, AktivasiOPDEdit, UpdateAktivasiOPD, generate_nop
from controller.PendaftaranWapu import PenonaktifanWapuEdit, PenonaktifanWapu, UpdatePenonaktifanWapu, AktivasiWapu, \
    AktivasiWapuEdit, UpdateAktivasiWapu, AddPendaftaranWapu, UpdatePendaftaranWapu, DeletePendaftaranWapu
from controller.PenetapanKB import PenetapanKB
from controller.PenetapanSamsat import PenetapanSamsat
from controller.RevenueCategories import RevenueCategories
from controller.RevenueLogType import RevenueLogType
from controller.RevenueSummary import RevenueSummary
from controller.TaxEntities import TaxEntities
from controller.Transactions import Transactions
from controller.articles.articles import ArticlesList, ArticlesCategoriesList, ArticlesById
from controller.chartRealUPTD import realUPTD
from controller.chats import UserOnlineStatus, UserRefreshStatus, UserChatById, SetReadChat
from controller.datawp import datawp
from controller.geodata import GeoData
from controller.login import UserLogin, UserLoginWPO, UpdateDevice, CheckSession, UserLogout, RegisterWPO, AuthOtpWPO, \
    UserLoginByGoogleWP, ChangePassword, ForgotCheckEmail, ForgotCheckOtp, ResetPwd, ForgotCheckOtpResetPwd
from controller.invoice import invoice_all, skp
from controller.DataAkhir import DataAkhir
from controller.Matangd import MATANGD
from controller.MsJenisPendapatan import MsJenisPendapatan, MsJenisPendapatan13
from controller.MsUPT import MsUPT
from controller.MsPegawai import MsPegawai
from controller.MsBendahara import MsBendahara
from controller.MsBank import MsBank
from controller.MsBankUPT import MsBankUPT
from controller.MsJenisStatus import MsJenisStatus
from controller.MsTargetPendapatan import MsTargetPendapatan
from controller.GeneralParameter import GeneralParameter
from controller.TransactionControl import TransactionControl
from controller.MsTipeLokasi import MsTipeLokasi
from controller.MsStrategisHdr import MsStrategisHdr
from controller.MsStrategisDtl import MsStrategisDtl
from controller.MsTitikLokasiHdr import MsTitikLokasiHdr
from controller.MsJenisUsaha import MsJenisUsaha
from controller.MsTarifLokasi import MsTarifLokasi, tarifpajak
from controller.GroupAttribute import GroupAttribute
from controller.MsGrupUsaha import MsGrupUsaha
from controller.MsJenisPungut import MsJenisPungut
from controller.MsLokasiKhusus import MsLokasiKhusus
from controller.MsKlasifikasiUsaha import MsKlasifikasiUsaha
from controller.MsSatuanOmzet import MsSatuanOmzet
from controller.MsKota import MsKota
from controller.MsKPP import MsKPP
from controller.MsKecamatan import MsKecamatan
from controller.MsKelurahan import MsKelurahan
from controller.MsRW import MsRW
from controller.MsRT import MsRT
from controller.MsWPData import MsWPData
from controller.MsWP import MsWP
from controller.MsOPD import MsOPD
from controller.Pendaftaran import AddPendaftaran, DeletePendaftaranMulti
from controller.PendaftaranWPO import AddPendaftaranWPO, UpdatePendaftaranWPO
from controller.Pendaftaran import AddPendaftaranRekening
from controller.Pendaftaran import UpdatePendaftaran
from controller.Pendaftaran import DeletePendaftaran

from controller.Pendaftaran import Penonaktifan, PenonaktifanEdit, UpdatePenonaktifan
from controller.Pendaftaran import Aktivasi, AktivasiEdit, UpdateAktivasi
from controller.PendaftaranMPOS import pendaftaran

from controller.PendataanByOmzet import PendataanByOmzet
from controller.PendataanByOmzetDtl import PendataanByOmzetDtl
from controller.PendataanReklameHdr import PendataanReklameHdr
from controller.PendataanReklameDtl import PendataanReklameDtl
from controller.PendataanSKP import PendataanSKP, AddPendataanBPHTB, pendataanpajak
from controller.PendataanSKP import PendataanSKP2
from controller.PendataanSKP import PendataanSKP3
from controller.PendataanSKP import PendataanSKPOmzet
from controller.PendataanSKP import AddPendataanSKP
from controller.PendataanSKP import UpdatePendataanSKP
from controller.PendataanSKP import DeletePendataanSKP
from controller.PendataanSKP import PendataanSKPOmset
from controller.HistPenetapanSKP import HistPenetapanSKP, UpdateHistPenetapanSKP
from controller.OmzetHarian import OmzetHarian, OmzetHarianSKP, OmzetHarianSKPOmzet, AddOmzetHarianSKP

from controller.PendataanSKPReklame import PendataanSKPReklame
from controller.PendataanSKPReklame import HitungSKPReklame
from controller.PendataanSKPReklame import AddPendataanSKPReklame
from controller.PendataanSKPReklame import UpdatePendataanSKPReklame
from controller.PendataanSKPReklame import DeletePendataanSKPReklame

from controller.PendataanSPTP import PendataanSPTP
from controller.PendataanSPTP import PendataanSPTP2
from controller.PendataanSPTP import PendataanSPTP3
from controller.PendataanSPTP import PendataanSPTPOmzet
from controller.PendataanSPTP import AddPendataanSPTP
from controller.PendataanSPTP import UpdatePendataanSPTP
from controller.PendataanSPTP import DeletePendataanSPTP

from controller.PenetapanSKP import PenetapanSKP, PenetapanSKP6
from controller.PenetapanSKP import PenetapanSKP2
from controller.PenetapanSKP import PenetapanSKP3
from controller.PenetapanSKP import PenetapanSKP4
from controller.PenetapanSKP import PenetapanSKP5
from controller.PenetapanSKP import AddPenetapanSKP
from controller.PenetapanSKP import UpdatePenetapanSKP
from controller.PenetapanSKP import UpdatePenetapanSKPKurangBayar
from controller.PenetapanSKP import DeletePenetapanSKP

from controller.ValidasiSPTP import ValidasiSPTP
from controller.ValidasiSPTP import ValidasiSPTP2
from controller.ValidasiSPTP import ValidasiSPTP3
from controller.ValidasiSPTP import ValidasiSPTP4
from controller.ValidasiSPTP import ValidasiSPTP5
from controller.ValidasiSPTP import AddValidasiSPTP
from controller.ValidasiSPTP import UpdateValidasiSPTP
from controller.ValidasiSPTP import UpdateValidasiSPTPKurangBayar
from controller.ValidasiSPTP import DeleteValidasiSPTP

from controller.PenetapanSKPReklame import PenetapanSKPReklame
from controller.PenetapanSKPReklame import PenetapanSKPReklame2
from controller.PenetapanSKPReklame import PenetapanSKPReklame3
from controller.PenetapanSKPReklame import PenetapanSKPReklame4
from controller.PenetapanSKPReklame import PenetapanSKPReklame5
from controller.PenetapanSKPReklame import AddPenetapanSKPReklame
from controller.PenetapanSKPReklame import UpdatePenetapanSKPReklame
from controller.PenetapanSKPReklame import UpdatePenetapanSKPReklameKurangBayar
from controller.PenetapanSKPReklame import DeletePenetapanSKPReklame

from controller.Pembayaran import Pembayaran
from controller.PembayaranSKP import PembayaranSKP, statuspembayaran
from controller.PembayaranSKP import genkodebayar
from controller.PembayaranSKP import HitungDenda
from controller.PembayaranSKP import PembayaranSKP3
from controller.PembayaranSKP import PembayaranSKP4
from controller.PembayaranSKP import PembayaranSKP5
from controller.PembayaranSKP import AddPembayaranSKP
from controller.PembayaranSKP import AddPembayaranSKPWPO
from controller.PembayaranSKP import UpdatePembayaranSKP
from controller.PembayaranSKP import DeletePembayaranSKP

from controller.PembayaranSPTP import PembayaranSPTP
from controller.PembayaranSPTP import PembayaranSPTP2
from controller.PembayaranSPTP import PembayaranSPTP3
from controller.PembayaranSPTP import PembayaranSPTP4
from controller.PembayaranSPTP import PembayaranSPTP5
from controller.PembayaranSPTP import AddPembayaranSPTP
from controller.PembayaranSPTP import UpdatePembayaranSPTP
from controller.PembayaranSPTP import DeletePembayaranSPTP

from controller.Setoran import Setoran
from controller.Setoran import Setoran2
from controller.Setoran import Setoran3
from controller.Setoran import Setoran4
from controller.Setoran import Setoran5
from controller.Setoran import Setoran6
from controller.Setoran import Setoran7
from controller.Setoran import AddSetoran
from controller.Setoran import UpdateSetoran
from controller.Setoran import DeleteSetoranDtl
from controller.Setoran import DeleteSetoran
from controller.Setoran import AddSetoranDtl

from controller.PenetapanByOmzet import PenetapanByOmzet
from controller.NomorKohir import NomorKohir
from controller.PenetapanReklameHdr import PenetapanReklameHdr
from controller.PenetapanReklameDtl import PenetapanReklameDtl
from controller.SetoranHist import SetoranHist
from controller.SuratTeguranHist import SuratTeguranHist
from controller.SetoranUPTHdr import SetoranUPTHdr
from controller.SetoranUPTDtl import SetoranUPTDtl
from controller.notifications.fcm_session import NotifToAdmin, NotifToAdmins
from controller.notifications.notifications import NotifList
from controller.opsen_sts import OpsenListResourceNotSTS, OpsenListResourceNotSTS4, OpsenListResourceNotSTS7
from controller.search import search
from controller.task.task_upload_articles_img import TaskUploadArticleImg, TaskDeleteArticleImg
from controller.task.task_upload_avatar import TaskUploadAvatar, TaskDeleteAvatar
from controller.task.task_upload_doc_lapor import TaskUploadDocLapor, TaskDeleteDocLapor
from controller.task.task_upload_opd_avatar import TaskUploadOPDAvatar, TaskDeleteOPDAvatar
from controller.task.task_upload_wapu_avatar import TaskUploadWapuAvatar, TaskDeleteWapuAvatar
from controller.task.task_upload_wp_avatar import TaskUploadWpAvatar, TaskDeleteWpAvatar
from controller.tblAkses import tblAkses
from controller.tblGroupUser import tblGroupUser
from controller.tblMenu import tblMenu
from controller.tblMenuDet import tblMenuDet
from controller.tblOpsen import tblOpsen
from controller.tblRole import tblRole
from controller.tblUser import tblUser
from controller.tblUserWP import tblUserWP
from controller.tblUrl import tblUrl
from controller.unit_prop import GetDomainProp
from controller.vw_setoranhist import vw_setoranhist
from controller.vw_userwp import vw_userwp
from controller.vw_pembayaran import vw_pembayaran
from controller.vw_pendataan import vw_pendataan
from controller.vw_penetapan import vw_penetapan
from controller.vw_setoran import vw_setoran
from controller.vw_obyekbadan import vw_obyekbadan
from controller.vw_suratteguranhist import vw_suratteguranhist
from controller.wpo_controller import GetListUsaha, GetSubscription, GetUsaha, GetAllBill, GetUsahaLookup, \
    AddUsahaFromOldWPO

from controller.chart import piutang
from controller.chartRealBulan import realbulan
from controller.chartRealTahun import realTahun
from controller.chartRealTW import realTW
from controller.chartWP import realWP
from controller.chartRelKecamatan import realKecamatan

api = Api()

###### URL API ALL ########
api.add_resource(DataAkhir, '/DataAkhir', endpoint='DataAkhir')
api.add_resource(MATANGD.ListAll, '/MATANGD', endpoint='MATANGD')
api.add_resource(MATANGD.ListAll2, '/MATANGDall2', endpoint='MATANGDall2')
api.add_resource(MATANGD.ListById, '/MATANGD/<int:id>', endpoint='MATANGDbyid')

api.add_resource(ApiUrlListResource, '/apiurl')
api.add_resource(ApiUrlResource, '/apiurl/<int:id>')

###### URL API INTEGRASI DASHBOARD ########
api.add_resource(RevenueSummary, '/revenue-summary', endpoint='revenue-summary')
api.add_resource(RevenueCategories, '/revenue-categories', endpoint='revenue-categories')
api.add_resource(TaxEntities, '/tax-entities', endpoint='tax-entities')
api.add_resource(RevenueLogType, '/revenue-log/<logType>', endpoint='revenue-log')
api.add_resource(Transactions, '/transactions', endpoint='transactions')

api.add_resource(ApiUrlLookup, '/lookupapi-url')
# api.add_resource(ApiPemdaLookup, '/lookupapi-pemda')

api.add_resource(MsJenisPendapatan.jenispajak, '/jenispajak', endpoint='jenispajak')
api.add_resource(MsJenisPendapatan.ListAll, '/MsJenisPendapatan', endpoint='MsJenisPendapatan')
api.add_resource(MsJenisPendapatan.ListAll2, '/MsJenisPendapatanall2', endpoint='MsJenisPendapatanall2')
api.add_resource(MsJenisPendapatan.ListAll3, '/MsJenisPendapatanall3', endpoint='MsJenisPendapatanall3')
api.add_resource(MsJenisPendapatan.ListAll4, '/MsJenisPendapatanall4', endpoint='MsJenisPendapatanall4')
api.add_resource(MsJenisPendapatan.ListAll5, '/MsJenisPendapatanall5', endpoint='MsJenisPendapatanall5')
api.add_resource(MsJenisPendapatan.ListAll50, '/MsJenisPendapatanall50', endpoint='MsJenisPendapatanall50')
api.add_resource(MsJenisPendapatan.ListAll51, '/MsJenisPendapatanall51', endpoint='MsJenisPendapatanall51')
api.add_resource(MsJenisPendapatan.ListAll6, '/MsJenisPendapatanall6', endpoint='MsJenisPendapatanall6')
api.add_resource(MsJenisPendapatan.ListAll7, '/MsJenisPendapatanall7', endpoint='MsJenisPendapatanall7')
api.add_resource(MsJenisPendapatan13.ListAll, '/MsJenisPendapatan13all', endpoint='MsJenisPendapatanall')
# api.add_resource(MsJenisPendapatan13.ListAll2, '/MsJenisPendapatan13all2', endpoint='MsJenisPendapatanall2')
api.add_resource(MsJenisPendapatan.ListById, '/MsJenisPendapatan/<int:id>', endpoint='MsJenisPendapatanbyid')

api.add_resource(MsUPT.ListAll, '/MsUPT', endpoint='MsUPT')
api.add_resource(MsUPT.ListAll2, '/MsUPTall2', endpoint='MsUPTall2')
api.add_resource(MsUPT.ListAll3, '/MsUPTall3', endpoint='MsUPTall3')
api.add_resource(MsUPT.ListAll4, '/MsUPTall4', endpoint='MsUPTall4')
api.add_resource(MsUPT.ListAll5, '/MsUPTall5', endpoint='MsUPTall5')
api.add_resource(MsUPT.ListAll6, '/MsUPTall6', endpoint='MsUPTall6')
api.add_resource(MsUPT.ListAll7, '/MsUPTall7', endpoint='MsUPTall7')
api.add_resource(MsUPT.ListAll8, '/MsUPTall8', endpoint='MsUPTall8')
api.add_resource(MsUPT.ListAll9, '/MsUPTall9', endpoint='MsUPTall9')
api.add_resource(MsUPT.ListById, '/MsUPT/<int:id>', endpoint='MsUPTbyid')

api.add_resource(MsPegawai.ListAll, '/MsPegawai', endpoint='MsPegawai')
api.add_resource(MsPegawai.ListAll2, '/MsPegawaiall2', endpoint='MsPegawaiall2')
api.add_resource(MsPegawai.ListAll3, '/MsPegawaiall3/<int:uptid>', endpoint='MsPegawaiall3')
api.add_resource(MsPegawai.ListAll4, '/MsPegawaiall4', endpoint='MsPegawaiall4')
api.add_resource(MsPegawai.ListAll5, '/MsPegawaiall5', endpoint='MsPegawaiall5')
api.add_resource(MsPegawai.ListById, '/MsPegawai/<int:id>', endpoint='MsPegawaibyid')

api.add_resource(MsBendahara.ListAll, '/MsBendahara', endpoint='MsBendahara')
api.add_resource(MsBendahara.ListAll2, '/MsBendaharaall2', endpoint='MsBendaharaall2')
api.add_resource(MsBendahara.ListById, '/MsBendahara/<int:id>', endpoint='MsBendaharabyid')
api.add_resource(MsBendahara.ListAll5, '/MsBendahara5', endpoint='MsBendahara5')

api.add_resource(MsBank.ListAll, '/MsBank', endpoint='MsBank')
api.add_resource(MsBank.ListAll2, '/MsBankall2', endpoint='MsBankall2')
api.add_resource(MsBank.ListById, '/MsBank/<int:id>', endpoint='MsBankbyid')
api.add_resource(MsBankUPT.ListAll, '/MsBankUPT', endpoint='MsBankUPT')
api.add_resource(MsBankUPT.ListById, '/MsBankUPT/<int:id>', endpoint='MsBankUPTbyid')
api.add_resource(MsBank.ListAll5, '/MsBank5', endpoint='MsBank5')

api.add_resource(MsJenisStatus.ListAll, '/MsJenisStatus', endpoint='MsJenisStatus')
api.add_resource(MsJenisStatus.ListAll2, '/MsJenisStatusall2', endpoint='MsJenisStatusall2')
api.add_resource(MsJenisStatus.ListAll3, '/MsJenisStatusall3', endpoint='MsJenisStatusall3')
api.add_resource(MsJenisStatus.ListAll4, '/MsJenisStatusall4', endpoint='MsJenisStatusall4')
# api.add_resource(MsJenisStatus.ListById, '/MsJenisStatus/<int:id>', endpoint='MsJenisStatusbyid')

api.add_resource(MsTargetPendapatan.ListAll, '/MsTargetPendapatan', endpoint='MsTargetPendapatan')
api.add_resource(MsTargetPendapatan.ListById, '/MsTargetPendapatan/<int:id>', endpoint='MsTargetPendapatanbyidbyid')

api.add_resource(GeneralParameter.ListAll, '/GeneralParameter', endpoint='GeneralParameter')
api.add_resource(GeneralParameter.ListById, '/GeneralParameter/<int:id>', endpoint='GeneralParameterbyidbyid')

api.add_resource(TransactionControl.ListAll, '/TransactionControl', endpoint='TransactionControl')
api.add_resource(TransactionControl.ListById, '/TransactionControl/<int:id>', endpoint='TransactionControlbyid')

api.add_resource(MsTipeLokasi.ListAll, '/MsTipeLokasi', endpoint='MsTipeLokasi')
api.add_resource(MsTipeLokasi.ListAll2, '/MsTipeLokasiall2', endpoint='MsTipeLokasiall2')
api.add_resource(MsTipeLokasi.ListAll3, '/MsTipeLokasiall3/<int:tipelokasiid>', endpoint='MsTipeLokasiall3')
api.add_resource(MsTipeLokasi.ListById, '/MsTipeLokasi/<int:id>', endpoint='MsTipeLokasibyid')

api.add_resource(MsStrategisHdr.ListAll, '/MsStrategisHdr', endpoint='MsStrategisHdr')
api.add_resource(MsStrategisHdr.ListAll2, '/MsStrategisHdrall2', endpoint='MsStrategisHdrall2')
api.add_resource(MsStrategisHdr.ListAll3, '/MsStrategisHdrall3', endpoint='MsStrategisHdrall3')
api.add_resource(MsStrategisHdr.ListById, '/MsStrategisHdr/<int:id>', endpoint='MsStrategisHdrbyid')

api.add_resource(MsStrategisDtl.ListAll, '/MsStrategisDtl', endpoint='MsStrategisDtl')
api.add_resource(MsStrategisDtl.ListAll1, '/MsStrategisDtlall1', endpoint='MsStrategisDtlall1')
api.add_resource(MsStrategisDtl.ListAll2, '/MsStrategisDtlall2', endpoint='MsStrategisDtlall2')
api.add_resource(MsStrategisDtl.ListAll3, '/MsStrategisDtlall3', endpoint='MsStrategisDtlall3')
api.add_resource(MsStrategisDtl.ListAll4, '/MsStrategisDtlall4', endpoint='MsStrategisDtlall4')
api.add_resource(MsStrategisDtl.ListAll5, '/MsStrategisDtlall5', endpoint='MsStrategisDtlall5')
api.add_resource(MsStrategisDtl.ListAll6, '/MsStrategisDtlall6', endpoint='MsStrategisDtlall6')
api.add_resource(MsStrategisDtl.ListAll7, '/MsStrategisDtlall7', endpoint='MsStrategisDtlall7')
api.add_resource(MsStrategisDtl.ListById, '/MsStrategisDtl/<int:id>', endpoint='MsStrategisDtlbyid')

api.add_resource(MsTitikLokasiHdr.ListAll, '/MsTitikLokasiHdr', endpoint='MsTitikLokasiHdr')
api.add_resource(MsTitikLokasiHdr.ListAll2, '/MsTitikLokasiHdrall2/<int:tipelokasiid>', endpoint='MsTitikLokasiHdrall2')
api.add_resource(MsTitikLokasiHdr.ListAll3, '/MsTitikLokasiHdrall3', endpoint='MsTitikLokasiHdrall3')
api.add_resource(MsTitikLokasiHdr.ListById, '/MsTitikLokasiHdr/<int:id>', endpoint='MsTitikLokasiHdrbyid')

api.add_resource(MsJenisUsaha.ListAll, '/MsJenisUsaha', endpoint='MsJenisUsaha')
api.add_resource(MsJenisUsaha.ListAll2, '/MsJenisUsaha2/<int:jenispendapatanid>', endpoint='MsJenisUsaha2')
api.add_resource(MsJenisUsaha.ListById, '/MsJenisUsaha/<int:id>', endpoint='MsJenisUsahabyidbyid')

api.add_resource(MsTarifLokasi.ListAll, '/MsTarifLokasi', endpoint='MsTarifLokasi')
api.add_resource(MsTarifLokasi.ListAll2, '/MsTarifLokasiall2/<int:jenispendapatanid>', endpoint='MsTarifLokasiall2')
api.add_resource(tarifpajak, '/tarifpajak/<int:jenispendapatanid>', endpoint='tarifpajak')
api.add_resource(MsTarifLokasi.ListById, '/MsTarifLokasi/<int:id>', endpoint='MsTarifLokasibyid')

api.add_resource(GroupAttribute.ListAll, '/GroupAttribute', endpoint='GroupAttribute')

# api.add_resource(GroupAttribute.ListById, '/GroupAttribute/<int:id>', endpoint='GroupAttributebyid')
api.add_resource(MsGrupUsaha.ListAll, '/MsGrupUsaha', endpoint='MsGrupUsaha')
api.add_resource(MsGrupUsaha.ListAll2, '/MsGrupUsahaall2', endpoint='MsGrupUsahaall2')
api.add_resource(MsGrupUsaha.ListById, '/MsGrupUsaha/<int:id>', endpoint='MsGrupUsahabyid')

api.add_resource(MsJenisPungut.ListAll, '/MsJenisPungut', endpoint='MsJenisPungut')
api.add_resource(MsJenisPungut.ListAll2, '/MsJenisPungutall2', endpoint='MsJenisPungutall2')
api.add_resource(MsJenisPungut.ListById, '/MsJenisPungut/<int:id>', endpoint='MsJenisPungutbyid')

api.add_resource(MsLokasiKhusus.ListAll, '/MsLokasiKhusus', endpoint='MsLokasiKhusus')
api.add_resource(MsLokasiKhusus.ListAll, '/MsLokasiKhususall2', endpoint='MsLokasiKhususall2')
# api.add_resource(MsLokasiKhusus.ListById, '/MsLokasiKhusus/<int:id>', endpoint='MsLokasiKhususbyid')

api.add_resource(MsKlasifikasiUsaha.ListAll, '/MsKlasifikasiUsaha', endpoint='MsKlasifikasiUsaha')
api.add_resource(MsKlasifikasiUsaha.ListAll2, '/MsKlasifikasiUsahaall2', endpoint='MsKlasifikasiUsahaall2')
api.add_resource(MsKlasifikasiUsaha.ListById, '/MsKlasifikasiUsaha/<int:id>', endpoint='MsKlasifikasiUsahabyid')

api.add_resource(MsSatuanOmzet.ListAll, '/MsSatuanOmzet', endpoint='MsSatuanOmzet')
api.add_resource(MsSatuanOmzet.ListAll2, '/MsSatuanOmzetall2', endpoint='MsSatuanOmzetall2')
api.add_resource(MsSatuanOmzet.ListAll3, '/MsSatuanOmzetall3', endpoint='MsSatuanOmzetall3')
# api.add_resource(MsSatuanOmzet.ListById, '/MsSatuanOmzet/<int:id>', endpoint='MsSatuanOmzetbyid')

api.add_resource(MsPropinsi.propinsi, '/propinsi', endpoint='propinsi')
api.add_resource(MsPropinsi.lookupPropinsi, '/lookupPropinsi', endpoint='lookupPropinsi')

api.add_resource(MsKota.kota, '/kota', endpoint='kota')
api.add_resource(MsKota.ListAll, '/MsKota', endpoint='MsKota')
api.add_resource(MsKota.ListAll2, '/MsKotaall2', endpoint='MsKotaall2')
api.add_resource(MsKota.ListAll3, '/MsKotaall3', endpoint='MsKotaall3')
api.add_resource(MsKota.ListAll4, '/MsKotaall4', endpoint='MsKotaall4   ')
api.add_resource(MsKota.ListById, '/MsKota/<int:id>', endpoint='MsKotabyid')

api.add_resource(MsKPP.ListAll, '/MsKPP', endpoint='MsKPP')
api.add_resource(MsKPP.ListAll2, '/MsKPPall2', endpoint='MsKPPall2')
api.add_resource(MsKPP.ListById, '/MsKPP/<int:id>', endpoint='MsKPPbyid')

api.add_resource(MsKecamatan.kecamatan, '/kecamatan', endpoint='kecamatan')
api.add_resource(MsKecamatan.ListAll, '/MsKecamatan', endpoint='MsKecamatan')
api.add_resource(MsKecamatan.ListAll2, '/MsKecamatanall2/<int:kotaid>', endpoint='MsKecamatanall2')
api.add_resource(MsKecamatan.ListAll3, '/MsKecamatanall3/<int:faxkecamatan>', endpoint='MsKecamatanall3')
api.add_resource(MsKecamatan.ListAll4, '/MsKecamatanall4', endpoint='MsKecamatanall4')
api.add_resource(MsKecamatan.ListAll5, '/MsKecamatanall5', endpoint='MsKecamatanall5')
api.add_resource(MsKecamatan.ListById, '/MsKecamatan/<int:id>', endpoint='MsKecamatanbyid')

api.add_resource(MsKelurahan.kelurahan, '/kelurahan', endpoint='kelurahan')
api.add_resource(MsKelurahan.ListAll, '/MsKelurahan', endpoint='MsKelurahan')
api.add_resource(MsKelurahan.ListAll2, '/MsKelurahanall2/<int:kecamatanid>', endpoint='MsKelurahanall2')
api.add_resource(MsKelurahan.ListById, '/MsKelurahan/<int:id>', endpoint='MsKelurahanbyid')

api.add_resource(MsRW.ListAll, '/MsRW', endpoint='MsRW')
api.add_resource(MsRW.ListAll2, '/MsRWall2/<int:kelurahanid>', endpoint='MsRWall2')
api.add_resource(MsRW.ListById, '/MsRW/<int:id>', endpoint='MsRWbyid')

api.add_resource(MsRT.ListAll, '/MsRT', endpoint='MsRT')
api.add_resource(MsRT.ListAll1, '/MsRTall2', endpoint='MsRTall1')
api.add_resource(MsRT.ListAll2, '/MsRTall2/<int:rwid>', endpoint='MsRTall2')
api.add_resource(MsRT.ListById, '/MsRT/<int:id>', endpoint='MsRTbyid')

api.add_resource(MsWPData.ListAll, '/MsWPData', endpoint='MsWPData')
api.add_resource(MsWPData.ListById, '/MsWPData/<int:id>', endpoint='MsWPDatabyid')
api.add_resource(MsWPData.ListAll2, '/MsWPDataall2', endpoint='MsWPDataall2')
api.add_resource(MsWPData.ListAll21, '/MsWPDataall21', endpoint='MsWPDataall21')
api.add_resource(MsWPData.ListAll3, '/MsWPDataall3/<int:wpid>', endpoint='MsWPDataall3')

api.add_resource(MsOPD.ListAll, '/MsOPD', endpoint='MsOPD')
# api.add_resource(MsOPD.ListById, '/MsOPD/<int:id>', endpoint='MsOPDbyid')
api.add_resource(MsOPD.ListAll2, '/MsOPDall2', endpoint='MsOPDall2')
api.add_resource(MsOPD.ListAll3, '/MsOPDall3/<int:opdid>', endpoint='MsOPDall3')

api.add_resource(MsWapu.ListAll, '/MsWapu', endpoint='MsWapu')
api.add_resource(MsWapu.ListById, '/MsWapu/<int:id>', endpoint='MsWapubyid')
api.add_resource(MsWapu.ListAll2, '/MsWapuall2', endpoint='MsWapuall2')
api.add_resource(MsWapu.ListAll3, '/MsWapuall3/<int:wapuid>', endpoint='MsWapuall3')
api.add_resource(MsWapu.ListAll5, '/MsWapuall5', endpoint='MsWapuall5')

# api.add_resource(MsWPData2.ListAll, '/MsWPData2', endpoint='MsWPData2')

api.add_resource(datawp, '/datawp', endpoint='datawp')

api.add_resource(MsWPOData.ListAll, '/MsWPOData', endpoint='MsWP)Data')
api.add_resource(MsWPOData.ListAll3, '/MsWPODataall3/<int:wpid>', endpoint='MsWPODataall3')

api.add_resource(MsWP.ListAll, '/MsWP', endpoint='MsWP')
api.add_resource(MsWP.ListById, '/MsWP/<int:id>', endpoint='MsWPbyid')

api.add_resource(AddPendaftaran, '/AddPendaftaran', endpoint='AddPendaftaran')
api.add_resource(AddPendaftaranRekening, '/AddPendaftaranRekening/<int:id>', endpoint='AddPendaftaranRekening')
api.add_resource(UpdatePendaftaran, '/UpdatePendaftaran/<int:id>', endpoint='UpdatePendaftaran')
api.add_resource(DeletePendaftaran, '/DeletePendaftaran/<int:id>', endpoint='DeletePendaftaran')

api.add_resource(AddPendaftaranObjekPajak, '/AddPendaftaranObjekPajak', endpoint='AddPendaftaranObjekPajak')
api.add_resource(generate_nop, '/generate_nop', endpoint='generate_nop')
api.add_resource(AddPendaftaranObjekPajakRekening, '/AddPendaftaranObjekPajakRekening/<int:id>', endpoint='AddPendaftaranObjekPajakRekening')
api.add_resource(UpdatePendaftaranObjekPajak, '/UpdatePendaftaranObjekPajak/<int:id>', endpoint='UpdatePendaftaranObjekPajak')
api.add_resource(DeletePendaftaranObjekPajak, '/DeletePendaftaranObjekPajak/<int:id>', endpoint='DeletePendaftaranObjekPajak')

api.add_resource(AddPendaftaranWapu, '/AddPendaftaranWapu', endpoint='AddPendaftaranWapu')
api.add_resource(UpdatePendaftaranWapu, '/UpdatePendaftaranWapu/<int:id>', endpoint='UpdatePendaftaranWapu')
api.add_resource(DeletePendaftaranWapu, '/DeletePendaftaranWapu/<int:id>', endpoint='DeletePendaftaranWapu')

api.add_resource(AddPendaftaranWPO, '/AddPendaftaranWPO', endpoint='AddPendaftaranWPO')
api.add_resource(UpdatePendaftaranWPO, '/UpdatePendaftaranWPO/<int:id>', endpoint='UpdatePendaftaranWPO')

api.add_resource(pendaftaran, '/pendaftaran', endpoint='pendaftaran')

api.add_resource(Penonaktifan, '/Penonaktifan', endpoint='Penonaktifan')
api.add_resource(PenonaktifanEdit, '/PenonaktifanEdit/<int:wpid>', endpoint='PenonaktifanEdit')
api.add_resource(UpdatePenonaktifan, '/UpdatePenonaktifan/<int:id>', endpoint='UpdatePenonaktifan')

api.add_resource(Aktivasi, '/Aktivasi', endpoint='Aktivasi')
api.add_resource(AktivasiEdit, '/AktivasiEdit/<int:wpid>', endpoint='AktivasiEdit')
api.add_resource(UpdateAktivasi, '/UpdateAktivasi/<int:id>', endpoint='UpdateAktivasi')

api.add_resource(PenonaktifanWapuEdit, '/PenonaktifanWapuEdit/<int:wapuid>', endpoint='PenonaktifanWapuEdit')
api.add_resource(PenonaktifanWapu, '/PenonaktifanWapu', endpoint='PenonaktifanWapu')
api.add_resource(UpdatePenonaktifanWapu, '/UpdatePenonaktifanWapu/<int:id>', endpoint='UpdatePenonaktifanWapu')

api.add_resource(AktivasiWapu, '/AktivasiWapu', endpoint='AktivasiWapu')
api.add_resource(AktivasiWapuEdit, '/AktivasiWapuEdit/<int:wapuid>', endpoint='AktivasiWapuEdit')
api.add_resource(UpdateAktivasiWapu, '/UpdateAktivasiWapu/<int:id>', endpoint='UpdateAktivasiWapu')

api.add_resource(PenonaktifanOPDEdit, '/PenonaktifanOPDEdit/<int:opdid>', endpoint='PenonaktifanOPDEdit')
api.add_resource(PenonaktifanOPD, '/PenonaktifanOPD', endpoint='PenonaktifanOPD')
api.add_resource(UpdatePenonaktifanOPD, '/UpdatePenonaktifanOPD/<int:id>', endpoint='UpdatePenonaktifanOPD')

api.add_resource(AktivasiOPD, '/AktivasiOPD', endpoint='AktivasiOPD')
api.add_resource(AktivasiOPDEdit, '/AktivasiOPDEdit/<int:opdid>', endpoint='AktivasiOPDEdit')
api.add_resource(UpdateAktivasiOPD, '/UpdateAktivasiOPD/<int:id>', endpoint='UpdateAktivasiWOPD')

api.add_resource(PendataanByOmzet.ListAll, '/PendataanByOmzet', endpoint='PendataanByOmzet')
api.add_resource(PendataanByOmzet.ListById, '/PendataanByOmzet/<int:id>', endpoint='PendataanByOmzetbyid')

api.add_resource(PendataanByOmzetDtl.ListAll, '/PendataanByOmzetDtl', endpoint='PendataanByOmzetDtl')
api.add_resource(PendataanByOmzetDtl.ListById, '/PendataanByOmzetDtl/<int:id>', endpoint='PendataanByOmzetDtlbyid')

api.add_resource(vw_pendataan.ListAll, '/vw_pendataan', endpoint='vw_pendataan')
api.add_resource(vw_penetapan.ListAll, '/vw_penetapan', endpoint='vw_penetapan')
api.add_resource(vw_pembayaran.ListAll, '/vw_pembayaran', endpoint='vw_pembayaran')
api.add_resource(vw_setoran.ListAll, '/vw_setoran', endpoint='vw_setoran')

api.add_resource(pendataanpajak, '/pendataanpajak', endpoint='pendataanpajak')
api.add_resource(PendataanSKP, '/PendataanSKP', endpoint='PendataanSKP')
api.add_resource(PendataanSKP2, '/PendataanSKP2', endpoint='PendataanSKP2')
api.add_resource(PendataanSKP3, '/PendataanSKP3/<int:opdid>', endpoint='PendataanSKP3')
api.add_resource(PendataanSKPOmzet, '/PendataanSKPOmzet/<int:opdid>', endpoint='PendataanSKPOmzet')
api.add_resource(AddPendataanSKP, '/AddPendataanSKP', endpoint='AddPendataanSKP')
api.add_resource(AddPendataanBPHTB, '/AddPendataanBPHTB', endpoint='AddPendataanBPHTB')
api.add_resource(UpdatePendataanSKP, '/UpdatePendataanSKP/<int:id>', endpoint='UpdatePendataanSKP')
api.add_resource(DeletePendataanSKP, '/DeletePendataanSKP/<int:id>', endpoint='DeletePendataanSKP')
api.add_resource(PendataanSKPOmset, '/PendataanSKPOmset/<int:opdid>', endpoint='PendataanSKPOmset')
api.add_resource(OmzetHarian.ListAll, '/OmzetHarianall', endpoint='OmzetHarianall')
api.add_resource(OmzetHarianSKP, '/omzetharian', endpoint='omzetharian')
api.add_resource(OmzetHarianSKPOmzet, '/omzetharianid/<int:opdid>', endpoint='omzetharianid')
api.add_resource(AddOmzetHarianSKP, '/addomzetharian', endpoint='/addomzetharian')

api.add_resource(PelaporanOmzet, '/PelaporanOmzet', endpoint='PelaporanOmzet')
api.add_resource(AddPelaporanOmzet, '/AddPelaporanOmzet', endpoint='AddPelaporanOmzet')
api.add_resource(PelaporanOmzetDet, '/PelaporanOmzetDet/<int:opdid>', endpoint='PelaporanOmzetDet')
api.add_resource(DeletePelaporanOmzet, '/DeletePelaporanOmzet/<int:id>', endpoint='/DeletePelaporanOmzet')

api.add_resource(PendataanSKPReklame, '/PendataanSKPReklame/<int:opdid>', endpoint='PendataanSKPReklame')
api.add_resource(HitungSKPReklame, '/HitungSKPReklame', endpoint='HitungSKPReklame')
api.add_resource(AddPendataanSKPReklame, '/AddPendataanSKPReklame', endpoint='AddPendataanSKPReklame')
api.add_resource(UpdatePendataanSKPReklame, '/UpdatePendataanSKPReklame/<int:id>', endpoint='UpdatePendataanSKPReklame')
api.add_resource(DeletePendataanSKPReklame, '/DeletePendataanSKPReklame/<int:id>', endpoint='DeletePendataanSKPReklame')

api.add_resource(PendataanSPTP, '/PendataanSPTP', endpoint='PendataanSPTP')
api.add_resource(PendataanSPTP2, '/PendataanSPTP2', endpoint='PendataanSPTP2')
api.add_resource(PendataanSPTP3, '/PendataanSPTP3/<int:opdid>', endpoint='PendataanSPTP23')
api.add_resource(PendataanSPTPOmzet, '/PendataanSPTPOmzet/<int:opdid>', endpoint='PendataanSPTPOmzet')
api.add_resource(AddPendataanSPTP, '/AddPendataanSPTP', endpoint='AddPendataanSPTP')
api.add_resource(UpdatePendataanSPTP, '/UpdatePendataanSPTP/<int:id>', endpoint='UpdatePendataanSPTP')
api.add_resource(DeletePendataanSPTP, '/DeletePendataanSPTP/<int:id>', endpoint='DeletePendataanSPTP')

api.add_resource(PendataanReklameHdr.ListAll, '/PendataanReklameHdr', endpoint='PendataanReklameHdr')
api.add_resource(PendataanReklameHdr.ListById, '/PendataanReklameHdr/<int:id>', endpoint='PendataanReklameHdrbyid')

# api.add_resource(PendataanReklameDtl.ListAll, '/PendataanReklameDtl', endpoint='PendataanReklameDtl')
# api.add_resource(PendataanReklameDtl.ListById, '/PendataanReklameDtl/<int:id>', endpoint='PendataanReklameDtlbyid')

api.add_resource(PenetapanByOmzet.ListAll, '/PenetapanByOmzet', endpoint='PenetapanByOmzet')
api.add_resource(PenetapanByOmzet.ListById, '/PenetapanByOmzet/<int:id>', endpoint='PenetapanByOmzetbyid')

api.add_resource(PenetapanSKPReklame, '/PenetapanSKPReklame', endpoint='PenetapanSKPReklame')
api.add_resource(PenetapanSKPReklame2, '/PenetapanSKPReklame2', endpoint='PenetapanSKPReklame2')
api.add_resource(PenetapanSKPReklame3, '/PenetapanSKPReklame3/<int:pendataanid>', endpoint='PenetapanSKPReklame3')
api.add_resource(PenetapanSKPReklame4, '/PenetapanSKPReklame4', endpoint='PenetapanSKPReklame4')
api.add_resource(PenetapanSKPReklame5, '/PenetapanSKPReklame5/<int:penetapanid>', endpoint='PenetapanSKPReklame5')
api.add_resource(AddPenetapanSKPReklame, '/AddPenetapanSKPReklame', endpoint='AddPenetapanSKPReklame')
api.add_resource(UpdatePenetapanSKPReklame, '/UpdatePenetapanSKPReklame/<int:id>', endpoint='UpdatePenetapanSKPReklame')
api.add_resource(UpdatePenetapanSKPReklameKurangBayar, '/UpdatePenetapanSKPReklameKurangBayar/<int:id>',
                 endpoint='UpdatePenetapanSKPReklameKurangBayar')
api.add_resource(DeletePenetapanSKPReklame, '/DeletePenetapanSKPReklame/<int:id>', endpoint='DeletePenetapanSKPReklame')

api.add_resource(PenetapanSKP, '/PenetapanSKP', endpoint='PenetapanSKP')
api.add_resource(PenetapanSKP2, '/PenetapanSKP2', endpoint='PenetapanSKP2')
api.add_resource(PenetapanSKP3, '/PenetapanSKP3/<int:pendataanid>', endpoint='PenetapanSKP3')
api.add_resource(PenetapanSKP4, '/PenetapanSKP4', endpoint='PenetapanSKP4')
api.add_resource(PenetapanSKP5, '/PenetapanSKP5/<int:penetapanid>', endpoint='PenetapanSKP5')
api.add_resource(PenetapanSKP6, '/PenetapanSKP6', endpoint='PenetapanSKP6')
api.add_resource(AddPenetapanSKP, '/AddPenetapanSKP', endpoint='AddPenetapanSKP')
api.add_resource(UpdatePenetapanSKP, '/UpdatePenetapanSKP/<int:id>', endpoint='UpdatePenetapanSKP')
api.add_resource(UpdatePenetapanSKPKurangBayar, '/UpdatePenetapanSKPKurangBayar/<int:id>',
                 endpoint='UpdatePenetapanSKPKurangBayar')
api.add_resource(DeletePenetapanSKP, '/DeletePenetapanSKP/<int:id>', endpoint='DeletePenetapanSKP')

api.add_resource(HistPenetapanSKP, '/HistPenetapanSKP', endpoint='HistPenetapanSKP')
api.add_resource(UpdateHistPenetapanSKP, '/UpdateHistPenetapanSKP/<int:id>', endpoint='UpdateHistPenetapanSKP')

api.add_resource(ValidasiSPTP, '/ValidasiSPTP', endpoint='ValidasiSPTP')
api.add_resource(ValidasiSPTP2, '/ValidasiSPTP2', endpoint='ValidasiSPTP2')
api.add_resource(ValidasiSPTP3, '/ValidasiSPTP3/<int:pendataanid>', endpoint='ValidasiSPTP3')
api.add_resource(ValidasiSPTP4, '/ValidasiSPTP4', endpoint='ValidasiSPTP4')
api.add_resource(ValidasiSPTP5, '/ValidasiSPTP5/<int:penetapanid>', endpoint='ValidasiSPTP5')
api.add_resource(AddValidasiSPTP, '/AddValidasiSPTP', endpoint='AddValidasiSPTP')
api.add_resource(UpdateValidasiSPTP, '/UpdateValidasiSPTP/<int:id>', endpoint='UpdateValidasiSPTP')
api.add_resource(UpdateValidasiSPTPKurangBayar, '/UpdateValidasiSPTPKurangBayar/<int:id>',
                 endpoint='UpdateValidasiSPTPKurangBayar')
api.add_resource(DeleteValidasiSPTP, '/DeleteValidasiSPTP/<int:id>', endpoint='DeleteValidasiSPTP')

api.add_resource(Pembayaran.ListAll, '/Pembayaran', endpoint='Pembayaran')
api.add_resource(PembayaranSKP, '/PembayaranSKP', endpoint='PembayaranSKP')
api.add_resource(statuspembayaran, '/statuspembayaran', endpoint='statuspembayaran')
api.add_resource(genkodebayar, '/genkodebayar', endpoint='genkodebayar')
api.add_resource(HitungDenda, '/HitungDenda', endpoint='HitungDenda')
api.add_resource(PembayaranSKP3, '/PembayaranSKP3/<int:kohirid>', endpoint='PembayaranSKP3')
api.add_resource(PembayaranSKP4, '/PembayaranSKP4/<int:kohirid>', endpoint='PembayaranSKP4')
api.add_resource(PembayaranSKP5, '/PembayaranSKP5/<int:penetapanid>', endpoint='PembayaranSKP5')
api.add_resource(AddPembayaranSKP, '/AddPembayaranSKP', endpoint='AddPembayaranSKP')
api.add_resource(AddPembayaranSKPWPO, '/AddPembayaranSKPWPO', endpoint='AddPembayaranSKPWPO')
api.add_resource(UpdatePembayaranSKP, '/UpdatePembayaranSKP/<int:id>', endpoint='UpdatePembayaranSKP')
api.add_resource(DeletePembayaranSKP, '/DeletePembayaranSKP/<int:id>', endpoint='DeletePembayaranSKP')

api.add_resource(PembayaranSPTP, '/PembayaranSPTP', endpoint='PembayaranSPTP')
api.add_resource(PembayaranSPTP2, '/PembayaranSPTP2', endpoint='PembayaranSPTP2')
api.add_resource(PembayaranSPTP3, '/PembayaranSPTP3/<int:kohirid>', endpoint='PembayaranSPTP3')
api.add_resource(PembayaranSPTP4, '/PembayaranSPTP4/<int:kohirid>', endpoint='PembayaranSPTP4')
api.add_resource(PembayaranSPTP5, '/PembayaranSPTP5/<int:kohirid>', endpoint='PembayaranSPTP5')
api.add_resource(AddPembayaranSPTP, '/AddPembayaranSPTP', endpoint='AddPembayaranSPTP')
api.add_resource(UpdatePembayaranSPTP, '/UpdatePembayaranSPTP/<int:id>', endpoint='UpdatePembayaranSPTP')
api.add_resource(DeletePembayaranSPTP, '/DeletePembayaranSPTP/<int:id>', endpoint='DeletePembayaranSPTP')

api.add_resource(Setoran, '/Setoran', endpoint='Setoran')
api.add_resource(Setoran2, '/Setoran2', endpoint='Setoran2')
api.add_resource(Setoran3, '/Setoran3/<int:headerid>', endpoint='Setoran3')
api.add_resource(Setoran4, '/Setoran4/<int:headerid>', endpoint='Setoran4')
api.add_resource(Setoran5, '/Setoran5/<int:headerid>', endpoint='Setoran5')
api.add_resource(Setoran6, '/Setoran6', endpoint='Setoran6')
api.add_resource(Setoran7, '/Setoran7', endpoint='Setoran7')
api.add_resource(AddSetoran, '/AddSetoran', endpoint='AddSetoran')
api.add_resource(AddSetoranDtl, '/AddSetoranDtl', endpoint='AddSetoranDtl')
api.add_resource(DeleteSetoranDtl, '/DeleteSetoranDtl/<int:id>', endpoint='DeleteSetoranDtl')
api.add_resource(UpdateSetoran, '/UpdateSetoran/<int:id>', endpoint='UpdateSetoran')
api.add_resource(DeleteSetoran, '/DeleteSetoran/<int:id>', endpoint='DeleteSetoran')

api.add_resource(NomorKohir.ListAll, '/NomorKohir', endpoint='NomorKohir')

api.add_resource(PenetapanReklameHdr.ListAll, '/PenetapanReklameHdr', endpoint='PenetapanReklameHdr')
api.add_resource(PenetapanReklameDtl.ListAll, '/PenetapanReklameDtl', endpoint='PenetapanReklameDtl')

api.add_resource(SetoranHist.ListAll, '/SetoranHist', endpoint='SetoranHist')
api.add_resource(SetoranHist.ListById, '/SetoranHist/<int:id>', endpoint='SetoranHistbyid')

api.add_resource(vw_suratteguranhist.ListAll, '/vw_suratteguranhist', endpoint='vw_suratteguranhist')
api.add_resource(SuratTeguranHist.ListAll, '/SuratTeguranHist', endpoint='SuratTeguranHist')
api.add_resource(SuratTeguranHist.ListAll2, '/SuratTeguranHist2', endpoint='SuratTeguranHist2')
api.add_resource(SuratTeguranHist.ListAll3, '/SuratTeguranHist3/<int:kohirid>', endpoint='SuratTeguranHist3')
api.add_resource(SuratTeguranHist.ListAll4, '/SuratTeguranHist4', endpoint='SuratTeguranHist4')
api.add_resource(SuratTeguranHist.ListById, '/SuratTeguranHist/<int:id>', endpoint='SuratTeguranHistbyid')

api.add_resource(SetoranUPTHdr.ListAll, '/SetoranUPTHdr', endpoint='SetoranUPTHdr')
api.add_resource(SetoranUPTHdr.ListById, '/SetoranUPTHdr/<int:id>', endpoint='SetoranUPTHdrbyid')

api.add_resource(SetoranUPTDtl.ListAll, '/SetoranUPTDtl', endpoint='SetoranUPTDtl')
api.add_resource(SetoranUPTDtl.ListById, '/SetoranUPTDtl/<int:id>', endpoint='SetoranUPTDtlbyid')

api.add_resource(tblUserWP.ListAll, '/tblUserWP', endpoint='tblUserWP')
api.add_resource(vw_userwp.ListAll, '/vw_userwp', endpoint='vw_userwp')

api.add_resource(PenetapanSamsat.listAll, '/opsenresource', endpoint='opsenresource')
api.add_resource(PenetapanKB.InstblOpsen, '/insopsen', endpoint='insopsen')
api.add_resource(PenetapanKB.InsSTS, '/inssts', endpoint='inssts')
api.add_resource(PenetapanKB.PenetapanKBResource, '/opsensource', endpoint='opsensource')
api.add_resource(PenetapanKB.PenetapanKBResource4, '/opsensource4/<int:headerid>', endpoint='opsensource4')
api.add_resource(PenetapanKB.PenetapanKBResource7, '/opsensource7', endpoint='opsensource7')
api.add_resource(PenetapanKB.PenetapanKBResourceID, '/opsensource/<int:id>', endpoint='opsensourcebyid')


api.add_resource(tblOpsen.OpsenListResource, '/opsen', endpoint='opsen')
api.add_resource(tblOpsen.OpsenListResource4, '/opsen4/<int:headerid>', endpoint='opsen4')
api.add_resource(tblOpsen.OpsenListResource7, '/opsen7', endpoint='opsen7')
api.add_resource(tblOpsen.opsenlist, '/opsenlist', endpoint='opsenlist')
api.add_resource(tblOpsen.OpsenResource, '/opsen/<int:id>', endpoint='opsenbyid')

api.add_resource(chartOpsen.realopsen, '/realopsen', endpoint='realopsen')

api.add_resource(OpsenListResourceNotSTS, '/opsensourcenotsend', endpoint='opsensourcenotsend')
api.add_resource(OpsenListResourceNotSTS4, '/opsensourcenotsend4/<int:headerid>', endpoint='opsensourcenotsend4')
api.add_resource(OpsenListResourceNotSTS7, '/opsensourcenotsend7', endpoint='opsensourcenotsend7')

api.add_resource(GeoData.ListAll, '/geodata', endpoint='geodata')
api.add_resource(GeoData.ListById, '/geodata/<int:id>', endpoint='geodatabyid')

api.add_resource(tblUrl.ListAll, '/tblUrl', endpoint='tblUrl')
api.add_resource(tblUrl.ListAll2, '/tblUrlall2', endpoint='tblUrlall2')
api.add_resource(tblUrl.ListAll3, '/tblUrlall3', endpoint='tblUrlall3')
api.add_resource(tblUrl.ListById, '/tblUrl/<int:id>', endpoint='tblUrlbyid')

api.add_resource(tblMenu.ListAll, '/tblMenu', endpoint='tblMenu')
api.add_resource(tblMenu.ListAll2, '/tblMenuall2', endpoint='tblMenuall2')
api.add_resource(tblMenu.ListAll3, '/tblMenuall3/<int:menuid>', endpoint='tblMenuall3')
api.add_resource(tblMenu.ListAll4, '/tblMenuall4', endpoint='tblMenuall4')
api.add_resource(tblMenu.ListById, '/tblMenu/<int:id>', endpoint='tblMenubyid')

api.add_resource(tblMenuDet.ListAll, '/tblMenuDet', endpoint='tblMenuDet')
api.add_resource(tblMenuDet.ListAll2, '/tblMenuDetall2', endpoint='tblMenuDetall2')
api.add_resource(tblMenuDet.ListAll3, '/tblMenuDetall3/<int:menuid>', endpoint='tblMenuDetall3')
api.add_resource(tblMenuDet.ListById, '/tblMenuDet/<int:id>', endpoint='tblMenuDetbyid')
api.add_resource(tblMenuDet.AddUrl, '/AddUrl/<int:id>', endpoint='AddUrl')

api.add_resource(tblAkses.ListAll, '/tblAkses', endpoint='tblAkses')
api.add_resource(tblAkses.ListAll2, '/tblAksesall2', endpoint='tblAksesall2')
api.add_resource(tblAkses.ListAll3, '/tblAksesall3', endpoint='tblAksesall3')
api.add_resource(tblAkses.tblAkses4, '/tblAkses4/<int:groupid>', endpoint='tblAkses4')
api.add_resource(tblAkses.ListAll4, '/tblAksesall4', endpoint='tblAksesall4')
api.add_resource(tblAkses.ListById, '/tblAkses/<int:id>', endpoint='tblAksesbyid')

api.add_resource(tblRole.ListAll, '/tblRole', endpoint='tblRole')
api.add_resource(tblRole.ListAll2, '/tblRoleall2', endpoint='tblRolelall2')
api.add_resource(tblRole.ListById, '/tblRole/<int:id>', endpoint='tblRolelbyid')

api.add_resource(piutang, '/piutang', endpoint='piutang')
api.add_resource(realbulan, '/realbulan', endpoint='realbulan')
api.add_resource(realTahun, '/realTahun', endpoint='realTahun')
api.add_resource(realTW, '/realTW', endpoint='realTW')
api.add_resource(realWP, '/realWP', endpoint='realWP')
api.add_resource(realUPTD, '/realUPTD', endpoint='realUPTD')
api.add_resource(realKecamatan, '/realKecamatan', endpoint='realKecamatan')


# WPO
api.add_resource(GetListUsaha, '/get_list_usaha', endpoint='get_list_usaha')
api.add_resource(GetUsaha, '/get_usaha/<npwpd>', endpoint='get_usaha')
api.add_resource(GetUsahaLookup, '/get_usaha_lookup/<npwpd>', endpoint='get_usaha_lookup')
api.add_resource(GetSubscription, '/get_subscription/<npwpd>', endpoint='get_subscription')
api.add_resource(GetAllBill, '/get_tagihan', endpoint='get_tagihan')
api.add_resource(AddUsahaFromOldWPO, '/add_npwpd/<npwpd>', endpoint='add_npwpd')
# api.add_resource(tblUserWP.ListById, '/tblUserWP/<int:id>', endpoint='tblUserWP')

# AUTH
api.add_resource(UserLogin, '/login', endpoint='login')
api.add_resource(UserLoginByGoogleWP, '/login_by_google', endpoint='login_by_google')
api.add_resource(UpdateDevice, '/devupdate', endpoint='devupdate')
api.add_resource(CheckSession, '/sess_check', endpoint='sess_check')
api.add_resource(UserLogout, '/logout', endpoint='logout')
api.add_resource(ChangePassword, '/change-pwd', endpoint='change-pwd')
api.add_resource(ForgotCheckEmail, '/forgot-pwd', endpoint='forgot-pwd')
api.add_resource(ForgotCheckOtp, '/forgot-auth-otp', endpoint='forgot-auth-otp')
api.add_resource(ResetPwd, '/reset-pwd', endpoint='reset-pwd')
api.add_resource(ForgotCheckOtpResetPwd, '/forgot-auth-otp-reset-pwd', endpoint='forgot-auth-otp-reset-pwd')


api.add_resource(UserLoginWPO, '/loginwpo', endpoint='loginwpo')
api.add_resource(UserLoginWPO, '/loginmpos', endpoint='loginmpos')
api.add_resource(RegisterWPO, '/register_wpo', endpoint='register_wpo')
api.add_resource(AuthOtpWPO, '/register_otp_wpo', endpoint='register_otp_wpo')


# INVOICE
api.add_resource(invoice_all.ExportRpt, '/invoice/<rpt_name>/<output_type>', endpoint='invoice_skp')
api.add_resource(invoice_all.KartuNpwpd, '/invoice_kartu_npwpd/<int:wpid>', endpoint='invoice_kartu_npwpd')
api.add_resource(skp.Report, '/invoice_skp', endpoint='invoice_ssskp')
api.add_resource(vw_obyekbadan.ListByKecUsaha, '/get_wp_by_kec_usaha', endpoint='get_wp_by_kec_usaha')

# NOTIFICATION
api.add_resource(NotifToAdmin, '/notif_online_to_admin', endpoint='notif_online_to_admin')
api.add_resource(NotifToAdmins, '/notif_online_to_admins', endpoint='notif_online_to_admins')
api.add_resource(NotifList, '/inbox', endpoint='inbox')

# UPLOAD MEDIA
api.add_resource(TaskUploadWpAvatar, '/task_upload_wp_avatar', endpoint='task_upload_wp_avatar')
api.add_resource(TaskDeleteWpAvatar, '/task_delete_wp_avatar', endpoint='task_delete_wp_avatar')
api.add_resource(TaskUploadAvatar, '/task_upload_avatar', endpoint='task_upload_avatar')
api.add_resource(TaskDeleteAvatar, '/task_delete_avatar', endpoint='task_delete_avatar')
api.add_resource(TaskUploadArticleImg, '/task_upload_article_img', endpoint='task_upload_article_img')
api.add_resource(TaskDeleteArticleImg, '/task_delete_article_img', endpoint='task_delete_article_img')

api.add_resource(TaskUploadWapuAvatar, '/task_upload_wapu_avatar', endpoint='task_upload_wapu_avatar')
api.add_resource(TaskDeleteWapuAvatar, '/task_delete_wapu_avatar', endpoint='task_delete_wapu_avatar')

api.add_resource(TaskUploadOPDAvatar, '/task_upload_opd_avatar', endpoint='task_upload_opd_avatar')
api.add_resource(TaskDeleteOPDAvatar, '/task_delete_opd_avatar', endpoint='task_delete_opd_avatar')

api.add_resource(TaskUploadDocLapor, '/task_upload_doc_lapor', endpoint='task_upload_doc_lapor')
api.add_resource(TaskDeleteDocLapor, '/task_delete_doc_lapor', endpoint='task_delete_doc_lapor')

# OTHERS
api.add_resource(search, '/search', endpoint='search')
api.add_resource(MsWPData.ProfileWp, '/profile_wp/<npwpd>', endpoint='profile_wp_by_id')
api.add_resource(GetDomainProp, '/unit_claim', endpoint='unit_claim')


api.add_resource(users.ListAll, '/users', endpoint='users')
api.add_resource(users.MyProfile, '/my_profile', endpoint='my_profile')
api.add_resource(users.ListById, '/users/<id>', endpoint='users_by_id')
api.add_resource(groups.ListAll, '/groups', endpoint='groups')
api.add_resource(groups.ListAll2, '/groups2', endpoint='groups2')
api.add_resource(groups.ListById, '/groups/<id>', endpoint='groups_by_id')

# CHAT
api.add_resource(UserOnlineStatus, '/users_online', endpoint='users_online')
api.add_resource(UserRefreshStatus, '/users_online_refresh', endpoint='users_online_refresh')
api.add_resource(UserChatById, '/users_chat/<email>', endpoint='users_chat_by_id')
api.add_resource(SetReadChat, '/users_chat_read/<int:id>', endpoint='users_chat_read')

# ARTICLE
api.add_resource(ArticlesCategoriesList, '/article-categories', endpoint='article-categories')
api.add_resource(ArticlesList, '/article', endpoint='article')
api.add_resource(ArticlesById, '/article/<int:id>', endpoint='article_by_id')