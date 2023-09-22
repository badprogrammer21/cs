from django import forms
from .models import DiaryPost

class PostForm(forms.ModelForm):
    class Meta:
        model = DiaryPost
        fields = ("title", "content", "plans")
        exclude = ["user"]

        widget = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.TextInput(attrs={'class': 'form-control'}),
            'plans': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __setitem__(self, i, elem):
        self.list[i] = elem