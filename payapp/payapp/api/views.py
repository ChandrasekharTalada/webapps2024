from django.http import JsonResponse
from django.views import View
from payapp.models import Rate
from decimal import Decimal
from django.db.models import Q


class ExchangeRateView(View):
    def get_exchange_rate(self, base_currency, target_currency):
        try:
            if base_currency == target_currency:
                return 1
            exchange_rate1 = ExchangeRate.objects.filter(
                base_currency=base_currency, target_currency=target_currency).first()
            if exchange_rate1 is not None:
                return exchange_rate1.rate
            else:
                exchange_rate2 = ExchangeRate.objects.get(
                    target_currency=base_currency, base_currency=target_currency)
                if exchange_rate2 is not None:
                    return 1/exchange_rate2.rate

        except (ExchangeRate.DoesNotExist):
            return None

    def get(self, request, currency1, currency2, amount_of_currency1):
        exchange_rate1_to_2 = self.get_exchange_rate(currency1, currency2)

        if exchange_rate1_to_2 is None:
            return JsonResponse({'error': 'Invalid currencies provided or exchange rate not found'}, status=400)

        # Perform the conversion
        amount_of_currency2 = Decimal(
            amount_of_currency1) * exchange_rate1_to_2

        response_data = {
            'currency1': currency1,
            'currency2': currency2,
            'amount': amount_of_currency2,
        }

        return JsonResponse(response_data)
