"""
Data Collection Manager
Manages multiple data collectors and provides unified interface
"""

from typing import Dict, List, Optional, Type
from .base_collector import BaseDataCollector
from .handwerkskammern_collector import HandwerkskammernCollector
from .caritas_collector import CaritasCollector
import json
from datetime import datetime
import os

class DataCollectionManager:
    """Manager for all data collectors"""
    
    def __init__(self):
        self.collectors = {
            "handwerkskammern": HandwerkskammernCollector,
            "caritas": CaritasCollector,
        }
        self.collected_data = {}
        
    def list_available_collectors(self) -> Dict[str, Dict]:
        """List all available collectors with their metadata"""
        collectors_info = {}
        
        for name, collector_class in self.collectors.items():
            collector = collector_class()
            collectors_info[name] = collector.get_metadata()
            
        return collectors_info
    
    def collect_from_source(self, source_name: str, **kwargs) -> Optional[List[Dict]]:
        """Collect data from a specific source"""
        if source_name not in self.collectors:
            print(f"❌ Unknown collector: {source_name}")
            print(f"Available collectors: {list(self.collectors.keys())}")
            return None
        
        collector_class = self.collectors[source_name]
        collector = collector_class()
        
        try:
            data = collector.collect_data(**kwargs)
            self.collected_data[source_name] = {
                "data": data,
                "collected_at": datetime.now().isoformat(),
                "count": len(data),
                "metadata": collector.get_metadata()
            }
            
            print(f"✅ Successfully collected {len(data)} items from {source_name}")
            return data
            
        except Exception as e:
            print(f"❌ Error collecting from {source_name}: {e}")
            return None
    
    def collect_from_all_sources(self, **kwargs) -> Dict[str, List[Dict]]:
        """Collect data from all available sources"""
        print("🔄 Collecting data from all sources...")
        
        all_data = {}
        
        for source_name in self.collectors.keys():
            print(f"\n--- Collecting from {source_name} ---")
            data = self.collect_from_source(source_name, **kwargs)
            if data:
                all_data[source_name] = data
        
        return all_data
    
    def get_collection_summary(self) -> Dict:
        """Get summary of all collected data"""
        summary = {
            "sources": len(self.collected_data),
            "total_locations": sum(info["count"] for info in self.collected_data.values()),
            "collections": {}
        }
        
        for source_name, info in self.collected_data.items():
            summary["collections"][source_name] = {
                "count": info["count"],
                "collected_at": info["collected_at"],
                "category": info["metadata"].get("category", "Unknown"),
                "country": info["metadata"].get("country", "Unknown")
            }
        
        return summary
    
    def combine_all_data(self) -> List[Dict]:
        """Combine data from all sources into a single list"""
        combined_data = []
        
        for source_name, info in self.collected_data.items():
            for location in info["data"]:
                # Add source information to each location
                location["collection_source"] = source_name
                location["collection_metadata"] = info["metadata"]
                combined_data.append(location)
        
        return combined_data
    
    def save_combined_data(self, filename: str = None) -> str:
        """Save combined data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"combined_data_{timestamp}.json"
        
        combined_data = self.combine_all_data()
        summary = self.get_collection_summary()
        
        output = {
            "summary": summary,
            "data": combined_data
        }
        
        output_path = f"data_collectors/processed_data/{filename}"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Combined data saved to {output_path}")
        print(f"📊 Total locations: {len(combined_data)}")
        
        return output_path
    
    def get_data_by_category(self, category: str = None) -> List[Dict]:
        """Filter data by category"""
        combined_data = self.combine_all_data()
        
        if not category:
            return combined_data
        
        filtered_data = []
        for location in combined_data:
            if category.lower() in location.get("category", "").lower():
                filtered_data.append(location)
        
        return filtered_data
    
    def get_user_selection_interface(self) -> Dict:
        """Generate interface for user to select data sources and categories"""
        collectors_info = self.list_available_collectors()
        
        interface = {
            "available_sources": {},
            "categories": set(),
            "countries": set()
        }
        
        for source_name, metadata in collectors_info.items():
            interface["available_sources"][source_name] = {
                "name": metadata["name"],
                "description": metadata["description"],
                "category": metadata["category"],
                "country": metadata["country"],
                "data_types": metadata.get("data_types", []),
                "subcategories": metadata.get("subcategories", [])
            }
            
            interface["categories"].add(metadata["category"])
            interface["countries"].add(metadata["country"])
        
        # Convert sets to lists for JSON serialization
        interface["categories"] = sorted(list(interface["categories"]))
        interface["countries"] = sorted(list(interface["countries"]))
        
        return interface