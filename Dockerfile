# Base image: Python ka slim version use karein taaki size kam rahe
FROM python:3.11-slim

# Working directory set karein
WORKDIR /app

# System dependencies (agar kabhi zaroorat pade)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Requirements file copy karein aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baaki saara project files copy karein
COPY . .

# Bot run karne ki command
CMD ["python", "bot.py"]
