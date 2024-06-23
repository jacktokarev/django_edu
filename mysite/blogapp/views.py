from django.contrib.syndication.views import Feed
from django.db.models.base import Model
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse, reverse_lazy
from .models import *

# Create your views here.


class ArticlesListView(ListView):

    queryset = (Article.objects
        .select_related("author")
        .select_related("category")
        .prefetch_related("tags")
        .defer("content")
        .order_by("-pub_date")
    )
    template_name = "blogapp/articles.html"
    context_object_name = "articles"


class ArticleDetailsView(DetailView):

    queryset = (Article.objects
        .select_related("author")
        .select_related("category")
        .prefetch_related("tags")
    )
    template_name = "blogapp/article-details.html"
    context_object_name = "article"


class LatestArticles(Feed):

    title = "Blog articles (latest)"
    description = "Updates on changes and addition blog articles"
    link = reverse_lazy("blogapp:articles")

    def items(self):
        return (Article.objects
            .select_related("author")
            .select_related("category")
            .prefetch_related("tags")
            .order_by("-pub_date")[:5]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]

    # def item_link(self, item: Article):
    #     # return reverse("blogapp:article-details", kwargs={"pk": item.pk})
    #     return item.get_absolute_url()
 
class ArticleCreateView(CreateView):
    
    model = Article
    fields = "title", "content", "author", "category", "tags"
    template_name = "blogapp/create-article.html"
    success_url = reverse_lazy("blogapp:articles")


class AuthorCreateView(CreateView):
    
    model = Author
    fields = "name", "bio"
    template_name = "blogapp/create-author.html"
    success_url = reverse_lazy("blogapp:articles")

class CategoryCreateView(CreateView):
    
    model = Category
    fields = "name",
    template_name = "blogapp/create-category.html"
    success_url = reverse_lazy("blogapp:articles")

class TagCreateView(CreateView):
    
    model = Tag
    fields = "name",
    template_name = "blogapp/create-tag.html"
    success_url = reverse_lazy("blogapp:articles")
