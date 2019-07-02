from django import forms

class GeoPointForm(forms.Form):
    latitude = forms.DecimalField()
    longitude = forms.DecimalField()
