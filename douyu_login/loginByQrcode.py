import sys
import os
import requests
import json
import time
import qrcode
import re
from PIL import Image
from basemodule.config import Config, BASE_DIR
from basemodule.logger import logger
from . import utils

cookie_file = os.path.join(BASE_DIR, 'cookie_douyu.txt')
qrcode_file = os.path.join(BASE_DIR, 'qrcode.png')

def pc_get_qrcode(session):
    #获取二维码

    url = 'https://passport.douyu.com/scan/generateCode'
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'referer': 'https://passport.douyu.com/index/login?passport_reg_callback=PASSPORT_REG_SUCCESS_CALLBACK&passport_login_callback=PASSPORT_LOGIN_SUCCESS_CALLBACK&passport_close_callback=PASSPORT_CLOSE_CALLBACK&passport_dp_callback=PASSPORT_DP_CALLBACK&type=login&client_id=1&state=https%3A%2F%2Fwww.douyu.com%2F&source=click_topnavi_login',
    }
    data = {'client_id': 1}

    
    try:
        logger.info('获取二维码请求')
        res = session.post(url, headers=headers, data=data)
        res_json = res.json()
        logger.debug(res_json)
        if res_json['error']!=0:
            logger.warning(f'获取二维码失败 {res_json}')
            return False

        ttl = time.time() + res_json.get('data').get('expire')
        check_url = res_json.get('data').get('url')
        code = res_json.get('data').get('code')
        scan_url = f'https://passport.douyu.com/scan/checkLogin?scan_code={code}'
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(scan_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        # ?print_ascii 对cmd不友好, 直接使用图片
        img.save(qrcode_file)
        os.startfile(qrcode_file)

        #invert=True白底黑块,有些app不识别黑底白块.
        #qr.print_ascii(out=None, tty=False, invert=True)

        return code,ttl

    except Exception as e:
        logger.exception(f'获取二维码异常 {e}')
        return False


def wait_to_scan_qrcode(session, code, ttl):
    # 等待扫码
    while(time.time() < ttl):
        try:
            url = f'https://passport.douyu.com/lapi/passport/qrcode/check?time={int(time.time()*1000)}&code={code}'
            headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
                'referer': 'https://passport.douyu.com/index/login?passport_reg_callback=PASSPORT_REG_SUCCESS_CALLBACK&passport_login_callback=PASSPORT_LOGIN_SUCCESS_CALLBACK&passport_close_callback=PASSPORT_CLOSE_CALLBACK&passport_dp_callback=PASSPORT_DP_CALLBACK&type=login&client_id=1&state=https%3A%2F%2Fwww.douyu.com%2F&source=click_topnavi_login',
            }

            res = session.get(url, headers=headers)
            res_json = res.json()
            logger.debug(res_json)

            error_code = res_json.get('error')
            # 1: 已扫码
            if error_code not in [0]:
                logger.info('未扫码，请扫码')
                time.sleep(5)
            else:
                logger.info(res_json)
                return res_json.get('data').get('url')

        except Exception as e:
            logger.exception(f'扫码二维码异常 {e}')
            return False


def redirect_scan_qrcode_success(session, loginurl):
    # 扫描成功后执行登录获取cookie
    # 保存cookie到txt中
    try:
        url = 'http:' + loginurl
        # //[图片]www.douyu.com/api/passport/login?code=bcb2980ce79f6e6f35061633b0e29ebb&loginType=scanCheck&uid=97475141
        # [图片]https://www.douyu.com/api/passport/login?code=bcb2980ce79f6e6f35061633b0e29ebb&loginType=scanCheck&uid=97475141&callback=appClient_json_callback&_=1575345382937
        uid = re.findall(r'uid\=(\d+)', url)[0]
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'referer': 'https://passport.douyu.com/index/login?passport_reg_callback=PASSPORT_REG_SUCCESS_CALLBACK&passport_login_callback=PASSPORT_LOGIN_SUCCESS_CALLBACK&passport_close_callback=PASSPORT_CLOSE_CALLBACK&passport_dp_callback=PASSPORT_DP_CALLBACK&type=login&client_id=1&state=https%3A%2F%2Fwww.douyu.com%2F&source=click_topnavi_login',
        }
        url = f'{url}&callback=appClient_json_callback&_={int(time.time()*1000)}'
        res = session.get(url, headers=headers)
        res = res.text.replace('appClient_json_callback(', '').rstrip(')')
        res_json = json.loads(res)
        logger.debug(res_json)
        error_code = res_json.get('error')
        if error_code != 0:
            logger.warning(f'登录失败 {res_json}')
            return False

        return save_cookie_to_txt(session)

    except Exception as e:
        logger.exception(f'登录异常 {e}')
        return False


def pc_qrcode_login():
    """二维码登录"""
    session = requests.Session()
    code = None
    ttl = None
    bsuss = False
    while True:
        code, ttl = pc_get_qrcode(session)
        if ttl and ttl>0:
            break
        else:
            logger.error('获取二维码失败，10秒后重试')
            time.sleep(10)
    logger.debug(f'code:{code} ttl:{ttl}')
    logger.success('获取二维码成功，请扫描登录')
    loginurl = wait_to_scan_qrcode(session, code, ttl)
    if loginurl:
        logger.success('扫码成功，开始执行登录!')
        if redirect_scan_qrcode_success(session, loginurl):
            logger.success('登录&&保存cookie 成功!')
            bsuss = True
        else:
            logger.success('执行登录失败!')
            bsuss = False
    else:
        logger.error('登录失败')
        bsuss = False
    
    return bsuss

def get_cookie_from_txt():
    # 从txt获取cookie
    cookie_douyu = dict()
    if os.path.exists(cookie_file):
        logger.info('存在 cookie_douyu.txt，加载中... ')
        with open(cookie_file, 'r') as f:
            # cookies 直接用浏览器获取
            txt=f.read()
            _list = txt.split(';')
            for item in _list:
                cookie= []
                cookie= item.split('=',1)
                if len(cookie)>=2:
                    cookie_douyu[cookie[0].strip()] = cookie[1]
        # s.cookies.update(cookie_douyu)
    if not cookie_douyu:
        logger.warning('cookie为空，请检测是否存在cookie_douyu.txt 或者 执行[pc_qrcode_login]重新获取')
        return False
    else:
        return cookie_douyu

def save_cookie_to_txt(session):
    # 保存cookie到txt
    try:
        cookiesdict = requests.utils.dict_from_cookiejar(session.cookies)
        logger.debug(cookiesdict)
        strcookie = ""
        for item in cookiesdict:
            strcookie = strcookie + '{}={};'.format(item,cookiesdict[item])

        logger.info('保存cookie -> cookie_douyu.txt')
        with open(cookie_file,'w') as f:
            f.write(strcookie)
    except Exception as e:
        logger.exception(f'保存cookie -> cookie_douyu.txt {e}')
        return False
    else:
        logger.success('保存cookie -> cookie_douyu.txt 成功!')
        return True

def test_get_csrf_cookie(cookie):
    # 验证cookie是否有效，并且获取Crsf
    # acf_ccn
    try:
        logger.info('验证&&获取csrf...')
        baseheaders = {
            'referer': 'https://www.douyu.com/9999',
            'origin': 'https://www.douyu.com',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        }

        with requests.Session() as s:
            url = 'https://www.douyu.com/curl/csrfApi/getCsrfCookie'

            s.cookies.update(cookie)
            res = s.get(url, headers=baseheaders)
            res.close()
            res = res.json()
            if res['error']==0 and res['msg']=='ok':
                logger.success('验证&&获取csrf，成功！')
                save_cookie_to_txt(s)
                return True
            else:
                logger.error(f'错误提示：{res}')
                logger.error('测试签到出错, 请更新查看错误提示，是否更新cookie_douyu!')
                return False

    except Exception as e:
        logger.exception('检测cookie是否过期: {}'.format(e))
        return False

