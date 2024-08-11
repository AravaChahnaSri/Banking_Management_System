from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Account, Transaction

class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class TransactionForm(forms.ModelForm):
    upi_id = forms.IntegerField(required=True, help_text="Enter your 6-digit UPI ID")

    class Meta:
        model = Transaction
        fields = ['amount','upi_id']

    def clean_upi_id(self):
        upi_id = self.cleaned_data['upi_id']
        if upi_id < 100000 or upi_id > 999999:
            raise forms.ValidationError("UPI ID must be a 6-digit number.")
        return upi_id

class DepositForm(TransactionForm):
    class Meta(TransactionForm.Meta):
        fields = TransactionForm.Meta.fields + ['amount']

class WithdrawalForm(TransactionForm):
    class Meta(TransactionForm.Meta):
        fields = TransactionForm.Meta.fields + ['amount']

class TransferForm(forms.Form):
    to_account = forms.CharField(max_length=20)
    amount = forms.DecimalField(max_digits=12, decimal_places=2)
    upi_id = forms.IntegerField(required=True, help_text="Enter your 6-digit UPI ID")

    def clean_upi_id(self):
        upi_id = self.cleaned_data['upi_id']
        if upi_id < 100000 or upi_id > 999999:
            raise forms.ValidationError("UPI ID must be a 6-digit number.")
        return upi_id





from django import forms
from .models import Account

from django import forms
from .models import Account
import random


class SetUpiIdForm(forms.ModelForm):
    otp = forms.IntegerField(required=True, help_text="Enter the OTP sent to your email")
    upi_id = forms.IntegerField(required=True, help_text="Enter a 6-digit UPI ID")

    class Meta:
        model = Account
        fields = ['otp', 'upi_id']

    def clean_upi_id(self):
        upi_id = self.cleaned_data['upi_id']
        if upi_id < 100000 or upi_id > 999999:
            raise forms.ValidationError("UPI ID must be a 6-digit number.")
        return upi_id

    def clean_otp(self):
        otp = self.cleaned_data['otp']
        # Check if the OTP matches the stored value
        # This logic needs to be implemented in your view
        return otp


from django import forms
from django.contrib.auth.models import User

class UpdateEmailForm(forms.ModelForm):
    email = forms.EmailField(required=True, help_text="Enter your new email")

    class Meta:
        model = User
        fields = ['email']

