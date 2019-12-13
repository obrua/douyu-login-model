import sys

# try:
#     b = u'\u2588'
#     sys.stdout.write(b + '\r')
#     sys.stdout.flush()
# except UnicodeEncodeError:
#     BLOCK = 'MM'
# else:
#     BLOCK = b

# def print_cmd_qr(qrText, white=BLOCK, black='  ', enableCmdQR=True):
#     blockCount = int(enableCmdQR)
#     if abs(blockCount) == 0:
#         blockCount = 1
#     white *= abs(blockCount)
#     if blockCount < 0:
#         white, black = black, white
#     sys.stdout.write(' '*50 + '\r')
#     sys.stdout.flush()
#     qr = qrText.replace('0', white).replace('1', black)
#     sys.stdout.write(qr)
#     sys.stdout.flush()