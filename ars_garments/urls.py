from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import FileResponse, HttpResponse
from django.urls import include, path
from store.sitemaps import ProductSitemap, StaticViewSitemap
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

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


def google_site_verification(request):
    verification_file = BASE_DIR / "google56c3d4631336badb.html"
    return FileResponse(verification_file.open("rb"), content_type="text/html")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("google56c3d4631336badb.html", google_site_verification, name="google_site_verification"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("", include("store.urls")),
]
