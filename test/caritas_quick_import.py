#!/usr/bin/env python3
"""
Quick Caritas Import - Import thêm 50 records để demo
"""

import sys
import os
import json
import requests
from bs4 import BeautifulSoup

# Thêm Django path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapproject.settings')

import django
django.setup()

from maps.models import Domain, HierarchicalCategory, HierarchicalLocation

def quick_caritas_import():
    """Import nhanh 50 records từ Caritas API"""
    
    print("🚀 QUICK CARITAS IMPORT - 50 Records")
    print("=" * 40)
    
    # API settings
    base_url = "https://www.caritas.de/Services/MappingService.svc/GetMapContents/ec7e69ee-35b9-45b9-b081-fc7a191a76c0/"
    datasource = "80c48846275643e0b82b83465979eb70"
    
    # Get domain
    domain = Domain.objects.get(domain_id='caritas_deutschland')
    print(f"✅ Domain: {domain.name}")
    
    # Category mapping
    category_mapping = {
        'jugendmigrationsdienst': 'jugendmigrationsdienst',
        'migrationsberatung für erwachsene': 'migrationsberatung_fur_erwachsene',
        'migrationsberatung': 'migrationsberatung',
        'gemeinwesenorientierte arbeit': 'gemeinwesenorientierte_arbeit',
        'iq - faire integration': 'iq_faire_integration',
        'beratungszentrum': 'beratungszentrum',
    }
    
    def parse_html_content(html_content):
        """Quick parse"""
        if not html_content:
            return None, None, None
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Service type
        service_type = None
        kicker = soup.find('h2', class_='kicker')
        if kicker:
            service_type = kicker.text.strip()
            
        # Organization name
        org_name = None
        h3_tag = soup.find('h3')
        if h3_tag:
            org_name = h3_tag.text.strip()
            
        # Address (simple)
        address = ""
        venue_info = soup.find('div', class_='venue-info')
        if venue_info:
            address_parts = []
            for p in venue_info.find_all('p')[:2]:  # Take first 2 paragraphs
                text = p.text.strip()
                if text and not text.startswith(('Tel:', 'E-Mail:', 'Fax:')):
                    address_parts.append(text)
            address = ', '.join(address_parts)
            
        return service_type, org_name, address
    
    try:
        # Download 1 page only (50 records)
        url = f"{base_url}?datasource={datasource}&page=1&pagesize=50"
        print("📥 Downloading page 2 (records 51-100)...")
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        contents = data.get('Contents', [])
        
        print(f"📊 Downloaded: {len(contents)} records")
        
        # Process and import
        imported_count = 0
        
        for record in contents:
            try:
                # Parse content
                html_content = record.get('HtmlContent', '')
                service_type, org_name, address = parse_html_content(html_content)
                
                if not service_type or not org_name:
                    continue
                    
                # Get coordinates
                lat = record.get('Latitude')
                lng = record.get('Longitude')
                
                if not lat or not lng:
                    continue
                
                location_id = f"caritas_quick_{record.get('Id', imported_count)}"
                
                # Check if already exists
                if HierarchicalLocation.objects.filter(location_id=location_id).exists():
                    continue
                
                # Create location
                location = HierarchicalLocation.objects.create(
                    location_id=location_id,
                    name=org_name,
                    description=f"{service_type} - {org_name}",
                    latitude=float(lat),
                    longitude=float(lng),
                    street=address or '',
                )
                
                # Find/create category
                category_key = None
                service_lower = service_type.lower()
                
                for key in category_mapping.keys():
                    if key in service_lower:
                        category_key = category_mapping[key]
                        break
                
                if not category_key:
                    category_key = 'allgemein'
                
                # Get or create category
                category, created = HierarchicalCategory.objects.get_or_create(
                    domain=domain,
                    category_id=category_key,
                    defaults={
                        'name': service_type,
                        'description': f'Caritas - {service_type}',
                        'color': '#3498db',
                        'icon': 'fas fa-hands-helping'
                    }
                )
                
                # Link location to category
                location.categories.add(category)
                
                imported_count += 1
                
                if imported_count % 10 == 0:
                    print(f"  ✅ Imported {imported_count} locations...")
                    
            except Exception as e:
                print(f"  ⚠️ Skip record {record.get('Id', '?')}: {e}")
                continue
        
        print(f"\n🎉 HOÀN THÀNH!")
        print(f"📍 Imported: {imported_count} new locations")
        
        # Final stats
        total_caritas = HierarchicalLocation.objects.filter(
            categories__domain__domain_id='caritas_deutschland'
        ).distinct().count()
        
        print(f"📊 Total Caritas locations: {total_caritas}")
        
        print(f"\n🔗 Test at: http://127.0.0.1:8000/embed/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    quick_caritas_import()