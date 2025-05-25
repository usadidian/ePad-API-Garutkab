import json
import os
from dotenv import load_dotenv

import requests

from config.config import baseUrl, baseUrlPort, baseUrlScheme
from config.helper import logger


def GoToTaskNotificationSendToAll(data):
    logger.info('----------------------------------------------------------------TASK BEGIN')
    logger.info('TASK : GoToTaskNotificationSendToAll START')
    url = f"{baseUrlScheme}://{baseUrl}/notif_online_to_admin"
    if baseUrlPort != None:
        url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/notif_online_to_admin"
    r = requests.post(url, data=json.dumps(data['body']), headers=data['headers'])
    logger.info('TASK : GoToTaskNotificationSendToAll RESULT -> ' + str(r.status_code) + ' ' + r.reason)
    logger.info('TASK : GoToTaskNotificationSendToAll FINISH')
    logger.info('----------------------------------------------------------------TASK END')


def GoToTaskNotificationSendToAdmins(data):
    logger.info('----------------------------------------------------------------TASK BEGIN')
    logger.info('TASK : GoToTaskNotificationSendToAll START')
    url = f"{baseUrlScheme}://{baseUrl}/notif_online_to_admins"
    if baseUrlPort != None:
        url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/notif_online_to_admins"
    for row in data:
        # print(row['headers'])
        # print(json.dumps(row))
        r = requests.post(url, data=json.dumps(row), headers=row['headers'])
        logger.info('TASK : GoToTaskNotificationSendToAll RESULT -> ' + str(r.status_code) + ' ' + r.reason)
    logger.info('TASK : GoToTaskNotificationSendToAll FINISH')
    logger.info('----------------------------------------------------------------TASK END')


def GoToTaskUploadWPAvatar(folderName, filenames, wpid, userid=None, self_upload=False, origin=None):
    logger.info('----------------------------------------------------------------TASK BEGIN')
    logger.info('TASK : GoToTaskUploadWPAvatar START')
    logger.info(baseUrl)
    url = f"{baseUrlScheme}://{baseUrl}/task_upload_wp_avatar"
    if baseUrlPort != None:
        url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/task_upload_wp_avatar"

    r = requests.post(url, headers={"Origin": f'{origin}'}, data=json.dumps(
        {'folder_name': folderName, 'filenames': filenames, 'wpid': wpid, 'userid': userid, 'self_upload': self_upload}))
    logger.info('TASK : GoToTaskUploadWPAvatar RESULT -> ' + str(r.status_code) + ' ' + r.reason)
    logger.info('TASK : GoToTaskUploadWPAvatar FINISH')
    logger.info('----------------------------------------------------------------TASK END')


def GoToTaskDeleteWPAvatar(pathx, origin=None):
    logger.info('----------------------------------------------------------------TASK BEGIN')
    logger.info('TASK : GoToTaskDeleteWPAvatar START')
    url = f"{baseUrlScheme}://{baseUrl}/task_delete_wp_avatar"
    if baseUrlPort != None:
        url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/task_delete_wp_avatar"
    r = requests.post(url, headers={"Origin": f'{origin}'}, data=json.dumps({'path': pathx}))
    logger.info('TASK : GoToTaskDeleteWPAvatar RESULT -> ' + str(r.status_code) + ' ' + r.reason)
    logger.info('TASK : GoToTaskDeleteWPAvatar FINISH')
    logger.info('----------------------------------------------------------------TASK END')


def GoToTaskUploadAvatar(folderName, filenames, userid_avatar, userid=None, origin=None):
    logger.info('----------------------------------------------------------------TASK BEGIN')
    logger.info('TASK : GoToTaskUploadAvatar START')
    # url = "https://epad-api.usadi.co.id/task_upload_avatar"
    url = f"{baseUrlScheme}://{baseUrl}/task_upload_avatar"
    if baseUrlPort != None:
        url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/task_upload_avatar"
    r = requests.post(url, headers={"Origin": f'{origin}'}, data=json.dumps(
        {'folder_name': folderName, 'filenames': filenames, 'userid_avatar': userid_avatar, 'userid': userid}))
    logger.info('TASK : GoToTaskUploadAvatar RESULT -> ' + str(r.status_code) + ' ' + r.reason)
    logger.info('TASK : GoToTaskUploadAvatar FINISH')
    logger.info('----------------------------------------------------------------TASK END')


def GoToTaskDeleteAvatar(pathx, origin=None):
    logger.info('----------------------------------------------------------------TASK BEGIN')
    logger.info('TASK : GoToTaskDeleteAvatar START')
    url = f"{baseUrlScheme}://{baseUrl}/task_delete_avatar"
    if baseUrlPort != None:
        url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/task_delete_avatar"
    r = requests.post(url, headers={"Origin": f'{origin}'}, data=json.dumps({'path': pathx}))
    logger.info('TASK : GoToTaskDeleteAvatar RESULT -> ' + str(r.status_code) + ' ' + r.reason)
    logger.info('TASK : GoToTaskDeleteAvatar FINISH')
    logger.info('----------------------------------------------------------------TASK END')


def GoToTaskUploadArticleImg(folderName, filenames, id, userid=None, origin=None):
    logger.info('----------------------------------------------------------------TASK BEGIN')
    logger.info('TASK : GoToTaskUploadArticleImg START')
    url = f"{baseUrlScheme}://{baseUrl}/task_upload_article_img"
    if baseUrlPort != None:
        url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/task_upload_article_img"
    r = requests.post(url, headers={"Origin": f'{origin}'}, data=json.dumps(
        {'folder_name': folderName, 'filenames': filenames, 'id': id, 'userid': userid}))
    logger.info('TASK : GoToTaskUploadArticleImg RESULT -> ' + str(r.status_code) + ' ' + r.reason)
    logger.info('TASK : GoToTaskUploadArticleImg FINISH')
    logger.info('----------------------------------------------------------------TASK END')


def GoToTaskDeleteArticleImg(pathx, origin=None):
    logger.info('----------------------------------------------------------------TASK BEGIN')
    logger.info('TASK : GoToTaskDeleteArticleImg START')
    url = f"{baseUrlScheme}://{baseUrl}/task_delete_article_img"
    if baseUrlPort != None:
        url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/task_delete_article_img"
    r = requests.post(url, headers={"Origin": f'{origin}'}, data=json.dumps({'path': pathx}))
    logger.info('TASK : GoToTaskDeleteArticleImg RESULT -> ' + str(r.status_code) + ' ' + r.reason)
    logger.info('TASK : GoToTaskDeleteArticleImg FINISH')
    logger.info('----------------------------------------------------------------TASK END')


def GoToTaskUploadWaPuAvatar(folderName, filenames, wapuid, userid=None, self_upload=False, origin=None):
    logger.info('----------------------------------------------------------------TASK BEGIN')
    logger.info('TASK : GoToTaskUploadWaPuAvatar START')
    logger.info(baseUrl)
    url = f"{baseUrlScheme}://{baseUrl}/task_upload_wapu_avatar"
    if baseUrlPort != None:
        url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/task_upload_wapu_avatar"
    logger.info(url)
    r = requests.post(url, headers={"Origin": f'{origin}'}, data=json.dumps(
        {'folder_name': folderName, 'filenames': filenames, 'wapuid': wapuid, 'userid': userid, 'self_upload': self_upload}))
    logger.info(r)
    logger.info('TASK : GoToTaskUploadWaPuAvatar RESULT -> ' + str(r.status_code) + ' ' + r.reason)
    logger.info('TASK : GoToTaskUploadWaPuAvatar FINISH')
    logger.info('----------------------------------------------------------------TASK END')

def GoToTaskDeleteWaPuAvatar(pathx, origin=None):
    logger.info('----------------------------------------------------------------TASK BEGIN')
    logger.info('TASK : GoToTaskDeleteWaPuAvatar START')
    url = f"{baseUrlScheme}://{baseUrl}/task_delete_wapu_avatar"
    if baseUrlPort != None:
        url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/task_delete_wapu_avatar"
    r = requests.post(url, headers={"Origin": f'{origin}'}, data=json.dumps({'path': pathx}))
    logger.info('TASK : GoToTaskDeleteWaPuAvatar RESULT -> ' + str(r.status_code) + ' ' + r.reason)
    logger.info('TASK : GoToTaskDeleteWaPuAvatar FINISH')
    logger.info('----------------------------------------------------------------TASK END')

def GoToTaskUploadOPDAvatar(folderName, filenames, opdid, userid=None, self_upload=False, origin=None):
    logger.info('----------------------------------------------------------------TASK BEGIN')
    logger.info('TASK : GoToTaskUploadOPDAvatar START')
    logger.info(baseUrl)
    url = f"{baseUrlScheme}://{baseUrl}/task_upload_opd_avatar"
    if baseUrlPort != None:
        url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/task_upload_opd_avatar"

    r = requests.post(url, headers={"Origin": f'{origin}'}, data=json.dumps(
        {'folder_name': folderName, 'filenames': filenames, 'opdid': opdid, 'userid': userid, 'self_upload': self_upload}))
    logger.info('TASK : GoToTaskUploadOPDAvatar RESULT -> ' + str(r.status_code) + ' ' + r.reason)
    logger.info('TASK : GoToTaskUploadOPDAvatar FINISH')
    logger.info('----------------------------------------------------------------TASK END')


def GoToTaskDeleteOPDAvatar(pathx, origin=None):
    logger.info('----------------------------------------------------------------TASK BEGIN')
    logger.info('TASK : GoToTaskDeleteOPDAvatar START')
    url = f"{baseUrlScheme}://{baseUrl}/task_delete_opd_avatar"
    if baseUrlPort != None:
        url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/task_delete_opd_avatar"
    r = requests.post(url, headers={"Origin": f'{origin}'}, data=json.dumps({'path': pathx}))
    logger.info('TASK : GoToTaskDeleteOPDAvatar RESULT -> ' + str(r.status_code) + ' ' + r.reason)
    logger.info('TASK : GoToTaskDeleteOPDAvatar FINISH')
    logger.info('----------------------------------------------------------------TASK END')

def GoToTaskUploadDocLapor(folderName, filenames, doc_lapor, userid=None, self_upload=False, origin=None):
    logger.info('----------------------------------------------------------------TASK BEGIN')
    logger.info('TASK : GoToTaskUploadDocLapor START')
    logger.info(baseUrl)
    url = f"{baseUrlScheme}://{baseUrl}/task_upload_doc_lapor"
    if baseUrlPort != None:
        url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/task_upload_doc_lapor"

    r = requests.post(url, headers={"Origin": f'{origin}'}, data=json.dumps(
        {'folder_name': folderName, 'filenames': filenames, 'doc_lapor': doc_lapor, 'userid': userid, 'self_upload': self_upload}))
    logger.info('TASK : GoToTaskUploadDoc RESULT -> ' + str(r.status_code) + ' ' + r.reason)
    logger.info('TASK : GoToTaskUploadDoc FINISH')
    logger.info('----------------------------------------------------------------TASK END')


def GoToTaskDeleteDocLapor(pathx, origin=None):
    logger.info('----------------------------------------------------------------TASK BEGIN')
    logger.info('TASK : GoToTaskDeleteDocLapor START')
    url = f"{baseUrlScheme}://{baseUrl}/task_delete_doc_lapor"
    if baseUrlPort != None:
        url = f"{baseUrlScheme}://{baseUrl}:{baseUrlPort}/task_delete_doc_lapor"
    r = requests.post(url, headers={"Origin": f'{origin}'}, data=json.dumps({'path': pathx}))
    logger.info('TASK : GoToTaskDeleteDocLapor RESULT -> ' + str(r.status_code) + ' ' + r.reason)
    logger.info('TASK : GoToTaskDeleteDoclapor FINISH')
    logger.info('----------------------------------------------------------------TASK END')