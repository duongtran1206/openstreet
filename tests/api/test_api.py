#!/usr/bin/env python
"""
Simple test script to debug the API issue
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

def test_query():
    """Test the hierarchical location query"""
    print("=== Testing Hierarchical Location Query ===")
    
    # Check what data exists
    print(f"Domains: {Domain.objects.count()}")
    print(f"Categories: {HierarchicalCategory.objects.count()}")  
    print(f"Locations: {HierarchicalLocation.objects.count()}")
    
    # Get the domain
    domain = Domain.objects.first()
    print(f"Domain: {domain.domain_id} - {domain.name}")
    
    # Test basic query
    try:
        query = Q(categories__domain__domain_id=domain.domain_id)
        locations = HierarchicalLocation.objects.filter(query).distinct()
        print(f"Basic query result: {locations.count()} locations")
        
        # Test with prefetch
        locations = HierarchicalLocation.objects.filter(query).distinct().prefetch_related('categories__domain')
        print(f"With prefetch: {locations.count()} locations")
        
        # Test iteration
        print("Testing iteration:")
        for i, location in enumerate(locations[:3]):
            print(f"  {i+1}. {location.name} at ({location.latitude}, {location.longitude})")
            print(f"     Categories: {[cat.name for cat in location.categories.all()]}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_query()