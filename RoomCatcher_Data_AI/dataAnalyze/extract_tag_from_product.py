import requests
import sqlite3
from django.core.exceptions import ImproperlyConfigured
import os
import json

def get_secret(setting, secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)
    
def extract_keywords(text):
    # 요청할 URL
    url = 'https://wordcount.com/api/extract_keywords'
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..', '..','secret.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())
        
    # 헤더 설정
    headers = get_secret('headersKeyword', secrets)

    # POST 데이터 설정
    data = {
        'text': text,
        'locale': 'ko'
    }

    # POST 요청 보내기
    response = requests.post(url, headers=headers, json=data)

    # 응답 상태 코드 출력
    print(f'Status Code: {response.status_code}')

    # 응답 내용 바이너리로 읽기
    response_content = response.content

    # 응답 내용을 텍스트로 디코딩 (UTF-8로 디코딩 시도)
    response_text = response_content.decode('utf-8')
    # 키워드를 분리하고 '-' 제거
    keywords = response_text.split('\n')
    cleaned_keywords = [keyword.replace('-','').replace('키워드:','').strip() for keyword in keywords if keyword.strip()]

    # 키워드를 문자열로 결합하여 반환
    return ', '.join(cleaned_keywords)

def add_tags_to_db():
    # SQLite 데이터베이스 경로
    db_path = 'room_lists.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 기존 테이블에 'tag' 열 추가
    try:
        cursor.execute("ALTER TABLE room_lists ADD COLUMN tag TEXT")
    except sqlite3.OperationalError as e:
        print(f"Column 'tag' already exists: {e}")

    # 모든 행에 대해 태그를 생성하고 업데이트
    cursor.execute("SELECT id, title FROM room_lists")
    rows = cursor.fetchall()

    for row in rows:
        row_id, title = row
        tags = extract_keywords(title)
        print(tags)
        cursor.execute("UPDATE room_lists SET tag = ? WHERE id = ?", (tags, row_id))

    conn.commit()
    conn.close()

    print("Tags have been added to the 'tag' column in the database.")

if __name__ == "__main__":
    add_tags_to_db()