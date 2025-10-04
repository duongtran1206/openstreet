from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'locations', views.LocationViewSet)

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/map-data/', views.map_data, name='map_data'),
    path('api/map-config/', views.map_config, name='map_config'),
    path('api/map-config/<str:config_name>/', views.map_config, name='map_config_named'),
    
    # Views
    path('', views.map_view, name='map_view'),
    path('embed/', views.embed_map_view, name='embed_map_view'),
    path('admin-map/', views.admin_map_view, name='admin_map_view'),
    path('upload-geojson/', views.upload_geojson, name='upload_geojson'),
]