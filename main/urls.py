from django.urls import path
from . import views

FIREBASE_API_BASE = 'firebase-api'

urlpatterns = [
    path('', views.home, name='home'),  
    path('api/currency-data/', views.get_currency_data, name='currency_data'), 
    path('api/brent-crude-data/', views.get_brent_crude_data, name='brent_crude_data'),    
    path('api/geopolitical-risk-data/', views.get_geopolitical_news, name='geopolitical-risk-data'),
    
    path(f'{FIREBASE_API_BASE}/add-production-row/', views.add_production_row, name='add_production_row'),
    path(f'{FIREBASE_API_BASE}/delete-production-forecast/<str:document_id>/', views.delete_production_forecast, name='delete_production_forecast'),
    path(f'{FIREBASE_API_BASE}/get-production-forecast/', views.get_production_forecast, name='get_production_forecast'),
    
    path(f'{FIREBASE_API_BASE}/add-asset-location/', views.add_asset_location, name='add_asset_location'),
    path(f'{FIREBASE_API_BASE}/delete-asset-location/<str:document_id>/', views.delete_asset_location, name='delete_asset_location'),
    path(f'{FIREBASE_API_BASE}/get-asset-locations/', views.get_asset_locations, name='get_asset_locations'), 
    
    path(f'{FIREBASE_API_BASE}/add-cashflow-projection/', views.add_cashflow_projection, name='add_cashflow_projection'),
    path(f'{FIREBASE_API_BASE}/delete-cashflow-projection/<str:document_id>/', views.delete_cashflow_projection, name='delete_cashflow_projection'),
    path(f'{FIREBASE_API_BASE}/get-cashflow-projections/', views.get_cashflow_projections, name='get_cashflow_projections'),
    path(f'{FIREBASE_API_BASE}/modify-cashflow-projection/<str:document_id>/', views.modify_cashflow_projection, name='modify_cashflow_projection'),
    
    path(f'{FIREBASE_API_BASE}/add-forward-contract/', views.add_forward_contract, name='add_forward_contract'),
    path(f'{FIREBASE_API_BASE}/delete-forward-contract/<str:document_id>/', views.delete_forward_contract, name='delete_forward_contract'),
    path(f'{FIREBASE_API_BASE}/delete-all-forward-contracts/', views.delete_all_forward_contracts, name='delete_all_forward_contracts'),
    path(f'{FIREBASE_API_BASE}/get-forward-contracts/', views.get_forward_contracts, name='get_forward_contracts'),
    
    path(f'{FIREBASE_API_BASE}/add-futures-contract/', views.add_futures_contract, name='add_futures_contract'),
    path(f'{FIREBASE_API_BASE}/delete-futures-contract/<str:document_id>/', views.delete_futures_contract, name='delete_futures_contract'),
    path(f'{FIREBASE_API_BASE}/get-futures-contracts/', views.get_futures_contracts, name='get_futures_contracts'),
    
    path(f'{FIREBASE_API_BASE}/add-PRI/', views.add_PRI, name='add_PRI'),
    path(f'{FIREBASE_API_BASE}/delete-PRI/<str:document_id>/', views.delete_PRI, name='delete_PRI'),
    path(f'{FIREBASE_API_BASE}/get-PRIs/', views.get_PRIs, name='get_PRIs'),
]


