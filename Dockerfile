FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir fastapi uvicorn requests google-genai gradio openai
# Set path so "from tasks import TASKS" works inside server/app.py
ENV PYTHONPATH=/app/server:/app
EXPOSE 7860
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]