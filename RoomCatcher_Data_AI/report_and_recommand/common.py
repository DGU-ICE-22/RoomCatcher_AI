import traceback
from django.core.exceptions import ImproperlyConfigured
import pymysql

def get_secret(setting, secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        traceback.print_exc()
        raise ImproperlyConfigured(error_msg)

def connect_db(secrets):
    # MySQL 데이터베이스에 연결
    password = get_secret('MySQL_PASSWORD', secrets)
    conn = pymysql.connect(host='localhost', user='root', password=password, db='RoomCatcherDB', charset='utf8mb4')
    return conn