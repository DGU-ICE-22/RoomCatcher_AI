from email.mime import application
from django.shortcuts import render
import requests
from characters import system_role, instruction
from chatbot.chatbot import Chatbot
from common import model

chatbot = Chatbot(
    model = model.basic,
    system_role = system_role,
    instruction = instruction
)

# Create your views here.
@application.route('/chat-api', methods = ["POST"])
def chat_api():
    request_message = requests.json['request_message']
    print("request_message: ", request_message)
    chatbot.add_user_message(request_message)
    response = chatbot.send_request()
    chatbot.add_response(response)
    response_message = chatbot.get_response_content()
    chatbot.clean_context()
    print("response_message: ", response_message)
    return {"response_message": response_message}

@application.route('/chat-api', methods=['POST'])
def chat_api():
    request_message = requests.json['request_message']
    print("request_message:", request_message)
    chatbot.add_user_message(request_message)
    response = chatbot.send_request()
    chatbot.add_response(response)
    response_message = chatbot.get_response_content()
    chatbot.handle_token_limit(response)
    chatbot.clean_context()
    print("response_message: ", response_message) 
    return {"response_message":response_message}   