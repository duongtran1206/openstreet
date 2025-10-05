"""
URL patterns for hierarchical views
Add these to your main urls.py
"""

from django.urls import path
from maps import hierarchical_views

hierarchical_patterns = [
    path('map/hierarchical/', hierarchical_views.hierarchical_map, name='hierarchical_map'),
    path('api/locations/', hierarchical_views.api_locations, name='api_locations'),
    path('api/categories/', hierarchical_views.api_categories, name='api_categories'),
]
