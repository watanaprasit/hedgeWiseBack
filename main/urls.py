from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path('api/currency-data/', views.get_currency_data, name='currency_data'), 
    path('api/brent-crude-data/', views.get_brent_crude_data, name='brent_crude_data'),    
    path('api/geopolitical-risk-data/', views.get_geopolitical_news, name='geopolitical-risk-data'),    
]

