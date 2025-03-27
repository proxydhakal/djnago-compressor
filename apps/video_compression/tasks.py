import os
import subprocess
from celery import shared_task
from django.conf import settings
import redis

@shared_task(bind=True)  # Add bind=True here
def compress_video(self, input_filename):
    # Connect to Redis
    redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    # Initialize task_id early to avoid UnboundLocalError
    task_id = None
    try:
        # Assign task_id using self.request.id
        task_id = self.request.id

        # Log the task ID
        print(f"Task ID: {task_id}")

        # Set the task status to PROCESSING
        redis_client.set(task_id, "PROCESSING")
        print(f"Processing video: {input_filename}")

        # Define input and output paths
        input_path = os.path.join(settings.MEDIA_ROOT, "uploads", input_filename)
        output_filename = f"compressed_{input_filename}"
        output_path = os.path.join(settings.MEDIA_ROOT, "compressed", output_filename)

        # Verify input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Ensure the compression directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Compress the video using ffmpeg
        command = [
            "ffmpeg",
            "-i", input_path,           # Input file
            "-vcodec", "h264",          # Use H.264 video codec
            "-acodec", "mp2",           # Use MP2 audio codec
            output_path                 # Output file path
        ]

        # Run the FFmpeg command
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Log FFmpeg output for debugging
        print(f"FFmpeg stdout: {result.stdout.decode()}")
        print(f"FFmpeg stderr: {result.stderr.decode()}")

        # Update the task status to COMPLETED and store the output filename
        redis_client.set(task_id, "COMPLETED")
        redis_client.set(f"completed:{task_id}", output_filename)
        print(f"Compression completed: {output_path}")

        return output_filename

    except Exception as e:
        # Handle all exceptions gracefully
        error_message = f"Error: {str(e)}"
        print(error_message)
        if task_id:
            redis_client.set(task_id, f"FAILED: {error_message}")
        return None