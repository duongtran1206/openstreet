#!/usr/bin/env python
"""
Import Caritas data directly from API into 3-tier Django models
URL: https://www.caritas.de/Services/MappingService.svc/GetMapContents/ec7e69ee-35b9-45b9-b081-fc7a191a76c0/?page=0&pagesize=10
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapproject.settings')
django.setup()

from maps.hierarchical_models import Domain, HierarchicalCategory, HierarchicalLocation

def download_caritas_data():
    """Download all Caritas data from API"""
    print("🚀 Downloading Caritas data from official API...")
    
    base_url = "https://www.caritas.de/Services/MappingService.svc/GetMapContents/ec7e69ee-35b9-45b9-b081-fc7a191a76c0/"
    
    all_locations = []
    categories_set = set()
    page = 0
    pagesize = 50
    
    while True:
        url = f"{base_url}?page={page}&pagesize={pagesize}"
        print(f"📥 Downloading page {page + 1}...")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            response_data = response.json()
            
            # API returns dict with 'Contents' key containing the locations
            if 'Contents' not in response_data or len(response_data['Contents']) == 0:
                print(f"✅ No more data on page {page + 1}")
                break
                
            data = response_data['Contents']
            print(f"   Found {len(data)} locations")
            all_locations.extend(data)
            
            # Collect categories from Caritas data (derive from titles/content)
            for location in data:
                title = location.get('Title', '')
                
                # Extract category hints from title
                category_keywords = [
                    'Migrationsdienst', 'Beratung', 'Familienzentrum', 
                    'Kindergarten', 'Pflege', 'Jugend', 'Sozial',
                    'Suchtkranken', 'Altenhilfe', 'Hospiz'
                ]
                
                for keyword in category_keywords:
                    if keyword.lower() in title.lower():
                        categories_set.add(keyword)
                        break
            
            # If we got less than pagesize, this is the last page
            if len(data) < pagesize:
                break
                
            page += 1
            
        except requests.RequestException as e:
            print(f"❌ Error downloading page {page + 1}: {e}")
            break
    
    print(f"✅ Downloaded {len(all_locations)} total locations")
    print(f"✅ Found {len(categories_set)} unique categories")
    
    return all_locations, list(categories_set)

def create_domain():
    """Create Caritas domain"""
    domain, created = Domain.objects.get_or_create(
        domain_id='caritas_deutschland',
        defaults={
            'name': 'Caritas Deutschland',
            'description': 'Caritas Deutschland - Soziale Dienste und Beratung',
            'country': 'Germany',
            'language': 'de',
            'color_scheme': 'caritas_red',
            'icon': 'Caritas',
            'is_active': True,
            'featured': True,
            'source_url': 'https://www.caritas.de'
        }
    )
    
    if created:
        print(f"✅ Created domain: {domain.name}")
    else:
        print(f"ℹ️ Domain already exists: {domain.name}")
    
    return domain

def create_categories(domain, category_names):
    """Create categories for domain"""
    print(f"🏷️ Creating {len(category_names)} categories...")
    
    created_categories = {}
    
    for i, cat_name in enumerate(category_names):
        # Generate unique category_id
        category_id = f"caritas_{cat_name.lower().replace(' ', '_').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')}"
        
        # Colors for categories
        colors = [
            '#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6',
            '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#16a085'
        ]
        
        category, created = HierarchicalCategory.objects.get_or_create(
            category_id=category_id,
            domain=domain,
            defaults={
                'name': cat_name,
                'color': colors[i % len(colors)],
                'icon': 'Caritas',
                'is_active': True,
                'external_id': cat_name
            }
        )
        
        created_categories[cat_name] = category
        
        if created:
            print(f"   ✅ Created category: {cat_name}")
        else:
            print(f"   ℹ️ Category exists: {cat_name}")
    
    return created_categories

def create_locations(domain, locations_data, categories_map):
    """Create locations for domain"""
    print(f"📍 Creating {len(locations_data)} locations...")
    
    created_count = 0
    
    for location_data in locations_data:
        try:
            # Extract data from Caritas API format
            title = location_data.get('Title', '').strip()
            if not title:
                continue
                
            # Coordinates
            lat = location_data.get('Latitude')
            lng = location_data.get('Longitude')
            
            if not lat or not lng:
                continue
            
            # Parse HTML content for address and contact info
            contents_html = location_data.get('Contents', '')
            popup_html = location_data.get('Popup', '')
            
            # Use BeautifulSoup to parse HTML
            from bs4 import BeautifulSoup
            import re
            
            # Combine both HTML sources
            combined_html = contents_html + ' ' + popup_html
            soup = BeautifulSoup(combined_html, 'html.parser')
            text_content = soup.get_text()
            
            # Extract address (look for patterns like street, city, postal code)
            phone = ''
            email = ''
            
            # Find phone
            phone_patterns = [r'Fon[:\s]*([+0-9\s\(\)\-/]+)', r'Tel[^:]*:?\s*([+0-9\s\(\)\-/]+)']
            for pattern in phone_patterns:
                match = re.search(pattern, text_content)
                if match:
                    phone = match.group(1).strip()
                    break
            
            # Find email
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text_content)
            if email_match:
                email = email_match.group(0)
            
            # Find address (simple heuristic)
            street = ''
            city = ''
            postal_code = ''
            
            # Look for postal code pattern (German format: 5 digits)
            postal_match = re.search(r'\b(\d{5})\s+([A-Za-zäöüß\s]+)', text_content)
            if postal_match:
                postal_code = postal_match.group(1)
                city = postal_match.group(2).strip()
            
            # Look for street (line before postal code)
            if postal_code:
                postal_index = text_content.find(postal_code)
                if postal_index > 0:
                    before_postal = text_content[:postal_index].strip()
                    lines_before = [l for l in before_postal.split('\n') if l.strip()]
                    if lines_before:
                        # Take the last line before postal code as street
                        potential_street = lines_before[-1].strip()
                        if len(potential_street) > 5 and not any(x in potential_street.lower() for x in ['telefon', 'fon', 'fax', 'email']):
                            street = potential_street
            
            # Generate unique location_id
            location_id = f"caritas_{location_data.get('ContentID', title)}"[:100]
            
            # Create location
            location, created = HierarchicalLocation.objects.get_or_create(
                location_id=location_id,
                defaults={
                    'name': title,
                    'latitude': float(lat),
                    'longitude': float(lng),
                    'street': street,
                    'city': city,
                    'postal_code': postal_code,
                    'phone': phone,
                    'email': email,
                    'website': '',
                    'description': text_content[:500] if text_content else '',
                    'is_active': True,
                    'source_name': 'Caritas Deutschland'
                }
            )
            
            if created:
                created_count += 1
                print(f"   ✅ {title[:50]}...")
                
        except Exception as e:
            print(f"   ❌ Error creating location {location_data.get('Title', 'Unknown')}: {e}")
            continue
    
    print(f"✅ Created {created_count} new locations")
    return created_count

def main():
    print("🚀 CARITAS DEUTSCHLAND DATA IMPORT")
    print("=" * 50)
    
    # Download data
    locations_data, category_names = download_caritas_data()
    
    if not locations_data:
        print("❌ No data downloaded, exiting")
        return
    
    # Create domain
    domain = create_domain()
    
    # Create categories
    categories_map = create_categories(domain, category_names)
    
    # Create locations
    locations_count = create_locations(domain, locations_data, categories_map)
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 IMPORT COMPLETED!")
    print(f"📁 Domain: {domain.name}")
    print(f"🏷️ Categories: {len(category_names)}")
    print(f"📍 Locations: {locations_count}")
    print("\n🔗 URLs to test:")
    print("   Main: http://127.0.0.1:8000/hierarchical/")
    print("   API: http://127.0.0.1:8000/api/hierarchical/domains/")
    print(f"   Categories: http://127.0.0.1:8000/api/hierarchical/categories/?domain=caritas_deutschland")

if __name__ == '__main__':
    main()