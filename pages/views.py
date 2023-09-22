from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout as lg
from django.http import Http404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages, auth
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from author.models import Author
from forum.models import Post, Category
from article.models import ArticlePost as ArticlePost
from article.models import ArticleCategory as ArticleCategory
from diary.models import DiaryPost
from forum.utils import update_views
from django.contrib import messages
from django.db.models import Count
from taggit.models import Tag
from django.http import JsonResponse
from django.core import serializers
from django.db.models import Count, F, Value
from collections import defaultdict
from django.core.mail import BadHeaderError, send_mail
import re
from django.contrib.auth.models import User



def index(request):
    return render(request, 'index.html', {})

def forum(request):
    category = Category.objects.order_by('title')[:6]
    posts = Post.objects.filter(approved=True)
    posts_iter = Paginator(posts, 6)
    post = request.GET.get('page')
    paged_posts = posts_iter.get_page(post)
    all_posts = Post.objects.filter(approved=True)
    fx=[len(Post.objects.filter(categories=cat)) for cat in category]
    dct=defaultdict(int)
    for post in posts:
        for tag in post.tags.all():
            dct[tag]+=1
    pop_tags = sorted(dct.items(),key = lambda ele : dct[ele[1]], reverse=True)[:5]
    context = {
        "pop_tags": pop_tags,
        "categories": category,
        "posts": paged_posts,
        "all_posts": all_posts,
        "cats": zip(category, fx)
    }
    return render(request, 'forum/forum.html', context)

@login_required
def diary(request):
    context = {
        "posts":zip(
            list(DiaryPost.objects.filter(
                user=Author.objects.get(user=request.user)
                ).order_by(
                    'date'
                )
                 .annotate(odd=F('day_count') % 2).filter(odd=True)),
            [[]] if not list(DiaryPost.objects.filter(
                user=Author.objects.get(user=request.user)
                ).order_by(
                    'date'   
                )
                .annotate(odd=F('day_count') % 2).filter(odd=False)) 
                else
                list(DiaryPost.objects.filter(
                user=Author.objects.get(user=request.user)
                ).order_by(
                    'date'   
                )
                .annotate(odd=F('day_count') % 2).filter(odd=False))

        )
    }
    return render(request, 'diary/diary.html', context)

def articles(request):
    category = ArticleCategory.objects.order_by('title')[:6]
    posts = ArticlePost.objects.filter(approved=True)
    posts_iter = Paginator(posts, 6)
    post = request.GET.get('page')
    paged_posts = posts_iter.get_page(post)
    all_posts = ArticlePost.objects.filter(approved=True)
    fx=[len(ArticlePost.objects.filter(categories=cat)) for cat in category]
    context = {
        "categories": category,
        "posts": paged_posts,
        "all_posts": all_posts,
        "cats": zip(category, fx)
    }
    return render(request, 'articles/articles.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        context = {'form': form}
        print(form)
        if form.is_valid():
            print('VALID')
            user = form.save()
            username = form.cleaned_data.get('username')
            Author.objects.create(
                user=user,
            )
            messages.success(request, 'You are now logged in')
            return redirect('login')
        else:
            print(form.errors.as_data())
            messages.error(request, "Invalid credentials")
    else:
        form = UserRegisterForm()
    return render(request, 'reg.html', {'form': form})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['pass']
        user = auth.authenticate(username=username, password=password)
        if user:
            messages.success(request, 'You are now logged in')
            print(messages)
            auth.login(request, user)
            return redirect('profile', user.id)
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def logout(request):
    lg(request)
    messages.success(request, 'You are now logged out')
    return redirect('login')


def recover_password(request):
    return render(request, 'partials/forgot_password.html', {
    })

def change_password(request):
    user = request.user
    user.set_password(request.POST['new_password'])
    user.save()
    messages.success(request, 'The password has been changed')
    return redirect(profile, user.id)

def validate_code(request):
    if request.POST.get('code') == request.session['generated_code']:
        messages.success(request, 'Change the password')
        return render(request, 'partials/change_password.html')
    else:
        messages.error(request, 'Invalid code')
    return render(request, 'partials/forgot_password.html', {})

def recover_password_code(request):
    emails = User.objects.filter(is_active=True).values_list('email', flat=True)
    from random import choice
    code=''.join([choice('QWERTYUIOPASDFGHJKLZXCVBNM1234567890') for _ in range(6)])
    if request.POST['is_sent'] == 'true':
        messages.warning(request, 'The code is being sending')
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        email = request.POST.get('email')
        if re.fullmatch(regex, email) and email in emails:
            send_mail('Password recovery', f'Your code is {code}', 'recoveryscienceandart01@gmail.com', [email])
            messages.success(request, 'The code has been send')
            request.session['generated_code'] = code
            return redirect(validate_code)
        else:
            messages.error(request, 'Invalid email')
            return redirect(login)
    return render(request,'partials/forgot_password.html')



@login_required
def create_profile(request, user_id):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.author)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile', user_id)

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.author)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user_id': user_id,
    }
    return render(request, 'profile/profile.html', context)

def profile(request, id_user):
    try:
        pf_user = User.objects.get(id=id_user)
    except:
        raise Http404("User not found")
    return render(request, 'profile/profile.html', {
        'users_forum_posts': Post.objects.filter(user=pf_user.author),
        'users_article_posts': ArticlePost.objects.filter(article_users=pf_user.author),
        'another_user': request.user,
        'user': pf_user,
        'lst': [
            len(Post.objects.filter(user=pf_user.author)),
            #len(ArticlePost.objects.filter(article_users=pf_user.author))
        ]
    })



@login_required
def edit_profile(request):
    author2 = get_object_or_404(Author, user=request.user)
    author = Author.objects.get(user=request.user)
    user = get_object_or_404(User, username=request.user)
    try:
        userform = UserUpdateForm(request.POST,instance=request.user)
        profileform = ProfileUpdateForm(request.POST,request.FILES,instance=author)
    except:
        userform, profileform = None, None
    if request.method == 'POST':
        ps1, ps2 = request.POST['inputPasswordNew'], request.POST['inputPasswordNew2']
        choice = request.POST.getlist("ph")
        if userform.is_valid() and profileform.is_valid():
            if user.check_password(request.POST['current_password']):
                if ps1 == ps2:
                    new_profile = profileform.save(commit=False)
                    if profileform.instance.bio == '':
                        new_profile.bio = author2.bio
                    if userform.instance.email == '':
                        userform.instance.email = user.email
                    new_profile.user = request.user
                    if "partially_hidden" in choice:
                        new_profile.hidden_profile = True
                    if "partially_hidden" not in choice:
                        new_profile.hidden_profile = False
                    if "completely_hidden" in choice:
                        new_profile.hidden = True
                    if "completely_hidden" not in choice:
                        new_profile.hidden = False
                    print(new_profile)
                    new_profile.save()
                    userform.save()
                    if len(ps1) > 6:
                        user.set_password(ps1)
                        messages.success(request, 'Profile settings have been updated')
                        user.save()
                    elif len(ps1)>0 and len(ps1)<7:
                        messages.warning(request,'Your new password is too short but other settings have been updated')
                        user.save()
                    return redirect('profile', request.user.id)
                else:
                    messages.error(request, 'Passwords do not match')
                return redirect('forum')
            else:
                messages.error(request, 'Incorrect password')
            return redirect('forum')
        else:
            messages.error(request, 'Invalid email or picture')
    else:
        messages.error(request, 'Invalid form')
        userform = UserUpdateForm(instance=request.user)
        profileform = ProfileUpdateForm(instance=author)
    
    return render(request,'profile/profile.html',context={'form1':userform,'form2':profileform})

