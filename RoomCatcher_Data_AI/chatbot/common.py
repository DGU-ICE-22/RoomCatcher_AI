import os, json, sqlite3
from openai import OpenAI
from dataclasses import dataclass
from django.core.exceptions import ImproperlyConfigured


@dataclass(frozen=True)
class Model:
    basic: str = "gpt-4o-mini"

model = Model()

def get_secret(setting, secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)
    
def makeup_response(message, finish_reason = "ERROR"):
    return {
        "choices": [
            {
                "finish_reason": finish_reason,
                "index": 0, 
                "message" : {
                    "role" : "assistant",
                    "content" : message
                }
            }
        ],
        "usage":{"total_tokens":0},
    }

base_dir = os.path.dirname(os.path.abspath(__file__))
secret_file = os.path.join(base_dir, '..', '..', 'secret.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())
    
# 데이터베이스 연결 설정
db_path = os.path.join(base_dir, '..', 'room_lists.db')

def get_db_connection():
    return sqlite3.connect(db_path)
    
# 헤더 설정
api_key = get_secret('OPENAI_API_KEY', secrets)
client = OpenAI(api_key=api_key, timeout=30, max_retries=1)