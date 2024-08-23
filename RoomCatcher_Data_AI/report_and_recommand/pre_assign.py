import json
import os
import pymysql
import traceback
import openai
from common import connect_db
from transformers import ElectraModel, ElectraTokenizer
import torch, numpy as np 
from sklearn.metrics.pairwise import cosine_similarity
from type_explain import type_1_money, type_2_option, type_3_structure, type_4_transport, type_5_nature, type_6_emotion, type_7_business, type_8_student
from calculate_similarity_userType_and_tag import get_user_input_embedding, get_secret, ensure_same_dimension

def calculate_similarity(embedding1, embedding2):
    # 두 임베딩 간의 유사도를 계산하는 함수
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

def insert_user_type_to_db(user_type_list,conn):
    cursor = conn.cursor()
    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS report_and_recommand_user_type (
            id INT PRIMARY KEY AUTO_INCREMENT,
            typeName VARCHAR(64),
            typeExplain VARCHAR(512),
            embedding BLOB
            )
        ''')
        
        cursor.execute("SELECT COUNT(*) FROM report_and_recommand_user_type")
        row_count = cursor.fetchone()[0]
        
        if row_count == 0:
            for user_type in user_type_list:
                typeName, typeExplain = user_type.split('\n',1)
                embedding = get_user_input_embedding(user_type, client)
                embedding_blob = np.array(embedding).tobytes()
                cursor.execute("INSERT INTO report_and_recommand_user_type (typeName, typeExplain, embedding) VALUES (%s, %s, %s)", 
                               (typeName, typeExplain, embedding_blob))
        
        cursor.execute("SHOW COLUMNS FROM report_and_recommand_user_type")
        columns = [info[0] for info in cursor.fetchall()]

        if 'embedding' not in columns:
            cursor.execute("ALTER TABLE report_and_recommand_user_type ADD COLUMN embedding BLOB")
            for user_type in user_type_list:
                typeName, typeExplain = user_type.split('\n',1)
                embedding = get_user_input_embedding(user_type, client)
                embedding_blob = np.array(embedding).tobytes()
                cursor.execute("UPDATE report_and_recommand_user_type SET embedding = %s WHERE typeName = %s", (embedding_blob, typeName))
        else:
            cursor.execute("SELECT typeExplain, embedding FROM report_and_recommand_user_type")
            user_type_embeddings = {user_type: np.frombuffer(embedding, dtype=np.float32) for user_type, embedding in cursor.fetchall()}
            
            # User type embedding dimension (assuming all user type embeddings have the same dimension)
            typeExplain = user_type.split('\n',1)[1]
            user_type_dim = user_type_embeddings[typeExplain].shape[0]
            
            # Adjust all user type embeddings to have the same dimension
            user_type_embeddings = {user_type: ensure_same_dimension(embedding, user_type_dim) for user_type, embedding in user_type_embeddings.items()}
            
            for user_type in user_type_list:
                typeName, typeExplain = user_type.split('\n',1)
                if user_type not in user_type_embeddings:
                    embedding = get_user_input_embedding(user_type, client)
                    embedding_blob = np.array(embedding).tobytes()
                    cursor.execute("UPDATE report_and_recommand_user_type SET embedding = %s WHERE typeName = %s", (embedding_blob, typeName))
        
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

# 테이블 데이터에 embedding이 없는 경우, embedding을 계산하여 업데이트
def assign_tag_from_db(user_type_list_embedding, client, conn, clear=False):
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW COLUMNS FROM data_analyze_tag_detail")
        columns = [info[0] for info in cursor.fetchall()]
        
        if 'embedding' not in columns:
            cursor.execute("SELECT id, tagName FROM data_analyze_tag_detail")
            tag_list = cursor.fetchall()

            cursor.execute("ALTER TABLE data_analyze_tag_detail ADD COLUMN embedding BLOB")

            for tag_id, tagName in tag_list:
                embedding = get_user_input_embedding(tagName, client)
                embedding_blob = np.array(embedding).tobytes()
                cursor.execute("UPDATE data_analyze_tag_detail SET embedding = %s WHERE id = %s", (embedding_blob, tag_id))
        else:
            cursor.execute("SELECT id, tagName, embedding FROM data_analyze_tag_detail")
            tag_list = cursor.fetchall()

            for tag_id, tagName, embedding in tag_list:
                if embedding is None:
                    embedding = get_user_input_embedding(tagName, client)
                    embedding_blob = np.array(embedding).tobytes()
                    cursor.execute("UPDATE data_analyze_tag_detail SET embedding = %s WHERE id = %s", (embedding_blob, tag_id))

        conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        conn.rollback()
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    user_type_list = [type_1_money, type_2_option, type_3_structure, type_4_transport, type_5_nature, type_6_emotion, type_7_business, type_8_student]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secret_file = os.path.join(base_dir, '..', '..', 'secret.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())

    client = openai.OpenAI(api_key=get_secret('OPENAI_API_KEY', secrets), timeout=30, max_retries=1)
    conn = connect_db(secrets)

    characteristic_embeddings = [get_user_input_embedding(user_type, client) for user_type in user_type_list]
    assign_tag_from_db(characteristic_embeddings, client, conn)
    # 사용자 유형을 DB에 저장
    # insert_user_type_to_db(user_type_list, conn)