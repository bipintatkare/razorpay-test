from django.urls import path
from .views import index, payment, paymenthandler


urlpatterns = [
    path('', index, name="index"),
    path('payment/', payment, name="payment"),
    path('verify/', paymenthandler, name="verify"),
]
