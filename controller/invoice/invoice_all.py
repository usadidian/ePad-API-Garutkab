import ast
import os
from datetime import datetime
from multiprocessing import Process
from pathlib import Path

import pytz
from flask import make_response, request, url_for, send_from_directory, jsonify
from flask_restful import Resource, abort
from werkzeug.utils import redirect

from config.helper import logger
from controller.GeneralParameter import GeneralParameter
from controller.MsWPData import MsWPData
from controller.invoice.global_report import getGeneral
from controller.invoice.invoice_controller import get_valuetype
from controller.tblUser import tblUser
from controller.invoice import invoice_controller as invoice


class ExportRpt(Resource):
    # method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, rpt_name, output_type):
        origin = request.headers.get('Origin')
        connection_map = ast.literal_eval(os.environ.get('EPAD_DB_CONNECTIONS'))
        connections = connection_map['default']
        if origin:
            origin = origin.replace('http://', '').replace('https://', '')
            if origin in connection_map.keys():
                connections = connection_map[origin]

        try:
            if request.args.get('rpt_path') and request.args.get('rpt_path') == "register":
                r = invoice.connect('controller/invoice/invoice_rpt/register/' + rpt_name + '.rpt', connections)
            else:
                r = invoice.connect('controller/invoice/invoice_rpt/' + rpt_name + '.rpt', connections)
            params = invoice.get_params(r)
            values = invoice.get_literals(request.args.get('values'))
            # print(values)
            generalFields = ["badan", "badan1", "pemda", "pemda1",
                             "alamat", "alamat1", "telp", "telepon",
                             "telepon1", "kota", "kota1", "daerah1", ]
            generalFieldsValue = getGeneral()
            for each in params:
                reportParamName = each.Name.replace('{?@', '').replace('}', '')
                parType = get_valuetype(each)
                # print(reportParamName, parType)
                # print(values.get(reportParamName))
                jakarta_tz = pytz.timezone("Asia/Jakarta")
                if values.get(reportParamName):
                    each.ClearCurrentValueAndRange()
                    # if parType == 'datetime':
                    #     date_str = values.get(reportParamName, "")
                    #     if date_str:
                    #         # Konversi string ke datetime tanpa zona waktu
                    #         dt_obj = datetime.fromisoformat(date_str)
                    #
                    #         # Pastikan waktu dalam zona Asia/Jakarta
                    #         dt_obj = jakarta_tz.localize(dt_obj)  # Tambahkan zona WIB
                    #
                    #         each.AddCurrentValue(dt_obj)  # Pastikan objek sudah diubah ke WIB sebelum disimpan
                    if parType == 'datetime':
                        each.AddCurrentValue(datetime.fromisoformat(values.get(reportParamName, "")))
                    else:
                        each.AddCurrentValue(values.get(reportParamName, ""))
                else:
                    if reportParamName in generalFields:
                        # print(generalFieldsValue)
                        each.ClearCurrentValueAndRange()
                        each.AddCurrentValue(generalFieldsValue[reportParamName])
                    else:
                        if parType == 'string':
                            each.AddCurrentValue("")
                        elif parType == 'number':
                            each.AddCurrentValue(0)
                        elif parType == 'datetime':
                            each.AddCurrentValue(datetime.now())

            filename = invoice.set_exportoption(r, output_type, rpt_name)
            # r.Database.Verify()
            # print(filename)
            r.Export(promptUser=False)
        except Exception as e:
            print(e)
            # return str(e)
            return abort(make_response(jsonify({
                'status_code': 76,
                'message': str(e),
                'data': {}
            }), 500))
        else:
            thread = Process(target=remove_after_response, args=('static/invoice_output/', filename,))
            thread.start()
            return send_from_directory('static/invoice_output', filename, as_attachment=False)


def remove_after_response(pathx, filename):
    files = sorted(Path(pathx).iterdir(), key=os.path.getmtime)
    files.sort(key=os.path.getctime)
    for filenamex in files[:-7]:
        os.remove(filenamex)


def copyf(dictlist, key, valuelist):
    return [dictio for dictio in dictlist if dictio[key] in valuelist][0]['ParamStrValue']


class KartuNpwpd(Resource):
    # method_decorators = [tblUser.auth_apikey_privilege]
    def get(self, wpid):
        # GENERATE HTML
        path_parent = Path(__file__).parent
        path = f"{path_parent}\/template_html/"
        with open('{}kartu_npwpd.html'.format(path), 'r') as u:
            html_str = u.read()
        dataGeneral = GeneralParameter.query.all()
        data_result = []
        for row in dataGeneral:
            data_result.append(row.to_dict())
        UNIT_LOGO = "https://epad2021.web.app/assets/layout/images/logo-owner.png"
        html_str = html_str.replace("{UNIT_LOGO}", UNIT_LOGO)

        UNIT_NAME = f"{copyf(data_result, 'ParamID', ('jenis_pemda',))} {copyf(data_result, 'ParamID', ('ibukota',))}"
        DINAS_NAME = f"{copyf(data_result, 'ParamID', ('nama_badan',))}"
        DINAS_ADDRESS = f"{copyf(data_result, 'ParamID', ('alamat_pemda',))}"
        DINAS_NAME_SHORT = f"{copyf(data_result, 'ParamID', ('badan_singkat',))} {UNIT_NAME}"

        html_str = html_str.replace("{UNIT_NAME}", UNIT_NAME.upper())
        html_str = html_str.replace("{DINAS_NAME}", DINAS_NAME.upper())
        html_str = html_str.replace("{DINAS_ADDRESS}", DINAS_ADDRESS)
        html_str = html_str.replace("{DINAS_NAME_SHORT}", DINAS_NAME_SHORT.upper())

        dataDetail = MsWPData.query.filter_by(WPID=wpid).first()
        html_str = html_str.replace("{NPWPD}", dataDetail.ObyekBadanNo)
        html_str = html_str.replace("{NPWPD_NAME}", dataDetail.NamaBadan.upper())
        html_str = html_str.replace("{NPWPD_ADDRESS}", dataDetail.AlamatBadan)

        # headers = {'Content-Type': 'text/html'}
        return make_response(html_str)