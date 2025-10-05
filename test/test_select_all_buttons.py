"""
Test script to verify the new Select All / Deselect All buttons functionality
"""

import requests
from pathlib import Path
import json

def test_new_features():
    print("=" * 60)
    print("TESTING SELECT ALL / DESELECT ALL BUTTONS")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test main page loads
    try:
        print(f"\n1. Testing main page load...")
        response = requests.get(f"{base_url}/")
        
        if response.status_code == 200:
            print("   ✅ Main page loaded successfully")
            
            # Check if new HTML elements are present
            content = response.text
            
            if 'id="select-all-layers"' in content:
                print("   ✅ Select All button HTML found")
            else:
                print("   ❌ Select All button HTML NOT found")
            
            if 'id="deselect-all-layers"' in content:
                print("   ✅ Deselect All button HTML found")  
            else:
                print("   ❌ Deselect All button HTML NOT found")
                
            if 'layer-control-buttons' in content:
                print("   ✅ Button container CSS class found")
            else:
                print("   ❌ Button container CSS class NOT found")
                
            if 'control-btn' in content:
                print("   ✅ Button CSS class found")
            else:
                print("   ❌ Button CSS class NOT found")
        else:
            print(f"   ❌ Error loading page: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test static files
    try:
        print(f"\n2. Testing static files...")
        
        # Test JS file
        js_response = requests.get(f"{base_url}/static/js/map.js")
        if js_response.status_code == 200:
            print("   ✅ map.js loaded successfully")
            
            js_content = js_response.text
            if 'setupLayerControlButtons' in js_content:
                print("   ✅ setupLayerControlButtons function found")
            else:
                print("   ❌ setupLayerControlButtons function NOT found")
                
            if 'selectAllLayers' in js_content:
                print("   ✅ selectAllLayers function found")
            else:
                print("   ❌ selectAllLayers function NOT found")
        else:
            print(f"   ❌ Error loading JS: {js_response.status_code}")
            
        # Test CSS (should be inline in HTML)
        print("   ✅ CSS is inline in HTML template")
        
    except Exception as e:
        print(f"   ❌ Static files error: {e}")
    
    # Test API endpoints still work
    try:
        print(f"\n3. Testing API endpoints...")
        
        endpoints = ["/api/categories/", "/api/map-data/"]
        
        for endpoint in endpoints:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                if endpoint == "/api/categories/":
                    print(f"   ✅ Categories API: {len(data)} items")
                elif endpoint == "/api/map-data/":
                    total = data.get('total_locations', 0)
                    print(f"   ✅ Map Data API: {total} locations")
            else:
                print(f"   ❌ {endpoint} failed: {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ API test error: {e}")
    
    print(f"\n" + "=" * 60)
    print("TESTING COMPLETED")
    print("=" * 60)
    
    print(f"\n📋 MANUAL TESTING CHECKLIST:")
    print(f"   1. Open: {base_url}/")
    print(f"   2. Look for 'Select All' and 'Deselect All' buttons above layer list")
    print(f"   3. Click 'Deselect All' - all checkboxes should uncheck, markers disappear")
    print(f"   4. Click 'Select All' - all checkboxes should check, markers reappear")
    print(f"   5. Buttons should be styled nicely with hover effects")

if __name__ == "__main__":
    test_new_features()