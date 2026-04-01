# Force rebuild v2
# Use Python 3.11
FROM python:3.11-slim

WORKDIR /app

# Copy ALL files (easier than listing them one by one)
COPY . .

# Install EVERYTHING needed
RUN pip install fastapi uvicorn pydantic requests google-genai gradio

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860", "python", "app.py"]