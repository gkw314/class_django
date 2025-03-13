
from django import forms
from blog.models import Blog


class BlogForm(forms.ModelForm): # Model을 가지고 만들어서 ModelForm 상속
    class Meta:
        model = Blog
        fields = ('title', 'content', ) # 전체를 적용하려면 '__all__'
