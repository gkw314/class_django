from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from blog.forms import CommentForm
from blog.models import Blog, Comment


class BlogListView(ListView): # ListView 상속
    # model = Blog
    # queryset = Blog.objects.all().order_by('-created_at')
    queryset = Blog.objects.all()
    template_name = 'blog_list.html' # 렌더링
    paginate_by = 10 # 페이지네이션
    ordering = ('-created_at', ) # 역정렬

    # ListView 내장 함수
    # 검색기능
    def get_queryset(self):
        queryset = super().get_queryset()

        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q)
            )
        return queryset


class BlogDetailView(ListView):
    model = Comment
    # 같이 조인 하는 방법, 디비요청 덜간다.
    # queryset = Blog.objects.all().prefetch_related('comment_set', 'comment_set__author')
    template_name = 'blog_detail.html'
    paginate_by = 10  # 페이지네이션

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(Blog, pk=kwargs.get('blog_pk'))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(blog=self.object).prefetch_related('author')

#     """
#         1. 이 속성은 URL에서 데이터를 찾을때 사용할 키 이름을 바꿔주는 것
#         보통 Django는 pk를 기준으로 데이터를 찾는데, 만약 URL 에서 id라는 이름을 쓰고 싶으면 이걸로 바꿔야함
#         URL이 blog/5/ 라면 pk를 쓰고, URL이 blog/<int:id>/라면 id를 씀
#         """
#     pk_url_kwarg = 'id'
#
#     """
# 2. get_queryset 메서드는 어떤 데이터를 보여줄지 결정하는 것으로 데이터전체에서 필터링하는 느낌
# 블로그 글이 100개 있는데, id=50이하인 글만 보여주고 싶을 때 사용
# queryset = super().get_queryset()        # 전체 데이터 가져오기
# return queryset.filter(id__lte=50)       # 그 중에서 id가 50 이하인 것만 골라내기
# 결과는 50번째 글까지만 보여줌
# """
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         return queryset.filter(id__lte=50)
#
#     """
# 3. get_object 메서드는 URL에서 특정 글(데이터) 하나를 가져오는 방법을 바꾸는것
# 지금은 별로 바뀌는게 없지만, 나중에 더 복잡한 조건(ex.이 글을 작성한 사람만 볼 수 있다) 같은 걸 추가가능
# object = super().get_object()        # 기본 방식으로 글 하나 가져오기
# object = self.model.objects.get(pk=self.kwargs.get('pk'))           # 다시 글 찾기
# self.model.objects.get()은 pk = 5인 데이터를 데이터베이스에서 직접 가져오는 방법
# self.kwargs.get('pk') 는 URL에서 pk값을 가져옴
# 결과는 그냥 글 하나 가져오는 기본 방식이랑 거의 똑같지만, 나중에 수정할 준비를 해둔 것
# """
#
#     def get_object(self, queryset=None):
#         object = super().get_object()
#         object = self.model.objects.get(pk=self.kwargs.get('pk'))
#
#         return object
#
#     """
# 4. 템플릿 추가로 데이터를 전달하는 것으로 템플릿에서 사용할 수 있는 변수를 더 만드는 것
# 템플릿에 CBV라는 텍스트를 표시하고 싶을때 쓸 수 있음
# 결과는 템플릿에서 {{ test }} 를 쓰면 CBV라는 값이 나옴
# context = super().get_context_data(**kwargs)        # 기본 데이터 가져오기
# context['test'] = 'CBV'                              # 추가로 test라는 이름으로 'CBV' 넣기
# """
#
# # 템플릿에 전달할 context 데이터
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['blog'] = self.object
        return context

    # 댓글기능 추가 방법 1
    def post(self, *args, **kwargs):
        comment_form = CommentForm(self.request.POST)

         # 유효성 검사 실패 시
        if not comment_form.is_valid():
            self.object = self.get_object()
            context = self.get_context_data(object=self.object)
            context['comment_form'] = comment_form
            return self.render_to_response(context)

        # 로그인 여부 확인
        if not self.request.user.is_authenticated:
            raise Http404

        comment = comment_form.save(commit=False)  # 댓글 객체를 데이터베이스에 저장하지 않고 반환
        comment.blog_id = self.kwargs['pk']  # 현재 블로그 게시글(pk)과 댓글을 연결
        comment.author = self.request.user  # 현재 로그인한 사용자를 댓글 작성자로 설정
        comment.save()  # 댓글을 데이터베이스에 저장

        return HttpResponseRedirect(reverse_lazy('blog:detail', kwargs={'pk': self.kwargs['pk']}))

'''
LoginRequiredMixin : 사용자가 로그인을 해야만 이 뷰에 접근할 수 있도록 합니다. 만약 로그인을 하지 않은 사용자가 접근하려고 하면, 로그인 페이지로 리디렉션됩니다.
CreateView : Django에서 제공하는 제네릭 뷰로, 새로운 객체를 생성하는 폼을 처리하는 데 사용됩니다.
'''

class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    template_name = 'blog_form.html'
    fields = ('category', 'title', 'content')
    # success_url = reverse_lazy('cb_blog_list')

    def form_valid(self, form): # 폼이 유효할 때 호출
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    # def get_success_url(self): # 새로 생성된 블로그 게시물의 상세 페이지로 리디렉션
    #     return reverse_lazy('blog:detail', kwargs={'pk': self.object.pk})

    # 추가
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_title'] = '작성'
        context['btn_name'] = '생성'
        return context

class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    template_name = 'blog_form.html'
    fields = ('category', 'title', 'content')

        # 전체 쿼리셋을 필터링하여 다수의 객체를 반환합니다.
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser: # admin추가
            return queryset
        return queryset.filter(author=self.request.user)

        # 단일 객체를 검색하고, 검색된 객체에 대해 추가적인 조건 검사를 수행합니다. 여기서는 객체의 작성자가 현재 사용자와 일치하는지 확인합니다.
    # def get_object(self, queryset=None):
    #     self.object = super().get_object(queryset)
    #
    #     if self.object.author != self.request.user:
    #         raise Http404
    #     return self.object

     # 추가
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_title'] = '수정'
        context['btn_name'] = '수정'
        return context


class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Blog

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser: # admin추가
            queryset = queryset.filter(author=self.request.user)
        return queryset

    def get_success_url(self):
        return reverse_lazy('blog:list')


# 댓글기능 추가 방법 2
# url도 추가해야함
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def get(self, *args, **kwargs):
        raise Http404

    def form_valid(self, form):
        blog = self.get_blog()
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.blog = blog
        self.object.save()
        return HttpResponseRedirect(reverse('blog:detail', kwargs={'blog_pk': blog.pk})) # kwargs를 blog.pk로 변경

    def get_blog(self):
        pk = self.kwargs['blog_pk']
        blog = get_object_or_404(Blog, pk=pk) # Blog가 없으면 404에러
        return blog