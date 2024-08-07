from django.shortcuts import render
import requests, json, os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from .characters import system_role, instruction
from chatbot.chatbot import Chatbot
from .common import model
from .serializers import ChatRequestSerializer

@method_decorator(csrf_exempt, name='dispatch')
class ChatApiView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = JSONParser().parse(request)  
            serializer = ChatRequestSerializer(data=data)
            if serializer.is_valid():
                result = serializer.save()
                response_message = result['response_message']
                chatbot_data = result['chatbot']
                
                auth_info = request.META.get('HTTP_AUTHORIZATION', None)
                if not auth_info:
                    return JsonResponse({'error': 'Auth information is missing'}, status=400)
                
                session_key = f'chatbot_{auth_info}'
                
                if chatbot_data is None:
                    if session_key in request.session:
                        chatbot = Chatbot.from_dict(request.session[session_key])
                        context = chatbot.get_context()
                        print("check")
                        # 다른 API로 context값을 전송하여 사용자의 성향을 받아옴. 
                        api_url = "http://"
                        response = requests.get(api_url, json=context)
                        if response.status_code != 200:
                            return JsonResponse({'error': 'Failed to get user type'}, status=500)
                        del request.session[session_key]
                else:
                    chatbot = Chatbot.from_dict(chatbot_data)
                    
                if 'request_message' in result:
                    chatbot.add_user_message(result['request_message'])
                    response = chatbot.send_request()
                    chatbot.add_response(response)
                    response_message = chatbot.get_response_content()
                
                request.session[session_key] = chatbot.to_dict()
                
                return JsonResponse({"response_message": response_message,
                                     "chatbot": chatbot.to_dict()})
            else:
                return JsonResponse(serializer.errors, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)