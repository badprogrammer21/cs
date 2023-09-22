from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from author.models import Author
from django.shortcuts import redirect
from django.conf import settings
import pytz
from datetime import datetime
from django.utils import timezone
from django.utils import timezone
import uuid

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_anonymous:
            tzname = request.user.timezone
            timezone.activate(tzname)
        else:
            timezone.deactivate()
        return self.get_response(request)

class DiaryPost(models.Model):
    idDiary = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=400, unique=True, blank=True)
    user = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField()    
    date = models.DateTimeField(default=timezone.now())
    day_count = models.IntegerField(default=1)
    plans = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.idDiary)
        super(DiaryPost, self).save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse("diary")