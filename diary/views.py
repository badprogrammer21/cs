from django.shortcuts import render
from .models import DiaryPost, Author
from diary.forms import *
from django.views.generic import CreateView, UpdateView
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from datetime import datetime
from django.db.models import Max
from django.utils.safestring import mark_safe
from django.db.models import Count, F, Value
from django.contrib import messages


def diary_sort(request, typesort):

    queryset_list = []
    if typesort == 'newest':
        return render(request, 'diary/diary.html', {
            "posts":zip(
            list(DiaryPost.objects.filter(
                user=Author.objects.get(user=request.user)
                ).order_by(
                    'date'
                )
                 .annotate(odd=F('day_count') % 2).filter(odd=True)),
            list(DiaryPost.objects.filter(
                user=Author.objects.get(user=request.user)
                ).order_by(
                    'date'   
                )
                .annotate(odd=F('day_count') % 2).filter(odd=False))
        )
        })
    elif typesort == 'oldest':
        return render(request, 'diary/diary.html', {
            "posts": zip(
            list(DiaryPost.objects.filter(
                user=Author.objects.get(user=request.user)
                ).order_by(
                    '-date'
                )
                 .annotate(odd=F('day_count') % 2).filter(odd=False)),
            list(DiaryPost.objects.filter(
                user=Author.objects.get(user=request.user)
                ).order_by(
                    '-date'   
                )
                .annotate(odd=F('day_count') % 2).filter(odd=True))
        )
        })
    context = {
        "posts":zip(
            list(DiaryPost.objects.filter(
                user=Author.objects.get(user=request.user)
                ).order_by(
                    'date'
                )
                 .annotate(odd=F('day_count') % 2).filter(odd=True)),
            list(DiaryPost.objects.filter(
                user=Author.objects.get(user=request.user)
                ).order_by(
                    'date'   
                )
                .annotate(odd=F('day_count') % 2).filter(odd=False))
        )
    }
    return render(request, 'diary/diary.html', context)

def search_diary_post(request):
    queryset_list = DiaryPost.objects.all()
    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            queryset_list = queryset_list.filter(content__icontains=keywords)
    context = {
        "user": request.user,
        "posts":zip(
            list(DiaryPost.objects.filter(
                user=Author.objects.get(user=request.user)
                ).order_by(
                    'date'
                )
                 .annotate(odd=F('day_count') % 2).filter(odd=True)
                 .filter(content__icontains=keywords)),
            list(DiaryPost.objects.filter(
                user=Author.objects.get(user=request.user)
                ).order_by(
                    'date'   
                )
                .annotate(odd=F('day_count') % 2).filter(odd=False)
                .filter(content__icontains=keywords))
        )
    }
    return render(request, 'diary/diary.html', context)

def detail(request, slug):
    post = get_object_or_404(DiaryPost, slug=slug)
    user = request.user
    content = post.content
    #content = content.replace('/**', '<h1 data-splitting>')
    #content = content.replace('**/', '</h1>' )
    content = mark_safe(content)
    context = {
        "plans": post.plans.split('.'),
        "content": content,
        "user": user,
        "post": post
    }
    return render(request, 'diary/details.html', context)

class DiaryPostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = DiaryPost
    fields = ['title', 'content', 'plans']
    template_name = 'diary/post_form_update.html'
    

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'The diary post has been updated')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user.id == post.user.id:
            return True
        return False
    

class PostCreateView(CreateView):
    model = DiaryPost
    template_name = 'diary/new_diary.html'
    form_class = PostForm

    def form_valid(self, form):
        candidate = form.save(commit=False)
        candidate.user = Author.objects.get(user=self.request.user)
        #tmep = candidate.date.strftime('%m/%d/%Y %I:%M %p')
        auth_posts = DiaryPost.objects.filter(user=Author.objects.get(user=self.request.user))
        prev_day_count = auth_posts.aggregate(Max('day_count'))
        prev_date = auth_posts.aggregate(Max('date'))
        if prev_date['date__max']:
            delta = candidate.date.replace(tzinfo=None) - prev_date.get('date__max').replace(tzinfo=None)
            difference = delta.days
            if difference < 1:
                print(messages.DEFAULT_TAGS)
                messages.error(self.request, 'You can not create more than 1 diary a day')
                return super(PostCreateView,self).form_invalid(form)
            candidate.day_count += 1 + prev_day_count.get('day_count__max')
        
        candidate.save()
        messages.success(self.request, 'The diary has been created')
        messages.warning(self.request, 'Next diary you may create only next day')
        return super(PostCreateView, self).form_valid(form)



 