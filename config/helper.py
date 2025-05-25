import locale
import logging
import math
import os
import random
import re
import sys
from datetime import datetime

import cloudinary
import pytz
from cryptography.fernet import Fernet
from flask import request, jsonify
from flask_restful import reqparse
from sqlalchemy.orm.base import class_mapper

# from controller.notifications.fcm_session import push_service
from controller.notifications.fcm_session import push_service


def receive_date():
    data = request.json  # Ambil data JSON dari frontend
    tgl_str = data.get('tgl')  # Ambil string tanggal dari payload

    if not tgl_str:
        return jsonify({"error": "Tanggal tidak boleh kosong"}), 400

    # Pastikan backend membaca timestamp dalam zona waktu Asia/Jakarta
    jakarta_tz = pytz.timezone("Asia/Jakarta")

    # Parsing string ke datetime tanpa timezone (karena frontend tidak mengirim zona waktu)
    tgl_obj = datetime.strptime(tgl_str, '%Y-%m-%d %H:%M:%S')

    # Beri tahu backend bahwa timestamp ini sudah dalam zona WIB
    tgl_obj = jakarta_tz.localize(tgl_obj)

    # Konversi ke UTC jika diperlukan
    tgl_utc = tgl_obj.astimezone(pytz.UTC)

    print("Tanggal yang diterima di WIB:", tgl_obj)
    print("Tanggal dalam UTC:", tgl_utc)

    return jsonify({
        "received_date_WIB": tgl_obj.strftime('%Y-%m-%d %H:%M:%S %Z'),
        "received_date_UTC": tgl_utc.strftime('%Y-%m-%d %H:%M:%S %Z')
    })
def setup_custom_logger():

    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('app_log_all.log', mode='a')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger


logger = setup_custom_logger()

# def toDict(self):
#     return {
#         c.key: getattr(self, c.key)
#         for c in inspect(self).mapper.column_attrs
#     }
from werkzeug.utils import secure_filename

from config.api_message import failed_upload

mapping_num_rep = [('0', 'edcrfv'), ('1', 'qazwsx'), ('2', 'bgtnhy'), ('3', 'ujmik'), ('4', '.lo/;p'), ('5', 'ol.p;/'),
                   ('6', 'zaqxs'), ('7', 'tgbyhn'), ('8', 'cdevfr'), ('9', 'mju,ki')]


def encrypt_otp(otp_str):
    otp = str(otp_str)
    for k, v in mapping_num_rep:
        otp = otp.replace(k, v)
    return otp


def decrypt_otp(encrypted_str):
    otp = str(encrypted_str)
    for k, v in mapping_num_rep:
        otp = otp.replace(v, k)
    return otp


str_source = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u",
              "v", "w", "x", "y"]
str_replacement = ["!", "~", "#", "@", "%", "$", "&", "^", "(", "*", ",", ")", "+", "`", "|", "=", "{", "}", "]", "[",
                   ":", ";", ">", "?", "<"]


def encrypt_token(token_str):
    token = token_str
    for x, y in zip(str_source, str_replacement):
        token = token.replace(x, y)
    return token


def decrypt_token(token_encrypted):
    token = token_encrypted
    for x, y in zip(str_source, str_replacement):
        token = token.replace(y, x)
    return token


def notif_fcm(par):
    try:
        print('SEND NOTIFICATIONS TO {}...'.format(par['destination']))
        push_service.notify_single_device(registration_id=par['destination'],
                                          message_title=par['title'],
                                          message_body=par['body'])
        print('SEND NOTIFICATIONS TO {}... OK'.format(par['destination']))
    except Exception as e:
        print('SEND NOTIFICATIONS TO {}... FAILED'.format(par['destination']))
        print(e)


def notif_sms(par):
    try:
        # client = Client(account_sid, auth_token_twilio)
        # print('SEND SMS TO {}...'.format(par['destination']))
        # message = client.messages.create(
        #     body=par['body'],
        #     from_=phoneOfficial,
        #     to=par['destination']
        # )
        # print(message.sid)
        # print('SEND SMS TO {}... OK'.format(par['destination']))
        return True
    except Exception as e:
        print('SEND SMS TO {}... FAILED'.format(par['destination']))
        print(e)
        return False


def toDict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = getattr(row, column.name)

    return d


def sterilize(obj):
    object_type = type(obj)
    if isinstance(obj, dict):
        return {k: sterilize(v) for k, v in obj.items()}
    elif object_type in (list, tuple):
        return [sterilize(v) for v in obj]
    elif object_type in (str, int, bool):
        return obj
    else:
        return obj.__repr__()


# UNTUK OBJECT YG ADA RELATIONSHIP
def object_to_dict(obj, found=None):
    if found is None:
        found = set()
    mapper = class_mapper(obj.__class__)
    columns = [column.key for column in mapper.columns]
    get_key_value = lambda c: (c, getattr(obj, c).isoformat()) if isinstance(getattr(obj, c), datetime) else (
        c, getattr(obj, c))
    out = dict(map(get_key_value, columns))
    for name, relation in mapper.relationships.items():
        if relation not in found:
            found.add(relation)
            related_obj = getattr(obj, name)
            if related_obj is not None:
                if relation.uselist:
                    # print([object_to_dict(child, found) for child in related_obj])
                    out[name] = [object_to_dict(child, found) for child in related_obj]
                else:
                    out[name] = object_to_dict(related_obj, found)
    return out


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


# UNTUK PARSE DARI REQUEST PARAMETER
parser = reqparse.RequestParser()

# FILE UPLOAD HANDLER
PROJECT_HOME = os.path.dirname(os.path.realpath('../app.py'))
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def delete_in_cloudinary(filename):
    cloudinary.uploader.destroy(filename)


def upload_to_cloudinary(unit_info, file, cloud_folder_name, prefixfilename=None, suffixfilename=None):
    if 'file' not in file:
        return failed_upload('file tidak ditemukan!')

    file = file['file']
    if file.filename == '':
        return failed_upload('filename tidak ditemukan!')

    if not allowed_file(file.filename):
        return failed_upload('tipe tidak diizinkan!')

    # GENERATE FILENAME & FOLDER
    folder_unit = "{}_".format(unit_info.code) if unit_info.code else ""
    filename_prefix = "{}_".format(prefixfilename) if prefixfilename else ""
    filename_cut_ext = secure_filename(file.filename.rsplit('.', 1)[0])
    filename_fix = cloud_folder_name + '_' + folder_unit + filename_prefix + filename_cut_ext
    public_id = (cloud_folder_name + '/' + folder_unit).replace('_', '/') + filename_fix

    upload_result = cloudinary.uploader.upload(file, public_id=public_id)
    if upload_result['public_id']:
        print('UPLOAD BUKTI TRANSAKSI KE CLOUDINARY SUCCESS!')
        return upload_result
    else:
        print('UPLOAD BUKTI TRANSAKSI KE CLOUDINARY GAGAL!')
        return upload_result


def gen_publicid_cloudinary(unit_info, files, cloud_folder_name, prefixfilename=None, suffixfilename=None):
    if 'file' not in files:
        return failed_upload('file tidak ditemukan!')

    file = files['file']
    if file.filename == '':
        return failed_upload('filename tidak ditemukan!')

    if not allowed_file(file.filename):
        return failed_upload('tipe tidak diizinkan!')

    # GENERATE FILENAME & FOLDER
    folder_unit = "{}_".format(unit_info.code) if unit_info.code else ""
    filename_prefix = "{}_".format(prefixfilename) if prefixfilename else ""
    filename_cut_ext = secure_filename(file.filename.rsplit('.', 1)[0])
    filename_fix = cloud_folder_name + '_' + folder_unit + filename_prefix + filename_cut_ext
    public_id = (cloud_folder_name + '/' + folder_unit).replace('_', '/') + filename_fix
    return public_id


# function to generate OTP
def generateOTP(digit=6):
    # Declare a digits variable
    # which stores all digits
    digits = "0123456789"
    OTP = ""

    # length of password can be chaged
    # by changing value in range
    for i in range(digit):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP


regex_email = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'


def checkValidEmail(email):
    # pass the regular expression
    # and the string in search() method
    if (re.search(regex_email, email)):
        print("Valid Email")
        return True
    else:
        print("Invalid Email")
        return False


def rupiah_format(angka, with_prefix=False, desimal=2):
    locale.setlocale(locale.LC_NUMERIC, 'IND')
    rupiah = locale.format("%.*f", (desimal, angka), True)
    if with_prefix:
        return "Rp. {}".format(rupiah)
    return rupiah


key = Fernet.generate_key()
cipher_suite = Fernet(key)


# cipher_text = cipher_suite.encrypt(b"A really secret message. Not for prying eyes.")
# plain_text = cipher_suite.decrypt(cipher_text)

def encryptMessage(key, message):
    ciphertext = [''] * key

    for col in range(key):
        position = col
        while position < len(message):
            ciphertext[col] += message[position]
            position += key
    return ''.join(ciphertext)  # Cipher text


def decryptMessage(key, message):
    numOfColumns = math.ceil(len(message) / key)
    numOfRows = key
    numOfShadedBoxes = (numOfColumns * numOfRows) - len(message)
    plaintext = float('') * numOfColumns
    col = 0
    row = 0

    for symbol in message:
        plaintext[col] += symbol
        col += 1
        if (col == numOfColumns) or (col == numOfColumns - 1 and row >= numOfRows - numOfShadedBoxes):
            col = 0
            row += 1
            return ''.join(plaintext)


def non_empty_string(s):
    if not s:
        raise ValueError("Must not be empty string")
    return s


regexEmail = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

regexUserid = r''

regexPhone = r'(\+62 ((\d{3}([ -]\d{3,})([- ]\d{4,})?)|(\d+)))|(\(\d+\) \d+)|\d{3}( \d+)+|(\d+[ -]\d+)|\d+'

# regexPhone = r'^08[0-9]{9,}$'


def checkIsEmail(email):
    if (re and re.match(regexEmail, email)):
        # print("Valid Email")
        return True
    else:
        # print("Invalid Email")
        return False

def checkIsUserId(userid):
    if (re and re.match(regexUserid, userid)):
        return True
    else:
        return False

def checkIsPhone(phone):
    if (re and re.match(regexPhone, phone)):
        return True
    else:
        return False