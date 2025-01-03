from django import forms
from user.models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'dp', 'phone_no', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg py-2 px-4 text-sm text-gray-700 focus:ring-2 focus:ring-blue-600 focus:outline-none'}),
            'dp': forms.FileInput(attrs={'class': 'w-full border border-gray-300 rounded-lg py-2 px-4 text-sm text-gray-700 focus:ring-2 focus:ring-blue-600 focus:outline-none'}),
            'phone_no': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg py-2 px-4 text-sm text-gray-700 focus:ring-2 focus:ring-blue-600 focus:outline-none'}),
            'email': forms.EmailInput(attrs={'class': 'w-full border border-gray-300 rounded-lg py-2 px-4 text-sm text-gray-700 hover:cursor-not-allowed'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Disable the email field so it can't be updated
        self.fields['email'].disabled = True
