#!/usr/bin/env python
"""
Test the exact API logic to find the issue
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapproject.settings')
django.setup()

from maps.hierarchical_models import Domain, HierarchicalCategory, HierarchicalLocation
from django.db.models import Q
import json

def test_api_logic():
    """Test the exact API logic"""
    print("=== Testing API Logic ===")
    
    domain_id = 'handwerkskammern_deutschland'
    category_ids = []  # Empty to get all categories
    
    # Build query (exact same as API)
    query = Q()
    
    if domain_id:
        query &= Q(categories__domain__domain_id=domain_id)
    
    if category_ids:
        query &= Q(categories__category_id__in=category_ids)
    
    print(f"Query: {query}")
    
    # Get locations (exact same as API) 
    locations = HierarchicalLocation.objects.filter(query).distinct().prefetch_related('categories__domain')
    print(f"Found {locations.count()} locations")
    
    # Build GeoJSON features (exact same as API)
    features = []
    for location in locations:
        print(f"Processing location: {location.name}")
        
        # Get location categories
        location_categories = []
        for category in location.categories.all():
            location_categories.append({
                'id': category.category_id,
                'name': category.name,
                'color': category.color or '#3388ff',
                'icon': category.icon or 'Category'
            })
        
        print(f"  Categories: {len(location_categories)}")
        print(f"  Coordinates: {location.longitude}, {location.latitude}")
        
        # Create feature
        try:
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [location.longitude, location.latitude]
                },
                'properties': {
                    'id': location.location_id,
                    'name': location.name,
                    'address': location.address,
                    'phone': location.phone,
                    'email': location.email,
                    'website': location.website,
                    'categories': location_categories,
                    'category': location_categories[0] if location_categories else None,
                    'raw_data': location.raw_data
                }
            }
            features.append(feature)
        except Exception as e:
            print(f"  ERROR creating feature for {location.name}: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Only process first 3 for testing
        if len(features) >= 3:
            break
    
    # Return GeoJSON
    geojson = {
        'type': 'FeatureCollection',
        'features': features,
        'meta': {
            'total_locations': len(features),
            'domain_id': domain_id,
            'categories_requested': category_ids
        }
    }
    
    print(f"Created GeoJSON with {len(features)} features")
    print("Sample feature:")
    print(json.dumps(features[0], indent=2))

if __name__ == "__main__":
    test_api_logic()