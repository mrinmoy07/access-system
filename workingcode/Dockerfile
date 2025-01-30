FROM python:3.11-slim

# Install required system dependencies for dlib
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dlib AFTER installing dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir dlib

# Install other Python dependencies
RUN pip install --no-cache-dir \
    djangorestframework \
    pytz \
    Pillow \
    numpy \
    face_recognition \
    requests

# Copy the rest of your Django project
COPY . /app/


CMD ["python3", "manage.py", "runserver", "--noreload", "0.0.0.0:8000"]