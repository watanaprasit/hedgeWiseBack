from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path('api/currency-data/', views.get_currency_data, name='currency_data'), 
    path('api/brent-crude-data/', views.get_brent_crude_data, name='brent_crude_data'),    
    path('api/geopolitical-risk-data/', views.get_geopolitical_news, name='geopolitical-risk-data'),
    path('firebase-api/add-production-row/', views.add_production_row, name='add_production_row'),
    path('firebase-api/delete-production-row/<str:doc_id>/', views.delete_production_row, name='delete_production_row'),   
]

