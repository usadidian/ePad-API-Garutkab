from flask import jsonify, make_response
from flask_restful import abort


# AUTH
# APIKEY GAK ADA
def apikey_required():
    return abort(make_response(jsonify({
        'status_code': 666,
        'message': "Server tidak dapat memverifikasi bahwa Anda berwenang untuk mengakses URL yang diminta. Anda memberikan kredensial yang salah (mis. Kata sandi yang buruk), atau browser Anda tidak mengerti bagaimana memasok kredensial yang diperlukan.",
        'data': {}
    }), 401))


# APIKEY NOT MATCH WITH VALUE IN TABLE USERS
def apikey_not_match():
    return abort(make_response(jsonify({
        'status_code': 667,
        'message': "Server tidak dapat memverifikasi bahwa Anda berwenang untuk mengakses URL yang diminta. Anda memberikan kredensial yang salah (mis. Kata sandi yang buruk), atau browser Anda tidak mengerti bagaimana memasok kredensial yang diperlukan.",
        'data': {}
    }), 401))


# APIKEY KADALUARSA
def apikey_expired():
    return abort(make_response(jsonify({
        'status_code': 668,
        'message': 'Signature EXPIRED!',
        'data': {}
    }), 401))


# APIKEY GAGAL
def failed_authentication():
    return abort(make_response(jsonify({
        'status_code': 669,
        'message': 'Otentikasi Gagal atau signature salah!',
        'data': {}
    }), 401))


# TIDAK DIIZINKAN KE ENDPOINT
def endpoint_restricted():
    return abort(make_response(jsonify({
        'status_code': 670,
        'message': 'Tidak diizinkan!',
        'data': {}
    }), 401))

# LOGIN SUKSES
def login_success(data):
    return jsonify({'status_code': 700, 'message': 'Login OK, otp send to device', 'data': data})

# LOGIN FAILED
def login_failed():
    return jsonify({'status_code': 701, 'message': 'Login Failed, otp not send to device'})


# CRUD
# READS
def success_reads(data):
    return jsonify({'status_code': 1, 'message': 'OK', 'data': data})


def success_reads_pagination(result, data):
    return jsonify({
        'status_code': 1,
        'message': 'OK',
        'page_total': result.pages,
        'page_current': result.page,
        'records_perpage': result.per_page,
        'records_total': result.total,
        'data': data
    })


def failed_reads(data):
    return abort(make_response(jsonify({
        'status_code': 52,
        'message':
            'Records Tidak Ditemukan atau Parameter Request Kamu Tidak Lengkap',
        'data': data
    }), 500))


# READ
def success_read(data):
    return jsonify({'status_code': 1, 'message': 'OK', 'data': data})


def failed_read(data):
    return abort(make_response(jsonify({
        'status_code': 52,
        'message':
            'Record Tidak Ditemukan atau Parameter Request Kamu Tidak Lengkap',
        'data': data
    }), 500))


# CREATE
def success_create(data):
    return jsonify({'status_code': 1, 'message': 'OK', 'data': data})


def failed_create(data, message=None):
    msg = message if message else 'Record Gagal di Tambahkan atau Parameter Request Kamu Tidak Lengkap'
    return abort(make_response(jsonify({
        'status_code': 51,
        'message': msg,
        'data': data
    }), 500))


def sql_failed_create(ex):
    # print(ex)
    code = ex.orig.args[0]
    msg = ex.orig.args[1]
    if code == '23000':
        # message = 'Data yang di posting duplikat dengan data yang sudah ada di database!'
        message = msg
    return abort(make_response(jsonify({
        'status_code': code,
        'message': msg,
        'data': {}
    }), 500))


# UPDATE
def success_update(data):
    return jsonify({'status_code': 1, 'message': 'OK', 'data': data})


def failed_update(data):
    return abort(make_response(jsonify({
        'status_code': 53,
        'message':
            'Record Gagal di Update atau Parameter Request Kamu Tidak Lengkap',
        'data': data
    }), 500))


# DELETE
def success_delete(data):
    return jsonify({'status_code': 1, 'message': 'OK', 'data': data})


def failed_delete(data):
    return abort(make_response(jsonify({
        'status_code': 54,
        'message':
            'Record Gagal di Hapus atau Parameter Request Kamu Tidak Lengkap',
        'data': data
    }), 500))


# DELETES
def success_deletes(data):
    return jsonify({'status_code': 1, 'message': 'OK', 'data': data})


def success_failed_deletes(data_successed, data_failed, count_successed,
                           count_failed):
    return abort(make_response(
        jsonify({
            'status_code': 1,
            'message':
                '{0} Records Berhasil Dihapus & {1} Records Gagal Dihapus'.format(
                    count_successed, count_failed),
            'data': {'success': data_successed, 'failed': data_failed}
        }), 500))


def failed_deletes(data_failed, count_failed):
    return abort(make_response(
        jsonify({
            'status_code': 60,
            'message': '{0} Records Gagal Dihapus'.format(count_failed),
            'data': data_failed
        }), 500))


def failed_all_deletes(data):
    return abort(make_response(
        jsonify({
            'status_code': 57,
            'message':
                'Records Gagal di Hapus atau Parameter Request Kamu Tidak Lengkap',
            'data': data
        }), 500))


# UPLOADS
def success_upload(data):
    return jsonify({'status_code': 1, 'message': 'OK', 'data': data})


def failed_upload(message=None):
    return abort(make_response(
        jsonify({
            'status_code': 71,
            'message': 'Gagal Upload, {}'.format(message),
            'data': {}
        }), 500))
