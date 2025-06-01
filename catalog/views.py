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
from django.views.decorators.csrf import ensure_csrf_cookie

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
    
    # QR 코드 파일이 생성되었는지 확인하고 반환
    if photo.qr_code and os.path.exists(photo.qr_code.path):
        try:
            # QR 코드 이미지를 직접 FileResponse로 반환
            response = FileResponse(
                open(photo.qr_code.path, 'rb'),
                content_type='image/png',
                filename=f'qr_code_{photo.id}.png'
            )
            
            # 응답 헤더에 추가 정보 포함
            response['X-Photo-ID'] = str(photo.id)
            response['X-Photo-Title'] = photo.title
            response['X-Download-URL'] = f"/api/photos/{photo.id}/download/"
            
            logger.info(f"QR 코드 반환 성공: {photo.qr_code.path}")
            return response
            
        except Exception as e:
            logger.error(f"QR 코드 파일 반환 오류: {e}")
            return Response({"error": "QR 코드를 반환할 수 없습니다"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.error("QR 코드가 생성되지 않았습니다")
        return Response({"error": "QR 코드가 생성되지 않았습니다"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        try:
            photo = self.get_object()
            
            if not photo.image:
                return Response({"error": "이미지 파일이 없습니다"}, status=status.HTTP_404_NOT_FOUND)
            
            file_path = photo.image.path
            
            if os.path.exists(file_path):
                response = FileResponse(
                    open(file_path, 'rb'), 
                    as_attachment=True,
                    filename=f"{photo.title}_{photo.id}.jpg"
                )
                return response
            else:
                return Response({"error": "파일을 찾을 수 없습니다"}, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({"error": f"다운로드 오류: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
@ensure_csrf_cookie
def get_csrf(request):
    return JsonResponse({
        'message': 'CSRF cookie set',
        'csrf_token': request.META.get('CSRF_COOKIE')
    })