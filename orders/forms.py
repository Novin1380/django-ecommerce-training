from django import forms
from .models import Order


class OrderCreateform(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email','address', 'zip_code','city','country','telephone']
        