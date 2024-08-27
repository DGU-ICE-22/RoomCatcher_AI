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
    conn = pymysql.connect(
    host='roomcatcher-database.cha2oikwwubl.ap-northeast-2.rds.amazonaws.com',  # 로컬 호스트
    port=3306,         # 로컬 머신의 3306 포트 (실제로는 RDS로 터널링됨)
    user='roomcatcher',
    password=password,
    database='roomcatcher'
    )
    return conn