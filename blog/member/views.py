from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login
from django.urls import reverse

# def sign_up(request):
#     # get 요청 시에는 None값
#     # username = request.POST.get('username')
#     # password1 = request.POST.get('password1')
#     # password2 = request.POST.get('password2')
#     #
#     # print('username', username)
#     # print('password1', password1)
#     # print('password2', password2)
#
#     # form = UserCreationForm() # Django에서 기본적으로 제공하는 가입 관련 폼
#
#     # username 중복확인
#     # 패스워드가 맞는지, 그리고 패스퉈드 정책에 올바른지
#     # 추가
#     if request.method == 'POST':  # POST 요청 시
#         form = UserCreationForm(request.POST)  # 요청된 폼을 form에 받습니다.
#         # form에 받은 데이터를 검증합니다
#         if form.is_valid():
#             form.save()
#             return redirect('/accounts/login/')
#     else:  # GET 요청 시 Form 새로 생성
#         form = UserCreationForm()
#
#
#     context = {
#         'form': form
#     }
#     return render(request, 'registration/signup.html', context)



# 현재 Django가 실행되는 환경의 config를 찾아서 import
# 혹시 config나 settings 파일의 이름이 바뀌어도 자동으로 인식
from django.conf import settings

def sign_up(request):

        # form은 POST 요청일 경우, POST 데이터를 사용하여 생성되고
    # 그렇지 않으면 빈 폼을 생성합니다.
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect(settings.LOGIN_URL)

    context = {
        'form': form
    }
    return render(request, 'registration/signup.html', context)


def login(request):
    form = AuthenticationForm(request, request.POST or None)
    if form.is_valid():
        django_login(request, form.get_user())
        # 추가
        next = request.GET.get('next')
        if next:
            return redirect(next)

        return redirect(reverse('blog:list'))

    else:
        form = AuthenticationForm(request)

    context = {
        'form': form
    }

    return render(request, 'registration/login.html', context)