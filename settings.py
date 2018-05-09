import os
import logging


log = logging.getLogger('app')
log.setLevel(logging.DEBUG)

f = logging.Formatter('[L:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', datefmt = '%d-%m-%Y %H:%M:%S')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(f)
log.addHandler(ch)

PROJECT_APP_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(PROJECT_APP_PATH, "templates")
STATIC_PATH = os.path.join(PROJECT_APP_PATH, "static")
MEDIA_PATH = os.path.join(PROJECT_APP_PATH, "media")
DB_FILE = "chat.db"
MAX_MSG = 20
