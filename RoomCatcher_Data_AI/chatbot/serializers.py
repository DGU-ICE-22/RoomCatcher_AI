from rest_framework import serializers

class ChatRequestSerializer(serializers.Serializer):
    request_message = serializers.CharField(required=False, allow_blank=True)
    user_name = serializers.CharField(required=False)