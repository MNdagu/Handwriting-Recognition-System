from django.db import models
from django.utils import timezone

class HandwrittenText(models.Model):
    image = models.ImageField(upload_to='handwritten_images/')
    extracted_text = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ])

    def __str__(self):
        return f"Handwritten Text {self.id} - {self.created_at}"
