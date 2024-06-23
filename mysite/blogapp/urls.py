from django.urls import path
from .views import (
    ArticlesListView, 
    AuthorCreateView,
    CategoryCreateView,
    TagCreateView,
    ArticleCreateView,
    ArticleDetailsView,
    LatestArticles,
)

app_name="blogapp"

urlpatterns = [
    path("", ArticlesListView.as_view(), name="articles"),
    path("article-details/<int:pk>/", ArticleDetailsView.as_view(), name="article-details"),
    path("create-author/", AuthorCreateView.as_view(), name="create-author"),
    path("create-category/", CategoryCreateView.as_view(), name="create-category"),
    path("create-tag/", TagCreateView.as_view(), name="create-tag"),
    path("create-article/", ArticleCreateView.as_view(), name="create-article"),
    path("articles/latests/feed/", LatestArticles(), name="articles-feed"),
]
