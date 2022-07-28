from django.urls import path

from payments.views import CreateCheckoutSessionView, CreatePaymentIntentView, StripeWebhookView
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path("create-checkout-session/", CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path("create-payment-intent/", CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path("stripe-webhooks/", StripeWebhookView.as_view(), name="stripe_webhooks"),
]

urlpatterns = format_suffix_patterns(urlpatterns)