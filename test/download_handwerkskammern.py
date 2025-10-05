#!/usr/bin/env python3
"""
Download and process Handwerkskammern data
German Craft Chambers data from ZDH (Zentralverband des Deutschen Handwerks)
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
    """Download and process Handwerkskammern data"""
    print("=" * 60)
    print("HANDWERKSKAMMERN DATA DOWNLOADER")
    print("=" * 60)
    
    # Initialize manager
    manager = DataSourceManager()
    source_id = "handwerkskammern"
    
    # Check if source exists
    source_config = manager.get_source(source_id)
    if not source_config:
        print(f"[ERROR] Source '{source_id}' not found in configuration")
        return
    
    print(f"Source: {source_config['name']}")
    print(f"URL: {source_config['url']}")
    print(f"Type: {source_config['type']}")
    
    try:
        # Step 1: Download raw data
        print(f"\n[STEP 1] Downloading raw data...")
        if manager.download_raw_data(source_id):
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
        
        # Show first few locations
        print(f"\n[SAMPLE LOCATIONS]:")
        for i, location in enumerate(processed_data['locations'][:5]):
            print(f"  {i+1}. {location['name']}")
            print(f"     City: {location['address']['city']}")
            print(f"     Coordinates: {location['latitude']}, {location['longitude']}")
            if location['contact']['phone']:
                print(f"     Phone: {location['contact']['phone']}")
            if location['contact']['website']:
                print(f"     Website: {location['contact']['website']}")
            print()
        
        if processed_data['total_locations'] > 5:
            print(f"  ... and {processed_data['total_locations'] - 5} more locations")
        
        print(f"\n[SUCCESS] Handwerkskammern data ready for import!")
        print(f"Raw data: test/data_sources/raw/{source_id}_raw.json")
        print(f"Processed data: test/data_sources/processed/{source_id}_processed.json")
        
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()