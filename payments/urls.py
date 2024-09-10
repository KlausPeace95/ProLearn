from django.urls import path

from .views import PaymentHandler, Webhook

urlpatterns=[
    path("Webhook/", Webhook.as_view()),
    path("", PaymentHandler.as_vews()),
]