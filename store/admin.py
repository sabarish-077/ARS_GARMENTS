from django.contrib import admin
from .models import Category, ContactInquiry, NewsletterSubscriber, Order, OrderItem, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price", "stock", "is_active", "is_featured")
    list_filter = ("category", "is_active", "is_featured")
    search_fields = ("name", "sku", "short_description")
    prepopulated_fields = {"slug": ("name",)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "sku", "unit_price", "quantity", "size")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "customer_name", "phone", "status", "total", "placed_at")
    list_filter = ("status", "placed_at")
    search_fields = ("order_number", "customer_name", "email", "phone")
    readonly_fields = ("order_number", "subtotal", "shipping", "total", "placed_at")
    inlines = [OrderItemInline]


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "inquiry_type", "email", "created_at")
    list_filter = ("inquiry_type", "created_at")
    search_fields = ("name", "company", "email", "phone", "message")
    readonly_fields = ("created_at",)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "subscribed_at")
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email",)
    readonly_fields = ("subscribed_at",)
