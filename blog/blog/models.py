from io import BytesIO
from pathlib import Path
# from PIL.Image import Image
from PIL import Image

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from django_extensions.db.models import TimeStampedModel

from utils.models import TimestampModel

User = get_user_model() # Django에 설정된 유저를 찾아서 가져오는 함수

class Blog(TimestampModel):
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
    # 추가
    image = models.ImageField('이미지', null=True, blank=True, upload_to='blog/%Y/%m/%d')
    thumbnail = models.ImageField('썸네일', null=True, blank=True, upload_to='blog/%Y/%m/%d/thumbnail')

    created_at = models.DateTimeField('작성일자', auto_now_add=True)
    updated_at = models.DateTimeField('수정일자', auto_now=True)

    # 제목이 노출되는 형식을 설정합니다. [카테고리] 제목은 최대 10자까지
    def __str__(self):
        return f'[{self.get_category_display()}] {self.title[:10]}'

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'blog_pk': self.pk})

    # Meta 클래스 코드 추가
    class Meta:
        verbose_name = '블로그'
        verbose_name_plural = '블로그 목록'

    # 모델을 이용해 처리
    def get_thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        elif self.image:
            return self.image.url
        return None

    # 오버라이드
    def save(self, *args, **kwargs):
        if not self.image:
            return super().save(*args, **kwargs)

        image = Image.open(self.image)
        image.thumbnail((300, 300))

        image_path = Path(self.image.name)  # Path 라이브러리를 사용해 이미지 경로를 가져옵니다

        thumbnail_name = image_path.stem  # /blog/2024/8/13/database.png -> database
        thumbnail_extension = image_path.suffix  # /blog/2024/8/13/database.png -> .png
        thumbnail_filename = f'{thumbnail_name}_thumb{thumbnail_extension}'

        if thumbnail_extension in ['.jpg', 'jpeg']:
            file_type = 'JPEG'
        elif thumbnail_extension == '.gif':
            file_type = 'GIF'
        elif thumbnail_extension == '.png':
            file_type = 'PNG'
        else:
            return super().save(*args, **kwargs)

        temp_thumb = BytesIO()
        image.save(temp_thumb, file_type)
        temp_thumb.seek(0)

        self.thumbnail.save(thumbnail_filename, temp_thumb, save=False)
        temp_thumb.close()
        return super().save(*args, **kwargs)


# 댓글 모델 정의

class Comment(TimestampModel):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    content = models.CharField('본문', max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.blog.title} 댓글'

    class Meta:
        verbose_name = '댓글'
        verbose_name_plural = '댓글 목록'
        ordering = ['-created_at', '-id']  # 역정렬