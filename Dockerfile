# Base image
FROM python:3-slim
# Define environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
# Set working directory
WORKDIR /app
# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg
# Copy requirements and install python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# Copy application
COPY . .
# Run the bot
CMD ["python", "-u", "app.py"]