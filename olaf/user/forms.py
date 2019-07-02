from django import forms

class MerchantLoginForm(forms.Form):
    phone_number = forms.CharField()
    password = forms.CharField()
