from django import forms
from .models import DiaryPost

class PostForm(forms.ModelForm):
    class Meta:
        model = DiaryPost
        fields = ("title", "content", "plans")
        exclude = ["user"]


        title = forms.CharField(widget=forms.TextInput(attrs={'class': 'each_post_create form-control '}))
        content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control each_post_create'}))
        plans = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control each_post_create', 'place_holder': 'Dot separated'}))
    
    def __setitem__(self, i, elem):
        self.list[i] = elem