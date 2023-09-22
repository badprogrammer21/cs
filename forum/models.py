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
import schedule
import uuid
from django.shortcuts import redirect


class Category(models.Model):
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
        super(Category, self).save(*args, **kwargs)

    def get_url(self):
        return reverse("posts", kwargs={
            "slug": self.slug
        })
    
    @property
    def num_posts(self):
        return str(Post.objects.filter(categories=self).count())

    @property
    def last_post(self):
        return Post.objects.filter(categories=self).latest("date")


class Reply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    liked_by = models.ManyToManyField(Author, related_name="reply_liked_by")
    disliked_by = models.ManyToManyField(Author, related_name="reply_disliked_by")
    upvotes = models.IntegerField(default=0)
    able_to_upvote = models.BooleanField(default=True)
    able_to_downvote = models.BooleanField(default=True)

    is_deleted = models.BooleanField(default=False)
    replied_to = models.ForeignKey(Author, on_delete=models.CASCADE,blank=True, null=True, related_name="replied_to")

    def __str__(self) -> str:
        return self.content[:100]
    
    class Meta:
        ordering = ('date', )
        verbose_name_plural = "replies"

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    replies = models.ManyToManyField(Reply, blank=True)

    replies = models.ManyToManyField(Reply, blank=True)
    amount_of_replies = models.IntegerField(default=0)

    upvotes = models.IntegerField(default=0)
    able_to_upvote = models.BooleanField(default=True)
    able_to_downvote = models.BooleanField(default=True)
    liked_by = models.ManyToManyField(Author, related_name="comment_liked_by")
    disliked_by = models.ManyToManyField(Author, related_name="comment_disliked_by")

    is_deleted = models.BooleanField(default=False)
    sp_post = models.ForeignKey('Post', on_delete=models.CASCADE, blank=True, null=True, related_name="post_comm")

    def __str__(self) -> str:
        return self.content[:100]
    

class Post(models.Model):
    title = models.CharField(max_length=400)
    slug = models.CharField(max_length=400, unique=True, blank=True)
    user = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField()
    categories = models.ManyToManyField(Category)
    date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    hit_count_generic = GenericRelation(HitCount, object_id_field="object_pk",
                                            related_query_name="hit_count_generic_relation")
    tags = TaggableManager(related_name="forum_tags")
    comments = models.ManyToManyField(Comment, blank=True)

    upvotes = models.IntegerField(default=0)
    able_to_upvote = models.BooleanField(default=True)
    able_to_downvote = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.title

    def length(self) -> int:
        return len(self.content)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse("details", kwargs={
            "slug": self.slug
        })
