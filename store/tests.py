from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from .models import Category, ContactInquiry, NewsletterSubscriber, Order, Product


class StorefrontFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Men’s Trunks & Vests", slug="trunks")
        cls.product = Product.objects.create(
            category=cls.category, name="Signature Trunk Pack", slug="signature-trunk-pack",
            sku="ARS-TEST-001", short_description="Soft combed cotton stretch trunks.",
            material="95% cotton", price=Decimal("549.00"), stock=8, is_active=True,
        )

    def test_catalog_search_filters_products(self):
        response = self.client.get(reverse("catalog"), {"q": "Signature"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Signature Trunk Pack")
        self.assertEqual(len(response.context["products"]), 1)

    def test_cart_checkout_creates_order_and_reduces_stock(self):
        self.client.post(reverse("add_to_cart", args=[self.product.pk]), {"quantity": "2", "size": "M"})
        response = self.client.post(reverse("checkout"), {
            "customer_name": "Test Customer", "email": "buyer@example.com", "phone": "+91 9876543210",
            "address": "14 Cotton Street", "city": "Tiruppur", "state": "Tamil Nadu", "postal_code": "641607",
        })
        order = Order.objects.get()
        self.assertRedirects(response, reverse("order_success", args=[order.order_number]))
        self.assertEqual(order.total, Decimal("1098.00"))
        self.assertEqual(self.product.__class__.objects.get(pk=self.product.pk).stock, 6)
        self.assertEqual(order.items.get().quantity, 2)

    def test_guest_order_confirmation_requires_checkout_session(self):
        order = Order.objects.create(
            customer_name="Test Customer", email="buyer@example.com", phone="9876543210",
            address="14 Cotton Street", city="Tiruppur", state="Tamil Nadu", postal_code="641607",
            subtotal=Decimal("549.00"), total=Decimal("628.00"),
        )
        response = self.client.get(reverse("order_success", args=[order.order_number]))
        self.assertEqual(response.status_code, 404)
        session = self.client.session
        session["order_confirmation"] = order.order_number
        session.save()
        response = self.client.get(reverse("order_success", args=[order.order_number]))
        self.assertEqual(response.status_code, 200)

    def test_tracking_requires_order_number_and_checkout_phone(self):
        self.client.post(reverse("add_to_cart", args=[self.product.pk]), {"quantity": "1"})
        self.client.post(reverse("checkout"), {
            "customer_name": "Test Customer", "email": "buyer@example.com", "phone": "+91 9876543210",
            "address": "14 Cotton Street", "city": "Tiruppur", "state": "Tamil Nadu", "postal_code": "641607",
        })
        order = Order.objects.get()
        response = self.client.post(reverse("track_order"), {"order_number": order.order_number, "phone": order.phone})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["order"], order)
        missing = self.client.post(reverse("track_order"), {"order_number": order.order_number, "phone": "00000000"})
        self.assertIsNone(missing.context["order"])

    def test_b2b_enquiry_is_saved(self):
        response = self.client.post(reverse("b2b"), {
            "name": "Test Buyer", "company": "Cotton House", "email": "buyer@example.com",
            "phone": "9876543210", "inquiry_type": "general", "message": "Please share job work details.",
        })
        self.assertRedirects(response, reverse("b2b"))
        inquiry = ContactInquiry.objects.get()
        self.assertEqual(inquiry.inquiry_type, ContactInquiry.InquiryType.JOB_WORK)

    def test_newsletter_signup_is_saved_once(self):
        response = self.client.post(reverse("newsletter_subscribe"), {"email": "hello@example.com"})
        self.assertRedirects(response, reverse("home"))
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)
        self.client.post(reverse("newsletter_subscribe"), {"email": "hello@example.com"})
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)

    def test_newsletter_endpoint_rate_limits_repeated_submissions(self):
        for index in range(5):
            self.client.post(reverse("newsletter_subscribe"), {"email": f"person{index}@example.com"})
        response = self.client.post(reverse("newsletter_subscribe"), {"email": "sixth@example.com"})
        self.assertEqual(response.status_code, 429)
        self.assertGreaterEqual(int(response["Retry-After"]), 1)
        self.assertLessEqual(int(response["Retry-After"]), 3600)

    def test_responsive_styles_cover_phone_tablet_and_desktop(self):
        from pathlib import Path
        css = Path(__file__).resolve().parent.parent / "static" / "store" / "css" / "site.css"
        styles = css.read_text(encoding="utf-8")
        self.assertIn("@media(max-width:767.98px)", styles)
        self.assertIn("@media(max-width:991.98px)", styles)
        self.assertIn("@media(max-width:380px)", styles)
