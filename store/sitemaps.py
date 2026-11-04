from django.contrib.sitemaps import Sitemap

from .models import Product


class StaticViewSitemap(Sitemap):
    protocol = "https"
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["home", "catalog", "b2b", "factory", "contact"]

    def location(self, item):
        from django.urls import reverse

        return reverse(item)


class ProductSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Product.objects.filter(is_active=True)
