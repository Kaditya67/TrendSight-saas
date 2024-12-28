from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    # Additional fields for signup form
    name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    phone_no = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    email = forms.EmailField(max_length=200, required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    
    # Custom password field, keeping 'password2' for confirmation
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))
    
    class Meta:
        model = User
        fields = ("name", "email", "phone_no", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Optional: Customize the form field's attributes (e.g., placeholder)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input', 'required': 'required'})

    def clean_phone_no(self):
        """
        Custom validation for phone number to ensure it only contains digits.
        """
        phone_no = self.cleaned_data.get("phone_no")
        if not phone_no.isdigit():
            raise forms.ValidationError("Phone number must be numeric")
        return phone_no

    def clean_password2(self):
        """
        Custom validation to ensure both passwords match.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        # Check if passwords match
        if password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ("email",)
