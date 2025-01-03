from django import forms
from user.models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'dp', 'phone_no','email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'dp': forms.FileInput(attrs={'class': 'form-control'}),
            'phone_no': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }