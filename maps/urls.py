from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .hierarchical_urls import map_urlpatterns

# Create router for ViewSets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'locations', views.LocationViewSet)

urlpatterns = [
    # 3-Tier Hierarchical Map System
    path('hierarchical/', include('maps.hierarchical_urls')),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/map-data/', views.map_data, name='map_data'),
    path('api/map-config/', views.map_config, name='map_config'),
    path('api/map-config/<str:config_name>/', views.map_config, name='map_config_named'),
    
    # Views
    path('', views.map_view, name='map_view'),
    path('embed/', views.embed_map_view, name='embed_map_view'),
    path('embed-debug/', views.embed_debug_view, name='embed_debug_view'),
    path('embed-test/', views.embed_test_view, name='embed_test_view'),
    path('admin-map/', views.admin_map_view, name='admin_map_view'),
    path('upload-geojson/', views.upload_geojson, name='upload_geojson'),
    
    # Multi-source data collection
    path('data-collection/', views.data_collection_interface, name='data_collection'),
    path('api/collect-data/', views.collect_data_ajax, name='collect_data_ajax'),
    path('api/collection-sources/', views.get_collection_sources, name='collection_sources'),
    path('api/collection-stats/', views.get_collection_stats, name='collection_stats'),
] + map_urlpatterns  # Add hierarchical map URLs