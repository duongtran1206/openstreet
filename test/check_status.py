#!/usr/bin/env python3
"""
Check Django Database Status - Kiểm tra trạng thái dữ liệu hiện tại
"""

import sys
import os

# Thêm Django path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapproject.settings')

import django
django.setup()

from maps.models import Domain, HierarchicalCategory, HierarchicalLocation

def check_database_status():
    """Kiểm tra trạng thái database"""
    print("🔍 KIỂM TRA TRẠNG THÁI DATABASE")
    print("=" * 50)
    
    # Domains
    domains = Domain.objects.all()
    print(f"\n📊 DOMAINS ({len(domains)}):")
    for domain in domains:
        print(f"  • {domain.domain_id}: {domain.name}")
        
        # Categories for this domain
        categories = HierarchicalCategory.objects.filter(domain=domain)
        print(f"    📂 Categories: {len(categories)}")
        
        # Locations for this domain (through categories)
        locations = HierarchicalLocation.objects.filter(categories__domain=domain).distinct()
        print(f"    📍 Locations: {len(locations)}")
        
        if domain.domain_id == 'caritas_deutschland':
            print("    🔄 Caritas data status:")
            for cat in categories[:5]:  # Show first 5
                loc_count = cat.locations.count()
                print(f"      - {cat.name}: {loc_count} locations")
    
    print(f"\n📊 TỔNG QUAN:")
    print(f"  • Total Domains: {len(domains)}")
    print(f"  • Total Categories: {HierarchicalCategory.objects.count()}")
    print(f"  • Total Locations: {HierarchicalLocation.objects.count()}")
    
    # Check API endpoints
    print(f"\n🔗 API TEST URLS:")
    print(f"  • Domains: http://127.0.0.1:8000/api/hierarchical/domains/")
    for domain in domains:
        print(f"  • {domain.name}: http://127.0.0.1:8000/api/hierarchical/locations/?domain={domain.domain_id}")
    
    print(f"\n🌐 MAP URLS:")
    print(f"  • Main Map: http://127.0.0.1:8000/")
    print(f"  • Hierarchical: http://127.0.0.1:8000/hierarchical/")
    print(f"  • **EMBED (Primary)**: http://127.0.0.1:8000/embed/")

if __name__ == '__main__':
    check_database_status()