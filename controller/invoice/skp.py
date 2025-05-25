import decimal
from pathlib import Path

from flask import make_response, request
from flask_restful import Resource
from sqlalchemy import null

from config.database import db
from config.helper import rupiah_format
from controller.invoice.global_report import getGeneral


class Report(Resource):
    # method_decorators = [tblUser.auth_apikey_privilege]
    def get(self):
        general = getGeneral()
        KohirID = request.args.get('KohirID')
        idkep = request.args.get('idkep')
        dataReport = db.session.execute(f"""SET NOCOUNT ON; exec SP_SKPD_REKAP 
                                        '{idkep}',
                                        '{general['DINAS_NAME']}',
                                        '{general['UNIT_NAME']}',
                                        '{general['DINAS_ADDRESS']}',
                                        '(0265) 771032, 773570',
                                        '{general['UNIT_CITY_NAME']}',
                                        '{general['UNIT_NAME']}',
                                        '{KohirID}',
                                        '1',
                                        'N',
                                        '',
                                        'SKPXX0K',
                                        '',
                                        0,
                                        '2020-06-02 00:00:00',
                                        '', 
                                        0, 
                                        0""")

        # GENERATE HTML
        path_parent = Path(__file__).parent
        path = f"{path_parent}\/template_html/"
        with open('{}skp.html'.format(path), 'r') as u:
            html_str = u.read()

        for row in general:
            # print(row)
            html_str = html_str.replace(f"[{row}]", general[row])

        dataReportResult = []
        detail = ""
        for row in dataReport:
            d = {}
            for key in row.keys():
                value = str(getattr(row, key))
                d[key] = value
                if value[-3:] == '.00' and value[0] != 'P':
                    html_str = html_str.replace(f"[{str(key)}]", rupiah_format(int(float(value)), 2))
                elif key == 'DET_JNSPAJAK':
                    if value and len(value) > 0:
                        if value[0] != '#':
                            detail += value+"<br/>"
                        else:
                            # print(value[4:])
                            detail += value[4:] + "<br/>"
                        # print(detail)
                else:
                    html_str = html_str.replace(f"[{str(key)}]", value)
            dataReportResult.append(d)
        html_str = html_str.replace(f"[DETAIL_ROWS]", detail.replace('None<br/>', ''))
        # print(dataReportResult)


        # headers = {'Content-Type': 'text/html'}
        return make_response(html_str)