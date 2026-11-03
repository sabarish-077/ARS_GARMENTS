# Initial catalog, customer inquiry and order schema.
import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=90, unique=True)),
                ("slug", models.SlugField(unique=True)),
                ("description", models.CharField(blank=True, max_length=240)),
            ],
            options={"ordering": ["name"], "verbose_name_plural": "categories"},
        ),
        migrations.CreateModel(
            name="ContactInquiry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("company", models.CharField(blank=True, max_length=180)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("inquiry_type", models.CharField(choices=[("general", "General enquiry"), ("wholesale", "Wholesale"), ("job_work", "B2B job work")], default="general", max_length=20)),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order_number", models.CharField(editable=False, max_length=14, unique=True)),
                ("customer_name", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=20)),
                ("address", models.TextField()),
                ("city", models.CharField(max_length=100)),
                ("state", models.CharField(max_length=100)),
                ("postal_code", models.CharField(max_length=12)),
                ("status", models.CharField(choices=[("placed", "Order placed"), ("confirmed", "Confirmed"), ("packed", "Packed"), ("shipped", "Shipped"), ("delivered", "Delivered"), ("cancelled", "Cancelled")], default="placed", max_length=16)),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=10)),
                ("shipping", models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
                ("placed_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                ("slug", models.SlugField(unique=True)),
                ("sku", models.CharField(max_length=50, unique=True)),
                ("short_description", models.CharField(max_length=240)),
                ("description", models.TextField(blank=True)),
                ("material", models.CharField(default="100% combed cotton", max_length=180)),
                ("image_url", models.URLField(blank=True, max_length=1000)),
                ("price", models.DecimalField(decimal_places=2, max_digits=9)),
                ("compare_at_price", models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ("stock", models.PositiveIntegerField(default=25)),
                ("is_featured", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to="store.category")),
            ],
            options={"ordering": ["-is_featured", "name"]},
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_name", models.CharField(max_length=180)),
                ("sku", models.CharField(max_length=50)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=9)),
                ("quantity", models.PositiveIntegerField()),
                ("size", models.CharField(default="M", max_length=12)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="store.order")),
                ("product", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="store.product")),
            ],
        ),
    ]
