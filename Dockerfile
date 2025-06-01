# Python 3.12 베이스 이미지 사용
FROM python:3.12-slim

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV DOCKER_ENV=1

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사 및 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 복사
COPY . .

# 미디어 및 정적 파일 디렉토리 생성
RUN mkdir -p media staticfiles

# 데이터베이스 마이그레이션
RUN python manage.py migrate

# 정적 파일 수집
RUN python manage.py collectstatic --noinput

# 포트 노출
EXPOSE 8000

# 개발 서버 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]