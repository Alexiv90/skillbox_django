from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleListView, ArticleDeleteView, LatestArticlesFeed

app_name = 'blogapp'

urlpatterns = [
    path("articles/", ArticleListView.as_view(), name="articles"),
    path("articles/<int:pk>/", ArticleDeleteView.as_view(), name="article"),
    path("articles/latest/feed/", LatestArticlesFeed(), name="latest-articles"),
]