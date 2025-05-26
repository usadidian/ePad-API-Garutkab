import json
import os
from datetime import datetime, timedelta

from flask import request

appName = os.environ.get('EPAD_APPNAME')
appNameMobile = os.environ.get('EPAD_MOBILE_APPNAME')
# appFrontWebUrl() = os.environ.get('EPAD_PUBLIC_URL')
#
# # Cari lokasi folder tempat config.py berada
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#
# # Naik satu folder dari config/ ke project/
# ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
#
# # Gabungkan path ke unitmapper.json
# UNITMAPPER_PATH = os.path.join(ROOT_DIR, "unit_mapper.json")
#
# # Load isi file unitmapper.json
# with open(UNITMAPPER_PATH) as f:
#     UNIT_MAPPERS = {item["id"]: item["attributes"] for item in json.load(f)}
#
# DEFAULT_PUBLIC_URL = os.environ.get("EPAD_PUBLIC_URL", "https://epad2021.web.app/")
#
# def appFrontWebUrl():
#     host = request.host.lower()
#     return UNIT_MAPPERS.get(host, {}).get("EPAD_PUBLIC_URL", DEFAULT_PUBLIC_URL)

appFrontWebUrlWp = os.environ.get('EPAD_PUBLIC_URL_WP')
appFrontWebUrlExecutive = os.environ.get('EPAD_PUBLIC_URL_EXECUTIVE')
appFrontWebLogo = os.environ.get('EPAD_PUBLIC_LOGO')
appFrontWebLogoBig = os.environ.get('EPAD_PUBLIC_LOGO_BIG')
appFrontWebMobileLogo = os.environ.get('EPAD_MOBILE_PUBLIC_LOGO')
appFrontWebMobileLogoBig = os.environ.get('EPAD_MOBILE_PUBLIC_LOGO_BIG')
appEmail = os.environ.get('EPAD_EMAIL')
appEmailPassword = os.environ.get('EPAD_EMAIL_PWD')
baseUrl = os.environ.get('EPAD_BASE_URL')
baseUrlPort = os.environ.get('EPAD_BASE_URL_PORT')
baseUrlScheme = os.environ.get('EPAD_BASE_URL_SCHEME')

oauth2_clientid = os.environ.get('EPAD_OAUTH2_CLIENTID')
# FCM
api_key_fcm = os.environ.get('EPAD_APIKEY_FCM')

# cloudinary
cloudinary_cloud_name = os.environ.get('EPAD_CLOUDINARY_NAME')
cloudinary_api_key = os.environ.get('EPAD_CLOUDINARY_APIKEY')
cloudinary_api_secret = os.environ.get('EPAD_CLOUDINARY_APISECRET')

# sightengine
sightengine_api_secret = os.environ.get('EPAD_SE_APISECRET')
sightengine_api_user = os.environ.get('EPAD_SE_APIUSER')

# JWT
jwt_secretkey = os.environ.get('EPAD_JWT_SECRET')
jwt_token_exp_min = timedelta(minutes=60)  # dalam menit
jwt_otp_exp_min = timedelta(minutes=15)  # dalam menit