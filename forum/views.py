from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import CreateView, UpdateView
from .models import Post, Category, Author, Comment, Reply
from .utils import update_views
from django.utils.decorators import method_decorator
from django import template
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core import serializers
from django.http import JsonResponse
from django.contrib import messages
import math
from datetime import timedelta
from django.utils import timezone 

def posts_by_tag(request, tag):
    category = Category.objects.order_by('title')
    category2 = Category.objects.order_by('title')
    posts = Post.objects.filter(approved=True, tags__name=tag)
    return render(request, 'forum/forum.html', {
        'max_posts': math.ceil(len(Post.objects.all()) / 6),
        'tag': tag,
        "all_posts": Post.objects.all()[:6],
        "user": request.user,
        "categories": category2[:6],
        "posts": posts,
        "cats": zip(
            category,
            [len(Post.objects.filter(categories=cat)) for cat in category]
        ),
    })

def categories_list(request):
    return render(request, 'categories_list.html', {
        'categories': Category.objects.all()
    })

def category_posts(request, slug):
    category = Category.objects.order_by('title')
    category2 = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(approved=True, categories=category2)
    context = {
        'max_posts': math.ceil(len(Post.objects.all()) / 6),
        "all_posts": Post.objects.all()[:6],
        "categoryy": category2,
        "categories": category[:6],
        "posts": posts,
        "cats": zip(
            category,
            [len(Post.objects.filter(categories=cat)) for cat in category]
        ),
    }
    return render(request, 'forum/forum.html', context)

def delete(request, slug, idd):
    post = Post.objects.get(slug=slug)
    comm = get_object_or_404(Comment, post=post, id=idd)
    comm.content, comm.is_deleted = "[deleted]", True
    comm.save()
    return redirect(detail, slug)

def delete_reply(request, slug, idd):
    reply = Reply.objects.get(id=idd)
    reply.content, reply.is_deleted = "[deleted]", True
    reply.save()
    return redirect(detail, slug)


def detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    category2 = Category.objects.order_by('title')
    posts = Post.objects.filter(approved=True)
    user = request.user
    if "comment_content" in request.POST:
        comment = request.POST.get("comment_content")
        commment_auth = Comment.objects.filter(user=request.user.author)
        last_comm = (timezone.now() - commment_auth.latest('date').date).seconds // 60 % 60
        if last_comm < 5:
            messages.error(request, 'You cannot comment more than 1 time in 5 minutes. So take this time to scrutinize the question')
            return redirect(detail, slug)
        new_comment, created = Comment.objects.get_or_create(user=user.author, content=comment, sp_post=post)

        post.comments.add(new_comment.id)

    if "reply" in request.POST:
        reply = request.POST.get("reply")
        st = request.POST['parent_comment_id']
        parent_comment = Comment.objects.get(id=st[:st.index(' ')]) if ' ' in st else Comment.objects.get(id=st)
        reply_auth = Reply.objects.filter(user=request.user.author)
        last_comm = (timezone.now() - reply_auth.latest('date').date).seconds // 60 % 60
        if last_comm < 5:
            messages.error(request, 'You cannot reply more than 1 time in 5 minutes. So take this time to scrutinize the question')
            return redirect(detail, slug)
        
        new_reply, created = '', ''
        if ' ' in st:
            reply_st=Reply.objects.get(id=st[st.index(' ')+1:])
            new_reply, created = Reply.objects.get_or_create(user=user.author, content=reply,
                                                             replied_to=Reply.objects.get(id=reply_st.id).user)
        elif "parent_comment_id" in request.POST:
            new_reply, created = Reply.objects.get_or_create(user=user.author, content=reply,
                                                                 replied_to=parent_comment.user)
        parent_comment.amount_of_replies += 1
        parent_comment.replies.add(new_reply)
        parent_comment.save()
        return redirect(detail, slug)

    
    comm = Comment.objects.filter(sp_post=get_object_or_404(Post, slug=slug))
    if 'typesort' in request.GET:
        typesort = request.GET.get('typesorted')
        commment = Comment.objects.filter(sp_post=get_object_or_404(Post, slug=slug))
        query_list = []
        if typesort == 'newest':
            print('newest')
            query_list = commment.order_by('-date')
        if typesort == 'oldest':
            print('oldest')
            query_list = commment.order_by('date')
        if typesort == 'top':
            print('top')
            query_list = commment.order_by('upvotes')
        comm = query_list
        
        
    category = Category.objects.order_by("title")
    context = {
        "user": user,
        "categories": category2[:6],
        "post": post,
        "comments": comm,
        "posts": posts,
        "cats": zip(
            category,
            [len(Post.objects.filter(categories=cat)) for cat in category]
        ),
    }
    update_views(request, post)
    return render(request, 'forum/details.html', context)

def posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(approved=True, categories=category)
    category2 = Category.objects.order_by('title')
    
    context = {
        "categories": category2,
        "posts": posts,
    }
    return render(request, 'forum/users_threads.html', context)

def new_forum(request):
    category2 = Category.objects.order_by('title')
    context = {
        "categories": category2,
    }
    return render(request, 'forum/new_forum.html', context)


def posts_sort(request, typesort):
    queryset_list = []
    category = Category.objects.order_by('title')[:6]
    if typesort == 'newest':
        queryset_list = Post.objects.order_by('-date')
    elif typesort == 'oldest':
        queryset_list = Post.objects.order_by('date')
    elif typesort == 'most_viewed':
        queryset_list = Post.objects.order_by('hit_count_generic')
    elif typesort == 'top':
        queryset_list = Post.objects.order_by('upvotes')

    return render(request, 'forum/forum.html', {
        'max_posts': math.ceil(len(Post.objects.all()) / 6),
        'sort': typesort,
        'user': request.user,
        'posts': queryset_list,
        'categories': category,
        'all_posts': Post.objects.all(),
        "cats": zip(
            category,
            [len(Post.objects.filter(categories=cat)) for cat in category]
        ),
    })

def search_forum_post(request):
    category = Category.objects.order_by('title')[:6]
    queryset_list = Post.objects.filter(approved=True)
    all_posts = Post.objects.all()
    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            queryset_list = queryset_list.filter(content__icontains=keywords)

    return render(request, 'forum/forum.html', {
        'max_posts': math.ceil(len(Post.objects.all()) / 6),
        'keywords': keywords,
        'user': request.user,
        'posts': queryset_list,
        'categories': category,
        'all_posts': all_posts,
        "cats": zip(
            category,
            [len(Post.objects.filter(categories=cat)) for cat in category]
        ),
    })


def comment_like(request):
    comment = ''
    if request.POST.get('action') == 'post':
        comment = Comment.objects.get(id=request.POST.get('comment_id'))
        if request.user.author in comment.disliked_by.all():
            comment.disliked_by.remove(request.user.author)
        if not request.user.author in comment.liked_by.all():
            comment.upvotes += 1
            comment.liked_by.add(request.user.author)
            comment.able_to_upvote, comment.able_to_downvote = False, True

        comment.save()
    return JsonResponse({'result': f'{comment.upvotes} points &bull; {comment.date}'})

def reply_like(request):
    reply = ''
    if request.POST.get('action') == 'post':
        reply = Reply.objects.get(id=request.POST.get('reply_id'))
        if request.user.author in reply.disliked_by.all():
            reply.disliked_by.remove(request.user.author)
        if not request.user.author in reply.liked_by.all():
            reply.upvotes += 1
            reply.liked_by.add(request.user.author)
            reply.able_to_upvote, reply.able_to_downvote = False, True

        reply.save()
    return JsonResponse({'result': f'{reply.upvotes} points &bull; {reply.date}'})

def comment_dislike(request):
    comment = ''
    if request.POST.get('action') == 'post':
        print(request.user.author)

        comment = Comment.objects.get(id=request.POST.get('cm_id'))
        if request.user.author in comment.liked_by.all():
            comment.liked_by.remove(request.user.author)
        if not request.user.author in comment.disliked_by.all():
            comment.upvotes -= 1
            comment.disliked_by.add(request.user.author)
            comment.able_to_upvote, comment.able_to_downvote = True, False

        comment.save()
    return JsonResponse({'result': f'{comment.upvotes} points &bull; {comment.date}'})


def reply_dislike(request):
    reply = ''
    if request.POST.get('action') == 'post':
        reply = Reply.objects.get(id=request.POST.get('cm_id'))
        if request.user.author in reply.liked_by.all():
            reply.liked_by.remove(request.user.author)
        if not request.user.author in reply.disliked_by.all():
            reply.upvotes -= 1
            reply.disliked_by.add(request.user.author)
            reply.able_to_upvote, reply.able_to_downvote = True, False

        reply.save()
    return JsonResponse({'result': f'{reply.upvotes} points &bull; {reply.date}'})

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'forum/post_form_update.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'The post has been updated')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user.id == post.user.id:
            return True
        return False

class PostCreateView(CreateView):
    model = Post
    template_name = 'forum/new_forum.html'
    form_class = PostForm


    def form_valid(self, form):
        auth_posts = Post.objects.filter(user=self.request.user.author)
        last_comm = (timezone.now() - auth_posts.latest('date').date).seconds // 60 % 60
        if last_comm < 5:
            messages.error(self.request, 'You cannot create a post more than 1 time in 5 minutes. So take this time to scrutinize the question')
            return super(PostCreateView, self).form_invalid(form)
        candidate = form.save(commit=False)
        candidate.user = Author.objects.get(user=self.request.user)
        candidate.save()
        messages.success(self.request, 'The post has been created. Please wait for it to be accepted')
        return super(PostCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(PostCreateView, self).get_context_data(**kwargs)
        category2 = Category.objects.order_by('title')
        ctx['categories'] = category2
        return ctx

