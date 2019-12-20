import sys
from basemodule.logger import logger
from urllib.parse import unquote


def get_uidAndname(cookie_douyu):
    acf_uid = None
    acf_nickname = ''
    try:
        if 'acf_uid' in cookie_douyu.keys():
            acf_uid = cookie_douyu['acf_uid']
        if 'acf_nickname' in cookie_douyu.keys():
            acf_nickname = cookie_douyu['acf_nickname']
            acf_nickname = unquote(acf_nickname, 'utf-8')
    except Exception as e:
        logger.exception(e)

    return acf_uid, acf_nickname