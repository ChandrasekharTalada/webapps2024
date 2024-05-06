from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save
from payapp.views import get_exchange_rate
import decimal

User = get_user_model()

@receiver(post_save, sender=User)
def handle_amount(sender, instance, created, **kwargs):
    if created:
        exchange_rate = get_exchange_rate('USD', instance.currency)
        if exchange_rate is not None:
            instance.amount =instance.amount * decimal.Decimal(exchange_rate)
            instance.save()