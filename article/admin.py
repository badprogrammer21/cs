from django.contrib import admin
from .models import ArticlePost, ArticleCategory
admin.site.register(ArticleCategory)
admin.site.register(ArticlePost)
