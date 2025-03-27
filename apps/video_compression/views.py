from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.conf import settings
import os
import redis
from .tasks import compress_video

# Connect to Redis
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

class VideoCompressionView(View):
    template_name = "public/video_compression.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if "video_file" not in request.FILES:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        video = request.FILES["video_file"]
        input_path = os.path.join(settings.MEDIA_ROOT, "uploads", video.name)

        try:
            # Ensure the uploads directory exists
            os.makedirs(os.path.dirname(input_path), exist_ok=True)

            # Save the uploaded file
            with open(input_path, "wb+") as destination:
                for chunk in video.chunks():
                    destination.write(chunk)

            # Start the compression task
            task = compress_video.apply_async(args=[video.name])

            # Set the task status in Redis
            redis_client.set(task.id, "PROCESSING", ex=3600)

            return JsonResponse({"task_id": task.id, "message": "Compression started!"})

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)




class CheckTaskStatus(View):
    def get(self, request, task_id):
        task_status = redis_client.get(task_id)
        if not task_status:
            return JsonResponse({"task_status": "EXPIRED"}, status=404)
        return JsonResponse({"task_status": task_status})

class GetCompressedVideo(View):
    def get(self, request, task_id):
        output_filename = redis_client.get(f"completed:{task_id}")
        if not output_filename:
            return JsonResponse({"error": "File not ready"}, status=404)

        output_path = os.path.join(settings.MEDIA_ROOT, "compressed", output_filename)
        if not os.path.exists(output_path):
            return JsonResponse({"error": "File not found"}, status=404)

        return JsonResponse({"download_url": f"/media/compressed/{output_filename}"})

