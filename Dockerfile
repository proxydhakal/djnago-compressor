# Base builder stage for dependencies
FROM python:3.12-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ghostscript \
    postgresql-client \
    libreoffice \
    libreoffice-script-provider-python \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install Python dependencies
RUN python -m pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final runtime stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    ghostscript \
    postgresql-client \
    libreoffice \
    libreoffice-script-provider-python \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create a user to manage static files
RUN useradd -m static_user

# Set working directory
WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /install /usr/local

# Copy application files
COPY . .

# Copy the entrypoint script and set permissions
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Ensure proper permissions for static/media
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R static_user:static_user /app/staticfiles /app/media

# Expose application port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
