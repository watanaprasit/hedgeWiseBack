from django.urls import path
from . import views
from django.http import JsonResponse


urlpatterns = [
    path('', views.home, name='home'),  
    path('api/currency-data/', views.get_currency_data, name='currency_data'), 
    path('api/brent-crude-data/', views.get_brent_crude_data, name='brent_crude_data'),    
    path('api/geopolitical-risk-data/', views.get_geopolitical_news, name='geopolitical-risk-data'),
    path('firebase-api/add-production-row/', views.add_production_row, name='add_production_row'),
    path('firebase-api/delete-production-forecast/<str:document_id>/', views.delete_production_forecast, name='delete_production_forecast'),
    path('firebase-api/get-production-forecast/', views.get_production_forecast, name='get_production_forecast'),
    path('firebase-api/add-asset-location/', views.add_asset_location, name='add_asset_location'),
    path('firebase-api/delete-asset-location/<str:document_id>/', views.delete_asset_location, name='delete_asset_location'),
    path('firebase-api/get-asset-locations/', views.get_asset_locations, name='get_asset_locations'),
    path('firebase-api/debug-delete-asset-location/<str:document_id>/', views.debug_view, name='debug_delete_asset_location'),
]

