from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("store", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="NewsletterSubscriber",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("subscribed_at", models.DateTimeField(auto_now_add=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
    ]
