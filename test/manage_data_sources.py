#!/usr/bin/env python3
"""
Main Data Source Manager Script
CRUD operations for all data sources
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

def show_menu():
    """Show main menu options"""
    print("\n" + "=" * 60)
    print("MULTI-SOURCE DATA MANAGER")
    print("=" * 60)
    print("1. List all data sources")
    print("2. Download raw data from source")
    print("3. Process raw data")
    print("4. Download + Process (full workflow)")
    print("5. Show data summary")
    print("6. Add new data source")
    print("7. Update data source")
    print("8. Remove data source")
    print("9. Show configuration")
    print("0. Exit")
    print("=" * 60)

def list_sources(manager):
    """List all configured data sources"""
    sources = manager.list_sources()
    
    print(f"\n[DATA SOURCES] ({len(sources)} total)")
    print("-" * 80)
    
    for i, (source_id, config) in enumerate(sources.items(), 1):
        status = "✅ Enabled" if config.get("enabled", True) else "❌ Disabled"
        last_updated = config.get("last_updated", "Never")
        total_records = config.get("total_records", "Unknown")
        
        print(f"{i}. {source_id}")
        print(f"   Name: {config['name']}")
        print(f"   Category: {config['category']}")
        print(f"   Type: {config['type']}")
        print(f"   Status: {status}")
        print(f"   Last Updated: {last_updated}")
        print(f"   Records: {total_records}")
        print(f"   URL: {config['url'][:80]}...")
        print()

def download_data(manager):
    """Download data from selected source"""
    sources = manager.list_sources()
    
    print(f"\n[SELECT SOURCE TO DOWNLOAD]")
    source_list = list(sources.keys())
    
    for i, source_id in enumerate(source_list, 1):
        config = sources[source_id]
        status = "✅" if config.get("enabled", True) else "❌"
        print(f"{i}. {source_id} - {config['name']} {status}")
    
    try:
        choice = int(input(f"\nEnter choice (1-{len(source_list)}): ")) - 1
        if 0 <= choice < len(source_list):
            source_id = source_list[choice]
            config = sources[source_id]
            
            print(f"\nSelected: {config['name']}")
            
            # Ask for max pages if paginated
            max_pages = None
            if config["type"] == "paginated_api":
                max_pages_input = input("Enter max pages (default 5, 0 for all): ").strip()
                max_pages = int(max_pages_input) if max_pages_input else 5
                if max_pages == 0:
                    max_pages = None
            
            # Download
            if manager.download_raw_data(source_id, max_pages):
                print(f"\n[SUCCESS] Downloaded data for {source_id}")
            else:
                print(f"\n[ERROR] Failed to download data for {source_id}")
        else:
            print("[ERROR] Invalid choice")
    except ValueError:
        print("[ERROR] Please enter a valid number")

def process_data(manager):
    """Process raw data for selected source"""
    sources = manager.list_sources()
    
    print(f"\n[SELECT SOURCE TO PROCESS]")
    source_list = []
    
    for i, (source_id, config) in enumerate(sources.items(), 1):
        raw_file = f"test/data_sources/raw/{source_id}_raw.json"
        has_raw = os.path.exists(raw_file)
        status = "📄 Has raw data" if has_raw else "❌ No raw data"
        
        if has_raw:
            source_list.append(source_id)
            print(f"{len(source_list)}. {source_id} - {config['name']} {status}")
    
    if not source_list:
        print("[INFO] No sources have raw data. Download data first.")
        return
    
    try:
        choice = int(input(f"\nEnter choice (1-{len(source_list)}): ")) - 1
        if 0 <= choice < len(source_list):
            source_id = source_list[choice]
            
            if manager.process_raw_data(source_id):
                print(f"\n[SUCCESS] Processed data for {source_id}")
            else:
                print(f"\n[ERROR] Failed to process data for {source_id}")
        else:
            print("[ERROR] Invalid choice")
    except ValueError:
        print("[ERROR] Please enter a valid number")

def full_workflow(manager):
    """Download and process data (full workflow)"""
    sources = manager.list_sources()
    
    print(f"\n[FULL WORKFLOW - DOWNLOAD + PROCESS]")
    source_list = list(sources.keys())
    
    for i, source_id in enumerate(source_list, 1):
        config = sources[source_id]
        status = "✅" if config.get("enabled", True) else "❌"
        print(f"{i}. {source_id} - {config['name']} {status}")
    
    print(f"{len(source_list) + 1}. ALL SOURCES")
    
    try:
        choice = int(input(f"\nEnter choice (1-{len(source_list) + 1}): "))
        
        if choice == len(source_list) + 1:
            # Process all sources
            print("\n[INFO] Processing all enabled sources...")
            
            for source_id, config in sources.items():
                if not config.get("enabled", True):
                    print(f"[SKIP] {source_id} is disabled")
                    continue
                
                print(f"\n[PROCESSING] {config['name']}")
                
                # Ask for max pages if paginated
                max_pages = None
                if config["type"] == "paginated_api":
                    max_pages = 3  # Default for batch processing
                    print(f"[INFO] Using default {max_pages} pages for {source_id}")
                
                # Download and process
                if manager.download_raw_data(source_id, max_pages):
                    if manager.process_raw_data(source_id):
                        print(f"[SUCCESS] Completed {source_id}")
                    else:
                        print(f"[ERROR] Failed to process {source_id}")
                else:
                    print(f"[ERROR] Failed to download {source_id}")
        
        elif 1 <= choice <= len(source_list):
            # Process single source
            source_id = source_list[choice - 1]
            config = sources[source_id]
            
            print(f"\n[PROCESSING] {config['name']}")
            
            # Ask for max pages if paginated
            max_pages = None
            if config["type"] == "paginated_api":
                max_pages_input = input("Enter max pages (default 5, 0 for all): ").strip()
                max_pages = int(max_pages_input) if max_pages_input else 5
                if max_pages == 0:
                    max_pages = None
            
            # Download and process
            if manager.download_raw_data(source_id, max_pages):
                if manager.process_raw_data(source_id):
                    print(f"\n[SUCCESS] Completed {source_id}")
                else:
                    print(f"\n[ERROR] Failed to process {source_id}")
            else:
                print(f"\n[ERROR] Failed to download {source_id}")
        else:
            print("[ERROR] Invalid choice")
    except ValueError:
        print("[ERROR] Please enter a valid number")

def show_summary(manager):
    """Show summary of all data sources"""
    summary = manager.get_summary()
    
    print(f"\n[DATA SOURCES SUMMARY]")
    print(f"Total sources: {summary['total_sources']}")
    print(f"Enabled sources: {summary['enabled_sources']}")
    print("-" * 60)
    
    for source_id, info in summary["sources"].items():
        print(f"\n{source_id.upper()}")
        print(f"  Name: {info['name']}")
        print(f"  Category: {info['category']}")
        print(f"  Enabled: {'Yes' if info['enabled'] else 'No'}")
        print(f"  Last Updated: {info['last_updated'] or 'Never'}")
        print(f"  Total Records: {info['total_records'] or 'Unknown'}")
        print(f"  Raw Data: {'Yes' if info['has_raw_data'] else 'No'}")
        print(f"  Processed Data: {'Yes' if info['has_processed_data'] else 'No'}")

def show_config(manager):
    """Show current configuration"""
    print(f"\n[CONFIGURATION]")
    print(json.dumps(manager.config, indent=2, ensure_ascii=False))

def main():
    """Main function"""
    manager = DataSourceManager()
    
    while True:
        show_menu()
        
        try:
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '0':
                print("\n👋 Goodbye!")
                break
            elif choice == '1':
                list_sources(manager)
            elif choice == '2':
                download_data(manager)
            elif choice == '3':
                process_data(manager)
            elif choice == '4':
                full_workflow(manager)
            elif choice == '5':
                show_summary(manager)
            elif choice == '6':
                print("\n[INFO] Feature not implemented yet")
            elif choice == '7':
                print("\n[INFO] Feature not implemented yet")
            elif choice == '8':
                print("\n[INFO] Feature not implemented yet")
            elif choice == '9':
                show_config(manager)
            else:
                print("\n[ERROR] Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")

if __name__ == "__main__":
    main()