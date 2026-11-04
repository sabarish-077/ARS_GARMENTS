from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.text import slugify
from .models import Category, ContactInquiry, NewsletterSubscriber, Order, Product


class ProductManagementForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ["created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-select" if isinstance(field.widget, forms.Select) else "form-control")
        self.fields["image_url"].help_text = "Paste a public, direct image URL (https://...). Local file paths cannot be displayed by the live website."
        self.fields["image_url"].widget.attrs["placeholder"] = "https://example.com/product-photo.jpg"


class CategoryManagementForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.widget.attrs["class"] = "form-control"
        self.fields["name"].help_text = "If this category already exists, choose it from the product form instead of adding it again. Its URL slug is generated automatically."

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        duplicates = Category.objects.filter(name__iexact=name)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError(
                "This category already exists. Select it in the product form instead of adding a duplicate."
            )
        return name

    def save(self, commit=True):
        category = super().save(commit=False)
        name_changed = category.pk and self.cleaned_data["name"] != self.initial.get("name")
        if not category.slug or name_changed:
            base_slug = slugify(category.name) or "category"
            candidate = base_slug
            suffix = 2
            existing = Category.objects.exclude(pk=category.pk)
            while existing.filter(slug=candidate).exists():
                candidate = f"{base_slug}-{suffix}"
                suffix += 1
            category.slug = candidate
        if commit:
            category.save()
            self.save_m2m()
        return category


class OrderManagementForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name", "email", "phone", "address", "city", "state", "postal_code", "status", "subtotal", "shipping", "total"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"


class InquiryManagementForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ["name", "company", "email", "phone", "inquiry_type", "message"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"


class SubscriberManagementForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.widget.attrs["class"] = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone = forms.RegexField(regex=r"^[0-9+()\- ]{8,20}$", error_messages={"invalid": "Enter a valid phone number."})
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), max_length=500)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    postal_code = forms.RegexField(regex=r"^[A-Za-z0-9\- ]{4,12}$", error_messages={"invalid": "Enter a valid postal code."})
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ["name", "company", "email", "phone", "inquiry_type", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "company": forms.TextInput(attrs={"placeholder": "Company name (optional)"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "+91 98765 43210"}),
            "inquiry_type": forms.Select(),
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell us about your products, quantity, timeline, or question…"}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["inquiry_type"].choices = [("", "Select an enquiry type"), *self.fields["inquiry_type"].choices]
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"


class NewsletterForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Your email address", "class": "form-control", "aria-label": "Email address"}))


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=False)
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.widget.attrs["class"] = "form-control"
    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
