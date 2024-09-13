from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class Author(models.Model):
    """
    Модель Author представляет автора статьи
    """
    class Meta:
        ordering = ['name']
        verbose_name_plural = _('Authors')
        verbose_name = _('Author')

    name = models.CharField(max_length=100, db_index=True)
    bio = models.TextField(null=False, blank=True, db_index=True)

    def __str__(self) ->str:
        return f"{self.name}"

class Category(models.Model):
    """
    Модель Category представляет категорию статьи
    """
    class Meta:
        verbose_name_plural = _('Categorys')
        verbose_name = _('Category')

    name = models.CharField(max_length=40, db_index=True)

    def __str__(self) ->str:
        return f"{self.name}"

class Tag(models.Model):
    """
    Модель Tag представляет тэг, который можно назначить статье
    """
    class Meta:
        verbose_name_plural = _('Tags')
        verbose_name = _('Tag')

    name = models.CharField(max_length=20, db_index=True)
    def __str__(self) ->str:
        return f"{self.name}"


class Article(models.Model):
    """
    Модель Article представляет статью
    """
    class Meta:
        ordering = ['author', 'category']
        verbose_name_plural = _('Articles')
        verbose_name = _('Articles')

    title = models.CharField(max_length=200, db_index=True)
    content = models.TextField(null=False, blank=True, db_index=True)
    pub_date = models.DateTimeField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)

    def get_absolute_url(self):
        return reverse('blogapp:article', kwargs={'pk':self.pk})

    def __str__(self) ->str:
        return f"{self.title}"
