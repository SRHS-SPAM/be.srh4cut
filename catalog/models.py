from django.db import models
from django.urls import reverse
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import uuid
import os
import win32print
import win32api

class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='photos/')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        qr_exists = bool(self.qr_code.name)
        is_new = self.pk is None
        
        if is_new:
            super().save(*args, **kwargs)

        try:
            qr_url = f'https://srh-photo.onrender.com/api/photos/{self.id}/download/'

            # QR 코드 생성
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            # QR 코드 파일 저장
            filename = f'qr_{self.id}.png'
            self.qr_code.save(filename, File(buffer), save=False)

            # 이미지와 QR 코드 합성
            if self.image and os.path.isfile(self.image.path):
                self.print_image_with_qr(self.image.path, buffer)

            if not is_new:
                super().save(*args, **kwargs)

        except Exception as e:
            print(f"QR 코드 생성 오류: {e}")
            if not is_new:
                super().save(*args, **kwargs)

    def print_image_with_qr(self, image_path, qr_buffer):
        try:
            # 이미지 불러오기
            base_image = Image.open(image_path)

            # QR 코드 이미지 불러오기
            qr_image = Image.open(qr_buffer)

            # QR 코드 크기 조정 (이미지 크기에 맞춰서 크기 변경 가능)
            qr_image = qr_image.resize((100, 100))  # 예시: QR 코드 크기 100x100

            # QR 코드 위치 지정 (이미지 오른쪽 하단)
            base_image.paste(qr_image, (base_image.width - qr_image.width, base_image.height - qr_image.height))

            # 임시 파일에 저장 후 출력
            temp_file_path = "temp_image_with_qr.png"
            base_image.save(temp_file_path)

            # 이미지 출력
            self.print_image(temp_file_path)

        except Exception as e:
            print(f"이미지 및 QR 코드 출력 오류: {e}")

    def print_image(self, filepath):
        try:
            printer_name = win32print.GetDefaultPrinter()
            print(f"사용 중인 프린터: {printer_name}")

            result = win32api.ShellExecute(
                0,
                "print",
                filepath,
                f'/d:"{printer_name}"',
                ".",
                0
            )
            print(f"출력 명령 실행 결과: {result}")

        except Exception as e:
            print(f"출력 오류: {e}")

    def get_absolute_url(self):
        return reverse('photo_detail', args=[str(self.id)])
