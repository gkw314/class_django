from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import path, include
from django.views import View
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from django.conf.urls.static import static

from blog import views, cb_views
from member import views as member_views

# CBV 방법 2
class AboutView(TemplateView):
    template_name = 'about.html'

class TestView(View): # Django의 View 클래스 상속
    def get(self, request):
        return render(request, 'test_get.html')

    def post(self, request):
        return render(request, 'test_post.html')

urlpatterns = [
    path('admin/', admin.site.urls),


    path('', include('blog.urls')),
    path('fb/', include('blog.fbv_urls')),


    # Authentication 코드 추가
    # Django에 내장된 url 사용
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', member_views.sign_up, name='signup'),
    path('login/', member_views.login, name='login'),

    # CBV 방법 1
    # path('about', TemplateView.as_view(template_name='about.html'), name='about'), # 추가
    # CBV 방법 2
    # path('about', AboutView.as_view(), name='about'),
    # path('redirect/', RedirectView.as_view(pattern_name='about'), name='redirect'), # 기본적인 방법
    # path('redirect2/', lambda req: redirect('about')), # 익명함수 lambda를 사용하는 방법인데 참고만 하세요!
    # path('test/', TestView.as_view(), name='test'),

    # summernote 추가
    path('summernote/', include('django_summernote.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)