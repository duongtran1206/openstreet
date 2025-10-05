#!/usr/bin/env python3
"""
Main Data Collection Script
Provides interface for collecting data from multiple sources
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collectors.data_manager import DataCollectionManager
import json

def main():
    """Main function for data collection"""
    print("🗺️  Multi-Source Data Collection System")
    print("=" * 50)
    
    # Initialize data manager
    manager = DataCollectionManager()
    
    # Show available data sources
    print("\n📋 Available Data Sources:")
    collectors_info = manager.list_available_collectors()
    
    for i, (source_name, metadata) in enumerate(collectors_info.items(), 1):
        print(f"\n{i}. {metadata['name']}")
        print(f"   📍 Category: {metadata['category']}")
        print(f"   🌍 Country: {metadata['country']}")
        print(f"   📝 Description: {metadata['description']}")
        if metadata.get('subcategories'):
            print(f"   🏷️  Subcategories: {', '.join(metadata['subcategories'])}")
    
    print("\n" + "=" * 50)
    print("Collection Options:")
    print("1. Collect from all sources")
    print("2. Collect from specific source")
    print("3. Show collection interface")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            collect_all_data(manager)
        elif choice == "2":
            collect_specific_data(manager, collectors_info)
        elif choice == "3":
            show_selection_interface(manager)
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n👋 Collection cancelled by user")

def collect_all_data(manager):
    """Collect data from all sources"""
    print("\n🔄 Starting collection from all sources...")
    
    all_data = manager.collect_from_all_sources()
    
    if all_data:
        print("\n📊 Collection Summary:")
        summary = manager.get_collection_summary()
        print(f"   Total sources: {summary['sources']}")
        print(f"   Total locations: {summary['total_locations']}")
        
        for source_name, info in summary['collections'].items():
            print(f"   📍 {source_name}: {info['count']} locations ({info['category']})")
        
        # Save combined data
        output_path = manager.save_combined_data()
        print(f"\n✅ All data saved to: {output_path}")
    else:
        print("❌ No data collected")

def collect_specific_data(manager, collectors_info):
    """Collect data from specific source"""
    print("\nAvailable sources:")
    sources = list(collectors_info.keys())
    
    for i, source_name in enumerate(sources, 1):
        metadata = collectors_info[source_name]
        print(f"{i}. {source_name} - {metadata['name']}")
    
    try:
        choice = int(input(f"\nSelect source (1-{len(sources)}): "))
        if 1 <= choice <= len(sources):
            source_name = sources[choice - 1]
            
            # Ask for additional parameters
            print(f"\n🔄 Collecting from {source_name}...")
            
            if source_name == "caritas":
                max_pages = input("Max pages to collect (default 10): ").strip()
                max_pages = int(max_pages) if max_pages.isdigit() else 10
                data = manager.collect_from_source(source_name, max_pages=max_pages)
            else:
                data = manager.collect_from_source(source_name)
            
            if data:
                print(f"\n✅ Collected {len(data)} locations from {source_name}")
                
                # Save individual source data
                output_path = manager.save_combined_data(f"{source_name}_data.json")
                print(f"📄 Data saved to: {output_path}")
            else:
                print("❌ No data collected")
        else:
            print("❌ Invalid choice")
    except ValueError:
        print("❌ Please enter a valid number")

def show_selection_interface(manager):
    """Show user selection interface"""
    print("\n🎛️  Data Collection Interface")
    
    interface = manager.get_user_selection_interface()
    
    print("\n📋 Available Data Sources:")
    for source_name, info in interface["available_sources"].items():
        print(f"\n🔹 {source_name.upper()}")
        print(f"   Name: {info['name']}")
        print(f"   Category: {info['category']}")
        print(f"   Country: {info['country']}")
        print(f"   Description: {info['description']}")
        print(f"   Data Types: {', '.join(info['data_types'])}")
        if info['subcategories']:
            print(f"   Subcategories: {', '.join(info['subcategories'])}")
    
    print(f"\n🏷️  Available Categories: {', '.join(interface['categories'])}")
    print(f"🌍 Available Countries: {', '.join(interface['countries'])}")
    
    # Save interface to file for web integration
    interface_path = "data_collectors/processed_data/collection_interface.json"
    os.makedirs(os.path.dirname(interface_path), exist_ok=True)
    
    with open(interface_path, 'w', encoding='utf-8') as f:
        json.dump(interface, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Interface data saved to: {interface_path}")

if __name__ == "__main__":
    main()