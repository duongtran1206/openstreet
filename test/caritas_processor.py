#!/usr/bin/env python3
"""
Caritas Data Processing Tool
Chuyển đổi dữ liệu Caritas thành định dạng 3-tier hierarchical
"""

import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os

class CaritasDataProcessor:
    """
    Tool để xử lý dữ liệu từ API Caritas
    """
    
    def __init__(self):
        self.base_url = "https://www.caritas.de/Services/MappingService.svc/GetMapContents/ec7e69ee-35b9-45b9-b081-fc7a191a76c0/"
        self.datasource = "80c48846275643e0b82b83465979eb70"
        self.raw_data = []
        self.processed_data = {
            'domain': {},
            'categories': [],
            'locations': []
        }
        
    def download_all_pages(self, max_pages=None):
        """Download tất cả data từ API Caritas"""
        print("🔄 Đang download dữ liệu Caritas...")
        
        page = 0
        pagesize = 50  # Tăng pagesize để giảm số request
        
        while True:
            url = f"{self.base_url}?datasource={self.datasource}&page={page}&pagesize={pagesize}"
            
            try:
                print(f"📥 Downloading page {page + 1}...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                contents = data.get('Contents', [])
                
                if not contents:
                    break
                    
                self.raw_data.extend(contents)
                
                # Kiểm tra xem còn trang nào không
                if len(contents) < pagesize:
                    break
                    
                # Kiểm tra max_pages limit
                if max_pages and page >= max_pages - 1:
                    break
                    
                page += 1
                
                # Delay để không spam server
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Lỗi download page {page}: {e}")
                break
        
        print(f"✅ Đã download {len(self.raw_data)} records")
        return len(self.raw_data)
    
    def parse_html_content(self, html_content):
        """Parse HTML để trích xuất thông tin"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        info = {
            'service_type': None,
            'organization': None,
            'address': None,
            'phone': None,
            'fax': None,
            'email': None,
            'website': None
        }
        
        # Trích xuất service type từ h2.kicker
        kicker = soup.find('h2', class_='kicker')
        if kicker:
            info['service_type'] = kicker.get_text().strip()
        
        # Trích xuất organization name từ h4 > a
        org_link = soup.find('h4', style=re.compile('color:#3f373f'))
        if org_link:
            link = org_link.find('a')
            if link:
                info['organization'] = link.get_text().strip()
        
        # Trích xuất địa chỉ từ venue section
        venue = soup.find('div', class_='venueGoogle')
        if venue:
            address_parts = []
            spans = venue.find_all('span')
            for span in spans:
                text = span.get_text().strip()
                if text and not text == 'month':
                    address_parts.append(text)
            info['address'] = ', '.join(address_parts) if address_parts else None
        
        # Trích xuất phone/fax
        info_section = soup.find('div', class_='infoGoogle')
        if info_section:
            # Phone
            phone_div = info_section.find('span', string='Fon:')
            if phone_div:
                phone_sibling = phone_div.find_next_sibling()
                if phone_sibling:
                    info['phone'] = phone_sibling.get_text().strip()
            
            # Fax
            fax_div = info_section.find('span', string='Fax:')
            if fax_div:
                fax_sibling = fax_div.find_next_sibling()
                if fax_sibling:
                    info['fax'] = fax_sibling.get_text().strip()
        
        # Trích xuất email
        email_link = soup.find('a', class_='mail-link')
        if email_link and email_link.get('href'):
            href = email_link.get('href')
            if href.startswith('mailto:'):
                info['email'] = href.replace('mailto:', '')
        
        # Trích xuất website
        web_link = soup.find('a', class_='ext-link')
        if web_link and web_link.get('href'):
            info['website'] = web_link.get('href')
        
        return info
    
    def categorize_service_type(self, service_type):
        """Chuyển đổi service type thành category ID"""
        if not service_type:
            return 'allgemein'
        
        service_type = service_type.lower()
        
        # Mapping rules
        category_mapping = {
            'jugendmigrationsdienst': 'jugendmigrationsdienst',
            'migrationsberatung für erwachsene': 'migrationsberatung_erwachsene', 
            'migrationsberatung': 'migrationsberatung',
            'gemeinwesenorientierte arbeit': 'gemeinwesenorientierte_arbeit',
            'iq - faire integration': 'iq_faire_integration',
            'beratungszentrum': 'beratungszentrum',
            'flüchtlings- und migrationsberatung': 'fluechtlingsberatung'
        }
        
        # Tìm exact match
        for key, value in category_mapping.items():
            if key in service_type:
                return value
        
        # Fallback categories
        if 'migration' in service_type:
            return 'migrationsberatung'
        elif 'beratung' in service_type:
            return 'beratungszentrum'
        else:
            return 'allgemein'
    
    def process_data(self):
        """Xử lý dữ liệu raw thành format 3-tier"""
        print("🔄 Đang xử lý dữ liệu...")
        
        # Tạo Domain
        self.processed_data['domain'] = {
            'domain_id': 'caritas_deutschland',
            'name': 'Caritas Deutschland',
            'description': 'Caritas Deutschland - Dịch vụ xã hội và tư vấn di cư',
            'country': 'Germany',
            'language': 'de',
            'color_scheme': 'caritas',
            'icon': 'Caritas',
            'source_url': 'https://www.caritas.de'
        }
        
        # Thu thập tất cả service types để tạo categories
        service_types = set()
        locations = []
        
        for idx, item in enumerate(self.raw_data):
            try:
                # Parse HTML content
                parsed_info = self.parse_html_content(item.get('Contents', ''))
                
                # Thu thập service type
                service_type = parsed_info.get('service_type')
                if service_type:
                    service_types.add(service_type)
                
                # Tạo location
                category_id = self.categorize_service_type(service_type)
                
                location = {
                    'location_id': f"caritas_{item.get('ContentID', idx)}",
                    'name': item.get('Title', 'Caritas Location'),
                    'latitude': float(item.get('Latitude', 0)),
                    'longitude': float(item.get('Longitude', 0)),
                    'street': '',
                    'city': '',
                    'postal_code': '',
                    'country': 'Germany',
                    'phone': parsed_info.get('phone', ''),
                    'fax': parsed_info.get('fax', ''),
                    'email': parsed_info.get('email', ''),
                    'website': parsed_info.get('website', ''),
                    'description': parsed_info.get('organization', ''),
                    'categories': [category_id],
                    'raw_data': {
                        'original_content': item.get('Contents', ''),
                        'popup': item.get('Popup', ''),
                        'data_source_id': item.get('DataSourceID', ''),
                        'service_type': service_type
                    }
                }
                
                # Parse address thành components
                if parsed_info.get('address'):
                    address_parts = parsed_info['address'].split(', ')
                    if len(address_parts) >= 2:
                        location['street'] = address_parts[0]
                        # Parse postal code và city
                        last_part = address_parts[-1]
                        if len(address_parts) >= 2:
                            city_part = address_parts[1]
                            # Tách postal code và city (format: "12345 CityName")
                            city_match = re.match(r'(\d{5})\s+(.+)', city_part)
                            if city_match:
                                location['postal_code'] = city_match.group(1)
                                location['city'] = city_match.group(2)
                            else:
                                location['city'] = city_part
                
                locations.append(location)
                
            except Exception as e:
                print(f"❌ Lỗi xử lý location {idx}: {e}")
                continue
        
        # Tạo Categories từ service types đã thu thập
        categories = []
        category_colors = {
            'jugendmigrationsdienst': '#FF6B6B',
            'migrationsberatung_erwachsene': '#4ECDC4', 
            'migrationsberatung': '#45B7D1',
            'gemeinwesenorientierte_arbeit': '#96CEB4',
            'iq_faire_integration': '#FFEAA7',
            'beratungszentrum': '#DDA0DD',
            'fluechtlingsberatung': '#98D8C8',
            'allgemein': '#F7DC6F'
        }
        
        category_names = {
            'jugendmigrationsdienst': 'Jugendmigrationsdienst',
            'migrationsberatung_erwachsene': 'Migrationsberatung für Erwachsene',
            'migrationsberatung': 'Migrationsberatung',
            'gemeinwesenorientierte_arbeit': 'Gemeinwesenorientierte Arbeit',
            'iq_faire_integration': 'IQ - Faire Integration',
            'beratungszentrum': 'Beratungszentrum',
            'fluechtlingsberatung': 'Flüchtlings- und Migrationsberatung',
            'allgemein': 'Allgemeine Beratung'
        }
        
        # Tạo categories dựa trên dữ liệu thực
        used_categories = set()
        for location in locations:
            used_categories.update(location['categories'])
        
        for category_id in used_categories:
            categories.append({
                'category_id': category_id,
                'name': category_names.get(category_id, category_id.title()),
                'domain_id': 'caritas_deutschland',
                'color': category_colors.get(category_id, '#3388ff'),
                'icon': 'Beratung',
                'description': f'Caritas {category_names.get(category_id, category_id.title())} Services',
                'source_identifier': category_id
            })
        
        self.processed_data['categories'] = categories
        self.processed_data['locations'] = locations
        
        print(f"✅ Xử lý hoàn thành:")
        print(f"   - Domain: 1")
        print(f"   - Categories: {len(categories)}")
        print(f"   - Locations: {len(locations)}")
        
    def save_data(self, output_dir='test'):
        """Lưu dữ liệu đã xử lý"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Lưu raw data
        raw_file = os.path.join(output_dir, f'caritas_raw_data_{timestamp}.json')
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(self.raw_data, f, ensure_ascii=False, indent=2)
        
        # Lưu processed data  
        processed_file = os.path.join(output_dir, f'caritas_processed_data_{timestamp}.json')
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump(self.processed_data, f, ensure_ascii=False, indent=2)
        
        # Lưu Django fixtures
        fixtures_file = os.path.join(output_dir, f'caritas_fixtures_{timestamp}.json')
        fixtures = []
        
        # Domain fixture
        fixtures.append({
            "model": "maps.domain",
            "pk": self.processed_data['domain']['domain_id'],
            "fields": {k: v for k, v in self.processed_data['domain'].items() if k != 'domain_id'}
        })
        
        # Category fixtures
        for cat in self.processed_data['categories']:
            fixtures.append({
                "model": "maps.hierarchicalcategory",
                "pk": cat['category_id'],
                "fields": {k: v for k, v in cat.items() if k != 'category_id'}
            })
        
        # Location fixtures
        for loc in self.processed_data['locations']:
            fixtures.append({
                "model": "maps.hierarchicallocation", 
                "pk": loc['location_id'],
                "fields": {k: v for k, v in loc.items() if k != 'location_id'}
            })
        
        with open(fixtures_file, 'w', encoding='utf-8') as f:
            json.dump(fixtures, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Đã lưu dữ liệu:")
        print(f"   - Raw data: {raw_file}")
        print(f"   - Processed: {processed_file}")
        print(f"   - Django fixtures: {fixtures_file}")
        
        return fixtures_file

def main():
    """Main function"""
    print("🚀 Caritas Data Processing Tool")
    print("="*50)
    
    processor = CaritasDataProcessor()
    
    # Download data (test với 5 pages đầu tiên)
    count = processor.download_all_pages(max_pages=5)
    
    if count > 0:
        # Process data
        processor.process_data()
        
        # Save data
        fixtures_file = processor.save_data()
        
        print("="*50)
        print("✅ Hoàn thành! Để import vào Django:")
        print(f"   python manage.py loaddata {fixtures_file}")
        
    else:
        print("❌ Không thể download dữ liệu")

if __name__ == "__main__":
    main()