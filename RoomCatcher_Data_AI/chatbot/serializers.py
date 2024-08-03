from rest_framework import serializers

class ChatRequestSerializer(serializers.Serializer):
    request_message = serializers.CharField(required=True)