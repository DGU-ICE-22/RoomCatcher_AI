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
    model=model.basic,
    system_role=system_role,
    instruction=instruction
)

# Create your views here.
@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            serializer = ChatRequestSerializer(data=data)
            if serializer.is_valid():
                result = serializer.save()
                response_message = result['response_message']
                chatbot_data = result['chatbot']
                request.session['chatbot'] = chatbot_data
                
                chatbot = Chatbot.from_dict(chatbot_data)
                context = chatbot.get_context()
                
                return JsonResponse({"response_message": response_message,
                                     "chatbot": chatbot.to_dict(),
                                     "context": context})
            else:
                return JsonResponse(serializer.errors, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)
