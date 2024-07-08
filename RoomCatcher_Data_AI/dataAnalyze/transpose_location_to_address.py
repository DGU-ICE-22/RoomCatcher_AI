import pandas as pd
import requests
import os 
import json
import ast
from django.core.exceptions import ImproperlyConfigured
from product_crawling import product_crawling
import sqlite3

# 주소 변환 함수 
def get_address_from_coordinates(x, y, API_KEY):
    url = f'https://api.vworld.kr/req/address?service=address&request=getAddress&type=both&crs=epsg:4326&version=2.0&point={x},{y}&zipcode=false&simple=false&key={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['response']['status'] == 'OK':
            return data['response']['result'][0]['text']
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
    room_data = product_crawling()
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
            CREATE TABLE IF NOT EXISTS room_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_type TEXT,
                selling_type TEXT,
                is_quick BOOLEAN,
                price_title TEXT,
                location TEXT,
                is_contract BOOLEAN,
                title TEXT,
                room_more_info TEXT,
                img_url TEXT,
                img_urls TEXT,
                address TEXT
            )
        """)

        # 데이터 삽입
        for room in room_data:
            cursor.execute("""
                INSERT INTO room_lists (room_type, selling_type, is_quick, price_title, location, is_contract, title, room_more_info, img_url, img_urls, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                room[1][0],
                room[1][1],
                room[1][2],
                room[1][3],
                json.dumps(room[1][4]),
                room[1][5],
                room[1][6],
                room[1][7],
                room[1][8],
                json.dumps(room[1][9]),
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

if __name__ == '__main__':
    transpose_location_to_address()