"""Database-backed request throttling for public form endpoints."""
import hashlib
import hmac
from functools import wraps

from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.utils import timezone

from .models import RateLimitBucket


def _bucket_key(request, scope):
    # Store only a keyed digest, never the client's raw IP address.
    identity = request.META.get("REMOTE_ADDR", "unknown")
    if getattr(settings, "DJANGO_TRUST_PROXY_CLIENT_IP", False):
        # Vercel overwrites X-Forwarded-For with the client IP; don't enable behind an untrusted proxy.
        identity = request.META.get("HTTP_X_FORWARDED_FOR", identity).split(",", 1)[0].strip() or identity
    message = f"{scope}\0{identity}".encode("utf-8")
    return hmac.new(settings.SECRET_KEY.encode("utf-8"), message, hashlib.sha256).hexdigest()


def _consume_attempt(request, scope, limit, period_seconds):
    now = timezone.now()
    key = _bucket_key(request, scope)
    with transaction.atomic():
        try:
            bucket = RateLimitBucket.objects.select_for_update().get(key=key)
        except RateLimitBucket.DoesNotExist:
            try:
                # Savepoint lets us recover safely if another request creates it first.
                with transaction.atomic():
                    bucket = RateLimitBucket.objects.create(
                        key=key, attempts=0, window_started_at=now, last_seen_at=now
                    )
            except IntegrityError:
                bucket = RateLimitBucket.objects.select_for_update().get(key=key)

        elapsed = (now - bucket.window_started_at).total_seconds()
        if elapsed >= period_seconds:
            bucket.attempts = 0
            bucket.window_started_at = now
        bucket.last_seen_at = now
        if bucket.attempts >= limit:
            retry_after = max(1, int(period_seconds - elapsed))
            bucket.save(update_fields=["attempts", "window_started_at", "last_seen_at"])
            return retry_after
        bucket.attempts += 1
        bucket.save(update_fields=["attempts", "window_started_at", "last_seen_at"])
    return None


def rate_limit(scope, limit, period_seconds):
    """Throttle POST attempts by endpoint and REMOTE_ADDR; return HTTP 429 on overflow."""
    def decorate(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.method == "POST":
                retry_after = _consume_attempt(request, scope, limit, period_seconds)
                if retry_after is not None:
                    response = HttpResponse(
                        "Too many attempts. Please wait before trying again.", status=429
                    )
                    response["Retry-After"] = str(retry_after)
                    return response
            return view(request, *args, **kwargs)
        return wrapped
    return decorate
