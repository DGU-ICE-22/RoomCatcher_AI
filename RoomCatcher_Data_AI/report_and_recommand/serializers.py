from rest_framework import serializers
from .models import DataAnalyzeTagDetail, ReportAndRecommandUserType, UserTagCrossTable

class DataAnalyzeTagDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataAnalyzeTagDetail
        fields = '__all__'

class ReportAndRecommandUserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAndRecommandUserType
        fields = '__all__'
        
class UserTagCrossTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTagCrossTable
        fields = '__all__'