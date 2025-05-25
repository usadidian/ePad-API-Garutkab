import os
from pathlib import Path

import yagmail

from config.config import appName, appFrontWebUrl, appFrontWebLogo, appEmail, appEmailPassword, appFrontWebLogoBig, \
    appFrontWebMobileLogo, appFrontWebUrlWp, appNameMobile, appFrontWebMobileLogoBig
from config.helper import logger


def emailSendOtp(UserEmail, otp_code):
    try:
        logger.info('DO COMPOSSING EMAIL OTP...')
        # print(os.environ)
        path = Path(__file__).parent

        # EMAIL OTP UNTUK USERS
        receiver_email = UserEmail
        subject = "Aktivasi Akun {}".format(appName)
        with open('{}\email_sendotp_user.html'.format(path), 'r') as f:
            message = f.read()
        # url_email_verif = f'{appFrontWebUrl()}/account_verifotp.html?userdata={userdata}&otp={otp_code}'
        messageUser = message.format(
            UNIT_LOGO=appFrontWebLogoBig,
            UNIT_PUBLIC_URL=appFrontWebUrl(),
            UNIT_NAME=appName,
            OTP_CODE=otp_code,
            URL_EMAIL_VERIFICATION='#',
            URL_UNIT_HELP='#',
            URL_UNIT_STATICPAGE='#'
        )
        yag = yagmail.SMTP({appEmail: appName}, appEmailPassword)
        yag.send(receiver_email, subject, [messageUser])
        logger.info('SEND EMAIL OTP TO USER {} OK'.format(receiver_email))
        yag.close()
        return True
    except Exception as e:
        logger.error('DO COMPOSSING EMAIL OTP FAILED!')
        logger.error(e)
        return False
    # finally:
    #     server.quit()


def emailSendOtpMobile(UserEmail, otp_code):
    try:
        logger.info('DO COMPOSSING EMAIL OTP WPO...')
        # print(os.environ)
        path = Path(__file__).parent

        # EMAIL OTP UNTUK USERS
        receiver_email = UserEmail
        subject = "Aktivasi Akun {}".format(appNameMobile)
        with open('{}\email_sendotp_user.html'.format(path), 'r') as f:
            message = f.read()
        # url_email_verif = f'{appFrontWebUrl()}/account_verifotp.html?userdata={userdata}&otp={otp_code}'
        messageUser = message.format(
            UNIT_LOGO=appFrontWebMobileLogoBig,
            UNIT_PUBLIC_URL=appFrontWebUrlWp,
            UNIT_NAME=appNameMobile,
            OTP_CODE=otp_code,
            URL_EMAIL_VERIFICATION='#',
            URL_UNIT_HELP='#',
            URL_UNIT_STATICPAGE='#'
        )
        yag = yagmail.SMTP({appEmail: appNameMobile}, appEmailPassword)
        yag.send(receiver_email, subject, [messageUser])
        logger.info('SEND EMAIL OTP WPO TO USER {} OK'.format(receiver_email))
        yag.close()
        return True
    except Exception as e:
        logger.error('DO COMPOSSING EMAIL OTP WPO FAILED!')
        logger.error(e)
        return False
    # finally:
    #     server.quit()


def emailSendOtpForgotPwd(data):
    try:
        logger.info('DO COMPOSSING EMAIL OTP FORGOT PWD...')
        # print(os.environ)
        path = Path(__file__).parent

        # EMAIL OTP UNTUK USERS
        receiver_email = data['email']
        subject = "Lupa Kata Sandi Akun {}".format(appName)
        with open('{}\email_sendotp_forgot_user.html'.format(path), 'r') as f:
            message = f.read()
        messageUser = message.format(
            UNIT_LOGO=appFrontWebLogoBig,
            UNIT_PUBLIC_URL=data['origin'],
            UNIT_NAME=appName,
            DATETIME=data['datetime'],
            OTP_CODE=data['code'],
            URL_UNIT_HELP='#',
            URL_UNIT_STATICPAGE='#'
        )
        yag = yagmail.SMTP({appEmail: appName}, appEmailPassword)
        yag.send(receiver_email, subject, [messageUser])
        logger.info('SEND EMAIL OTP FORGOT PWD TO USER {} OK'.format(receiver_email))
        yag.close()
        return True
    except Exception as e:
        logger.error('DO COMPOSSING EMAIL OTP FORGOT PWD FAILED!')
        logger.error(e)
        return False
    # finally:
    #     server.quit()