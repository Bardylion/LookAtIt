from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count #Это функция агрегирования Count из Django ORM-преобразователя
from django.contrib.postgres.search import TrigramSimilarity




# Create your views here.

def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # Постраничная разбивка с 3 постами на страницу
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
    # Если page_number не целое число, то
    # выдать первую страницу
        posts = paginator.page(1)
    except EmptyPage:
    # Если page_number находится вне диапазона, то
    # выдать последнюю страницу результатов
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # Список активных комментариев к этому посту
    comments = post.comments.filter(active=True)#набор запросов QuerySet, чтобы извлекать все активные комментарии к посту

    # Форма для комментирования пользователями
    form = CommentForm()

    # Список схожих постов
    post_tags_ids = post.tags.values_list('id', flat=True)#извлекается Python’овский список идентификаторов тегов текущего поста.
    similar_posts = Post.published.filter(tags__in=post_tags_ids) \
        .exclude(id=post.id)#берутся все посты, содержащие любой из этих тегов, за исключением текущего поста
    similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
                        .order_by('-same_tags', '-publish')[:4]#передается в  контекстный словарь для функции render(), same_tags, – которое содержит число тегов

    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                  'similar_posts': similar_posts}
                  )

class PostListView(ListView):
    """
    Альтернативное представление списка постов
    """
    queryset = Post.published.all()#используется для того, чтобы иметь конкретно-прикладной набор запросов QuerySet, не извлекая все объекты
    context_object_name = 'posts'#используется для результатов запроса.
    paginate_by = 3#задается постраничная разбивка результатов с возвратом трех объектов на страницу
    template_name = 'blog/post/list.html'#конкретно-прикладной шаблон используется для прорисовки страницы шаблоном template_name.

def post_share(request, post_id):
     # Извлечь пост по идентификатору id
     post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

     sent = False

     if request.method == 'POST':#страница загружается в первый раз, представление получает запрос GET
        # Форма была передана на обработку
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля формы успешно прошли валидацию
            cd = form.cleaned_data
            # ... отправить электронное письмо
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'rinjustone@gmail.com',
                      [cd['to']])
            sent = True
     else:
        form = EmailPostForm()
     return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})

@require_POST
def post_comment(request, post_id):
     post = get_object_or_404(Post,
     id=post_id,
     status=Post.Status.PUBLISHED)
     comment = None
     # Комментарий был отправлен
     form = CommentForm(data=request.POST)
     if form.is_valid():
         # Создать объект класса Comment, не сохраняя его в базе данных
         comment = form.save(commit=False)
         # Назначить пост комментарию
         comment.post = post
         # Сохранить комментарий в базе данных
         comment.save()
     return render(request, 'blog/post/comment.html',
                            {'post': post,
                            'form': form,
                            'comment': comment})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['query']
        results = Post.published.annotate(
            similarity=TrigramSimilarity('title', query),
        ).filter(similarity__gt=0.1).order_by('-similarity')

    return render(request,
                  'blog/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})
