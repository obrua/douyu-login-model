from douyu_login import loginByQrcode

while True:
	# 从文件获取cookie
	cookie_douyu = loginByQrcode.get_cookie_from_txt()
	if cookie_douyu and loginByQrcode.test_get_csrf_cookie(cookie_douyu):
		break
	else:
		# 二维码登录
		blogin_suss = loginByQrcode.pc_qrcode_login()
		if blogin_suss:
			break