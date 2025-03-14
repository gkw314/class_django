
from django import forms
from blog.models import Blog, Comment


class BlogForm(forms.ModelForm): # Model을 가지고 만들어서 ModelForm 상속
    class Meta:
        model = Blog
        fields = ('title', 'content', ) # 전체를 적용하려면 '__all__'

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content', )
        # 폼 필드가 렌더링될 때 사용할 HTML 위젯을 정의
        widgets = {
            'content': forms.TextInput(attrs={'class': 'form-control'})  # 부트스트랩
        }
        labels = {
            'content': '댓글'
        }