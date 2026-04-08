FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn requests openai gradio python-multipart

ENV PYTHONPATH=/app/server:/app
ENV PYTHONUNBUFFERED=1

EXPOSE 7860

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]