# 매물의 이름과 설명, 기타 정보 등으로 키워드를 추출해내는 방법 
import requests
import pymysql  # MySQL 연결을 위해 pymysql 사용
from django.core.exceptions import ImproperlyConfigured
import os
import json
from dataAnalyze.common import connect_db  # 오타 수정

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
    secret_file = os.path.join(base_dir, '..', '..', 'secret.json')

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

    # 응답 내용 바이너리로 읽기
    response_content = response.content

    # 응답 내용을 텍스트로 디코딩 (UTF-8로 디코딩 시도)
    response_text = response_content.decode('utf-8')
    response_json = json.loads(response_text)
    content = response_json.get('content', '')

    # 키워드를 쉼표로 분리하여 리스트로 반환
    keywords = [keyword.replace('-', '').replace('키워드:', '').strip() for keyword in content.replace('\n', ',').split(',') if keyword.strip()]

    return keywords

def add_tags_to_db(secrets):
    # MySQL 데이터베이스에 연결
    conn = connect_db(secrets)
    cursor = conn.cursor()

    # 기존 테이블에 'tag' 열 추가
    try:
        cursor.execute("ALTER TABLE dataAnalyze_productTag ADD COLUMN tag TEXT")
    except pymysql.MySQLError as e:
        print(f"Column 'tag' already exists or another error occurred: {e}")

    # 모든 행에 대해 태그를 생성하고 업데이트
    cursor.execute("SELECT id, title FROM dataAnalyze_product")
    rows = cursor.fetchall()

    for row in rows:
        row_id, title = row
        tags = ', '.join(extract_keywords(title))  # 태그를 쉼표로 구분된 문자열로 변환
        print(tags)
        cursor.execute("UPDATE dataAnalyze_productTag SET tag = %s WHERE id = %s", (tags, row_id))

    conn.commit()
    conn.close()

    print("Tags have been added to the 'tag' column in the database.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..', '..','secret.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())
    add_tags_to_db(secrets)