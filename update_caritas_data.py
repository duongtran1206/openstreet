#!/usr/bin/env python
"""
Update Caritas data from new API endpoint
URL: https://www.caritas.de/Services/MappingService.svc/GetMapData/ec7e69ee-35b9-45b9-b081-fc7a191a76c0/?datasource=80c48846275643e0b82b83465979eb70
"""

import os
import sys
import django
import requests
import json
from django.utils.text import slugify
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapproject.settings')
django.setup()

from maps.hierarchical_models import Domain, HierarchicalCategory, HierarchicalLocation

def download_caritas_new_data():
    """Download Caritas data from new API endpoint"""
    print("🚀 Downloading Caritas data from new API endpoint...")
    
    url = "https://www.caritas.de/Services/MappingService.svc/GetMapData/ec7e69ee-35b9-45b9-b081-fc7a191a76c0/?datasource=80c48846275643e0b82b83465979eb70"
    
    try:
        print(f"📥 Fetching data from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Status: {response.status_code}")
        print(f"📋 Content-Type: {response.headers.get('content-type')}")
        
        data = response.json()
        print(f"📊 Data type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"📋 Keys: {list(data.keys())}")
            
            # Check for Caritas API structure
            if 'Clusters' in data:
                clusters = data['Clusters']
                print(f"✅ Found {len(clusters)} clusters")
                
                # Extract markers from clusters
                locations = []
                for cluster in clusters:
                    if 'Markers' in cluster:
                        markers = cluster['Markers']
                        locations.extend(markers)
                        print(f"   📍 Cluster has {len(markers)} markers")
                
                print(f"✅ Total markers extracted: {len(locations)}")
                
            elif 'Contents' in data:
                locations = data['Contents']
                print(f"✅ Found {len(locations)} locations in Contents")
            elif 'Data' in data:
                locations = data['Data']
                print(f"✅ Found {len(locations)} locations in Data")
            else:
                # Show first few keys to understand structure
                for key, value in list(data.items())[:5]:
                    print(f"  {key}: {type(value)} -> {str(value)[:100]}...")
                locations = []
        elif isinstance(data, list):
            locations = data
            print(f"✅ Found {len(locations)} locations as direct array")
        else:
            print(f"❌ Unexpected data type: {type(data)}")
            locations = []
            
        return locations
        
    except requests.RequestException as e:
        print(f"❌ Error downloading data: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return []

def clear_existing_caritas_data():
    """Clear existing Caritas data"""
    print("🧹 Clearing existing Caritas data...")
    
    # Delete existing Caritas locations
    caritas_locations = HierarchicalLocation.objects.filter(source_name__icontains='Caritas')
    count = caritas_locations.count()
    caritas_locations.delete()
    print(f"   ❌ Deleted {count} existing Caritas locations")
    
    # Delete existing Caritas categories
    try:
        caritas_domain = Domain.objects.get(domain_id='caritas_deutschland')
        caritas_categories = HierarchicalCategory.objects.filter(domain=caritas_domain)
        count = caritas_categories.count()
        caritas_categories.delete()
        print(f"   ❌ Deleted {count} existing Caritas categories")
    except Domain.DoesNotExist:
        print("   ℹ️ No existing Caritas domain found")

def analyze_data_structure(locations_data):
    """Analyze the structure of location data"""
    print("\n🔍 Analyzing data structure...")
    
    if not locations_data:
        print("❌ No data to analyze")
        return {}
    
    # Take first item to analyze structure
    first_item = locations_data[0]
    print(f"📋 First item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
    
    if isinstance(first_item, dict):
        for key, value in first_item.items():
            print(f"  {key}: {type(value)} -> {str(value)[:100] if value else 'None'}...")
    
    # Collect unique keys across all items
    all_keys = set()
    for item in locations_data[:5]:  # Check first 5 items
        if isinstance(item, dict):
            all_keys.update(item.keys())
    
    print(f"\n📊 All unique keys found: {sorted(all_keys)}")
    return {'keys': sorted(all_keys), 'sample': first_item if isinstance(first_item, dict) else None}

def parse_popup_content(popup_html):
    """Parse popup content HTML to extract address and contact info"""
    if not popup_html:
        return {}
    
    # Use BeautifulSoup to parse HTML
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(popup_html, 'html.parser')
    
    info = {}
    
    # Extract address
    venue_div = soup.find('div', class_='venueGoogle')
    if venue_div:
        address_parts = []
        spans = venue_div.find_all('span')
        for span in spans:
            text = span.get_text(strip=True)
            if text and text not in address_parts:
                address_parts.append(text)
        info['address'] = ' '.join(address_parts) if address_parts else ''
    
    # Extract phone
    for span in soup.find_all('span'):
        text = span.get_text(strip=True)
        if text and (text.startswith('+49') or text.startswith('0')):
            if 'phone' not in info:
                info['phone'] = text
            elif 'fax' not in info and 'fax' in span.parent.get_text().lower():
                info['fax'] = text
    
    # Extract email
    email_link = soup.find('a', class_='mail-link')
    if email_link and email_link.get('href'):
        info['email'] = email_link.get('href').replace('mailto:', '')
    
    # Extract website
    for a_tag in soup.find_all('a'):
        href = a_tag.get('href', '')
        if href and href.startswith('http') and 'caritas-' in href:
            info['website'] = href
            break
    
    return info

def import_caritas_data(locations_data):
    """Import Caritas data into the hierarchical model"""
    print("\n🚀 Starting Caritas data import...")
    
    # Clear existing data
    clear_existing_caritas_data()
    
    # Get or create Caritas domain
    caritas_domain, created = Domain.objects.get_or_create(
        domain_id='caritas_deutschland',
        defaults={
            'name': 'Caritas Deutschland',
            'description': 'Caritas Dienststellen in Deutschland',
            'api_endpoint': 'https://www.caritas.de/Services/MappingService.svc/GetMapData/ec7e69ee-35b9-45b9-b081-fc7a191a76c0/?datasource=80c48846275643e0b82b83465979eb70'
        }
    )
    print(f"📁 {'Created' if created else 'Using existing'} Caritas domain")
    
    # Analyze categories from titles
    categories_found = set()
    for location in locations_data:
        title = location.get('Title', '')
        if title:
            # Extract category from title (before comma or first part)
            if ',' in title:
                category = title.split(',')[0].strip()
            else:
                # Take first meaningful part
                words = title.split()
                if len(words) > 2:
                    category = ' '.join(words[:2])
                else:
                    category = title
            categories_found.add(category)
    
    print(f"📋 Found {len(categories_found)} categories")
    
    # Create categories
    category_objects = {}
    category_counter = 1
    for category_name in categories_found:
        if category_name and len(category_name) > 2:
            # Create unique category_id by adding counter if needed
            base_id = slugify(category_name)
            category_id = base_id
            
            # Check if this category_id already exists
            while HierarchicalCategory.objects.filter(
                domain=caritas_domain,
                category_id=category_id
            ).exists():
                category_id = f"{base_id}-{category_counter}"
                category_counter += 1
            
            category_obj, created = HierarchicalCategory.objects.get_or_create(
                domain=caritas_domain,
                name=category_name,
                defaults={'category_id': category_id}
            )
            category_objects[category_name] = category_obj
            print(f"   📂 {'Created' if created else 'Found'} category: {category_name}")
    
    # Import locations
    imported_count = 0
    errors = 0
    
    for location_data in locations_data:
        try:
            title = location_data.get('Title', '')
            lat = location_data.get('Latitude')
            lon = location_data.get('Longitude')
            
            if not title or lat is None or lon is None:
                print(f"⚠️ Skipping location with missing data: {title}")
                continue
            
            # Parse additional info from popup
            popup_info = parse_popup_content(location_data.get('PopupContents', ''))
            
            # Determine category
            category_obj = None
            if ',' in title:
                category_name = title.split(',')[0].strip()
                category_obj = category_objects.get(category_name)
            
            if not category_obj:
                # Use a default category
                default_category, created = HierarchicalCategory.objects.get_or_create(
                    domain=caritas_domain,
                    name='Caritas Einrichtung',
                    defaults={'category_id': 'caritas-einrichtung'}
                )
                category_obj = default_category
            
            # Create location
            location_obj = HierarchicalLocation.objects.create(
                location_id=location_data.get('ContentID', ''),
                name=title,
                latitude=float(lat),
                longitude=float(lon),
                street=popup_info.get('address', ''),
                phone=popup_info.get('phone', ''),
                email=popup_info.get('email', ''),
                website=popup_info.get('website', ''),
                source_name='Caritas Deutschland New API',
                description=f"Caritas Einrichtung: {title}",
                raw_data=location_data
            )
            
            # Add to category
            location_obj.categories.add(category_obj)
            imported_count += 1
            
            if imported_count % 50 == 0:
                print(f"   ✅ Imported {imported_count} locations...")
                
        except Exception as e:
            errors += 1
            print(f"❌ Error importing location {location_data.get('Title', 'Unknown')}: {str(e)}")
            continue
    
    print(f"\n📊 Import Summary:")
    print(f"   ✅ Successfully imported: {imported_count} locations")
    print(f"   ❌ Errors: {errors}")
    print(f"   � Categories created: {len(category_objects)}")
    
    return imported_count, errors

def main():
    print("�🚀 CARITAS DATA UPDATE FROM NEW ENDPOINT")
    print("=" * 60)
    
    # Download data
    locations_data = download_caritas_new_data()
    
    if not locations_data:
        print("❌ No data downloaded, exiting")
        return
    
    # Analyze structure
    structure_info = analyze_data_structure(locations_data)
    
    print(f"\n📊 Summary:")
    print(f"   📍 Total locations found: {len(locations_data)}")
    print(f"   📋 Data keys: {structure_info.get('keys', [])}")
    
    # Ask for confirmation before clearing old data
    print(f"\n⚠️  This will replace existing Caritas data")
    print(f"   Current Caritas locations: {HierarchicalLocation.objects.filter(source_name__icontains='Caritas').count()}")
    
    # Show sample data
    print(f"\n🔍 Sample location data:")
    if structure_info.get('sample'):
        for key, value in structure_info['sample'].items():
            if key in ['Title', 'Latitude', 'Longitude']:
                print(f"   {key}: {value}")
    
    # Proceed with import
    print(f"\n🚀 Proceeding with data import...")
    try:
        imported_count, errors = import_caritas_data(locations_data)
        
        print(f"\n✅ Import completed!")
        print(f"� Final results:")
        print(f"   📍 Locations imported: {imported_count}")
        print(f"   ❌ Errors encountered: {errors}")
        print(f"   📂 Total domains: {Domain.objects.count()}")
        print(f"   📂 Total categories: {HierarchicalCategory.objects.count()}")
        print(f"   📍 Total locations: {HierarchicalLocation.objects.count()}")
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()