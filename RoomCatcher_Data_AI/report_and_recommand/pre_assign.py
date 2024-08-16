# 사용자 유형마다 가질 수 있는 태그들을 할당해주어야 함. 
import json
import os
import sqlite3
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

def assign_tag_from_db(user_type_list_embedding, client, clear=False):
    # openai를 사용한 유사도 계산
    conn = sqlite3.connect('room_lists.db')

    try:
        # 데이터베이스 연결
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(dataAnalyze_tag_detail)")
        columns = [info[1] for info in cursor.fetchall()]
        
        # 각 tagName에 대한 임베딩 계산 및 업데이트
        # 전체 태그에 대해 임베딩을 계산하고 데이터베이스에 업데이트
        if 'embedding' not in columns:
        # 데이터베이스에서 유저 유형과 태그 정보 가져오기
            cursor.execute("SELECT id, tagName FROM dataAnalyze_tag_detail")
            tag_list = cursor.fetchall()
            for tag_id, tagName in tag_list:
                embedding = get_user_input_embedding(tagName, client)
                embedding_blob = sqlite3.Binary(np.array(embedding).tobytes())
                cursor.execute("UPDATE dataAnalyze_tag_detail SET embedding = ? WHERE id = ?", (embedding_blob, tag_id))
        else:
        # 비어있는 태그에 대해 임베딩 계산 및 업데이트
                # 데이터베이스에서 유저 유형과 태그 정보 가져오기
            cursor.execute("SELECT id, tagName, embedding FROM dataAnalyze_tag_detail")
            tag_list = cursor.fetchall()
            for tag_id, tagName, embedding in tag_list:
                if embedding is None:
                    embedding = get_user_input_embedding(tagName, client)
                    embedding_blob = sqlite3.Binary(np.array(embedding).tobytes())
                    cursor.execute("UPDATE dataAnalyze_tag_detail SET embedding = ? WHERE id = ?", (embedding_blob, tag_id))
        # 변경사항 커밋
        conn.commit()
        
        cursor.execute("SELECT id, tagName, embedding FROM dataAnalyze_tag_detail")
        tag_embeddings = {tagName: np.frombuffer(embedding, dtype=np.float32) for _, tagName, embedding in cursor.fetchall()}
        sorted_tags = sorted(tag_embeddings.keys(), 
                             key=lambda tag: 
                                 cosine_similarity(tag_embeddings[tag].reshape(-1, 1),
                                user_type_list_embedding[1].reshape(-1, 1))[0][0],
                             reverse=True)
        print(sorted_tags[:int(len(sorted_tags)/8)])
        return (sorted_tags[:int(len(sorted_tags)/8)])
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        conn.rollback()
        return None
    finally:
        conn.close()
    # KoELECTRA를 사용한 유사도 계산
    # try:
    #     # 데이터베이스 연결
    #     conn = sqlite3.connect('room_lists.db')
    #     cursor = conn.cursor()
        
    #     cursor.execute("PRAGMA table_info(dataAnalyze_tag_detail)")
    #     columns = [info[1] for info in cursor.fetchall()]
        
    #     # 각 tagName에 대한 임베딩 계산 및 업데이트
    #     # 전체 태그에 대해 임베딩을 계산하고 데이터베이스에 업데이트
    #     if 'embedding' not in columns or clear == True:
    #         # 데이터베이스에서 유저 유형과 태그 정보 가져오기
    #         cursor.execute("SELECT id, tagName FROM dataAnalyze_tag_detail")
    #         tag_list = cursor.fetchall()
    #         cursor.execute("ALTER TABLE dataAnalyze_tag_detail ADD COLUMN embedding BLOB")
    #         for tag_id, tagName in tag_list:
    #             embedding = get_embedding(tagName)
    #             embedding_blob = sqlite3.Binary(np.array(embedding).tobytes())
    #             cursor.execute("UPDATE dataAnalyze_tag_detail SET embedding = ? WHERE id = ?", (embedding_blob, tag_id))
    #     else:
    #     # 비어있는 태그에 대해 임베딩 계산 및 업데이트
    #             # 데이터베이스에서 유저 유형과 태그 정보 가져오기
    #         cursor.execute("SELECT id, tagName, embedding FROM dataAnalyze_tag_detail")
    #         tag_list = cursor.fetchall()
    #         for tag_id, tagName, embedding in tag_list:
    #             if embedding is None:
    #                 embedding = get_embedding(tagName)
    #                 embedding_blob = sqlite3.Binary(np.array(embedding).tobytes())
    #                 cursor.execute("UPDATE dataAnalyze_tag_detail SET embedding = ? WHERE id = ?", (embedding_blob, tag_id))
    #     # 변경사항 커밋
    #     conn.commit()
        
    #     cursor.execute("SELECT id, tagName, embedding FROM dataAnalyze_tag_detail")
    #     tag_embeddings = {tagName: np.frombuffer(embedding, dtype=np.float32) for _, tagName, embedding in cursor.fetchall()}
    #     conn.close()

    #     sorted_tags = sorted(tag_embeddings.keys(), key=lambda tag: calculate_similarity(tag_embeddings[tag], user_type_list_embedding[3]), reverse=True)
    #     print(sorted_tags[:int(len(sorted_tags)/8)])
    #     return (sorted_tags[:int(len(sorted_tags)/8)])
    # except Exception as e:
    #     print(f"Error: {e}")
    #     traceback.print_exc()
    #     return None
    
 
if __name__ == "__main__":
    user_type_list = [type_1_money, type_2_option, type_3_structure, type_4_transport, type_5_nature, type_6_emotion, type_7_business, type_8_student]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..', '..', 'secret.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())

    client = openai.OpenAI(api_key=get_secret('OPENAI_API_KEY', secrets), timeout=30, max_retries=1)
    characteristic_embeddings = [get_user_input_embedding(user_type, client) for user_type in user_type_list]
    #DB에 있는 태그들과 사용자 유형 설명에 대해 유사도 분석 및 DB 태그들에 대해 embedding 값 업데이트
    assign_tag_from_db(characteristic_embeddings, client)