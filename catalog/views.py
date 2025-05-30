from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse, JsonResponse
from .models import Photo
from .forms import PhotoForm
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from .serializers import PhotoSerializer
import os
from datetime import datetime
from rest_framework.parsers import MultiPartParser, FormParser
import logging

logger = logging.getLogger(__name__)

# 기존 뷰 유지
def photo_list(request):
    photos = Photo.objects.all().order_by('-created_at')
    return render(request, 'photos/photo_list.html', {'photos': photos})

def photo_detail(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    return render(request, 'photos/photo_detail.html', {'photo': photo})

def photo_create(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save()
            return redirect('photo_detail', pk=photo.id)
    else:
        form = PhotoForm()
    return render(request, 'photos/photo_form.html', {'form': form})

# React와 통신하기 위한 API 뷰 추가
@api_view(['POST'])
def upload_photo(request):
    logger.info("파일 업로드 요청 받음")
    logger.debug(f"Request data: {request.data}")
    logger.debug(f"Request FILES: {request.FILES}")
    
    serializer = PhotoSerializer(data=request.data)
    if not serializer.is_valid():
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    photo = serializer.save()
    logger.info("사진 업로드 성공")
    return Response({'message': '업로드 및 출력 완료'}, status=status.HTTP_201_CREATED)

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all().order_by('-created_at')
    serializer_class = PhotoSerializer
    parser_classes = (MultiPartParser, FormParser)  # 파일 업로드 지원

    def create(self, request, *args, **kwargs):
        logger.info("PhotoViewSet - 파일 업로드 요청 받음")
        logger.debug(f"Request data: {request.data}")
        logger.debug(f"Request FILES: {request.FILES}")

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        logger.info("사진 업로드 성공")
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        photo = self.get_object()
        file_path = photo.image.path
        
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'))
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
        
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)

# 날짜 보내주는 API
def get_current_date(request):
    current_date = datetime.now().strftime('%Y-%m-%d')
    return JsonResponse({'current_date': current_date})

def some_endpoint(request):
    data = {'message': 'Hello from Django!'}
    return JsonResponse(data)

#이미지 자동 출력
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Photo

# 그리고 Django에서 /api/get-csrf/ 라우트를 만들어서 CSRF 쿠키를 강제로 설정
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

@ensure_csrf_cookie
def get_csrf(request):
    return JsonResponse({'message': 'CSRF cookie set'})