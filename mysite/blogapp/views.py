from django.contrib.gis.feeds import Feed
from django.views.generic import ListView, DetailView
from .models import Article
from django.urls import reverse, reverse_lazy

# class ArticleListView(ListView):
#     template_name = 'blogapp/article_list.html'
#     queryset = Article.objects.all().select_related("author").prefetch_related("tags").defer("content")
#     context_object_name = 'articles'

class ArticleListView(ListView):
    queryset = (
        Article.objects.filter(pub_date__isnull=False).order_by('-pub_date')
    )

class ArticleDeleteView(DetailView):
    model = Article

class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on change articles"
    link = reverse_lazy("blogapp:articles")
    def items(self):
        return (
            Article.objects.filter(pub_date__isnull=False).order_by('-pub_date')[:5]
        )

    def item_title(self, item:Article):
        return item.title

    def item_description(self, item:Article):
        return item.content[:200]
