# cython: language_level=3
import loguru
import os
import sys
from basemodule.config import Config, BASE_DIR
# TRACE 5	logger.trace()
# DEBUG	10	logger.debug()
# INFO	20	logger.info()
# SUCCESS	25	logger.success()
# WARNING	30	logger.warning()
# ERROR	40	logger.error()
# CRITICAL	50	logger.critical()
#logger.success('mulargs',a,b,c,j=3,v=2)

logger = loguru.logger
logger.remove()

fmt = "<g>{time}</> | <lvl>{level}</> | <c>{name}</>:<c>{line}</>:<c>{line}</>;<c>{thread.name}</> - <lvl>{message}</>"
if Config.ENV == 'PRODUCTION':
    fmt = "<g>{time}</> | <lvl>{level}</> | <c>{name}</>; - <lvl>{message}</>"
log_file_path = os.path.join(BASE_DIR,f'log/{Config.LOGURU_LOGFILE}')

logger.add(sys.stdout,
           format=fmt,
           level=Config.LOGURU_LEVEL)
if Config.ENV == 'PRODUCTION':
    logger.add(log_file_path,
               format=fmt,
               level=Config.LOGURU_LEVEL,
               enqueue=True,
               rotation="50 MB",
               retention="7 days",
               encoding='utf-8')