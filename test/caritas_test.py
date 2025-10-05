#!/usr/bin/env python3
"""
Quick Caritas Data Test - Download 1 page only
"""

import json
import requests
from bs4 import BeautifulSoup
import re

def test_caritas_api():
    """Test download và parse 1 page dữ liệu Caritas"""
    print("🧪 Testing Caritas API...")
    
    # URL cho 1 page đầu tiên
    url = "https://www.caritas.de/Services/MappingService.svc/GetMapContents/ec7e69ee-35b9-45b9-b081-fc7a191a76c0/?datasource=80c48846275643e0b82b83465979eb70&page=0&pagesize=5"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        contents = data.get('Contents', [])
        
        print(f"✅ Downloaded {len(contents)} records")
        
        # Test parse HTML cho record đầu tiên
        if contents:
            first_item = contents[0]
            
            print(f"\n📍 Test record:")
            print(f"   Title: {first_item.get('Title')}")
            print(f"   Latitude: {first_item.get('Latitude')}")
            print(f"   Longitude: {first_item.get('Longitude')}")
            
            # Parse HTML content
            html_content = first_item.get('Contents', '')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Trích xuất service type
            kicker = soup.find('h2', class_='kicker')
            service_type = kicker.get_text().strip() if kicker else "Unknown"
            print(f"   Service Type: {service_type}")
            
            # Trích xuất địa chỉ
            venue = soup.find('div', class_='venueGoogle')
            address = "Unknown"
            if venue:
                spans = venue.find_all('span')
                address_parts = [span.get_text().strip() for span in spans if span.get_text().strip()]
                address = ', '.join(address_parts) if address_parts else "Unknown"
            print(f"   Address: {address}")
            
            # Trích xuất phone
            info_section = soup.find('div', class_='infoGoogle')
            phone = "Unknown"
            if info_section:
                phone_span = info_section.find('span', string='Fon:')
                if phone_span:
                    phone_div = phone_span.parent.find_next_sibling()
                    if phone_div:
                        phone = phone_div.get_text().strip()
            print(f"   Phone: {phone}")
            
            # Trích xuất email
            email_link = soup.find('a', class_='mail-link')
            email = "Unknown"
            if email_link and email_link.get('href'):
                href = email_link.get('href')
                if href.startswith('mailto:'):
                    email = href.replace('mailto:', '')
            print(f"   Email: {email}")
        
        # Lưu test data
        test_data = {
            'total_available': data.get('TotalCount', 0),
            'test_sample': contents
        }
        
        with open('caritas_test_data.json', 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Saved test data to: caritas_test_data.json")
        print(f"📊 Total records available: {data.get('TotalCount', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_caritas_api()