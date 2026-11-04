from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path
from store.sitemaps import ProductSitemap, StaticViewSitemap

sitemaps = {
    "pages": StaticViewSitemap,
    "products": ProductSitemap,
}


def robots_txt(request):
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /account/\n"
        "Disallow: /dashboard/\n"
        "Disallow: /admin/\n"
        "Disallow: /cart/\n"
        "Disallow: /checkout/\n"
        "Disallow: /orders/\n"
        "Disallow: /track-order/\n"
        "Disallow: /newsletter/\n"
        "Sitemap: https://arsgarments.vercel.app/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("", include("store.urls")),
]
