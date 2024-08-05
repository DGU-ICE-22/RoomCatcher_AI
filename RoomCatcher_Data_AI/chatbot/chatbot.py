from .common import client, model, makeup_response
from .characters import system_role, instruction
from pprint import pprint
import math

class Chatbot:
    
    def __init__(self, model, system_role, instruction):
        self.context = [{"role":"system","content":system_role}]
        self.model = model
        self.system_role = system_role
        self.instruction = instruction
        self.max_token_size = 16 * 1024
        self.available_token_rate = 0.9
        
    def to_dict(self):
        return {
            "model": self.model,
            "system_role": self.system_role,
            "instruction": self.instruction,
            "context": self.context
        }
        
    def get_context(self):
        return self.context  # context를 반환
    
    @classmethod
    def from_dict(cls, data):
        chatbot = cls(data["model"], data["system_role"], data["instruction"])
        chatbot.context = data["context"]
        return chatbot
    
    def handle_token_limit(self, response):
        try:
            current_usage_rate = response['usage']['total_tokens'] / self.max_token_size
            exceeded_token_rate = current_usage_rate - self.available_token_rate
            if exceeded_token_rate > 0:
                remove_size = math.ceil(len(self.context) / 10)
                self.context = [self.context[0]] + self.context[remove_size+1:]
        except Exception as e:
            print(f"handle_token_limit exception: {e}")
            
    def add_user_message(self, message):
        self.context.append({"role":"user","content":message})
        
    def _send_request(self):
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=self.context,
                temperature=0.68,
                max_tokens=400,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            ).model_dump()
        except Exception as e:
            print(f"Failed to send request: {e}")
            if 'maximum context length' in str(e):
                self.context.pop()
                return makeup_response("메세지가 너무 길어요... 다시 입력해주세요.")
            else:
                return makeup_response("죄송해요, 채팅에 문제가 생겼어요. 잠시 후 다시 시도해주세요.")
        return response
    
    def send_request(self):
        self.context[-1]['content']+=self.instruction
        return self._send_request()
    
    def add_response(self, response):
        self.context.append({
            "role": response['choices'][0]['message']["role"],
            "content":response['choices'][0]['message']["content"]
        })
    
    def reset_context(self):
        self.context = [{"role":"system","content":system_role}]
    
    def get_response_content(self):
        return self.context[-1]["content"]
    
    def clean_context(self):
        for idx in reversed(range(len(self.context))):
            if self.context[idx]["role"] == "user":
                self.context[idx]["content"] = self.context[idx]["content"].split("instruction")[0].strip()
                break
        
if __name__=="__main__":
    chatbot = Chatbot(model.basic, system_role, instruction)
    chatbot.add_user_message("안녕하세요")
    response = chatbot.send_request()
    chatbot.add_response(response)
    pprint(chatbot.context[2]['content'])
 