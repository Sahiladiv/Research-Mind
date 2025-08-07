from django.db import models

class UploadedPaper(models.Model):
    paper_id = models.CharField(max_length=100, unique=True)
    s3_url = models.URLField()
    original_filename = models.CharField(max_length=255)
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_filename
