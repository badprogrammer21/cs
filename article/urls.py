from django.urls import path
from article.views import *
import pages
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("posts/<slug>/", articles, name="articles"),
    path('<int:page_id>', pages.views.articles, name='page'),
    path("detail/<slug>/", detail, name="article_details"),
    path("new_article", new_article, name="new_article"),
    path("new_article/create_post", login_required(ArticlePostCreateView.as_view()), name="create_article"),
    path("post/<slug:slug>/update/", ArticlePostUpdateView.as_view(), name="update_post_article"),
    path('categories_list', categories_list, name="categories_list"),
    path("search_article_post", search_article_post, name="search_article_post"),
    path("category/<slug>/", category_articles, name="category_articles"),
    path("sort_by/<str:typesort>", articles_sort, name="articles_sort"),
]