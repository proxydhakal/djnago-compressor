from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from apps.compressor_app.models import FileCompressLog
from django.db import models
import json
from django.utils import timezone

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    login_url = '/'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        
        total_compressed_files = FileCompressLog.objects.count()

        total_original_size = FileCompressLog.objects.aggregate(
            total_original_size=models.Sum('original_size')
        )['total_original_size'] or 0 
        total_original_size_mb = total_original_size / (1024 * 1024)  

        total_compressed_size = FileCompressLog.objects.aggregate(
            total_compressed_size=models.Sum('compressed_size')
        )['total_compressed_size'] or 0  
        total_compressed_size_mb = total_compressed_size / (1024 * 1024)  
        compressed_files_by_type = FileCompressLog.objects.values('file_type').annotate(
            count=models.Count('id')
        ).order_by('-count')  

        context['compressed_files_by_type'] = json.dumps(list(compressed_files_by_type))
        compressed_files_by_type_list = list(FileCompressLog.objects.values('file_type').annotate(count=models.Count('id')).order_by('-count'))
        context['compressed_files_by_type_list'] = compressed_files_by_type_list
        context['total_compressed_files'] = total_compressed_files
        context['total_original_size_mb'] = total_original_size_mb
        context['total_compressed_size_mb'] = total_compressed_size_mb
        current_datetime = timezone.now()
        context['current_datetime'] = current_datetime

        return context


class FileCompressLogList(ListView):
    model = FileCompressLog
    context_object_name = 'logs'
    template_name='dashboard/compresslogs/view.html'