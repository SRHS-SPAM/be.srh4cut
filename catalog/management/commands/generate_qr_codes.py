# management/commands/generate_qrcodes.py
from django.core.management.base import BaseCommand
from catalog.models import Photo
from django.urls import reverse
from io import BytesIO
from django.core.files import File
import qrcode
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '모든 사진에 대한 QR 코드 생성'
    
    def handle(self, *args, **options):
        photos = Photo.objects.all()
        created_count = 0
        error_count = 0
        
        self.stdout.write(f"총 {photos.count()}개 사진에 대한 QR 코드 생성 시작")
        
        for photo in photos:
            try:
                # QR 코드가 없는 경우에만 생성
                if not photo.qr_code:
                    # QR 코드에 저장할 URL 생성(배포 후에 이부분 변경)
                    qr_url = 'https://srh-photo.onrender.com/' + reverse('photo_detail', args=[str(photo.id)])
                    
                    # QR 코드 생성
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(qr_url)
                    qr.make(fit=True)
                    
                    # QR 코드 이미지 생성
                    img = qr.make_image(fill_color="black", back_color="white")
                    
                    # BytesIO를 사용하여 메모리에 저장
                    buffer = BytesIO()
                    img.save(buffer, format='PNG')
                    buffer.seek(0)
                    
                    # 파일명 생성
                    filename = f'qr_{photo.id}.png'
                    
                    # QR 코드 저장
                    photo.qr_code.save(filename, File(buffer), save=True)
                    created_count += 1
                    self.stdout.write(f"사진 {photo.id}의 QR 코드 생성 완료")
                else:
                    self.stdout.write(f"사진 {photo.id}는 이미 QR 코드가 있습니다")
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"사진 {photo.id} QR 코드 생성 오류: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"총 {created_count}개 QR 코드 생성 완료, {error_count}개 오류 발생"))