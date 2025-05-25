import sys, ast, uuid
import time
from sqlalchemy.engine.url import make_url
import pythoncom
import win32com
from win32com.client import Dispatch


def connect(rpt, condb=None):
    url = make_url(condb)
    mssql_pwd = url.password
    mssql_server = url.host
    mssql_dbname = url.database
    mssql_user = url.username
    pythoncom.CoInitialize()
    rep = openreport(rpt)
    rep.EnableParameterPrompting = False
    # rep.VerifyOnEveryPrint = True
    # shell = gencache.EnsureDispatch('CrystalRuntime.Application')
    # tes = shell.OpenReport(rpt).Database.Tables(1).ConnectionProperties
    # print(tes)
    # rep.Database.Tables(1).DLLName = 'crdb_ado.dll'
    # rep.Database.Tables(1).ConnectionProperties.DeleteAll()
    # rep.Database.Tables.Item(1).ConnectionProperties.Delete('Data Source')
    # rep.Database.Tables.Item(1).ConnectionProperties.Delete('Initial Catalog')
    # rep.Database.Tables.Item(1).ConnectionProperties.Delete('Database')
    # rep.Database.Tables.Item(1).ConnectionProperties.Delete('User ID')
    # rep.Database.Tables.Item(1).ConnectionProperties.Delete('Password')

    # rep.Database.Tables.Item(1).ConnectionProperties.Add('DSN', 'ODBC DSN')

    # ConnectionInfo = rep.Database.Tables(1).ConnectionProperties
    #
    # ConnectionInfo.Add('Provider', 'SQLOLEDB')
    # ConnectionInfo.Add('Data Source', mssql_server)
    # ConnectionInfo.Add('Initial Catalog', mssql_dbname)
    # ConnectionInfo.Add('User ID', mssql_user)
    # ConnectionInfo.Add('Password', mssql_pwd)
    # ConnectionInfo.Add('Integrated Security', '0')
    # rep.Database.Tables.Item(1).Location = f'{mssql_dbname}.dbo.SP_SKPD_REKAP'

    tbl = rep.Database.Tables(1)
    ConnectionInfo = tbl.ConnectionProperties
    prop = ConnectionInfo.Item('Data Source')
    prop.Value = mssql_server
    prop = ConnectionInfo.Item('Initial Catalog')
    prop.Value = mssql_dbname
    prop = ConnectionInfo.Item('User ID')
    prop.Value = mssql_user
    prop = ConnectionInfo.Item('Password')
    prop.Value = mssql_pwd
    prop = ConnectionInfo.Item('Integrated Security')
    prop.Value = '0'
    spName = tbl.Name.replace(';1', '')
    rep.Database.Tables(1).Location = f'{mssql_dbname}.dbo.{spName}'
    return rep


def openreport(name):
    app = Dispatch('CrystalRuntime.Application')
    # app = win32com.client.dynamic.Dispatch('CrystalRuntime.Application', clsctx=pythoncom.CLSCTX_ALL)
    # print(name)
    return app.OpenReport(name)


def get_params(self):
    return self.ParameterFields


# do not change the constants; ref:CRFieldValueType
def get_valuetype(self):
    vtype = "none"
    if self.ValueType == 12:
        vtype = "string"
    elif self.ValueType == 9:
        vtype == "bool"
    elif self.ValueType == 8:
        vtype == "curr"
    elif self.ValueType == 10:
        vtype = "date"
    elif self.ValueType == 16:
        vtype = "datetime"
    elif self.ValueType == 7:
        vtype = "number"
    elif self.ValueType == 11:
        vtype = "time"
    return vtype


def get_fieldname(self):
    return self.parameterfieldname


def get_prompt_text(self):
    return self.prompt


def get_literals(self):
    return ast.literal_eval(self)


def gen_filekey():
    x = uuid.uuid4()
    # x = time.time()
    return str(x)


# do not change the constants; ref:CRExportFormatType
# didieu => https://metacpan.org/dist/Win32-OLE-CrystalRuntime-Application/source/lib/Win32/OLE/CrystalRuntime/Application/Constants.pm
def set_exportoption(r, typ, rpt_name):
    exp = r.ExportOptions
    key = rpt_name.replace("_", "-") + '-' + gen_filekey()
    filename = ""
    if typ in "csv":
        exp.DestinationType = 1
        exp.DiskFileName = 'static/invoice_output/' + key + '.csv'
        exp.FormatType = 5
        filename = key + '.csv'
    elif typ in "pdf":
        exp.DestinationType = 1
        exp.FormatType = 31
        exp.DiskFileName = 'static/invoice_output/' + key + '.pdf'
        filename = key + '.pdf'
    elif typ in "xls":
        exp.DestinationType = 1
        exp.FormatType = 36
        exp.DiskFileName = 'static/invoice_output/' + key + '.xls'
        filename = key + '.xls'
    # elif typ in "html":
    #     exp.DestinationType = 1
    #     exp.FormatType = 24
    #     exp.DiskFileName = 'static/invoice_output/' + key + '.html'
    #     filename = key + '.html'
    # elif typ in "xml":
    #     exp.DestinationType = 1
    #     exp.FormatType = 37
    #     exp.DiskFileName = 'static/invoice_output/' + key + '.xls'
    #     filename = key + '.xml'
    return filename