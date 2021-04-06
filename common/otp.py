import logging
from base64 import b32encode

import requests
from pyotp import totp

from system.settings import settings

logger = logging.getLogger("api")
OTP_API = 'http://control.msg91.com/api/sendotp.php'


def generate_secret_key(phone: str):
    return b32encode(('{}{}'.format(phone, settings.SECRET_KEY)).encode())


def generate_otp(phone: str):
    TOTP = totp.TOTP(generate_secret_key(phone), interval=settings.OTP_VALIDITY_PERIOD, digits=settings.OTP_LENGTH)
    return TOTP.now()


def verify_generated_otp(phone, otp):
    TOTP = totp.TOTP(generate_secret_key(phone), interval=settings.OTP_VALIDITY_PERIOD, digits=settings.OTP_LENGTH)
    return TOTP.verify(otp)


def generate_and_send_otp(phone) -> (bool, str):
    otp = generate_otp(phone)

    params = dict()
    params['authkey'] = settings.MSG91_AUTHKEY
    params['template_id'] = settings.MST91_OTP_TEMPLATE_ID
    params['mobile'] = phone
    params['message'] = "<#>OTP for Quikmile login is {} FEOQmH7HwNd".format(otp)
    params['otp'] = otp
    params['sender'] = "QKMILE"

    r = requests.get(OTP_API, params=params)
    if r.status_code == 200 and r.json().get('type', '') != 'error':
        logger.info("{}".format(r.json()))
        return True, None
    else:
        logger.error("{}".format(r.json()))
        return False, r.json()
