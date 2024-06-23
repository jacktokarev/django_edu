from django.contrib.sitemaps import Sitemap
from .models import Product


class ShopSitemap(Sitemap):

    changefreq = "daily"
    priority = 0.6

    def items(self):
        return (Product.objects
            .select_related("created_by")
            .defer("orders")
            .order_by("-created_at")
        )

    def lastmod(self, item: Product):
        return item.created_at
