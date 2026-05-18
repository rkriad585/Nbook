FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 52896

ENV FLASK_ENV=production
ENV NBOOK_PORT=52896

CMD ["python", "app.py", "free"]
