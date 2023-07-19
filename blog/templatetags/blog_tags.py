from django import template
from ..models import Post
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown #конкретно-прикладной фильтр, который позволит использовать синтаксис упрощенной разметки Markdown в постах блога, а затем в шаблонах конвертировать текст поста в HTML.

register = template.Library()
@register.simple_tag
def total_posts():#возвращает число опубликованных в блоге постов
    return Post.published.count()

@register.inclusion_tag('blog/post/latest_posts.html')#отображение последних постов в боковой панели
def show_latest_posts(count=5):#задаем число отображаемых постов
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}

@register.simple_tag
def get_most_commented_posts(count=5):#отображаем посты с наибольшим числом комментариев
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))