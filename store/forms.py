from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Category, ContactInquiry, NewsletterSubscriber, Order, Product


class ProductManagementForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ["created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-select" if isinstance(field.widget, forms.Select) else "form-control")


class CategoryManagementForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.widget.attrs["class"] = "form-control"


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
