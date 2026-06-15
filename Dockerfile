# Use a lightweight, official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for compilation and networking tools cleanly
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container first to optimize build caching
COPY requirements.txt .

# Install the Python dependencies cleanly without storing a local cache directory
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code into the workspace
COPY . .

# Instruct the container execution sequence to launch your primary bot thread
CMD ["python", "bot.py"]
