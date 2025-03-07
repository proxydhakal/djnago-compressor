import os
import subprocess
from celery import shared_task
from django.conf import settings

@shared_task
def compress_video(input_filename):
    print('Hello')
    import redis
    redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    input_path = os.path.join(settings.MEDIA_ROOT, "uploads", input_filename)
    output_filename = f"compressed_{input_filename}"
    output_path = os.path.join(settings.MEDIA_ROOT, "compressed", output_filename)

    try:
        # Use the task ID from self.request.id
        task_id = self.request.id
        print('******Task ID******************')
        print(task_id)
        print('************************')
        redis_client.set(task_id, "PROCESSING")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Compress the video using ffmpeg
        command = [
            "ffmpeg",
            "-i", input_path,
            "-vcodec", "libx265",
            "-crf", "28",  # Adjust this for desired compression (higher = more compression)
            "-b:v", "1000k",  # Optional: Set a target bitrate (in this case, ~1000k)
            "-preset", "fast",  # Optional: Adjust encoding speed/quality balance
            output_path
        ]

        subprocess.run(command, check=True)

        # Update the task status to COMPLETED and store the output filename
        redis_client.set(task_id, "COMPLETED")
        redis_client.set(f"completed:{task_id}", output_filename)

        return output_filename

    except Exception as e:
        # Update the task status to FAILED if an error occurs
        redis_client.set(task_id, f"FAILED: {str(e)}")
        return None




