import random

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, DepositForm, WithdrawalForm, TransferForm
from .models import Account, Transaction

def home(request):
    if request.user.is_authenticated:
        return redirect('account_summary')
    return redirect('login')

def nomoney(request):
    return render(request, 'bank/nomoney.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Account.objects.create(user=user, account_number="ACCT" + str(user.id))
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'bank/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('account_summary')
    return render(request, 'bank/login.html')

@login_required
def account_summary(request):
    account = Account.objects.get(user=request.user)
    transactions = Transaction.objects.filter(account=account)
    return render(request, 'bank/account_summary.html', {'account': account, 'transactions': transactions})

@login_required
def deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            account = Account.objects.get(user=request.user)
            amount = form.cleaned_data['amount']
            upi_id = form.cleaned_data['upi_id']

            # Validate UPI ID
            if account.upi_id == 0:
                form.add_error('upi_id', 'Please set your UPI ID')
                return render(request, 'bank/deposit.html', {'form': form})
            elif account.upi_id != upi_id:
                form.add_error('upi_id', 'Incorrect UPI ID.')
                return render(request, 'bank/deposit.html', {'form': form})

            account.balance += amount
            account.save()
            Transaction.objects.create(account=account, transaction_type='Deposit', amount=amount)
            return redirect('account_summary')
    else:
        form = DepositForm()
    return render(request, 'bank/deposit.html', {'form': form})

@login_required
def withdraw(request):
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            account = Account.objects.get(user=request.user)
            amount = form.cleaned_data['amount']
            upi_id = form.cleaned_data['upi_id']
            if account.upi_id == 0:
                form.add_error('upi_id', 'Please set your UPI ID')
                return render(request, 'bank/deposit.html', {'form': form})
            elif account.upi_id != upi_id:
                form.add_error('upi_id', 'Incorrect UPI ID.')
                return render(request, 'bank/deposit.html', {'form': form})
            if account.balance >= amount:
                account.balance -= amount
                account.save()
                Transaction.objects.create(account=account, transaction_type='Withdrawal', amount=amount)
                return redirect('account_summary')
            else:
                return redirect('nomoney')
    else:
        form = WithdrawalForm()
    return render(request, 'bank/withdraw.html', {'form': form})

@login_required
def transfer(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            to_account_number = form.cleaned_data['to_account']
            account = Account.objects.get(user=request.user)

            amount = form.cleaned_data['amount']
            upi_id = form.cleaned_data['upi_id']

            # Validate UPI ID
            if account.upi_id == 0:
                form.add_error('upi_id', 'Please set your UPI ID')
                return render(request, 'bank/deposit.html', {'form': form})
            elif account.upi_id != upi_id:
                form.add_error('upi_id', 'Incorrect UPI ID.')
                return render(request, 'bank/deposit.html', {'form': form})
            from_account = Account.objects.get(user=request.user)
            to_account = Account.objects.get(account_number=to_account_number)
            if from_account.balance >= amount:
                from_account.balance -= amount
                to_account.balance += amount
                from_account.save()
                to_account.save()
                Transaction.objects.create(account=from_account, transaction_type='Transfer', amount=amount, description=f"To {to_account_number}")
                Transaction.objects.create(account=to_account, transaction_type='Transfer', amount=amount, description=f"From {from_account.account_number}")
                return redirect('account_summary')
            else:
                return redirect('nomoney')
    else:
        form = TransferForm()
    return render(request, 'bank/transfer.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

from django.shortcuts import get_object_or_404

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UpdateEmailForm, SetUpiIdForm
from .models import Account

@login_required
def profile(request, account_id):
    account = get_object_or_404(Account, id=account_id)

    if request.method == 'POST':
        email_form = UpdateEmailForm(request.POST, instance=request.user)
        upi_form = SetUpiIdForm(request.POST, instance=account)

        if email_form.is_valid() and upi_form.is_valid():
            email_form.save()
            upi_form.save()
            return redirect('account_summary')
    else:
        email_form = UpdateEmailForm(instance=request.user)
        upi_form = SetUpiIdForm(instance=account)

    return render(request, 'bank/profile.html', {
        'account': account,
        'email_form': email_form,
        'upi_form': upi_form
    })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import SetUpiIdForm
from .models import Account

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import SetUpiIdForm
from .models import Account
import random
from django.core.mail import send_mail
from django.conf import settings


@login_required
def set_upi_id(request):
    account = Account.objects.get(user=request.user)

    if request.method == 'POST':
        form = SetUpiIdForm(request.POST, instance=account)
        if form.is_valid():
            # Check OTP and UPI ID validity
            upi_id = form.cleaned_data['upi_id']
            otp = form.cleaned_data['otp']
            # Retrieve OTP from session or another secure storage
            stored_otp = request.session.get('otp', None)

            if str(otp) != str(stored_otp):
                form.add_error('otp', 'Incorrect OTP.')
                return render(request, 'bank/set_upi_id.html', {'form': form})

            # Save UPI ID if OTP is correct
            account.upi_id = upi_id
            account.save()
            # Clear OTP from session after use
            del request.session['otp']
            return redirect('account_summary')
    else:
        form = SetUpiIdForm(instance=account)

    # Generate and send OTP
    otp = random.randint(100000, 999999)
    request.session['otp'] = otp
    send_mail(
        'Your OTP Code',
        f'Your OTP code is {otp}',
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
        fail_silently=False,
    )

    return render(request, 'bank/set_upi_id.html', {'form': form})

