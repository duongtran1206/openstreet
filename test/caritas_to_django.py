#!/usr/bin/env python3
"""
Caritas to Django 3-Tier Converter
Chuyển đổi dữ liệu Caritas thành Django fixtures cho hệ thống 3-tier
"""

import json
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time

class CaritasToDjangoConverter:
    """
    Converter chuyển đổi dữ liệu Caritas sang Django 3-tier format
    """
    
    def __init__(self):
        self.base_url = "https://www.caritas.de/Services/MappingService.svc/GetMapContents/ec7e69ee-35b9-45b9-b081-fc7a191a76c0/"
        self.datasource = "80c48846275643e0b82b83465979eb70"
        
        # Category mapping cho Caritas services
        self.category_mapping = {
            'jugendmigrationsdienst': {
                'name': 'Jugendmigrationsdienst', 
                'color': '#FF6B6B',
                'icon': 'Jugend'
            },
            'migrationsberatung für erwachsene': {
                'name': 'Migrationsberatung für Erwachsene',
                'color': '#4ECDC4',
                'icon': 'Erwachsene'
            },
            'migrationsberatung': {
                'name': 'Migrationsberatung',
                'color': '#45B7D1', 
                'icon': 'Beratung'
            },
            'gemeinwesenorientierte arbeit': {
                'name': 'Gemeinwesenorientierte Arbeit',
                'color': '#96CEB4',
                'icon': 'Gemeinwesen'
            },
            'iq - faire integration': {
                'name': 'IQ - Faire Integration',
                'color': '#FFEAA7',
                'icon': 'Integration'
            },
            'beratungszentrum': {
                'name': 'Beratungszentrum',
                'color': '#DDA0DD',
                'icon': 'Zentrum'
            }
        }
        
    def download_sample_data(self, pages=3):
        """Download sample data để test (chỉ vài pages đầu)"""
        print(f"📥 Downloading {pages} pages of Caritas data...")
        
        all_data = []
        
        for page in range(pages):
            url = f"{self.base_url}?datasource={self.datasource}&page={page}&pagesize=20"
            
            try:
                print(f"   Page {page + 1}/{pages}...")
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                contents = data.get('Contents', [])
                all_data.extend(contents)
                
                # Delay để không spam server
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Error downloading page {page}: {e}")
                continue
        
        print(f"✅ Downloaded {len(all_data)} records")
        return all_data
    
    def parse_location_info(self, html_content):
        """Parse HTML content để trích xuất thông tin location"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        info = {
            'service_type': None,
            'organization': None,
            'street': '',
            'city': '',
            'postal_code': '',
            'phone': '',
            'fax': '',
            'email': '',
            'website': ''
        }
        
        # Service type từ h2.kicker
        kicker = soup.find('h2', class_='kicker')
        if kicker:
            info['service_type'] = kicker.get_text().strip().lower()
        
        # Organization name từ h4 link
        org_h4 = soup.find('h4', style=re.compile('color:#3f373f'))
        if org_h4:
            link = org_h4.find('a')
            if link:
                info['organization'] = link.get_text().strip()
        
        # Address từ venue section
        venue = soup.find('div', class_='venueGoogle')
        if venue:
            spans = venue.find_all('span')
            address_parts = [s.get_text().strip() for s in spans if s.get_text().strip() and 'month' not in s.get('class', [])]
            
            if len(address_parts) >= 3:
                info['street'] = address_parts[0]
                info['postal_code'] = address_parts[1] 
                info['city'] = address_parts[2]
            elif len(address_parts) == 2:
                info['street'] = address_parts[0]
                # Parse "12345 CityName" format
                city_match = re.match(r'(\d{5})\s+(.+)', address_parts[1])
                if city_match:
                    info['postal_code'] = city_match.group(1)
                    info['city'] = city_match.group(2)
                else:
                    info['city'] = address_parts[1]
        
        # Contact info từ infoGoogle section
        info_div = soup.find('div', class_='infoGoogle')
        if info_div:
            # Phone
            phone_pattern = r'Fon:\s*</span>.*?<span[^>]*>([^<]+)</span>'
            phone_match = re.search(phone_pattern, str(info_div), re.DOTALL)
            if phone_match:
                info['phone'] = phone_match.group(1).strip()
            
            # Fax  
            fax_pattern = r'Fax:\s*</span>.*?<span[^>]*>([^<]+)</span>'
            fax_match = re.search(fax_pattern, str(info_div), re.DOTALL)
            if fax_match:
                info['fax'] = fax_match.group(1).strip()
        
        # Email từ mail-link
        email_link = soup.find('a', class_='mail-link')
        if email_link and email_link.get('href'):
            href = email_link.get('href')
            if href.startswith('mailto:'):
                info['email'] = href.replace('mailto:', '')
        
        # Website từ ext-link
        web_link = soup.find('a', class_='ext-link')
        if web_link and web_link.get('href'):
            info['website'] = web_link.get('href')
        
        return info
    
    def get_category_id(self, service_type):
        """Chuyển service type thành category ID"""
        if not service_type:
            return 'caritas_allgemein'
        
        service_type = service_type.lower().strip()
        
        # Direct mapping
        if service_type in self.category_mapping:
            return f"caritas_{service_type.replace(' ', '_').replace('-', '_')}"
        
        # Fallback patterns
        if 'jugend' in service_type and 'migration' in service_type:
            return 'caritas_jugendmigrationsdienst'
        elif 'erwachsene' in service_type:
            return 'caritas_migrationsberatung_fuer_erwachsene'
        elif 'migration' in service_type or 'beratung' in service_type:
            return 'caritas_migrationsberatung'
        elif 'integration' in service_type:
            return 'caritas_iq_faire_integration'
        elif 'gemeinwesen' in service_type:
            return 'caritas_gemeinwesenorientierte_arbeit'
        else:
            return 'caritas_allgemein'
    
    def convert_to_django_fixtures(self, raw_data):
        """Chuyển đổi raw data thành Django fixtures"""
        print("🔄 Converting to Django 3-tier format...")
        
        fixtures = []
        
        # 1. DOMAIN - Caritas Deutschland
        domain_fixture = {
            "model": "maps.domain",
            "pk": "caritas_deutschland", 
            "fields": {
                "name": "Caritas Deutschland",
                "description": "Caritas Deutschland - Soziale Dienste und Migrationsberatung",
                "country": "Germany",
                "language": "de",
                "color_scheme": "caritas_red",
                "icon": "Caritas",
                "is_active": True,
                "featured": True,
                "source_url": "https://www.caritas.de"
            }
        }
        fixtures.append(domain_fixture)
        
        # 2. CATEGORIES - Thu thập unique service types
        unique_services = set()
        processed_locations = []
        
        for idx, item in enumerate(raw_data):
            try:
                parsed_info = self.parse_location_info(item.get('Contents', ''))
                service_type = parsed_info.get('service_type')
                
                if service_type:
                    unique_services.add(service_type)
                
                # Process location
                category_id = self.get_category_id(service_type)
                
                location_data = {
                    'location_id': f"caritas_{item.get('ContentID', f'loc_{idx}')}",
                    'name': item.get('Title', 'Caritas Standort'),
                    'latitude': float(item.get('Latitude', 0)),
                    'longitude': float(item.get('Longitude', 0)),
                    'street': parsed_info.get('street', ''),
                    'city': parsed_info.get('city', ''),
                    'postal_code': parsed_info.get('postal_code', ''),
                    'country': 'Germany',
                    'phone': parsed_info.get('phone', ''),
                    'fax': parsed_info.get('fax', ''),
                    'email': parsed_info.get('email', ''),
                    'website': parsed_info.get('website', ''),
                    'description': parsed_info.get('organization', ''),
                    'category_ids': [category_id],
                    'raw_data': {
                        'content_id': item.get('ContentID'),
                        'data_source_id': item.get('DataSourceID'),
                        'service_type': service_type,
                        'original_title': item.get('Title')
                    }
                }
                
                processed_locations.append(location_data)
                
            except Exception as e:
                print(f"   ❌ Error processing item {idx}: {e}")
                continue
        
        # Tạo category fixtures từ unique services
        used_categories = set()
        for loc in processed_locations:
            used_categories.update(loc['category_ids'])
        
        for category_id in used_categories:
            # Lấy thông tin category
            base_name = category_id.replace('caritas_', '').replace('_', ' ')
            
            # Tìm mapping info
            category_info = None
            for service_key, info in self.category_mapping.items():
                if service_key.replace(' ', '_').replace('-', '_') in category_id:
                    category_info = info
                    break
            
            if not category_info:
                category_info = {
                    'name': base_name.title(),
                    'color': '#3388ff', 
                    'icon': 'Caritas'
                }
            
            category_fixture = {
                "model": "maps.hierarchicalcategory",
                "pk": category_id,
                "fields": {
                    "name": category_info['name'],
                    "domain_id": "caritas_deutschland",
                    "color": category_info['color'],
                    "icon": category_info['icon'],
                    "description": f"Caritas {category_info['name']} Dienste",
                    "is_active": True,
                    "source_identifier": category_id.replace('caritas_', '')
                }
            }
            fixtures.append(category_fixture)
        
        # 3. LOCATIONS
        for loc_data in processed_locations:
            location_fixture = {
                "model": "maps.hierarchicallocation",
                "pk": loc_data['location_id'],
                "fields": {
                    "name": loc_data['name'],
                    "latitude": loc_data['latitude'],
                    "longitude": loc_data['longitude'],
                    "street": loc_data['street'],
                    "city": loc_data['city'],
                    "postal_code": loc_data['postal_code'],
                    "country": loc_data['country'],
                    "phone": loc_data['phone'],
                    "fax": loc_data['fax'],
                    "email": loc_data['email'],
                    "website": loc_data['website'],
                    "description": loc_data['description'],
                    "is_active": True,
                    "verified": False,
                    "source_name": "Caritas Deutschland API",
                    "raw_data": loc_data['raw_data']
                }
            }
            fixtures.append(location_fixture)
        
        print(f"✅ Created {len(fixtures)} fixtures:")
        print(f"   - 1 Domain")
        print(f"   - {len(used_categories)} Categories") 
        print(f"   - {len(processed_locations)} Locations")
        
        return fixtures
    
    def save_fixtures(self, fixtures, filename=None):
        """Lưu Django fixtures"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'caritas_django_fixtures_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(fixtures, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved Django fixtures: {filename}")
        return filename

def main():
    """Main function"""
    print("🚀 Caritas to Django 3-Tier Converter")
    print("="*60)
    
    converter = CaritasToDjangoConverter()
    
    # Download sample data (3 pages = ~60 locations)
    raw_data = converter.download_sample_data(pages=3)
    
    if raw_data:
        # Convert to Django fixtures
        fixtures = converter.convert_to_django_fixtures(raw_data)
        
        # Save fixtures
        fixtures_file = converter.save_fixtures(fixtures)
        
        print("="*60)
        print("✅ Conversion completed!")
        print(f"📁 Fixtures file: {fixtures_file}")
        print("\n🔧 To import into Django:")
        print(f"   python manage.py loaddata {fixtures_file}")
        print("\n📍 Next steps:")
        print("   1. Copy fixtures file to Django project root")
        print("   2. Run loaddata command")
        print("   3. Create many-to-many relationships between locations and categories")
        
    else:
        print("❌ No data downloaded")

if __name__ == "__main__":
    main()