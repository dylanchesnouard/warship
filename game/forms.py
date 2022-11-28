from django import forms

from .models import Shot


class ShotForm(forms.ModelForm):
    class Meta:
        model = Shot
        fields = (
            "grid",
            "x",
            "y",
        )
        widgets = {"grid": forms.HiddenInput()}
