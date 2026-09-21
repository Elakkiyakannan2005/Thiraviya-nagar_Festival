from django import forms

from .models import Donation


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ["name", "mobile", "address", "amount"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter your name", "id": "id_name"}),
            "mobile": forms.TextInput(
                attrs={
                    "placeholder": "10-digit mobile",
                    "id": "id_mobile",
                    "pattern": "[0-9]{10}",
                }
            ),
            "address": forms.Textarea(
                attrs={"placeholder": "Enter your address", "rows": 3, "id": "id_address"}
            ),
            "amount": forms.NumberInput(
                attrs={"placeholder": "Enter amount", "min": "1", "id": "amount"}
            ),
        }

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Please enter a valid donation amount.")
        return amount
