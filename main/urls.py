from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Root URL points to the home view
    path('api/currency-data/', views.get_currency_data, name='currency_data'),  # API endpoint
]

