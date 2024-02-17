FROM python:3.10-slim
WORKDIR /app
# Установка зависимостей без копирования в образ
RUN --mount=type=bind,source=./requirements.txt,target=/app/requirements.txt \
    pip3 install --upgrade setuptools && \
    pip3 install -r requirements.txt
COPY . .
CMD ["python", "main.py"]