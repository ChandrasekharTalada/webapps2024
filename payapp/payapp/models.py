from django.db import models
from django import forms
from django.core.validators import ValidationError
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .views import get_exchange_rate
from django.contrib.auth import get_user_model
import decimal
User = get_user_model()


class Notif(models.Model):
    TYPES = (
        "amount_transfer",
        "amount_transfer_request",
        "amount_transfer_result",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.BigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    user = models.ForeignKey(
        User,related_name="user_notif",on_delete=models.CASCADE
    )
    message = models.CharField(max_length=150)
    viewed = models.BooleanField(default=False)
    types = models.CharField(
        max_length=50, choices=list(zip(TYPES,TYPES))
    )
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_date"]



CURRENCIES = (
    ('EUR', 'Euro'),
    ('USD', 'US Dollar'),
    ('GBP', 'British Pound Sterling'),
)

class Rate(models.Model):
    base_currency = models.CharField(max_length=5, choices=CURRENCIES)
    target_currency = models.CharField(max_length=5, choices=CURRENCIES)
    rate = models.DecimalField(max_digits=10, decimal_places=6)

    class Meta:
        unique_together = ("base_currency", "target_currency")

    def save(self, *args, **kwargs):
        if self.base_currency == self.target_currency:
            raise ValidationError("Base currency and Target currency can't be the same")
        super().save(*args, **kwargs)


class Transfer(models.Model):
    transferrer = models.ForeignKey(User,related_name="transfer_user",on_delete=models.CASCADE)
    obtainer = models.ForeignKey(User,related_name="obtain_user",on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        created = not self.pk
        try:
            super().save(*args, **kwargs)

            if created:
                rate = get_exchange_rate(self.transferrer.currency, self.obtainer.currency)
                amount = (self.amount * decimal.Decimal(rate)).quantize(decimal.Decimal('0.01'))
                Notif.objects.create(
                    content_object=self,
                    user=self.obtainer,
                    message=f"You have been transferred {self.obtainer.currency} {amount} amount by {self.transferrer}",
                    types="amount_transfer",
                )

            if self.transferrer and self.amount > self.transferrer.amount:
                raise ValidationError("Amount is not enough")

            try:
                from timestamp_service.thrift_client import send_timestamp
                timestamp = send_timestamp()
            except Exception as e:
                timestamp = timezone.now()
        except Exception as e:
            pass

    class Meta:
        ordering = ["-created_date"]


class Request(models.Model):
    pay_to = models.ForeignKey(User,related_name="pay_to_user",on_delete=models.CASCADE)
    pay_from = models.ForeignKey(User,related_name="pay_from_user",on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_accepted = models.BooleanField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_date"]
    
    def save(self, *args, **kwargs):
        created = not self.pk 
        super().save(*args, **kwargs) 

        if created: 
            rate_receive = get_exchange_rate(self.pay_to.currency, self.pay_from.currency)
            amount_receive = (rate_receive *decimal.Decimal(self.amount)).quantize(decimal.Decimal('0.01'))
            Notif.objects.create(
                content_object=self,
                user=self.pay_from,
                message=f"You have transfer request of {self.pay_from.currency} {amount_receive} amount from {self.pay_to}",
                types="amount_transfer_request",
            )
        else:
            result = "accepted" if self.is_accepted else "rejected"
            Notif.objects.create(
                content_object=self,
                user=self.pay_to,
                message=f"Your payment request of amount {self.pay_to.currency} {self.amount} from {self.pay_from} was {result}",
                types="amount_transfer_result",
            )




class TransferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        
        user = kwargs.pop("user", None)
        super(TransferForm, self).__init__(*args, **kwargs)
        if user:
            self.fields["transferrer"].initial = user
            self.fields["transferrer"].widget = forms.HiddenInput()

        self.fields["obtainer"].label = "Email"
        self.fields["obtainer"].widget = forms.EmailInput(
            attrs={"class": "form-control", "required": True}
        )
        self.fields["amount"].widget.attrs.update(
            {"class": "form-control", "required": True}
        )

    class Meta:
        model = Transfer
        fields = ["transferrer", "obtainer", "amount"]


class RequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(RequestForm, self).__init__(*args, **kwargs)
        if user:
            self.fields["pay_to"].initial = user
            self.fields["pay_to"].widget = forms.HiddenInput()
        self.fields["pay_from"].widget = forms.EmailInput(
            attrs={"class": "form-control", "required": True}
        )
        self.fields["pay_from"].label = "From"
        self.fields["amount"].widget.attrs.update({"class": "form-control"})

    class Meta:
        model = Request
        fields = ["pay_to", "pay_from", "amount"]
