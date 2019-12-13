from douyu_login import loginByQrcode
import requests

# 二维码登录
blogin_suss = loginByQrcode.pc_qrcode_login()
if blogin_suss:
    # 从文件获取cookie
    cookie_douyu = loginByQrcode.get_cookie_from_txt()
    # test_get_csrf_cookie
    if loginByQrcode.test_get_csrf_cookie(cookie_douyu):
        pass

