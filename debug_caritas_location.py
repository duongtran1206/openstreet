#!/usr/bin/env python
"""
Debug individual Caritas location structure
"""

import requests
import json
from bs4 import BeautifulSoup
import re

def debug_caritas_location():
    url = "https://www.caritas.de/Services/MappingService.svc/GetMapContents/ec7e69ee-35b9-45b9-b081-fc7a191a76c0/?page=0&pagesize=2"
    
    print("🔍 Debugging individual Caritas location...")
    
    try:
        response = requests.get(url, timeout=30)
        data = response.json()
        
        if 'Contents' in data and len(data['Contents']) > 0:
            location = data['Contents'][0]
            
            print(f"\n📍 Location structure:")
            print(f"Type: {type(location)}")
            print(f"Keys: {list(location.keys()) if isinstance(location, dict) else 'Not a dict'}")
            
            if isinstance(location, dict):
                for key, value in location.items():
                    print(f"\n{key}: {type(value)}")
                    if isinstance(value, str) and len(value) > 100:
                        print(f"  Content preview: {value[:200]}...")
                        
                        # If it's HTML content, try to parse
                        if '<' in value and '>' in value:
                            print("  Parsing as HTML...")
                            soup = BeautifulSoup(value, 'html.parser')
                            
                            # Look for common fields
                            text = soup.get_text()
                            print(f"  Text content: {text[:300]}...")
                            
                            # Look for patterns
                            if 'Tel' in text or 'Telefon' in text:
                                tel_match = re.search(r'Tel[^:]*:?\s*([0-9\s\-\(\)\+/]+)', text)
                                if tel_match:
                                    print(f"  Found phone: {tel_match.group(1).strip()}")
                            
                            if '@' in text:
                                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
                                if email_match:
                                    print(f"  Found email: {email_match.group(0)}")
                    else:
                        print(f"  Value: {value}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    debug_caritas_location()