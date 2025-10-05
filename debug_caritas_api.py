#!/usr/bin/env python
"""
Debug Caritas API to understand data structure
"""

import requests
import json

def debug_caritas_api():
    url = "https://www.caritas.de/Services/MappingService.svc/GetMapContents/ec7e69ee-35b9-45b9-b081-fc7a191a76c0/?page=0&pagesize=5"
    
    print("🔍 Debugging Caritas API...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        data = response.json()
        print(f"Data type: {type(data)}")
        print(f"Data length: {len(data) if hasattr(data, '__len__') else 'N/A'}")
        
        # Print first few items
        if isinstance(data, list):
            print("\n📋 First items:")
            for i, item in enumerate(data[:2]):
                print(f"Item {i}: {type(item)} -> {item}")
        elif isinstance(data, dict):
            print(f"\n📋 Dictionary keys: {list(data.keys())}")
            for key, value in list(data.items())[:3]:
                print(f"{key}: {type(value)} -> {str(value)[:100]}...")
        else:
            print(f"\n📋 Raw data: {data}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    debug_caritas_api()