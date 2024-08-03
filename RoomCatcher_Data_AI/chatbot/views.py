from email.mime import application
from django.shortcuts import render
import requests, json, os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from characters import system_role, instruction
from chatbot.chatbot import Chatbot
from common import model

chatbot = Chatbot(
    model = model.basic,
    system_role = system_role,
    instruction = instruction
)

# Create your views here.
@csrf_exempt
def chat_api_v1(request):
    if request.method == 'POST':
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
       
@csrf_exempt
def chat_api_v2(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('user_input')
            if not user_input:
                return JsonResponse({'error': 'user_input is required'}, status=400)
            
            chatbot.add_user_message(user_input)
            response = chatbot.send_request()
            chatbot.add_response(response)
            response_message = chatbot.get_response_content()
            chatbot.clean_context()
            
            return JsonResponse({'response_message': response_message})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)