from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import F
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import (CategoryManagementForm, InquiryManagementForm,
                    OrderManagementForm, ProductManagementForm,
                    SubscriberManagementForm)
from .models import Category, ContactInquiry, NewsletterSubscriber, Order, Product


class StaffOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "login"

    def test_func(self):
        return self.request.user.is_staff


class ManagementList(StaffOnlyMixin, ListView):
    template_name = "store/management_list.html"
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("q", "").strip()[:100]
        if search and self.search_fields:
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f"{field}__icontains": search})
            queryset = queryset.filter(query)
        status = self.request.GET.get("status", "")
        if self.model is Order and status in Order.Status.values:
            queryset = queryset.filter(status=status)
        if self.model is Product:
            active = self.request.GET.get("active", "")
            if active in {"yes", "no"}:
                queryset = queryset.filter(is_active=(active == "yes"))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.management_context)
        return context


class ManagementCreate(StaffOnlyMixin, SuccessMessageMixin, CreateView):
    template_name = "store/management_form.html"
    success_message = "Record created successfully."

    def get_success_url(self): return reverse_lazy(self.return_route)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"title": f"Add {self.singular}", "return_route": self.return_route})
        return context


class ManagementUpdate(StaffOnlyMixin, SuccessMessageMixin, UpdateView):
    template_name = "store/management_form.html"
    success_message = "Changes saved successfully."

    def get_success_url(self): return reverse_lazy(self.return_route)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"title": f"Edit {self.singular}", "return_route": self.return_route})
        return context


class ManagementDelete(StaffOnlyMixin, DeleteView):
    template_name = "store/management_confirm_delete.html"
    success_message = "Record deleted."

    def get_success_url(self): return reverse_lazy(self.return_route)

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, "This category is still used by products. Move those products before deleting it.")
            return self.get_success_url()
        messages.success(self.request, self.success_message)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"title": f"Delete {self.singular}", "return_route": self.return_route})
        return context


class ProductList(ManagementList):
    model = Product
    search_fields = ("name", "sku", "short_description", "category__name")
    management_context = {"title": "Products", "kind": "products", "list_route": "manage_products", "add_route": "manage_product_add", "add_label": "product", "edit_route": "manage_product_edit", "delete_route": "manage_product_delete"}

class ProductCreate(ManagementCreate):
    model = Product; form_class = ProductManagementForm; return_route = "manage_products"; singular = "product"

class ProductUpdate(ManagementUpdate):
    model = Product; form_class = ProductManagementForm; return_route = "manage_products"; singular = "product"

class ProductDelete(ManagementDelete):
    model = Product; return_route = "manage_products"; singular = "product"; success_message = "Product deleted."


class CategoryList(ManagementList):
    model = Category
    search_fields = ("name", "slug", "description")
    management_context = {"title": "Categories", "kind": "categories", "list_route": "manage_categories", "add_route": "manage_category_add", "add_label": "category", "edit_route": "manage_category_edit", "delete_route": "manage_category_delete"}

class CategoryCreate(ManagementCreate):
    model = Category; form_class = CategoryManagementForm; return_route = "manage_categories"; singular = "category"

class CategoryUpdate(ManagementUpdate):
    model = Category; form_class = CategoryManagementForm; return_route = "manage_categories"; singular = "category"

class CategoryDelete(ManagementDelete):
    model = Category; return_route = "manage_categories"; singular = "category"; success_message = "Category deleted."


class OrderList(ManagementList):
    model = Order
    search_fields = ("order_number", "customer_name", "email", "phone")
    management_context = {"title": "Orders", "kind": "orders", "list_route": "manage_orders", "add_route": None, "add_label": "order", "edit_route": "manage_order_edit", "delete_route": "manage_order_delete"}

class OrderCreate(ManagementCreate):
    model = Order; form_class = OrderManagementForm; return_route = "manage_orders"; singular = "order"

class OrderUpdate(ManagementUpdate):
    model = Order; form_class = OrderManagementForm; return_route = "manage_orders"; singular = "order"

class OrderDelete(ManagementDelete):
    model = Order; return_route = "manage_orders"; singular = "order"; success_message = "Order deleted."

    def form_valid(self, form):
        with transaction.atomic():
            for line in self.object.items.select_for_update():
                if line.product_id:
                    Product.objects.filter(pk=line.product_id).update(stock=F("stock") + line.quantity)
            return super().form_valid(form)


class InquiryList(ManagementList):
    model = ContactInquiry
    search_fields = ("name", "company", "email", "phone", "message")
    management_context = {"title": "Enquiries", "kind": "inquiries", "list_route": "manage_inquiries", "add_route": "manage_inquiry_add", "add_label": "enquiry", "edit_route": "manage_inquiry_edit", "delete_route": "manage_inquiry_delete"}

class InquiryCreate(ManagementCreate):
    model = ContactInquiry; form_class = InquiryManagementForm; return_route = "manage_inquiries"; singular = "enquiry"

class InquiryUpdate(ManagementUpdate):
    model = ContactInquiry; form_class = InquiryManagementForm; return_route = "manage_inquiries"; singular = "enquiry"

class InquiryDelete(ManagementDelete):
    model = ContactInquiry; return_route = "manage_inquiries"; singular = "enquiry"; success_message = "Enquiry deleted."


class SubscriberList(ManagementList):
    model = NewsletterSubscriber
    search_fields = ("email",)
    management_context = {"title": "Subscribers", "kind": "subscribers", "list_route": "manage_subscribers", "add_route": "manage_subscriber_add", "add_label": "subscriber", "edit_route": "manage_subscriber_edit", "delete_route": "manage_subscriber_delete"}

class SubscriberCreate(ManagementCreate):
    model = NewsletterSubscriber; form_class = SubscriberManagementForm; return_route = "manage_subscribers"; singular = "subscriber"

class SubscriberUpdate(ManagementUpdate):
    model = NewsletterSubscriber; form_class = SubscriberManagementForm; return_route = "manage_subscribers"; singular = "subscriber"

class SubscriberDelete(ManagementDelete):
    model = NewsletterSubscriber; return_route = "manage_subscribers"; singular = "subscriber"; success_message = "Subscriber deleted."
