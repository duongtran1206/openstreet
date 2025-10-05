#!/usr/bin/env python3
"""
Download and process Caritas Germany data
Catholic charity organization services data
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(current_dir)

from data_source_manager import DataSourceManager
import json

def main():
    """Download and process Caritas data"""
    print("=" * 60)
    print("CARITAS GERMANY DATA DOWNLOADER")
    print("=" * 60)
    
    # Initialize manager
    manager = DataSourceManager()
    source_id = "caritas"
    
    # Check if source exists
    source_config = manager.get_source(source_id)
    if not source_config:
        print(f"[ERROR] Source '{source_id}' not found in configuration")
        return
    
    print(f"Source: {source_config['name']}")
    print(f"URL: {source_config['url']}")
    print(f"Type: {source_config['type']}")
    print(f"Pagination: {source_config['pagination']['max_per_page']} items per page")
    
    # Ask user for max pages
    try:
        max_pages_input = input(f"\nEnter max pages to download (default 5, 0 for all): ").strip()
        max_pages = int(max_pages_input) if max_pages_input else 5
        if max_pages == 0:
            max_pages = None
            print("[INFO] Will download ALL pages (this may take a while)")
        else:
            print(f"[INFO] Will download maximum {max_pages} pages")
    except ValueError:
        max_pages = 5
        print(f"[INFO] Using default: {max_pages} pages")
    
    try:
        # Step 1: Download raw data
        print(f"\n[STEP 1] Downloading raw data...")
        if manager.download_raw_data(source_id, max_pages):
            print("[SUCCESS] Raw data downloaded")
        else:
            print("[ERROR] Failed to download raw data")
            return
        
        # Step 2: Process raw data
        print(f"\n[STEP 2] Processing raw data...")
        if manager.process_raw_data(source_id):
            print("[SUCCESS] Data processed")
        else:
            print("[ERROR] Failed to process data")
            return
        
        # Step 3: Show summary
        print(f"\n[STEP 3] Data Summary:")
        
        # Load processed data to show details
        processed_file = f"test/data_sources/processed/{source_id}_processed.json"
        with open(processed_file, 'r', encoding='utf-8') as f:
            processed_data = json.load(f)
        
        print(f"  Total locations: {processed_data['total_locations']}")
        print(f"  Category: {processed_data['category']}")
        print(f"  Processed: {processed_data['processed_timestamp']}")
        
        # Count categories
        categories = {}
        cities = set()
        
        for location in processed_data['locations']:
            # Subcategories from description
            desc = location.get('description', '').lower()
            if 'migration' in desc:
                cat = 'Migration Services'
            elif 'jugend' in desc:
                cat = 'Youth Services'
            elif 'beratung' in desc:
                cat = 'Counseling Services'
            else:
                cat = 'General Services'
            
            categories[cat] = categories.get(cat, 0) + 1
            
            city = location['address'].get('city', '').split()[0]  # First word only
            if city:
                cities.add(city)
        
        print(f"\n[CATEGORIES BREAKDOWN]:")
        for cat, count in categories.items():
            print(f"  - {cat}: {count} locations")
        
        print(f"\n[GEOGRAPHIC COVERAGE]:")
        print(f"  Cities covered: {len(cities)}")
        print(f"  Sample cities: {', '.join(sorted(list(cities))[:10])}...")
        
        # Show first few locations
        print(f"\n[SAMPLE LOCATIONS]:")
        for i, location in enumerate(processed_data['locations'][:3]):
            print(f"  {i+1}. {location['name']}")
            print(f"     City: {location['address']['city']}")
            print(f"     Coordinates: {location['latitude']}, {location['longitude']}")
            if location['contact']['phone']:
                print(f"     Phone: {location['contact']['phone']}")
            if location['contact']['email']:
                print(f"     Email: {location['contact']['email']}")
            if location.get('description'):
                desc = location['description'][:100] + "..." if len(location['description']) > 100 else location['description']
                print(f"     Description: {desc}")
            print()
        
        if processed_data['total_locations'] > 3:
            print(f"  ... and {processed_data['total_locations'] - 3} more locations")
        
        print(f"\n[SUCCESS] Caritas Germany data ready for import!")
        print(f"Raw data: test/data_sources/raw/{source_id}_raw.json")
        print(f"Processed data: test/data_sources/processed/{source_id}_processed.json")
        
    except KeyboardInterrupt:
        print(f"\n[INFO] Download cancelled by user")
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()