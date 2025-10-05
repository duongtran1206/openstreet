"""
Quick test for Caritas data source - download 2 pages and process
"""

import sys
sys.path.append('.')

from data_source_manager import DataSourceManager

def test_caritas():
    manager = DataSourceManager("data_sources/sources_config.json")
    
    print("=" * 60)
    print("CARITAS GERMANY TEST - DOWNLOADING 2 PAGES")
    print("=" * 60)
    
    # Download raw data (max 2 pages = 100 records)
    print("[INFO] Downloading Caritas data...")
    success = manager.download_raw_data("caritas", max_pages=2)
    
    if success:
        print("[SUCCESS] Download completed")
        
        # Process the data
        print("[INFO] Processing data...")
        process_success = manager.process_raw_data("caritas")
        
        if process_success:
            print("[SUCCESS] Processing completed")
            
            # Show summary
            import json
            processed_file = "test/data_sources/processed/caritas_processed.json"
            
            try:
                with open(processed_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"\n📊 SUMMARY:")
                print(f"Total locations: {data['total_locations']}")
                
                if data['locations']:
                    sample = data['locations'][0]
                    print(f"\n📍 Sample location:")
                    print(f"  Name: {sample['name']}")
                    print(f"  City: {sample['address']['city']}")
                    print(f"  Coordinates: ({sample['latitude']}, {sample['longitude']})")
                    if sample['contact']['phone']:
                        print(f"  Phone: {sample['contact']['phone']}")
                    if sample['contact']['website']:
                        print(f"  Website: {sample['contact']['website']}")
                
                print(f"\n✅ Test completed successfully!")
                return True
                
            except FileNotFoundError:
                print(f"❌ Processed file not found: {processed_file}")
                return False
        else:
            print("❌ Processing failed")
            return False
    else:
        print("❌ Download failed")
        return False

if __name__ == "__main__":
    test_caritas()