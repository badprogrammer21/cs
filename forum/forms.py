from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "categories", "content", "tags")
        exclude = ["user"]

        widget = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.TextInput(attrs={'class': 'form-control'}),
            'categories': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __setitem__(self, i, elem):
        self.list[i] = elem

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('user', 'content')