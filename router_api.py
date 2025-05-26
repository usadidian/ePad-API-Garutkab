from flask_restful import Api

from controller import users, groups
from controller.RevenueCategories import RevenueCategories
from controller.RevenueLogType import RevenueLogType
from controller.RevenueSummary import RevenueSummary
from controller.TaxEntities import TaxEntities
from controller.Transactions import Transactions
from controller.login import UserLogin, UpdateDevice, CheckSession, UserLogout, UserLoginByGoogleWP, ChangePassword, \
    ForgotCheckEmail, ForgotCheckOtp, ResetPwd, ForgotCheckOtpResetPwd
from controller.tblAkses import tblAkses
from controller.tblMenu import tblMenu
from controller.tblMenuDet import tblMenuDet
from controller.tblRole import tblRole
from controller.tblUrl import tblUrl
from controller.unit_prop import GetDomainProp

api = Api()


###### URL API INTEGRASI DASHBOARD ########
api.add_resource(RevenueSummary, '/revenue-summary', endpoint='revenue-summary')
api.add_resource(RevenueCategories, '/revenue-categories', endpoint='revenue-categories')
api.add_resource(TaxEntities, '/tax-entities', endpoint='tax-entities')
api.add_resource(RevenueLogType, '/revenue-log/<logType>', endpoint='revenue-log')
api.add_resource(Transactions, '/transactions', endpoint='transactions')


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


# OTHERS
api.add_resource(GetDomainProp, '/unit_claim', endpoint='unit_claim')


api.add_resource(users.ListAll, '/users', endpoint='users')
api.add_resource(users.MyProfile, '/my_profile', endpoint='my_profile')
api.add_resource(users.ListById, '/users/<id>', endpoint='users_by_id')
api.add_resource(groups.ListAll, '/groups', endpoint='groups')
api.add_resource(groups.ListAll2, '/groups2', endpoint='groups2')
api.add_resource(groups.ListById, '/groups/<id>', endpoint='groups_by_id')
