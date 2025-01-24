from django.db import models
from django.utils.timezone import now

# Create your models here.

class AIChat(models.Model):
    response_id = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(default=now)
    model = models.CharField(max_length=255, null=True)
    user_question = models.TextField(null=True)
    content = models.TextField(null=True)
    total_tokens = models.CharField(null=True, default=256, max_length=255)
    session_id = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=50, null=True) 
    user_id = models.CharField(max_length=255, null=True)
    def __str__(self):
        return self.response_id
