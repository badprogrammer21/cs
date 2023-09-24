from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django_resized import ResizedImageField
from tinymce.models import HTMLField
from hitcount.models import HitCountMixin, HitCount
from django.contrib.contenttypes.fields import GenericRelation

expire_after = timedelta(seconds=10)
resume_after = timedelta(seconds=30)

class Author(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=0)
    profile_pic = ResizedImageField(size=[50,80], quality=100, upload_to='profile_pictures/', null=True, blank=True)
    bio = models.CharField(max_length=200)
    slug = slug = models.SlugField(max_length=400, unique=True,blank=True)
    hidden = models.BooleanField(default=False)
    hidden_profile = models.BooleanField(default=False)

    objects = models.Manager()

    def __str__(self) -> str:
        return f'{self.user.username}'
    
    @property
    def has_full_access(self):
        pass
    
    @property
    def resume_full_access(self):
        pass

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.user.username)
        super(Author, self).save(*args, **kwargs)