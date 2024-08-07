from django.urls import path
from .views import ChatApiView

urlpatterns = [
    path('chat/', ChatApiView.as_view(), name='chat_api'),
]