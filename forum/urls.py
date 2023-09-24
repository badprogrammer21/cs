from django.urls import path
from .views import *
import pages
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('<int:page_id>', pages.views.forum, name='page'),
    path("detail/<slug>/", detail, name="details"),
    path("new_forum", new_forum, name="new_forum"),
    path("new_forum/create_post", login_required(PostCreateView.as_view()), name="create_post"),
    path("post/<slug:slug>/update", PostUpdateView.as_view(), name="update_post_forum"),
    path("search_forum_post", search_forum_post, name="search_forum_post"),
    path("delete/<slug>/<uuid:idd>/", delete, name="delete"),
    path("delete_reply/<slug>/<uuid:idd>/", delete_reply, name="delete_reply"),
    path("category/<slug>/", category_posts, name="category_posts"),
    path("sort_by/<str:typesort>", posts_sort, name="posts_sort"),
    path("tag/<tag>", posts_by_tag, name="posts_by_tag"),
    
    path('categories_list/', categories_list, name="categories_list"),

    path("comment_like", comment_like, name="comment_like"),
    path("dislike_comment", comment_dislike, name="dislike_comment"),
    path("reply_like", reply_like, name="reply_like"),
    path("dislike_reply", reply_dislike, name="dislike_reply"),
]