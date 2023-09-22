from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import CreateView, UpdateView
from .models import ArticlePost, ArticleCategory, Author
from django.utils.decorators import method_decorator
from django import template
from .forms import ArticlePostForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core import serializers
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.contrib import messages



def category_articles(request, slug):
    category = ArticleCategory.objects.order_by('title')
    category2 = get_object_or_404(ArticleCategory, slug=slug)
    posts = ArticlePost.objects.filter(approved=True, categories=category2)
    context = {
        "all_posts": ArticlePost.objects.all()[:6],
        "categoryy": category2,
        "categories": category[:6],
        "posts": posts,
        "cats": zip(
            category,
            [len(ArticlePost.objects.filter(categories=cat)) for cat in category]
        ),
    }
    return render(request, 'articles/articles.html', context)


def detail(request, slug):
    post = get_object_or_404(ArticlePost, slug=slug)
    category2 = ArticleCategory.objects.order_by('title')
    posts = ArticlePost.objects.filter(approved=True)
    user = request.user
    
    content = post.content
    content = content.replace('/**', '<h1 data-splitting>')
    content = content.replace('**/', '</h1>' )
    content = mark_safe(content)
    category = ArticleCategory.objects.order_by("title")
    context = {
        "content": content,
        "user": user,
        "categories": category2[:6],
        "post": post,
        "posts": posts,
        "cats": zip(
            category,
            [len(ArticlePost.objects.filter(categories=cat)) for cat in category]
        ),
    }
    return render(request, 'articles/details.html', context)

def new_article(request):
    category2 = ArticleCategory.objects.order_by('title')
    context = {
        "categories": category2,
    }
    return render(request, 'articles/new_articles.html', context)

def articles(request, slug):
    category = get_object_or_404(ArticleCategory, slug=slug)
    posts = ArticlePost.objects.filter(approved=True, categories=category)
    category2 = ArticleCategory.objects.order_by('title')
    
    context = {
        "categories": category2,
        "posts": posts,
    }
    return render(request, 'articles/articles.html', context)


def articles_sort(request, typesort):
    queryset_list = []
    category = ArticleCategory.objects.order_by('title')
    if typesort == 'newest':
        queryset_list = ArticlePost.objects.order_by('-date')
    elif typesort == 'oldest':
        queryset_list = ArticlePost.objects.order_by('date')

    return render(request, 'articles/articles.html', {
        'user': request.user,
        'posts': queryset_list,
        'categories': category,
        'all_posts': ArticlePost.objects.all(),
        "cats": zip(
            category,
            [len(ArticlePost.objects.filter(categories=cat)) for cat in category]
        ),
    })

def search_article_post(request):
    category = ArticleCategory.objects.order_by('title')
    queryset_list = ArticlePost.objects.filter(approved=True)
    all_posts = ArticlePost.objects.all()
    keywords = ''
    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            queryset_list = queryset_list.filter(content__icontains=keywords)

    return render(request, 'articles/articles.html', {
        'keywords': keywords,
        'user': request.user,
        'posts': queryset_list,
        'categories': category,
        'all_posts': all_posts,
        "cats": zip(
            category,
            [len(ArticlePost.objects.filter(categories=cat)) for cat in category]
        ),
    })


class ArticlePostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ArticlePost
    fields = ['title', 'content']
    template_name = 'articles/post_form_update.html'


    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'The article has been updated')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user.id == post.user.id:
            return True
        return False


class ArticlePostCreateView(CreateView):
    model = ArticlePost
    template_name = 'articles/new_article.html'
    form_class = ArticlePostForm


    def form_valid(self, form):
        candidate = form.save(commit=False)
        candidate.article_users = Author.objects.get(user=self.request.user)
        candidate.save()
        messages.success(self.request, 'The article has been created. Please wait for it to be accepted')
        return super(ArticlePostCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(ArticlePostCreateView, self).get_context_data(**kwargs)
        category2 = ArticleCategory.objects.order_by('title')
        ctx['categories'] = category2
        return ctx


