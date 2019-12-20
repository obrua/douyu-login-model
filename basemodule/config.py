import sys
import os
from dotenv import load_dotenv

# see by https://github.com/mytliulei/boundless/blob/master/python/%E6%89%93%E5%8C%85exe/pyinstaller.md
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 文件所在目录
    #BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # 文件所在目录上级
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    # 运行环境所在目录
    #BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ENV支持中文 编码为GBK
load_dotenv(os.path.join('.', '.env'), encoding='utf-8')

class Config(object):

    ENV = os.environ.get('LOGURU_LEVEL') or 'PRODUCTION'
    LOGURU_LEVEL = os.environ.get('LOGURU_LEVEL') or 'INFO'
    LOGURU_LOGFILE = os.environ.get('LOGURU_LOGFILE') or 'logfile.log'
