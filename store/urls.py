from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from . import dashboard_views as management
from .security import rate_limit


class StoreLoginView(auth_views.LoginView):
    template_name = "store/login.html"

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse("admin_dashboard")
        return reverse("home")

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect("admin_dashboard")
        return super().get(request, *args, **kwargs)

from django.shortcuts import redirect
from django.urls import reverse

urlpatterns = [
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/products/", management.ProductList.as_view(), name="manage_products"),
    path("dashboard/products/add/", management.ProductCreate.as_view(), name="manage_product_add"),
    path("dashboard/products/<int:pk>/edit/", management.ProductUpdate.as_view(), name="manage_product_edit"),
    path("dashboard/products/<int:pk>/delete/", management.ProductDelete.as_view(), name="manage_product_delete"),
    path("dashboard/categories/", management.CategoryList.as_view(), name="manage_categories"),
    path("dashboard/categories/add/", management.CategoryCreate.as_view(), name="manage_category_add"),
    path("dashboard/categories/<int:pk>/edit/", management.CategoryUpdate.as_view(), name="manage_category_edit"),
    path("dashboard/categories/<int:pk>/delete/", management.CategoryDelete.as_view(), name="manage_category_delete"),
    path("dashboard/orders/", management.OrderList.as_view(), name="manage_orders"),
    path("dashboard/orders/add/", management.OrderCreate.as_view(), name="manage_order_add"),
    path("dashboard/orders/<int:pk>/edit/", management.OrderUpdate.as_view(), name="manage_order_edit"),
    path("dashboard/orders/<int:pk>/delete/", management.OrderDelete.as_view(), name="manage_order_delete"),
    path("dashboard/enquiries/", management.InquiryList.as_view(), name="manage_inquiries"),
    path("dashboard/enquiries/add/", management.InquiryCreate.as_view(), name="manage_inquiry_add"),
    path("dashboard/enquiries/<int:pk>/edit/", management.InquiryUpdate.as_view(), name="manage_inquiry_edit"),
    path("dashboard/enquiries/<int:pk>/delete/", management.InquiryDelete.as_view(), name="manage_inquiry_delete"),
    path("dashboard/subscribers/", management.SubscriberList.as_view(), name="manage_subscribers"),
    path("dashboard/subscribers/add/", management.SubscriberCreate.as_view(), name="manage_subscriber_add"),
    path("dashboard/subscribers/<int:pk>/edit/", management.SubscriberUpdate.as_view(), name="manage_subscriber_edit"),
    path("dashboard/subscribers/<int:pk>/delete/", management.SubscriberDelete.as_view(), name="manage_subscriber_delete"),
    path("", views.home, name="home"),
    path("shop/", views.catalog, name="catalog"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:product_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/placed/<str:order_number>/", views.order_success, name="order_success"),
    path("track-order/", views.track_order, name="track_order"),
    path("b2b/", views.b2b, name="b2b"),
    path("factory/", views.factory, name="factory"),
    path("contact/", views.contact, name="contact"),
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
    path("account/register/", views.register, name="register"),
    path("account/login/", rate_limit("login", limit=10, period_seconds=15 * 60)(StoreLoginView.as_view()), name="login"),
    path("account/logout/", auth_views.LogoutView.as_view(), name="logout"),
]
