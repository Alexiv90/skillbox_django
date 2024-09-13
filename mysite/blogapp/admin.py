from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Author, Article, Tag, Category

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name", "bio"]

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]

class TagsInline(admin.StackedInline):
    extra = 0
    model = Article.tags.through

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "pub_date",
        "author",
        "category",
    ]