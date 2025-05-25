from pathlib import Path

from flask import make_response
from flask_restful import Resource

from config.helper import logger
from controller.GeneralParameter import GeneralParameter
from controller.MsWPData import MsWPData
from controller.tblUser import tblUser


def copyf(dictlist, key, valuelist):
    return [dictio for dictio in dictlist if dictio[key] in valuelist][0]['ParamStrValue']


def getGeneral():
    try:
        dataGeneral = GeneralParameter.query.all()
        data_result = []
        for row in dataGeneral:
            data_result.append(row.to_dict())
        UNIT_NAME = f"{copyf(data_result, 'ParamID', ('jenis_pemda',))} {copyf(data_result, 'ParamID', ('ibukota',))}"
        ["", "", "", "", "", "telp"]
        Result = {
            'UNIT_LOGO': "https://epad2021.web.app/assets/layout/images/logo-owner.png",
            'UNIT_NAME': UNIT_NAME,
            'UNIT_NAME_UPPER': UNIT_NAME.upper(),
            'UNIT_CITY_NAME': f"{copyf(data_result, 'ParamID', ('ibukota',))}",
            'DINAS_NAME': f"{copyf(data_result, 'ParamID', ('nama_badan',))}",
            'DINAS_NAME_UPPER': f"{copyf(data_result, 'ParamID', ('nama_badan',)).upper()}",
            'DINAS_ADDRESS': f"{copyf(data_result, 'ParamID', ('alamat_pemda',))}",
            'DINAS_NAME_SHORT_UPPER': f"{copyf(data_result, 'ParamID', ('badan_singkat',)).upper()}",
            'DINAS_NAME_SHORT': f"{copyf(data_result, 'ParamID', ('badan_singkat',))}",

            'badan': f"{copyf(data_result, 'ParamID', ('nama_badan',))}",
            'pemda': UNIT_NAME,
            'alamat': f"{copyf(data_result, 'ParamID', ('alamat_pemda',))}",
            'telp': f"{copyf(data_result, 'ParamID', ('telp_pemda',))}",
            'kota': f"{copyf(data_result, 'ParamID', ('ibukota',))}",
            'badan1': f"{copyf(data_result, 'ParamID', ('nama_badan',))}",
            'pemda1': UNIT_NAME,
            'alamat1': f"{copyf(data_result, 'ParamID', ('alamat_pemda',))}",
            'telp1': f"{copyf(data_result, 'ParamID', ('telp_pemda',))}",
            'telepon': f"{copyf(data_result, 'ParamID', ('telp_pemda',))}",
            'telepon1': f"{copyf(data_result, 'ParamID', ('telp_pemda',))}",
            'kota1': f"{copyf(data_result, 'ParamID', ('ibukota',))}",
            'daerah': f"{copyf(data_result, 'ParamID', ('ibukota',))}",
            'daerah1': f"{copyf(data_result, 'ParamID', ('ibukota',))}",

        }
        return Result
    except Exception as e:
        print(e)
        return None