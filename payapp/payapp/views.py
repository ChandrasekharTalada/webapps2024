from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from itertools import chain
from django.db import transaction
from register.models import User
from decimal import Decimal
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        from .models import Transfer, Request
        current_user = request.user
        transfer_transactions = Transfer.objects.filter(
            transferrer=current_user
        ) | Transfer.objects.filter(obtainer=current_user)
        request_transactions = Request.objects.filter(
            pay_to=current_user
        ) | Request.objects.filter(pay_from=current_user)
        transactions = list(chain(transfer_transactions, request_transactions))
        transactions= sorted(
            transactions, key=lambda x: x.created_date, reverse=True
        )
        context = {
            "recent_updates": transactions[:5],
        }
        return render(request, "payapp/home.html", context)


class RequestDetailView(LoginRequiredMixin, View):
    def get(self, request):
        from .models import TransferForm, RequestForm, Request
        transferform = TransferForm(user=request.user)
        requestform = RequestForm(user=request.user)
        requests = Request.objects.filter(pay_from=request.user)
        context = {
            "transferform": transferform,
            "requestform": requestform,
            "requests":requests, 
        }
        return render(request, "payapp/requestlog.html", context)


class TransactionDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        from .models import Transfer,Request
        current_user = request.user
        transfer_transactions = Transfer.objects.filter(
            transferrer=current_user
        ) | Transfer.objects.filter(obtainer=current_user)
        request_transactions = Request.objects.filter(
            pay_to=current_user
        ) | Request.objects.filter(pay_from=current_user)
        transactions = list(chain(transfer_transactions, request_transactions))
        transactions= sorted(
            transactions, key=lambda x: x.created_date, reverse=True
        )
        context = {"transactions": transactions}
        return render(request, "payapp/transaction.html", context)


class AllTransactionView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        from .models import Transfer,Request
        transfer_transactions = Transfer.objects.filter()
        request_transactions = Request.objects.filter()
        transactions = list(chain(transfer_transactions, request_transactions))
        transactions= sorted(
            transactions, key=lambda x: x.created_date, reverse=True
        )
        context = {"transactions": transactions}
        return render(request, "payapp/transaction_all.html", context)

 
       

class NotificationView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        from .models import Notif
        notifications = Notif.objects.filter(user=request.user)
        context = {"notifications": notifications}
        return render(request, "payapp/notification.html", context)


class NotificationUnseen(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        notifications = Notif.objects.filter(user=request.user,viewed=False)
        context = {"notifications": notifications}
        html_content = render(
            request, "payapp/filter/unseen_notification.html", context
        )
        return HttpResponse(html_content)


class NotificationMarkSeen(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        from .models import Notif
        id = kwargs.get("id")
        notification = Notif.objects.filter(id=id).first()
        if notification:
            notification.viewed = True
            notification.save()
        response = HttpResponse()
        response["HX-Redirect"] = reverse("notification")
        return response


class SendPayment(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        from .models import TransferForm
        form = TransferForm(user=request.user)
        return render(request, "payapp/payment_send.html", {"form": form})

    def post(self, request, *args, **kwargs):
        from .models import TransferForm,Transfer
        form = TransferForm(user=request.user)
        email = request.POST.get("obtainer")
        user = User.objects.filter(email=email).first() 
        amount = Decimal(request.POST.get("amount"))
        if email == request.user.email:
            messages.warning(request, "Sending money to own's accout is forbidden")
            return render(request, "payapp/payment_send.html", {"form": form})
        if not user:
            messages.warning(request, "User doesn't exist")
            return render(request, "payapp/payment_send.html", {"form": form})
        with transaction.atomic():
            instance = Transfer.objects.create(
                transferrer=request.user,obtainer=user,amount=amount
            )
            obtainer = instance.obtainer
            transferrer = instance.transferrer
            principal = Decimal(instance.amount)
            transferrer.amount -= principal
            actual_principal = (
                get_exchange_rate(transferrer.currency, obtainer.currency) * principal
            )
            obtainer.amount += actual_principal
            transferrer.save()
            obtainer.save()
            instance.save()
            messages.success(request, "Payment completed successfully")
            return redirect("home")
        return render(request, "payapp/payment_send.html", {"form": form})


class RequestPayment(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        from .models import RequestForm
        form = RequestForm()
        return render(request, "payapp/payment_request.html", {"form": form})

    def post(self, request, *args, **kwargs):
        from .models import Request,RequestForm
        email = request.POST.get("pay_from")
        pay_from = User.objects.filter(email=email).first()
        amount = request.POST.get("amount")
        if email == request.user.email:
            messages.warning(request,"Requesting money from own's accout is forbidden")
            return redirect(request.META.get("HTTP_REFERER"))
        if not pay_from:
            messages.success(request, "User doesn't exist")
        instance = Request.objects.create(
            pay_to=request.user, pay_from=pay_from, amount=amount
        )
        if instance:
            messages.success(request, "Request submitted successfully")
            return redirect("transaction")
        form = RequestForm()
        return render(request, "payapp/payment_request.html", {"form": form})

    


class ApprovePaymentRequest(View):
    def post(self, request, *args, **kwargs):
        from .models import Request,RequestForm,Transfer
        id = request.POST.get("tr_id")
        Transactionreq = Request.objects.filter(id=id).first()
        receiver_id = request.POST.get("pay_to")
        sender_id = request.POST.get("pay_from")
        sender = User.objects.filter(uuid=sender_id).first()
        receiver = User.objects.filter(uuid=receiver_id).first()
        amount = Decimal(request.POST.get("amount"))
        if sender.amount >= amount:
            with transaction.atomic():
                sending_amount = (
                    get_exchange_rate(receiver.currency, sender.currency) * amount
                )
                sender.amount -= sending_amount
                receiver.amount += amount
                sender.save()
                receiver.save()
                Transfer(transferrer=sender, obtainer=receiver, amount=sending_amount).save()
                Transactionreq.is_accepted = True
                Transactionreq.save()
                messages.success(request, "Payment completed Successfully")
        else:
            Transactionreq.is_accepted = False
            Transactionreq.save()
            messages.warning(request, "Not enough balance")
        return redirect("transaction")


class RejectPaymentRequest(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from .models import Request
        id = request.POST.get("tr_id")
        Transactionreq = Request.objects.get(id=id)
        Transactionreq.is_accepted = False
        Transactionreq.save()
        messages.success(request, "Payment Request Rejected")
        return redirect("transaction")


def get_exchange_rate(base_currency, target_currency):
    from .models import Rate

    rate = Rate.objects.filter(
        base_currency=base_currency, target_currency=target_currency
    ).first()
    if rate is not None:
        return rate.rate

    if base_currency == target_currency:
        return 1

    else:
        rate = Rate.objects.filter(
            base_currency=base_currency, target_currency=target_currency
        ).first()
        if rate is not None:
            return rate.rate
        else:
            inverse_rate = Rate.objects.filter(
                base_currency=target_currency, target_currency=base_currency
            ).first()
            if inverse_rate is not None:
                return 1 / inverse_rate.rate
            else:
                import requests

                request_url = "https://api.freecurrencyapi.com/v1/latest?apikey=fca_live_8JuYeKm6pK2kkYAV3mRUPSyk3iylp6fSGCm9jlh1&currencies={}&base_currency={}".format(
                    target_currency, base_currency
                )
                response = requests.get(request_url)
                if response.status_code == 200:
                    data = response.json()
                    rate = data["data"][target_currency]
                    Rate.objects.create(
                        base_currency=base_currency,
                        target_currency=target_currency,
                        rate=rate,
                    )
                    return rate
                else:
                    return 1
