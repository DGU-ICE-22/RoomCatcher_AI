import requests
import os 
import json
from django.core.exceptions import ImproperlyConfigured
from .product_crawling import product_crawling
import sqlite3

# 주소 변환 함수 
def get_address_from_coordinates(x, y, API_KEY):
    try:
        url = f'https://api.vworld.kr/req/address?service=address&request=getAddress&type=both&crs=epsg:4326&version=2.0&point={x},{y}&zipcode=false&simple=false&key={API_KEY}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('response', {}).get('status') == 'OK':
                results = data['response'].get('result', [])
                if results:
                    return results[0].get('text')  # 도로명 주소가 필요하면 인덱스를 1로 변경
        else:
            print(f"Error: HTTP {response.status_code}")
            
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except json.JSONDecodeError as e:
        print("JSON decoding error:", e)
    except KeyError as e:
        print("Key error:", e)
    except IndexError as e:
        print("Index error:", e)

    return None

def get_secret(setting, secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

def transpose_location_to_address():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..', '..','secret.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())

    # 데이터 가져오기
    room_data = product_crawling(secrets)
    # API 키 설정
    API_KEY = get_secret('API_KEY', secrets)

    # 주소 열 추가
    for room in room_data:
        location = room[1][4]
        x, y = location[0], location[1]
        address = get_address_from_coordinates(x, y, API_KEY)
        room[1].append(address)  # Append address to the room data


    # print(room_data)

    # SQLite3 데이터베이스 연결
    connection = sqlite3.connect('room_lists.db')
    cursor = connection.cursor()

    # 트랜잭션 시작
    cursor.execute("BEGIN TRANSACTION;")

    try:
        # 테이블 생성 (없을 경우)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dataAnalyze_product (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                productRoomType TEXT,
                productSellingType TEXT,
                productIsQuick BOOLEAN,
                productPrice TEXT,
                productIsContract BOOLEAN,
                productName TEXT,
                productInfo TEXT,
                productImage TEXT,
                productAddr TEXT
            )
        """)

        # 데이터 삽입
        for room in room_data:
            cursor.execute("""
                INSERT INTO dataAnalyze_product (productRoomType, productSellingType, productIsQuick, productPrice, productIsContract, productName, productInfo, productImage, productAddr)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                room[1][0],
                room[1][1],
                room[1][2],
                room[1][3],
                room[1][5],
                room[1][6],
                room[1][7],
                json.dumps([room[1][8], room[1][9]]),
                room[1][10]  # address
            ))

        # 변경사항 커밋
        connection.commit()
    except sqlite3.Error as err:
        print(f"Error: {err}")
        # 오류가 발생하면 롤백
        connection.rollback()
    finally:
        # 연결 종료
        cursor.close()
        connection.close()
        
def update_missing_addresses():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..', '..','secret.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())

    # API 키 설정
    API_KEY = get_secret('API_KEY', secrets)

    # SQLite3 데이터베이스 연결
    connection = sqlite3.connect('room_lists.db')
    cursor = connection.cursor()

    try:
        # 결측치가 있는 레코드 선택
        cursor.execute("SELECT id, location FROM dataAnalyze_product WHERE productAddr IS NULL OR productAddr = ''")
        rows = cursor.fetchall()

        # 결측치 주소 업데이트
        for row in rows:
            row_id, location = row
            location = json.loads(location)
            x, y = location[0], location[1]
            address = get_address_from_coordinates(x, y, API_KEY)
            if address:
                cursor.execute("UPDATE dataAnalyze_product SET productAddr = ? WHERE id = ?", (address, row_id))

        # 변경사항 커밋
        connection.commit()
    except sqlite3.Error as err:
        print(f"Error: {err}")
        # 오류가 발생하면 롤백
        connection.rollback()
    finally:
        # 연결 종료
        cursor.close()
        connection.close()

    print("Missing addresses have been updated.")

if __name__ == '__main__':
    transpose_location_to_address()
    update_missing_addresses()