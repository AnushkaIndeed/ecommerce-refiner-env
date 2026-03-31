# Use Python 3.11
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy your files into the container
COPY requirements.txt .
COPY app.py .
COPY tasks.py .

# Install dependencies
RUN pip install fastapi uvicorn pydantic

# Expose the port FastAPI runs on
EXPOSE 8000

# Start the server
CMD ["python", "app.py"]