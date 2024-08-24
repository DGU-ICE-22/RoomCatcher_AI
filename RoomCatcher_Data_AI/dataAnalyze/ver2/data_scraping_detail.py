import json
import os, sys
import sqlite3
import traceback
import pymysql

# 현재 파일의 상위 두 디렉토리 경로를 sys.path에 추가
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from dataAnalyze.common import process_single_ad
from dataAnalyze.ver2.product_crawling_detail import product_crawling_detail
import concurrent.futures  # 멀티스레딩을 위한 라이브러리
from dataAnalyze.common import get_secret, connect_db, detail_and_save_data, get_listing_serial_number

def add_tag_to_KB_detail(table_name, secrets):
    try:
        conn = connect_db(secrets)
        cursor = conn.cursor()

        if table_name == 'data_analyze_product_kb_detail':
            cursor.execute('''
                SELECT id, 매물일련번호, 특징광고내용
                FROM {}
                WHERE id < 1000
            '''.format(table_name))
            product_ads = cursor.fetchall()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_analyze_tag_detail (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    tagName VARCHAR(255)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_analyze_product_tag_detail (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    product_detail_id INT,
                    listing_serial_number INT,
                    tag_id INT,
                    product_id INT,
                    FOREIGN KEY(product_detail_id) REFERENCES data_analyze_product_kb_detail(id) ON DELETE CASCADE,
                    FOREIGN KEY(tag_id) REFERENCES data_analyze_tag_detail(id) ON DELETE CASCADE,
                    FOREIGN KEY(product_id) REFERENCES data_analyze_ProductKB(id) ON DELETE CASCADE
                )
            ''')

            # ThreadPoolExecutor 사용
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(process_single_ad, product_ad, secrets) for product_ad in product_ads]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as exc:
                        print(f'Generated an exception: {exc}')

    except Exception as e:
        print(f"An error occurred in add_tag_to_KB: {e}")
        traceback.print_exc()

    finally:
        if conn:
            conn.close()
            
def main_detail_ver():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..', '..','..','secret.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())
            
    conn = connect_db(secrets)
    cursor = conn.cursor()
    listing_serial_number_lists = get_listing_serial_number(conn, cursor)         #productKB에서 모든 매물일련번호 리스트 가져오기 

    for serial_number in listing_serial_number_lists:
        detail_info = product_crawling_detail(serial_number, secrets)  # 매물 상세 정보 가져오기
        detail_and_save_data(detail_info, serial_number, conn, cursor)     # 가져온 상세 정보로 데이터베이스에 저장
    
    add_tag_to_KB_detail("data_analyze_product_kb_detail", secrets)        # 상세 정보에 태그 추가
    
if __name__ == "__main__":
    main_detail_ver()