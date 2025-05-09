# Dockerfile
FROM python:3.10

# 환경 변수 설정 (캐시 X, 콘솔 버퍼링 제거)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 작업 디렉토리 생성
WORKDIR /app

# requirements 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 서버 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
