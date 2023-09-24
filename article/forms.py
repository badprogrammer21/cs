from django import forms
from .models import ArticlePost, ArticleCategory

class ArticlePostForm(forms.ModelForm):
    class Meta:
        model = ArticlePost
        fields = ("title", "categories", "content", "article_tags", 'article_image')
        exclude = ["article_users"]

        title = forms.CharField(widget=forms.TextInput(attrs={'class': 'each_post_create form-control '}))
        content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control each_post_create'}))
        categories = forms.ModelMultipleChoiceField(queryset=ArticleCategory.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'form-control each_post_create pst_create_categories'}))
        article_tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control each_post_createpst_create_categories'}))
        article_image = forms.ImageField(required=False)  # ImageField doesn't have a "class" attribute

    def __setitem__(self, i, elem):
        self.list[i] = elem