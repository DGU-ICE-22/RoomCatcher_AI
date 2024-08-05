from email.mime import application
from django.shortcuts import render
import requests, json, os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .characters import system_role, instruction
from chatbot.chatbot import Chatbot
from .common import model
from .serializers import ChatRequestSerializer
from rest_framework.parsers import JSONParser


chatbot = Chatbot(
    model = model.basic,
    system_role = system_role,
    instruction = instruction
)

# Create your views here.
@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            serializer = ChatRequestSerializer(data=data)
            if serializer.is_valid():
                request_message = serializer.validated_data['request_message']
                chatbot.add_user_message(request_message)
                response = chatbot.send_request()
                chatbot.add_response(response)
                response_message = chatbot.get_response_content()
                chatbot.handle_token_limit(response)
                chatbot.clean_context()
                print(chatbot.context[1:])
                return JsonResponse({"response_message": response_message})
            else:
                return JsonResponse(serializer.errors, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)
