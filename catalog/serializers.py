# serializers.py
from rest_framework import serializers
from catalog.models import Photo

class PhotoSerializer(serializers.ModelSerializer):
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Photo
        fields = ['id', 'title', 'image', 'qr_code', 'qr_code_url', 'created_at']
        
    def get_qr_code_url(self, obj):
        if obj.qr_code:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code.url)
        return None
    
    def create(self, validated_data):
        # 파일 업로드를 처리하는 코드 추가
        return Photo.objects.create(**validated_data)