"""
URL patterns for 3-Tier Hierarchical Map System
"""

from django.urls import path
from . import hierarchical_views_new as views

app_name = 'hierarchical'

urlpatterns = [
    # Main hierarchical map interface
    path('', views.HierarchicalMapView.as_view(), name='map'),
    path('map/', views.HierarchicalMapView.as_view(), name='hierarchical_map'),
    
    # API endpoints for data
    path('api/locations/', views.HierarchicalLocationsAPI.as_view(), name='api_locations'),
    path('api/categories/', views.category_list_api, name='api_categories'),
    path('api/search/', views.search_locations_api, name='api_search'),
    path('api/domains/', views.domain_list_api, name='api_domains'),
    
    # Legacy compatibility
    path('legacy/', views.hierarchical_map, name='legacy_map'),
    path('legacy/api/', views.api_locations, name='legacy_api'),
]

# Additional URL patterns for integration with main maps app
map_urlpatterns = [
    path('hierarchical/', views.HierarchicalMapView.as_view(), name='hierarchical_map_view'),
    path('api/hierarchical/locations/', views.HierarchicalLocationsAPI.as_view(), name='hierarchical_locations_api'),
    path('api/hierarchical/categories/', views.category_list_api, name='hierarchical_categories_api'),
    path('api/hierarchical/search/', views.search_locations_api, name='hierarchical_search_api'),
    path('api/hierarchical/domains/', views.domain_list_api, name='hierarchical_domains_api'),
]