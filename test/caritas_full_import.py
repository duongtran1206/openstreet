#!/usr/bin/env python3
"""
Caritas Full Data Import - Download và import tất cả 516 records
"""

import sys
import os
import json
import requests
from bs4 import BeautifulSoup
import time

# Thêm Django path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapproject.settings')

import django
django.setup()

from maps.models import Domain, HierarchicalCategory, HierarchicalLocation

class CaritasFullImporter:
    """Import toàn bộ dữ liệu Caritas"""
    
    def __init__(self):
        self.base_url = "https://www.caritas.de/Services/MappingService.svc/GetMapContents/ec7e69ee-35b9-45b9-b081-fc7a191a76c0/"
        self.datasource = "80c48846275643e0b82b83465979eb70"
        
        # Service type mapping
        self.category_mapping = {
            'jugendmigrationsdienst': 'Jugendmigrationsdienst',
            'migrationsberatung für erwachsene': 'Migrationsberatung für Erwachsene',
            'migrationsberatung': 'Migrationsberatung',
            'gemeinwesenorientierte arbeit': 'Gemeinwesenorientierte Arbeit',
            'iq - faire integration': 'IQ - Faire Integration',
            'beratungszentrum': 'Beratungszentrum',
        }
        
    def download_all_data(self):
        """Download tất cả dữ liệu từ API"""
        print("🔄 Downloading toàn bộ dữ liệu Caritas...")
        
        all_data = []
        page = 0
        pagesize = 50
        
        while True:
            url = f"{self.base_url}?datasource={self.datasource}&page={page}&pagesize={pagesize}"
            
            try:
                print(f"📥 Page {page + 1}...", end=" ")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                contents = data.get('Contents', [])
                
                if not contents:
                    print("✅ Hoàn thành!")
                    break
                    
                all_data.extend(contents)
                print(f"({len(contents)} records)")
                
                page += 1
                time.sleep(0.5)  # Tránh spam API
                
                # Safety check
                if page > 20:  # Max 20 pages = 1000 records
                    print("⚠️ Đã đạt giới hạn an toàn")
                    break
                    
            except Exception as e:
                print(f"❌ Lỗi tại page {page}: {e}")
                break
                
        print(f"📊 Tổng cộng tải về: {len(all_data)} records")
        return all_data
        
    def parse_html_content(self, html_content):
        """Parse HTML content để extract thông tin"""
        if not html_content:
            return None, None, None, None
            
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
            
        # Address
        address = None
        venue_info = soup.find('div', class_='venue-info')
        if venue_info:
            address_parts = []
            for p in venue_info.find_all('p'):
                text = p.text.strip()
                if text and not text.startswith('Tel:') and not text.startswith('E-Mail:'):
                    address_parts.append(text)
            address = ', '.join(address_parts)
            
        # Contact
        contact = {}
        if venue_info:
            for p in venue_info.find_all('p'):
                text = p.text.strip()
                if text.startswith('Tel:'):
                    contact['phone'] = text.replace('Tel:', '').strip()
                elif text.startswith('E-Mail:'):
                    contact['email'] = text.replace('E-Mail:', '').strip()
                    
        return service_type, org_name, address, contact
        
    def categorize_service_type(self, service_type):
        """Phân loại service type"""
        if not service_type:
            return 'allgemein'
            
        service_lower = service_type.lower()
        
        for key, _ in self.category_mapping.items():
            if key in service_lower:
                return key.replace(' ', '_').replace('-', '_')
                
        return 'allgemein'
        
    def import_to_django(self, all_data):
        """Import toàn bộ data vào Django"""
        print("\n🚀 Bắt đầu import vào Django...")
        
        # 1. Create/Update Domain
        domain, created = Domain.objects.get_or_create(
            domain_id='caritas_deutschland',
            defaults={
                'name': 'Caritas Deutschland',
                'description': 'Caritas Deutschland - Soziale Dienste und Migrationsberatung',
                'country': 'Germany',
                'language': 'de'
            }
        )
        
        if created:
            print("✅ Created domain: Caritas Deutschland")
        else:
            print("🔄 Updated domain: Caritas Deutschland")
            
        # 2. Collect all categories
        categories_found = set()
        processed_records = []
        
        print("📊 Analyzing categories...")
        for record in all_data:
            html_content = record.get('HtmlContent', '')
            service_type, org_name, address, contact = self.parse_html_content(html_content)
            
            if service_type and org_name:
                category_id = self.categorize_service_type(service_type)
                categories_found.add((category_id, service_type))
                
                processed_records.append({
                    'record': record,
                    'service_type': service_type,
                    'org_name': org_name,
                    'address': address,
                    'contact': contact,
                    'category_id': category_id
                })
                
        print(f"🎯 Found {len(categories_found)} unique categories")
        print(f"📋 Processed {len(processed_records)} valid records")
        
        # 3. Create Categories
        category_objects = {}
        for category_id, service_type in categories_found:
            display_name = self.category_mapping.get(service_type.lower(), service_type)
            
            category, created = HierarchicalCategory.objects.get_or_create(
                domain=domain,
                category_id=category_id,
                defaults={
                    'name': display_name,
                    'description': f'Caritas - {display_name}',
                    'color': self.get_category_color(category_id),
                    'icon': 'fas fa-hands-helping'
                }
            )
            
            category_objects[category_id] = category
            
            if created:
                print(f"✅ Created category: {display_name}")
            else:
                print(f"🔄 Found category: {display_name}")
                
        # 4. Create Locations
        location_count = 0
        for item in processed_records:
            record = item['record']
            
            # Parse coordinates
            lat = record.get('Latitude')
            lng = record.get('Longitude')
            
            if not lat or not lng:
                continue
                
            location_id = f"caritas_{record.get('Id', location_count)}"
            
            location, created = HierarchicalLocation.objects.get_or_create(
                location_id=location_id,
                defaults={
                    'name': item['org_name'],
                    'description': f"{item['service_type']} - {item['org_name']}",
                    'latitude': float(lat),
                    'longitude': float(lng),
                    'address': item['address'] or '',
                    'contact_info': json.dumps(item['contact'])
                    # Note: domain relationship through categories
                }
            )
            
            # Add to category
            category = category_objects.get(item['category_id'])
            if category:
                location.categories.add(category)
                
            if created:
                location_count += 1
                if location_count % 50 == 0:
                    print(f"📍 Imported {location_count} locations...")
                    
        print(f"✅ Total imported: {location_count} locations")
        
        return domain, category_objects, location_count
        
    def get_category_color(self, category_id):
        """Màu sắc cho từng category"""
        colors = {
            'jugendmigrationsdienst': '#e74c3c',
            'migrationsberatung_für_erwachsene': '#3498db',
            'migrationsberatung': '#f39c12',
            'gemeinwesenorientierte_arbeit': '#2ecc71',
            'iq_faire_integration': '#e67e22',
            'beratungszentrum': '#9b59b6',
            'allgemein': '#95a5a6'
        }
        return colors.get(category_id, '#95a5a6')
        
    def run_full_import(self):
        """Chạy toàn bộ quy trình import"""
        try:
            # Download data
            all_data = self.download_all_data()
            
            if not all_data:
                print("❌ Không có dữ liệu để import")
                return
                
            # Import to Django
            domain, categories, location_count = self.import_to_django(all_data)
            
            print("\n🎉 HOÀN THÀNH IMPORT:")
            print(f"📊 Domain: {domain.name}")
            print(f"🏷️ Categories: {len(categories)}")
            print(f"📍 Locations: {location_count}")
            
            print("\n🔗 Test URLs:")
            print(f"Main: http://127.0.0.1:8000/")
            print(f"Embed: http://127.0.0.1:8000/embed/")
            print(f"API: http://127.0.0.1:8000/api/hierarchical/locations/?domain=caritas_deutschland")
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    importer = CaritasFullImporter()
    importer.run_full_import()