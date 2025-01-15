# Use a slim Python base image
FROM python:3-slim

EXPOSE 8000

# Prevent Python from generating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Turn off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install Ghostscript for PDF compression
RUN apt-get update && \
    apt-get install -y ghostscript && \
    rm -rf /var/lib/apt/lists/*

# Install pip requirements
COPY requirements.txt . 
RUN python -m pip install -r requirements.txt

# Set the working directory to /app
WORKDIR /app

# Copy the application code to the container
COPY . /app

# Ensure the media directory is created and accessible
RUN mkdir -p /app/media/input /app/media/output && \
    chmod -R 775 /app/media

# Command to run the app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "compressor.wsgi"]
