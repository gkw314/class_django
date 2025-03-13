from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model() # Django에 설정된 유저를 찾아서 가져오는 함수

class Blog(models.Model):
    CATEGORY_CHOICES = (
        ('free', '자유'),
        ('travle', '여행'),
        ('cat', '고양이'),
        ('dog', '강아지')
    )

    category = models.CharField('카테고리', max_length=10, choices=CATEGORY_CHOICES)
    title = models.CharField('제목', max_length=100)
    content = models.TextField('본문')

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # models.CASCADE => 같이 삭제
    # models.PROTECT => 삭제가 불가능함 (유저를 삭제하려고할때 블로그가 있으면 유저 삭제가 불가능)
    # models.SET_NULL => null값을 넣습니다. => 유저 삭제시 블로그의 author가 null이 됨, 이 때 null=True 옵션도 함께 설정 필요

    created_at = models.DateTimeField('작성일자', auto_now_add=True)
    updated_at = models.DateTimeField('수정일자', auto_now=True)

    # 제목이 노출되는 형식을 설정합니다. [카테고리] 제목은 최대 10자까지
    def __str__(self):
        return f'[{self.get_category_display()}] {self.title[:10]}'

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    # Meta 클래스 코드 추가
    class Meta:
        verbose_name = '블로그'
        verbose_name_plural = '블로그 목록'