from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from store.models import RateLimitBucket


class Command(BaseCommand):
    help = "Delete rate-limit identities that have been inactive for 30 days."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=30)
        deleted, _ = RateLimitBucket.objects.filter(last_seen_at__lt=cutoff).delete()
        self.stdout.write(self.style.SUCCESS(f"Removed {deleted} stale rate-limit records."))
