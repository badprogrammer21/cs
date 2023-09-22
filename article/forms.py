from django import forms
from .models import ArticlePost

class ArticlePostForm(forms.ModelForm):
    class Meta:
        model = ArticlePost
        fields = ("title", "categories", "content", "article_tags")
        exclude = ["article_users"]

        widget = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.TextInput(attrs={'class': 'form-control'}),
            'categories': forms.Select(attrs={'class': 'form-control'}),
            'article_tags': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __setitem__(self, i, elem):
        self.list[i] = elem