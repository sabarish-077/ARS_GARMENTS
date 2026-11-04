import uuid
from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=90, unique=True)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=240, blank=True)
    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"
    def __str__(self): return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT)
    name = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=50, unique=True)
    short_description = models.CharField(max_length=240)
    description = models.TextField(blank=True)
    material = models.CharField(max_length=180, default="100% combed cotton")
    image_url = models.URLField(max_length=1000, blank=True)
    image_data = models.BinaryField(blank=True, null=True, editable=False)
    image_content_type = models.CharField(max_length=30, blank=True, editable=False)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=25)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-is_featured", "name"]
    def __str__(self): return self.name
    def get_absolute_url(self): return reverse("product_detail", args=[self.slug])
    @property
    def display_image_url(self):
        if self.image_data:
            return reverse("product_image", args=[self.pk])
        return self.image_url or "/static/store/product-placeholder.svg"


class Order(models.Model):
    class Status(models.TextChoices):
        PLACED = "placed", "Order placed"
        CONFIRMED = "confirmed", "Confirmed"
        PACKED = "packed", "Packed"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
    order_number = models.CharField(max_length=32, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="orders", null=True, blank=True, on_delete=models.SET_NULL)
    customer_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=12)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PLACED)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    placed_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = uuid.uuid4().hex.upper()
        super().save(*args, **kwargs)
    def __str__(self): return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=180)
    sku = models.CharField(max_length=50)
    unit_price = models.DecimalField(max_digits=9, decimal_places=2)
    quantity = models.PositiveIntegerField()
    size = models.CharField(max_length=12, default="M")
    @property
    def line_total(self): return self.unit_price * self.quantity
    def __str__(self): return f"{self.product_name} × {self.quantity}"


class ContactInquiry(models.Model):
    class InquiryType(models.TextChoices):
        GENERAL = "general", "General enquiry"
        WHOLESALE = "wholesale", "Wholesale"
        JOB_WORK = "job_work", "B2B job work"
    name = models.CharField(max_length=150)
    company = models.CharField(max_length=180, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    inquiry_type = models.CharField(max_length=20, choices=InquiryType.choices, default=InquiryType.GENERAL)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.name} — {self.get_inquiry_type_display()}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.email


class RateLimitBucket(models.Model):
    """One expiring attempt counter per endpoint and pseudonymous client key."""
    key = models.CharField(max_length=64, unique=True)
    attempts = models.PositiveIntegerField(default=0)
    window_started_at = models.DateTimeField()
    last_seen_at = models.DateTimeField()

    class Meta:
        indexes = [models.Index(fields=["last_seen_at"])]

    def __str__(self):
        return f"Rate limit bucket {self.pk}"
