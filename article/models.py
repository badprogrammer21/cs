from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django_resized import ResizedImageField
from tinymce.models import HTMLField
from hitcount.models import HitCountMixin, HitCount
from django.contrib.contenttypes.fields import GenericRelation
from taggit.managers import TaggableManager
from django.shortcuts import reverse
from django.db.models import Count, Sum
from author.models import Author


class ArticleCategory(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=400, unique=True, blank=True)
    description = models.TextField(default="description")

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.title  

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(ArticleCategory, self).save(*args, **kwargs)

    def get_url(self):
        return reverse("posts", kwargs={
            "slug": self.slug
        })
    
    @property
    def num_posts(self):
        ArticlePost.objects.filter(categories=self).count()

    @property
    def last_post(self):
        ArticlePost.objects.filter(categories=self).latest("date")


class ArticlePost(models.Model):
    title = models.CharField(max_length=400)
    slug = models.CharField(max_length=400, unique=True, blank=True)
    article_users = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="article_users")
    content = models.TextField()
    categories = models.ManyToManyField(ArticleCategory)
    date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    hit_count_generic = GenericRelation(HitCount, object_id_field="object_pk",
                                            related_query_name="hit_count_generic_relation")
    article_tags = TaggableManager(related_name="article_tags")
    article_image = models.ImageField(null=True, blank=True, upload_to="article_images/")

    def __str__(self) -> str:
        return self.title

    @property
    def length(self) -> int:
        return len(self.content)

    @property
    def get_category(self):
        return [v for v in self.categories.all()]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(ArticlePost, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("article_details", kwargs={
            "slug": self.slug
    })