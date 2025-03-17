from django.db.models import Q
from django.shortcuts import redirect, reverse

from blog.forms import BlogForm
from blog.models import Blog
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse

from django.views.decorators.http import require_http_methods

# 쿠키 실습
# def blog_list(request):
#     blogs = Blog.objects.all()
#
#     visits = int(request.COOKIES.get('visits', 0)) + 1
#
#     context = {'blogs': blogs}
#
#     response = render(request, 'blog_list.html', context)
#     response.set_cookie('visits', visits)
#     return response

# 세션 실습
# def blog_list(request):
#     blogs = Blog.objects.all().order_by('-created_at')
#
#     visits = int(request.COOKIES.get('visits', 0)) + 1
#
#     request.session['count'] = request.session.get('count', 0) + 1  # 추가
#
#     context = {
#         'blogs': blogs,
#         'count': request.session['count'],
#     }
#
#     response = render(request, 'blog_list.html', context)
#     response.set_cookie('visits', visits)  # visits라는 이름으로 visits값을 담아준다.
#     return response

def blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')

    # 제목과 본문 모두 검색 대상으로 설정
    q = request.GET.get('q')
    if q:
        blogs = blogs.filter(
            Q(title__icontains=q) |
            Q(content__icontains=q)
        )


    # 한 페이지당 10개씩 보이도록
    paginator = Paginator(blogs, 10)

    # request.GET은 쿼리스트링을 가져옵니다.
    page = request.GET.get('page')
    page_object = paginator.get_page(page)

    context = {
        # 'blogs': blogs,
        'object_list': page_object.object_list,
        'page_obj': page_object,
    }

    return render(request, 'blog_list.html', context)


def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    context = { 'blog' : blog }
    return render(request, 'blog_detail.html', context)

@login_required() # 인증된 유저가 아닐 경우 settings.py에 설정된 LOGIN_URL로 이동하는 데코레이터
def blog_create(request):
    form = BlogForm(request.POST or None)
    if form.is_valid():
        blog = form.save(commit=False) # 블로그 모델만 생성, commit=False 왜 사용? -> form에는 없는 사용자의 정보를 입력하기 위함
        blog.author = request.user # author는 현재 로그인 된 유저
        blog.save()
        # kwargs는 reverse 함수에서 URL을 생성할 때, URL 패턴에서 요구하는 동적 경로 매개변수에 값을 전달하기 위해 사용
        return redirect(reverse('fb:detail', kwargs={'pk': blog.pk}))

    context = {'form': form}
    return render(request, 'blog_form.html', context)


@login_required()
def blog_update(request, pk):
    if not request.user.is_superuser:
        blog = get_object_or_404(Blog, pk=pk)
    else:
        blog = get_object_or_404(Blog, pk=pk, author=request.user)

    form = BlogForm(request.POST or None,request.FILES or None, instance=blog)  # instance로 기초데이터 세팅
    if form.is_valid():
        blog = form.save()
        return redirect(reverse('fb:detail', kwargs={'pk': blog.pk}))

    context = {
        'blog': blog,
        'form' : form,
    }
    return render(request, 'blog_form.html', context)

@login_required()
# 특정 요청만 허락하는 데코레이터. 삭제나 수정은 POST 요청으로 받아야합니다.
@require_http_methods(['POST'])
def blog_delete(request, pk):
    blog = get_object_or_404(Blog, pk=pk, author=request.user)
    blog.delete()

    return redirect(reverse('fb:list'))