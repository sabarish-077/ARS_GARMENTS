from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import CheckoutForm, ContactForm, NewsletterForm, RegistrationForm
from .models import Category, ContactInquiry, NewsletterSubscriber, Order, OrderItem, Product
from .security import rate_limit


def _cart_products(request):
    cart = request.session.get("cart", {})
    products = []
    total = Decimal("0.00")
    for key, entry in list(cart.items()):
        try:
            product = Product.objects.get(pk=int(key), is_active=True)
            quantity = max(1, min(int(entry.get("quantity", 1)), 99))
        except (Product.DoesNotExist, TypeError, ValueError, AttributeError):
            cart.pop(key, None)
            continue
        size = entry.get("size", "M") if isinstance(entry, dict) else "M"
        if size not in {"XS", "S", "M", "L", "XL", "XXL"}: size = "M"
        cart[key] = {"quantity": quantity, "size": size}
        line_total = product.price * quantity
        total += line_total
        products.append({"product": product, "quantity": quantity, "size": size, "line_total": line_total})
    request.session["cart"] = cart
    return products, total


def home(request):
    featured = list(Product.objects.filter(is_active=True, is_featured=True)[:8])
    if not featured:
        featured = list(Product.objects.filter(is_active=True)[:8])
    return render(request, "store/home.html", {"featured": featured, "newsletter_form": NewsletterForm()})


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        raise PermissionDenied
    return render(request, "store/admin_dashboard.html", {
        "product_count": Product.objects.count(),
        "active_product_count": Product.objects.filter(is_active=True).count(),
        "category_count": Category.objects.count(),
        "order_count": Order.objects.count(),
        "new_order_count": Order.objects.filter(status=Order.Status.PLACED).count(),
        "inquiry_count": ContactInquiry.objects.count(),
        "subscriber_count": NewsletterSubscriber.objects.filter(is_active=True).count(),
        "recent_orders": Order.objects.order_by("-placed_at")[:8],
    })


def catalog(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(short_description__icontains=query) | Q(category__name__icontains=query))
    selected = request.GET.get("category", "")
    if selected:
        products = products.filter(category__slug=selected)
    max_price = request.GET.get("max_price", "").strip()
    if max_price:
        try:
            ceiling = Decimal(max_price)
            if not ceiling.is_finite() or ceiling < 0 or ceiling > Decimal("9999999.99"):
                raise InvalidOperation
            products = products.filter(price__lte=ceiling)
        except (InvalidOperation, ValueError): max_price = ""
    ordering = request.GET.get("sort", "featured")
    products = products.order_by("price" if ordering == "price_low" else "-price" if ordering == "price_high" else "-is_featured", "name")
    return render(request, "store/catalog.html", {
        "products": products, "categories": Category.objects.all(), "query": query,
        "selected_category": selected, "max_price": max_price, "sort": ordering,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    return render(request, "store/product_detail.html", {"product": product, "related": related})


def add_to_cart(request, product_id):
    if request.method != "POST": raise Http404
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    try: quantity = max(1, min(int(request.POST.get("quantity", 1)), 99))
    except (TypeError, ValueError): quantity = 1
    cart = request.session.get("cart", {})
    key = str(product.pk)
    try: current = max(0, int(cart.get(key, {}).get("quantity", 0)))
    except (TypeError, ValueError, AttributeError): current = 0
    size = request.POST.get("size", "M")
    if size not in {"XS", "S", "M", "L", "XL", "XXL"}: size = "M"
    if current + quantity > min(product.stock, 99):
        messages.error(request, "There is not enough stock for that quantity.")
    else:
        cart[key] = {"quantity": current + quantity, "size": size}
        request.session["cart"] = cart
        messages.success(request, f"{product.name} was added to your bag.")
    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next_url = product.get_absolute_url()
    return redirect(next_url)


def cart(request):
    items, subtotal = _cart_products(request)
    return render(request, "store/cart.html", {"items": items, "subtotal": subtotal, "shipping": Decimal("0.00") if subtotal >= 999 or subtotal == 0 else Decimal("79.00")})


def update_cart(request, product_id):
    if request.method != "POST": raise Http404
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    try: quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError): quantity = 1
    cart_data = request.session.get("cart", {})
    key = str(product.pk)
    if quantity <= 0: cart_data.pop(key, None)
    elif quantity <= min(product.stock, 99): cart_data.setdefault(key, {})["quantity"] = quantity
    else: messages.error(request, f"Only {product.stock} are currently available.")
    request.session["cart"] = cart_data
    return redirect("cart")


def remove_from_cart(request, product_id):
    if request.method != "POST": raise Http404
    cart_data = request.session.get("cart", {})
    cart_data.pop(str(product_id), None)
    request.session["cart"] = cart_data
    return redirect("cart")


def checkout(request):
    items, subtotal = _cart_products(request)
    if not items:
        messages.info(request, "Your bag is empty. Add something you love before checkout.")
        return redirect("catalog")
    shipping = Decimal("0.00") if subtotal >= 999 else Decimal("79.00")
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = Order(
                    user=request.user if request.user.is_authenticated else None,
                    customer_name=form.cleaned_data["customer_name"], email=form.cleaned_data["email"],
                    phone=form.cleaned_data["phone"], address=form.cleaned_data["address"],
                    city=form.cleaned_data["city"], state=form.cleaned_data["state"],
                    postal_code=form.cleaned_data["postal_code"], subtotal=subtotal, shipping=shipping,
                    total=subtotal + shipping,
                )
                order.save()
                for entry in items:
                    product = Product.objects.select_for_update().get(pk=entry["product"].pk)
                    if product.stock < entry["quantity"]:
                        messages.error(request, f"{product.name} no longer has enough stock. Please update your bag.")
                        transaction.set_rollback(True)
                        return render(request, "store/checkout.html", {"form": form, "items": items, "subtotal": subtotal, "shipping": shipping})
                    product.stock -= entry["quantity"]
                    product.save(update_fields=["stock"])
                    OrderItem.objects.create(order=order, product=product, product_name=product.name, sku=product.sku,
                                             unit_price=product.price, quantity=entry["quantity"], size=entry["size"])
            request.session["cart"] = {}
            if order.user_id is None:
                # A guest may view their confirmation only in the session that placed it.
                request.session["order_confirmation"] = order.order_number
            return redirect("order_success", order_number=order.order_number)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {"customer_name": request.user.get_full_name(), "email": request.user.email}
        form = CheckoutForm(initial=initial)
    return render(request, "store/checkout.html", {"form": form, "items": items, "subtotal": subtotal, "shipping": shipping})


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if order.user_id and order.user_id != (request.user.pk if request.user.is_authenticated else None):
        raise Http404
    if order.user_id is None and request.session.get("order_confirmation") != order.order_number:
        raise Http404
    return render(request, "store/order_success.html", {"order": order})


@rate_limit("track_order", limit=12, period_seconds=15 * 60)
def track_order(request):
    order = None
    if request.method == "POST":
        number = request.POST.get("order_number", "").strip().upper()
        phone = request.POST.get("phone", "").strip()
        order = Order.objects.filter(order_number=number, phone=phone).first()
        if order is None: messages.error(request, "We couldn't find an order with those details. Check the order number and phone number.")
    return render(request, "store/track_order.html", {"order": order})


@rate_limit("b2b_inquiry", limit=5, period_seconds=60 * 60)
def b2b(request):
    quote_total = None
    quote_qty = None
    style = request.GET.get("style", "trunks")
    if request.GET.get("qty"):
        try:
            quote_qty = max(100, min(int(request.GET["qty"]), 100000))
            unit_rates = {"trunks": 68, "panties": 42, "vests": 55, "tees": 115}
            if style not in unit_rates: style = "trunks"
            discount = 0.92 if quote_qty >= 5000 else 0.96 if quote_qty >= 1000 else 1
            quote_total = Decimal(quote_qty) * Decimal(unit_rates[style]) * Decimal(str(discount))
        except (TypeError, ValueError):
            quote_qty = None
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.inquiry_type = ContactInquiry.InquiryType.JOB_WORK
            inquiry.save()
            messages.success(request, "Thank you. Our manufacturing team will be in touch soon.")
            return redirect("b2b")
    else: form = ContactForm(initial={"inquiry_type": ContactInquiry.InquiryType.JOB_WORK})
    return render(request, "store/b2b.html", {"form": form, "quote_total": quote_total, "quote_qty": quote_qty or 1000, "quote_style": style})


def factory(request):
    return render(request, "store/factory.html")


@rate_limit("contact", limit=5, period_seconds=60 * 60)
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for writing to us. We'll reply as soon as we can.")
            return redirect("contact")
    else: form = ContactForm()
    return render(request, "store/contact.html", {"form": form})


@rate_limit("newsletter", limit=5, period_seconds=60 * 60)
def newsletter_subscribe(request):
    if request.method != "POST": raise Http404
    form = NewsletterForm(request.POST)
    if form.is_valid():
        existing = NewsletterSubscriber.objects.filter(email__iexact=form.cleaned_data["email"]).first()
        if existing:
            existing.is_active = True
            existing.save(update_fields=["is_active"])
            messages.success(request, "Thanks for signing up for ARS collection updates.")
        else:
            NewsletterSubscriber.objects.create(email=form.cleaned_data["email"])
            messages.success(request, "Thanks for signing up for ARS collection updates.")
    else:
        for errors in form.errors.values():
            for error in errors: messages.error(request, error)
    return redirect("home")


@rate_limit("register", limit=5, period_seconds=15 * 60)
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data["email"]
            user.save(update_fields=["email"])
            login(request, user)
            messages.success(request, "Your ARS Garments account is ready.")
            return redirect("home")
    else: form = RegistrationForm()
    return render(request, "store/register.html", {"form": form})
