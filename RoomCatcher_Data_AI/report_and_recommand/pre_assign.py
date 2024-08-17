import json
import os
import pymysql
import traceback
import openai
from transformers import ElectraModel, ElectraTokenizer
import torch, numpy as np 
from sklearn.metrics.pairwise import cosine_similarity
from type_explain import type_1_money, type_2_option, type_3_structure, type_4_transport, type_5_nature, type_6_emotion, type_7_business, type_8_student
from calculate_similarity_userType_and_tag import get_user_input_embedding, get_secret

def calculate_similarity(embedding1, embedding2):
    # 두 임베딩 간의 유사도를 계산하는 함수
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

def assign_tag_from_db(user_type_list_embedding, client, conn, clear=False):
    # MySQL을 사용한 유사도 계산
    try:
        # 데이터베이스 커서 생성
        cursor = conn.cursor()
        
        # MySQL에서 테이블의 컬럼 정보를 가져오는 쿼리
        cursor.execute("SHOW COLUMNS FROM dataAnalyze_tag_detail")
        columns = [info[0] for info in cursor.fetchall()]
        
        # 각 tagName에 대한 임베딩 계산 및 업데이트
        # 만약 테이블에 'embedding' 컬럼이 없다면 생성하고 값을 채움
        if 'embedding' not in columns:
            # 데이터베이스에서 태그 정보 가져오기
            cursor.execute("SELECT id, tagName FROM dataAnalyze_tag_detail")
            tag_list = cursor.fetchall()

            # 'embedding' 컬럼을 추가 (BLOB 타입)
            cursor.execute("ALTER TABLE dataAnalyze_tag_detail ADD COLUMN embedding BLOB")

            # 각 태그에 대해 임베딩 계산 후 데이터베이스에 저장
            for tag_id, tagName in tag_list:
                embedding = get_user_input_embedding(tagName, client)
                embedding_blob = np.array(embedding).tobytes()
                cursor.execute("UPDATE dataAnalyze_tag_detail SET embedding = %s WHERE id = %s", (embedding_blob, tag_id))
        else:
            # 'embedding' 컬럼이 이미 존재할 경우, 비어있는 태그에 대해서만 임베딩을 계산하여 업데이트
            cursor.execute("SELECT id, tagName, embedding FROM dataAnalyze_tag_detail")
            tag_list = cursor.fetchall()

            for tag_id, tagName, embedding in tag_list:
                if embedding is None:
                    embedding = get_user_input_embedding(tagName, client)
                    embedding_blob = np.array(embedding).tobytes()
                    cursor.execute("UPDATE dataAnalyze_tag_detail SET embedding = %s WHERE id = %s", (embedding_blob, tag_id))

        # 변경사항 커밋
        conn.commit()
        
        # 모든 태그의 임베딩을 가져와서 유사도 계산
        cursor.execute("SELECT id, tagName, embedding FROM dataAnalyze_tag_detail")
        tag_embeddings = {tagName: np.frombuffer(embedding, dtype=np.float32) for _, tagName, embedding in cursor.fetchall()}
        
        # 태그를 유사도에 따라 정렬하여 반환
        sorted_tags = sorted(tag_embeddings.keys(), 
                             key=lambda tag: 
                                 cosine_similarity(tag_embeddings[tag].reshape(1, -1),
                                user_type_list_embedding[1].reshape(1, -1))[0][0],
                             reverse=True)
        
        print(sorted_tags[:int(len(sorted_tags)/8)])
        return (sorted_tags[:int(len(sorted_tags)/8)])
    except Exception as e:
        # 오류 발생 시 트랜잭션 롤백
        print(f"Error: {e}")
        traceback.print_exc()
        conn.rollback()
        return None
    finally:
        # 데이터베이스 연결 종료
        conn.close()
    # # KoELECTRA를 사용한 유사도 계산
    # try:
    #  
    #     cursor = conn.cursor()
        
    #     # MySQL에서 테이블의 컬럼 정보를 가져오는 쿼리
    #     cursor.execute("SHOW COLUMNS FROM dataAnalyze_tag_detail")
    #     columns = [info[0] for info in cursor.fetchall()]
        
    #     # 각 tagName에 대한 임베딩 계산 및 업데이트
    #     # 전체 태그에 대해 임베딩을 계산하고 데이터베이스에 업데이트
    #     if 'embedding' not in columns or clear == True:
    #         # 데이터베이스에서 유저 유형과 태그 정보 가져오기
    #         cursor.execute("SELECT id, tagName FROM dataAnalyze_tag_detail")
    #         tag_list = cursor.fetchall()

    #         # 'embedding' 컬럼을 추가 (BLOB 타입)
    #         cursor.execute("ALTER TABLE dataAnalyze_tag_detail ADD COLUMN embedding BLOB")
            
    #         # 각 태그에 대해 임베딩 계산 후 데이터베이스에 저장
    #         for tag_id, tagName in tag_list:
    #             embedding = get_embedding(tagName)
    #             embedding_blob = np.array(embedding).tobytes()
    #             cursor.execute("UPDATE dataAnalyze_tag_detail SET embedding = %s WHERE id = %s", (embedding_blob, tag_id))
    #     else:
    #         # 비어있는 태그에 대해 임베딩 계산 및 업데이트
    #         # 데이터베이스에서 유저 유형과 태그 정보 가져오기
    #         cursor.execute("SELECT id, tagName, embedding FROM dataAnalyze_tag_detail")
    #         tag_list = cursor.fetchall()

    #         # 각 태그에 대해 임베딩이 없는 경우에만 계산하여 데이터베이스에 저장
    #         for tag_id, tagName, embedding in tag_list:
    #             if embedding is None:
    #                 embedding = get_embedding(tagName)
    #                 embedding_blob = np.array(embedding).tobytes()
    #                 cursor.execute("UPDATE dataAnalyze_tag_detail SET embedding = %s WHERE id = %s", (embedding_blob, tag_id))
        
    #     # 변경사항 커밋
    #     conn.commit()
        
    #     # 태그 임베딩들을 불러와서 유사도 계산
    #     cursor.execute("SELECT id, tagName, embedding FROM dataAnalyze_tag_detail")
    #     tag_embeddings = {tagName: np.frombuffer(embedding, dtype=np.float32) for _, tagName, embedding in cursor.fetchall()}
    #     conn.close()

    #     # 태그를 유사도에 따라 정렬하여 반환
    #     sorted_tags = sorted(tag_embeddings.keys(), key=lambda tag: calculate_similarity(tag_embeddings[tag], user_type_list_embedding[3]), reverse=True)
    #     print(sorted_tags[:int(len(sorted_tags)/8)])
    #     return (sorted_tags[:int(len(sorted_tags)/8)])
    # except Exception as e:
    #     # 오류 발생 시 트랜잭션 롤백
    #     print(f"Error: {e}")
    #     traceback.print_exc()
    #     conn.rollback()
    #     return None

if __name__ == "__main__":
    # 사용자 유형 리스트
    user_type_list = [type_1_money, type_2_option, type_3_structure, type_4_transport, type_5_nature, type_6_emotion, type_7_business, type_8_student]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..', '..', 'secret.json')

    # 비밀 정보 읽기 (API 키 등)
    with open(secret_file) as f:
        secrets = json.loads(f.read())

    # OpenAI 클라이언트 초기화
    client = openai.OpenAI(api_key=get_secret('OPENAI_API_KEY', secrets), timeout=30, max_retries=1)
    
    #MySQL 데이터베이스에 연결
    password = get_secret('MySQL_PASSWORD',secrets)
    conn = pymysql.connect(host='localhost', user='root', password=password, db='room_lists', charset='utf8mb4')

    # 사용자 유형에 대한 임베딩 생성
    characteristic_embeddings = [get_user_input_embedding(user_type, client) for user_type in user_type_list]
    
    # DB 태그들에 대해 임베딩 값 업데이트 및 DB에 있는 태그 임베딩 값과 사용자 유형 설명 임베딩 값에 대해 유사도 분석
    assign_tag_from_db(characteristic_embeddings, client)