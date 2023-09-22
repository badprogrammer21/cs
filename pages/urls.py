from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('forum/', views.forum, name="forum"),
    path('articles/', views.articles, name="articles"),
    path('diary/', views.diary, name="diary"),
    path('register/', views.register, name="register"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('profile/id<int:id_user>', views.profile, name="profile"),
    path('recover_password', views.recover_password, name="recover_password"),
    path('recover_password_code', views.recover_password_code, name="recover_password_code"),
    path('validate_code', views.validate_code, name="validate_code"),
    path('change_password', views.change_password, name="change_password"),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('create_profile/id<int:user_id>', views.create_profile, name="create_profile"),
]