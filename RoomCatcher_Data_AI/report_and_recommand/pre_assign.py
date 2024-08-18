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
from calculate_similarity_userType_and_tag import get_user_input_embedding, get_secret

def calculate_similarity(embedding1, embedding2):
    # 두 임베딩 간의 유사도를 계산하는 함수
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

def ensure_same_dimension(embedding, target_dim):
    # 임베딩의 차원이 target_dim과 다르면, 차원을 맞추는 함수
    current_dim = embedding.shape[0]
    if current_dim > target_dim:
        # 차원이 큰 경우 차원 축소 (앞에서 자름)
        return embedding[:target_dim]
    elif current_dim < target_dim:
        # 차원이 작은 경우 차원 확장 (0으로 패딩)
        return np.pad(embedding, (0, target_dim - current_dim), 'constant')
    return embedding

def assign_tag_from_db(user_type_list_embedding, client, conn, clear=False):
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW COLUMNS FROM dataAnalyze_tag_detail")
        columns = [info[0] for info in cursor.fetchall()]
        
        if 'embedding' not in columns:
            cursor.execute("SELECT id, tagName FROM dataAnalyze_tag_detail")
            tag_list = cursor.fetchall()

            cursor.execute("ALTER TABLE dataAnalyze_tag_detail ADD COLUMN embedding BLOB")

            for tag_id, tagName in tag_list:
                embedding = get_user_input_embedding(tagName, client)
                embedding_blob = np.array(embedding).tobytes()
                cursor.execute("UPDATE dataAnalyze_tag_detail SET embedding = %s WHERE id = %s", (embedding_blob, tag_id))
        else:
            cursor.execute("SELECT id, tagName, embedding FROM dataAnalyze_tag_detail")
            tag_list = cursor.fetchall()

            for tag_id, tagName, embedding in tag_list:
                if embedding is None:
                    embedding = get_user_input_embedding(tagName, client)
                    embedding_blob = np.array(embedding).tobytes()
                    cursor.execute("UPDATE dataAnalyze_tag_detail SET embedding = %s WHERE id = %s", (embedding_blob, tag_id))

        conn.commit()
        
        cursor.execute("SELECT id, tagName, embedding FROM dataAnalyze_tag_detail")
        tag_embeddings = {tagName: np.frombuffer(embedding, dtype=np.float32) for _, tagName, embedding in cursor.fetchall()}

        # User type embedding dimension (assuming all user type embeddings have the same dimension)
        user_type_dim = user_type_list_embedding[0].shape[0]

        # Adjust all tag embeddings to have the same dimension as user type embeddings
        tag_embeddings = {tag: ensure_same_dimension(embedding, user_type_dim) for tag, embedding in tag_embeddings.items()}
        
        sorted_tags = sorted(tag_embeddings.keys(), 
                             key=lambda tag: 
                                 cosine_similarity(tag_embeddings[tag].reshape(1, -1),
                                                   user_type_list_embedding[0].reshape(1, -1)).flatten()[0],
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