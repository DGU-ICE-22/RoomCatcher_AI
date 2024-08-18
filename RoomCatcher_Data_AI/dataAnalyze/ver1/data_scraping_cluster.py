from datetime import datetime
import json
import os, sys
import concurrent.futures
import traceback  # 멀티스레딩을 위한 라이브러리

# 현재 파일의 상위 두 디렉토리 경로를 sys.path에 추가
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if module_path not in sys.path:
    sys.path.append(module_path)
    
from dataAnalyze.common import get_secret, connect_db, process_single_ad
from dataAnalyze.ver1.transpose_location_to_address_dabang import get_address_from_coordinates
from dataAnalyze.ver2.product_crawling_v2 import product_crawling_v2

def return_room_data(secrets):
    flag = False
    room_data = product_crawling_v2(secrets, flag)
    return room_data

def create_address(item, secrets):
    
    API_KEY = get_secret('API_KEY', secrets)
    x,y = item.get('wgs84위도', None), item.get('wgs84경도', None)
    
    if x is None or y is None:
        return ValueError("No location information found.")
    
    address = get_address_from_coordinates(y, x, API_KEY)
    
    return address

def process_and_save_data(room_data, conn, cursor, secrets):
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dataAnalyze_ProductKB (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            층구분 TEXT,
            연면적 REAL,
            욕실수 INTEGER,
            전세가율 REAL,
            주택형 TEXT,
            최소월세가 INTEGER,
            매물유입구분 TEXT,
            매매가 INTEGER,
            위도 REAL,
            건축면적 REAL,
            허위매물처리결과 TEXT,
            건축물용도 TEXT,
            단지명 TEXT,
            월세보증금 INTEGER,
            방수 INTEGER,
            사용월 TEXT,
            전용면적 REAL,
            중개업소주소 TEXT,
            등록일 TEXT,
            매물상태 TEXT,
            사용년차 REAL,
            건폐율 TEXT,
            매물일련번호 INTEGER,
            광고내용 TEXT,
            이미지수 INTEGER,
            순공급면적 REAL,
            매물종별 TEXT,
            순전용면적 REAL,
            매물유입구분명 TEXT,
            최대전세가 INTEGER,
            매물거래구분 TEXT,
            용적률 TEXT,
            융자금 TEXT,
            중개업소명 TEXT,
            최대대출가능금액 REAL,
            총층수 INTEGER,
            매물명 TEXT,
            단지기본일련번호 INTEGER,
            입주가능일 TEXT,
            실거래가대비 INTEGER,
            층수 TEXT,
            경도 REAL,
            사용년 TEXT,
            클러스터식별자 TEXT,
            시군구주소 TEXT,
            평당단가 INTEGER,
            방향구분 TEXT,
            승강기유무 INTEGER,
            매물종별구분 TEXT,
            카테고리2 TEXT,
            매물종별그룹구분 TEXT,
            상세번지 TEXT,
            건물명 TEXT,
            대지면적 REAL,
            이미지URL TEXT,
            현관구조 TEXT,
            주소 TEXT
        )
    ''')
    try:
        for items in room_data:
            items = items["dataBody"]["data"]["propertyList"]
            for item in items:
                image_url = f"{item.get('이미지도메인URL', '')}{item.get('이미지디렉토리경로내용', '')}{item.get('이미지파일명', '')}"
                address = create_address(item, secrets)
                registration_date = str(datetime.strptime(item.get('등록년월일', ''), '%Y.%m.%d').date() if item.get('등록년월일') else None)

                cursor.execute('''
                    INSERT INTO dataAnalyze_ProductKB (
                        층구분, 연면적, 욕실수, 전세가율, 주택형,
                        최소월세가, 매물유입구분, 매매가, 위도, 건축면적,
                        허위매물처리결과, 건축물용도, 단지명, 월세보증금,
                        방수, 사용월, 전용면적, 중개업소주소, 등록일,
                        매물상태, 사용년차, 건폐율, 매물일련번호,
                        광고내용, 이미지수, 순공급면적, 매물종별, 순전용면적,
                        매물유입구분명, 최대전세가, 매물거래구분, 용적률, 융자금,
                        중개업소명, 최대대출가능금액, 총층수, 매물명, 단지기본일련번호,
                         입주가능일, 실거래가대비, 층수, 경도,
                        사용년, 클러스터식별자, 시군구주소, 평당단가, 방향구분,
                        승강기유무, 매물종별구분, 카테고리2, 매물종별그룹구분, 상세번지,
                        건물명, 대지면적, 이미지URL, 현관구조, 주소
                    ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
                ''', (
                    item.get('해당층구분', ''), item.get('연면적', 0.0), item.get('욕실수', 0), item.get('전세가율', 0.0),
                    item.get('주택형타입내용', ''), item.get('최소월세가', 0), item.get('매물유입구분', ''), item.get('매매일반거래가', 0),
                    item.get('wgs84위도', 0.0), item.get('건축면적', 0.0), item.get('허위매물처리결과구분명', ''), item.get('건축물용도코드명', ''),
                    item.get('단지명', ''), item.get('월세보증금', 0), item.get('방수', 0), item.get('사용월', ''), item.get('전용면적', 0.0),
                    item.get('중개업소주소', ''), registration_date, item.get('매물상태구분', ''), item.get('사용년차', 0.0), item.get('건폐율내용', ''),
                    item.get('매물일련번호', 0), item.get('특징광고내용', ''), item.get('매물이미지개수', 0), item.get('순공급면적', 0),
                    item.get('매물종별구분명', ''), item.get('순전용면적', 0.0), item.get('매물유입구분명', ''), item.get('최대전세가', 0),
                    item.get('매물거래구분명', ''), item.get('용적률내용', ''), item.get('융자금', ''), item.get('중개업소명', ''), item.get('최대대출가능금액', 0.0),
                    item.get('총층수', 0), item.get('매물명', ''), item.get('단지기본일련번호', 0), item.get('입주가능일내용', ''),
                    item.get('실거래가대비', 0), item.get('해당층수', ''), item.get('wgs84경도', 0.0), item.get('사용년', ''), item.get('클러스터식별자', ''),
                    item.get('시군구주소', ''), item.get('평당단가', 0), item.get('방향구분명', ''), item.get('승강기유무', 0), item.get('매물종별구분', ''),
                    item.get('카테고리2', ''), item.get('매물종별그룹구분명', ''), item.get('상세번지내용', ''), item.get('건물명', ''), item.get('대지면적', 0.0),
                    image_url, item.get('현관구조내용', ''), address
                ))

        conn.commit()
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Transaction failed: {e}")
        traceback.print_exc()

def add_tag_to_KB_cluster(table_name, secrets):
    
    try:
        conn = connect_db(secrets)
        cursor = conn.cursor()

        if table_name == 'dataAnalyze_ProductKB':
            cursor.execute('SELECT id, ad_description FROM {}'.format(table_name))
            product_ads = cursor.fetchall()

            # ThreadPoolExecutor 사용
            with concurrent.futures.ThreadPoolExecutor() as executor:
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

            
def main_cluster_ver():        # 매물 데이터 클러스터 단위로 크롤링 및 저장
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..','..','..','secret.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())
        
    try:
        conn = connect_db(secrets)
        cursor = conn.cursor()
    except Exception as e:
        print(f"An error occurred in main_cluster_ver: {e}")
        traceback.print_exc()
        return
    try:
    
        room_data = return_room_data(secrets)
        process_and_save_data(room_data, conn, cursor, secrets)
        # add_tag_to_KB_cluster("dataAnalyze_productkb", secrets)   
        conn.commit() 
    except Exception as e:
        print(f"An error occurred in main_cluster_ver: {e}")
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()
    
if __name__ == "__main__":
    main_cluster_ver()