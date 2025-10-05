"""
3-Tier Data Processing Template
Template chuẩn để xử lý bất kỳ nguồn dữ liệu nào thành cấu trúc 3 tầng
"""

import json
import os
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class DataProcessor3Tier(ABC):
    """Base class cho xử lý dữ liệu 3 tầng"""
    
    def __init__(self, output_dir: str = "data_sources/hierarchical"):
        self.output_dir = output_dir
        self.ensure_directory()
    
    def ensure_directory(self):
        """Tạo thư mục output"""
        os.makedirs(self.output_dir, exist_ok=True)
    
    @abstractmethod
    def extract_domain_info(self, raw_data: Dict) -> Dict:
        """Trích xuất thông tin Tầng 1 (Domain)"""
        pass
    
    @abstractmethod
    def extract_categories(self, raw_data: Dict) -> Dict:
        """Trích xuất thông tin Tầng 2 (Categories)"""
        pass
    
    @abstractmethod
    def extract_locations(self, raw_data: Dict) -> List[Dict]:
        """Trích xuất thông tin Tầng 3 (Locations)"""
        pass
    
    @abstractmethod
    def categorize_locations(self, locations: List[Dict], categories: Dict) -> Dict:
        """Phân loại locations vào categories"""
        pass
    
    def process_to_3tier(self, raw_data: Dict) -> Dict:
        """Xử lý chính thành cấu trúc 3 tầng"""
        print(f"🔄 Processing data into 3-tier structure...")
        
        # Tầng 1: Domain
        domain_info = self.extract_domain_info(raw_data)
        
        # Tầng 2: Categories
        categories = self.extract_categories(raw_data)
        
        # Tầng 3: Locations
        locations = self.extract_locations(raw_data)
        
        # Phân loại locations vào categories
        categorized_data = self.categorize_locations(locations, categories)
        
        # Tạo cấu trúc cuối cùng
        result = {
            **domain_info,
            "categories": categorized_data
        }
        
        # Thống kê
        total_categories = len([cat for cat in categorized_data.values() if len(cat["locations"]) > 0])
        total_locations = len(locations)
        total_associations = sum(len(cat["locations"]) for cat in categorized_data.values())
        
        print(f"✅ Processed successfully:")
        print(f"   📁 Domain: {domain_info['domain_name']}")
        print(f"   📂 Categories: {total_categories}")
        print(f"   📍 Locations: {total_locations}")
        print(f"   🔗 Associations: {total_associations}")
        
        return result

class HandwerkskammernProcessor(DataProcessor3Tier):
    """Processor cho dữ liệu Handwerkskammern"""
    
    def extract_domain_info(self, raw_data: Dict) -> Dict:
        return {
            "domain_id": "handwerkskammern_deutschland", 
            "domain_name": "Deutschlandkarte der Handwerkskammern",
            "domain_description": "German Craft Chambers Directory",
            "country": "Germany",
            "language": "de",
            "created_at": datetime.now().isoformat()
        }
    
    def extract_categories(self, raw_data: Dict) -> Dict:
        categories = {}
        
        filter_data = raw_data.get("lists", {}).get("locations", {}).get("filter", {})
        handwerk_filter = filter_data.get("handwerkid", {})
        handwerk_values = handwerk_filter.get("values", [])
        
        for handwerk in handwerk_values:
            if handwerk.get("$value") != "":  # Skip "Alle"
                category_id = f"handwerk_{handwerk['$value']}"
                categories[category_id] = {
                    "category_id": category_id,
                    "category_name": handwerk["title"],
                    "handwerk_id": handwerk["$value"],
                    "locations": []
                }
        
        return categories
    
    def extract_locations(self, raw_data: Dict) -> List[Dict]:
        locations_data = raw_data.get("lists", {}).get("locations", {}).get("$items", [])
        standardized_locations = []
        
        for location in locations_data:
            standardized = self._standardize_handwerk_location(location)
            standardized_locations.append(standardized)
        
        return standardized_locations
    
    def categorize_locations(self, locations: List[Dict], categories: Dict) -> Dict:
        result_categories = {cat_id: {**cat_data} for cat_id, cat_data in categories.items()}
        
        for location in locations:
            handwerk_ids = location["metadata"].get("handwerk_ids", [])
            
            for handwerk_id in handwerk_ids:
                category_key = f"handwerk_{handwerk_id}"
                if category_key in result_categories:
                    result_categories[category_key]["locations"].append(location)
        
        return result_categories
    
    def _standardize_handwerk_location(self, raw_location: Dict) -> Dict:
        """Chuẩn hóa location của Handwerkskammer"""
        adresse = raw_location.get("adresse", {})
        
        return {
            "location_id": raw_location.get("uid", ""),
            "name": raw_location.get("title", ""),
            "coordinates": {
                "latitude": float(raw_location.get("latitude", 0)),
                "longitude": float(raw_location.get("longitude", 0))
            },
            "address": {
                "street": adresse.get("address", ""),
                "city": adresse.get("city", ""),
                "postal_code": adresse.get("zip", ""),
                "country": "Germany"
            },
            "contact": {
                "phone": adresse.get("phone", ""),
                "fax": adresse.get("fax", ""),
                "email": self._extract_email(adresse.get("email_link", "")),
                "website": adresse.get("www", "")
            },
            "metadata": {
                "source": "Handwerkskammer Deutschland",
                "detail_url": raw_location.get("detailUrl", ""),
                "handwerk_ids": raw_location.get("handwerkid", [])
            }
        }
    
    def _extract_email(self, email_link: str) -> str:
        """Trích xuất email từ mailto link"""
        if not email_link:
            return ""
        import re
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', email_link)
        return email_match.group(1) if email_match else ""

class CaritasProcessor(DataProcessor3Tier):
    """Processor cho dữ liệu Caritas (example for social services)"""
    
    def extract_domain_info(self, raw_data: Dict) -> Dict:
        return {
            "domain_id": "caritas_germany",
            "domain_name": "Caritas Germany Social Services",
            "domain_description": "Catholic charity organization services in Germany",
            "country": "Germany", 
            "language": "de",
            "created_at": datetime.now().isoformat()
        }
    
    def extract_categories(self, raw_data: Dict) -> Dict:
        # For Caritas, we'll create categories based on service types
        # This would need to be implemented based on actual data structure
        categories = {
            "migration_services": {
                "category_id": "migration_services",
                "category_name": "Migrationsdienst",
                "locations": []
            },
            "youth_services": {
                "category_id": "youth_services", 
                "category_name": "Jugendhilfe",
                "locations": []
            },
            "elderly_care": {
                "category_id": "elderly_care",
                "category_name": "Altenpflege",
                "locations": []
            }
        }
        return categories
    
    def extract_locations(self, raw_data: Dict) -> List[Dict]:
        # Implementation for Caritas locations
        # This would be based on the actual Caritas data structure
        return []
    
    def categorize_locations(self, locations: List[Dict], categories: Dict) -> Dict:
        # Implementation for categorizing Caritas locations
        # Based on service type detection from name/description
        return categories

class Universal3TierManager:
    """Manager tổng thể cho xử lý nhiều nguồn dữ liệu"""
    
    def __init__(self):
        self.processors = {
            "handwerkskammern": HandwerkskammernProcessor(),
            "caritas": CaritasProcessor()
        }
    
    def register_processor(self, source_id: str, processor: DataProcessor3Tier):
        """Đăng ký processor mới"""
        self.processors[source_id] = processor
    
    def process_source(self, source_id: str, raw_data: Dict) -> Dict:
        """Xử lý một nguồn dữ liệu cụ thể"""
        if source_id not in self.processors:
            raise ValueError(f"No processor found for source: {source_id}")
        
        processor = self.processors[source_id]
        result = processor.process_to_3tier(raw_data)
        
        return result
    
    def save_processed_data(self, source_id: str, processed_data: Dict):
        """Lưu dữ liệu đã xử lý"""
        output_dir = "data_sources/hierarchical"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save main hierarchical data
        main_file = os.path.join(output_dir, f"{processed_data['domain_id']}_hierarchical.json")
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        # Save summary
        summary = self._create_summary(processed_data)
        summary_file = os.path.join(output_dir, f"{processed_data['domain_id']}_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # Save map data
        map_data = self._create_map_data(processed_data)
        map_file = os.path.join(output_dir, f"{processed_data['domain_id']}_map.json")
        with open(map_file, 'w', encoding='utf-8') as f:
            json.dump(map_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved processed data:")
        print(f"   📄 Main: {main_file}")
        print(f"   📊 Summary: {summary_file}")
        print(f"   🗺️ Map: {map_file}")
        
        return main_file
    
    def _create_summary(self, processed_data: Dict) -> Dict:
        """Tạo summary cho processed data"""
        categories = processed_data.get("categories", {})
        
        category_stats = []
        total_locations = 0
        
        for cat_id, cat_data in categories.items():
            location_count = len(cat_data["locations"])
            total_locations += location_count
            
            if location_count > 0:
                category_stats.append({
                    "category_id": cat_id,
                    "category_name": cat_data["category_name"],
                    "location_count": location_count
                })
        
        category_stats.sort(key=lambda x: x["location_count"], reverse=True)
        
        return {
            "domain_summary": {
                "domain_id": processed_data["domain_id"],
                "domain_name": processed_data["domain_name"],
                "total_categories": len(category_stats),
                "total_locations": total_locations,
                "created_at": processed_data["created_at"]
            },
            "category_statistics": category_stats
        }
    
    def _create_map_data(self, processed_data: Dict) -> Dict:
        """Tạo dữ liệu cho hiển thị bản đồ"""
        map_data = {
            "type": "FeatureCollection",
            "domain": {
                "id": processed_data["domain_id"],
                "name": processed_data["domain_name"]
            },
            "categories": [],
            "features": []
        }
        
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57"]
        
        for i, (cat_id, cat_data) in enumerate(processed_data["categories"].items()):
            if len(cat_data["locations"]) > 0:
                map_data["categories"].append({
                    "id": cat_id,
                    "name": cat_data["category_name"],
                    "count": len(cat_data["locations"]),
                    "color": colors[i % len(colors)]
                })
                
                for location in cat_data["locations"]:
                    if location["coordinates"]["latitude"] and location["coordinates"]["longitude"]:
                        feature = {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [
                                    location["coordinates"]["longitude"],
                                    location["coordinates"]["latitude"]
                                ]
                            },
                            "properties": {
                                "name": location["name"],
                                "category_id": cat_id,
                                "category_name": cat_data["category_name"],
                                "address": location["address"],
                                "contact": location["contact"]
                            }
                        }
                        map_data["features"].append(feature)
        
        return map_data

def main():
    """Test với dữ liệu Handwerkskammern"""
    print("🚀 UNIVERSAL 3-TIER DATA PROCESSING SYSTEM")
    print("=" * 60)
    
    # Load raw data
    raw_file = "data_sources/raw/handwerkskammern_raw.json"
    
    if not os.path.exists(raw_file):
        print(f"❌ Raw data file not found: {raw_file}")
        return
    
    with open(raw_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # Initialize manager
    manager = Universal3TierManager()
    
    # Process data
    processed_data = manager.process_source("handwerkskammern", raw_data)
    
    # Save data
    saved_file = manager.save_processed_data("handwerkskammern", processed_data)
    
    print(f"\n🎉 UNIVERSAL 3-TIER PROCESSING COMPLETE!")
    print(f"📁 Main file: {saved_file}")
    
    print(f"\n💡 TEMPLATE IS READY FOR OTHER DATA SOURCES!")
    print(f"   1. Tạo class Processor kế thừa DataProcessor3Tier")
    print(f"   2. Implement 4 abstract methods")
    print(f"   3. Register processor với Universal3TierManager")
    print(f"   4. Call process_source() với raw data")

if __name__ == "__main__":
    main()