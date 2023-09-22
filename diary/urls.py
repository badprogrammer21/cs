from django.urls import path
from . import views
import pages
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("create_diary_post", login_required(views.PostCreateView.as_view()), name="create_diary_post"),
    path("search_diary_post", views.search_diary_post, name="search_diary_post"),
    path("update/<slug:slug>", views.DiaryPostUpdateView.as_view(), name="update_post_diary"),
    path("detail/<slug>", views.detail, name="detail"),
    path("sort_by/<str:typesort>/", views.diary_sort, name="diary_sort"),
]