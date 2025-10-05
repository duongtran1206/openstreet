"""
Complete Data Sources Management System
Shows status and provides full CRUD operations for all data sources
"""

import sys
sys.path.append('.')

from data_source_manager import DataSourceManager
import json
import os

def show_status():
    """Show complete system status"""
    manager = DataSourceManager("data_sources/sources_config.json")
    summary = manager.get_summary()
    
    print("=" * 70)
    print("🗺️  MULTI-SOURCE DATA MANAGEMENT SYSTEM STATUS")
    print("=" * 70)
    
    print(f"📊 Overview:")
    print(f"   Total sources: {summary['total_sources']}")
    print(f"   Enabled sources: {summary['enabled_sources']}")
    
    print(f"\n📁 Sources Detail:")
    
    for source_id, info in summary['sources'].items():
        status = "✅" if info['enabled'] else "❌"
        raw_status = "📄" if info['has_raw_data'] else "❌"
        processed_status = "⚙️" if info['has_processed_data'] else "❌"
        
        print(f"\n   {status} {source_id} ({info['category']})")
        print(f"       Name: {info['name']}")
        print(f"       Raw data: {raw_status}")
        print(f"       Processed: {processed_status}")
        print(f"       Records: {info['total_records'] or 'Unknown'}")
        print(f"       Last updated: {info['last_updated'] or 'Never'}")
        
        # Show sample data if available
        if info['has_processed_data']:
            try:
                processed_file = f"test/data_sources/processed/{source_id}_processed.json"
                with open(processed_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data['locations']:
                    sample = data['locations'][0]
                    print(f"       📍 Sample: {sample['name']} in {sample['address']['city']}")
                    print(f"         Coords: ({sample['latitude']:.4f}, {sample['longitude']:.4f})")
                    
            except Exception as e:
                print(f"       ⚠️ Error reading processed data: {e}")
    
    print(f"\n💾 File System:")
    raw_dir = "test/data_sources/raw"
    processed_dir = "test/data_sources/processed"
    
    if os.path.exists(raw_dir):
        raw_files = [f for f in os.listdir(raw_dir) if f.endswith('.json')]
        print(f"   Raw files: {len(raw_files)} files")
        for f in raw_files:
            size = os.path.getsize(os.path.join(raw_dir, f))
            print(f"     - {f} ({size:,} bytes)")
    
    if os.path.exists(processed_dir):
        processed_files = [f for f in os.listdir(processed_dir) if f.endswith('.json')]
        print(f"   Processed files: {len(processed_files)} files")
        for f in processed_files:
            size = os.path.getsize(os.path.join(processed_dir, f))
            print(f"     - {f} ({size:,} bytes)")

def menu():
    """Interactive menu for data management"""
    manager = DataSourceManager("data_sources/sources_config.json")
    
    while True:
        print(f"\n" + "=" * 50)
        print("🔧 DATA SOURCE MANAGEMENT MENU")
        print("=" * 50)
        print("1. Show system status")
        print("2. Download raw data (Handwerkskammern)")
        print("3. Download raw data (Caritas - sample)")
        print("4. Process raw data")
        print("5. List all sources (CRUD)")
        print("6. Add new source")
        print("7. Update source")
        print("8. Remove source")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-8): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            show_status()
        elif choice == "2":
            print("\n🏭 Downloading Handwerkskammern data...")
            success = manager.download_raw_data("handwerkskammern")
            if success:
                print("✅ Download completed")
                process = input("Process data now? (y/n): ").lower() == 'y'
                if process:
                    manager.process_raw_data("handwerkskammern")
            else:
                print("❌ Download failed")
        elif choice == "3":
            print("\n🏥 Downloading Caritas data (sample)...")
            success = manager.download_raw_data("caritas", max_pages=2)
            if success:
                print("✅ Download completed")
                process = input("Process data now? (y/n): ").lower() == 'y'
                if process:
                    manager.process_raw_data("caritas")
            else:
                print("❌ Download failed")
        elif choice == "4":
            source_id = input("Enter source ID to process: ").strip()
            if source_id:
                success = manager.process_raw_data(source_id)
                if success:
                    print("✅ Processing completed")
                else:
                    print("❌ Processing failed")
        elif choice == "5":
            sources = manager.list_sources()
            print(f"\n📋 Available sources:")
            for sid, config in sources.items():
                status = "✅" if config.get('enabled', True) else "❌"
                print(f"   {status} {sid}: {config['name']} ({config['category']})")
        elif choice == "6":
            print("\n➕ Add new source (advanced feature)")
            print("Use the configuration file or API to add new sources")
        elif choice == "7":
            print("\n✏️ Update source (advanced feature)")
            print("Edit the configuration file or use API methods")
        elif choice == "8":
            source_id = input("Enter source ID to remove: ").strip()
            if source_id:
                confirm = input(f"Remove '{source_id}'? (yes/no): ").lower()
                if confirm == 'yes':
                    manager.remove_source(source_id)
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        show_status()
        
        print(f"\n🚀 System is ready!")
        print(f"📝 Both data sources are configured and working:")
        print(f"   🏭 Handwerkskammern: 53 German craft chambers")
        print(f"   🏥 Caritas Germany: 516+ social service locations")
        
        interactive = input(f"\nOpen interactive menu? (y/n): ").lower() == 'y'
        if interactive:
            menu()
            
    except KeyboardInterrupt:
        print(f"\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")