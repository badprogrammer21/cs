from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from author.models import Author
from django.shortcuts import redirect, render, get_object_or_404


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['username'].required = False


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['user','profile_pic', 'bio']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        print(*args, *kwargs.values())
        self.fields['user'].required = False
        self.fields['profile_pic'].required = False
        self.fields['bio'].required = False