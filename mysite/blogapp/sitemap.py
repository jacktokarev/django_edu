from django.contrib.sitemaps import Sitemap
from .models import Article


class BlogSitemap(Sitemap):

    changefreq = "never"
    priority = 0.5

    def items(self):
        return (Article.objects
            .select_related("author")
            .select_related("category")
            .prefetch_related("tags")
            .order_by("-pub_date")
        )

    def lastmod(self, item: Article):
        return item.pub_date

    # def item_link(self, item: Article):
    #     return item.get_absolute_url()
