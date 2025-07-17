FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

CMD ["gunicorn", "--bind", "0.0.0.0:5555", "--workers", "4", "--threads", "2", "app:create_app()"]