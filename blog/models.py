from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager


# Create your models here.
class PublishedManager(models.Manager):# создадим конкретно-прикладной менеджер, чтобы извлекать все посты, имеющие статус PUBLISHED.
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):

    class Status(models.TextChoices):#Мы добавим в модель поле статуса, которое позволит управлять статусом постов блога. В  постах будут использоваться статусы Draft (Черновик) и Published(Опубликован).
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User,    #Это поле определяет взаимосвязь многие-к-одному, означающую, что каждый пост написан пользователем и пользователь может написать любое число постов
                               on_delete=models.CASCADE,#Параметр on_delete определяет поведение, которое следует применять при удалении объекта, на который есть ссылка.
                               related_name='blog_posts')#ы используем related_name, чтобы указывать имя обратной связи, от User к Post

    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)#Оно будет использоваться для хранения даты и времени публикации поста.
    created = models.DateTimeField(auto_now_add=True)#Оно будет использоваться для хранения даты и  времени создания поста
    updated = models.DateTimeField(auto_now=True)#Оно будет использоваться для хранения последней даты и времени обновления поста.
    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)

    objects = models.Manager()  # менеджер, применяемый по умолчанию
    published = PublishedManager()  # конкретно-прикладной менеджер

    class Meta:#Мы используем атрибут ordering, сообщающий Django, что он должен сортировать результаты по полю publish.
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]#Указанная опция позволяет определять в модели индексы базы данных, которые могут содержать одно или несколько полей в возрастающем либо убывающем порядке, или функциональные выражения и функции базы данных.

    def __str__(self):
        return self.title

    tags = TaggableManager()#Менеджер tags позволит добавлять, извлекать и удалять теги из объектов Post.

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])


class Comment(models.Model):#многие к одному
     post = models.ForeignKey(Post,
                                on_delete=models.CASCADE,
                                related_name='comments')
     name = models.CharField(max_length=80)
     email = models.EmailField()
     body = models.TextField()
     created = models.DateTimeField(auto_now_add=True)
     updated = models.DateTimeField(auto_now=True)
     active = models.BooleanField(default=True)
     class Meta:
         ordering = ['created']
         indexes = [
         models.Index(fields=['created']),
     ]
     def __str__(self):
        return f'Comment by {self.name} on {self.post}'