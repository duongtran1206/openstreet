"""
3-Tier Hierarchical Data Structure Manager
Tầng 1: Lĩnh vực (Domain)
Tầng 2: Mảng/Danh mục (Category) 
Tầng 3: Địa điểm (Locations)
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from data_source_manager import DataSourceManager

class HierarchicalDataManager:
    """Quản lý dữ liệu theo cấu trúc phân cấp 3 tầng"""
    
    def __init__(self, output_dir: str = "data_sources/hierarchical"):
        self.output_dir = output_dir
        self.ensure_directory()
        
    def ensure_directory(self):
        """Tạo thư mục output nếu chưa có"""
        os.makedirs(self.output_dir, exist_ok=True)
        
    def process_handwerkskammern_data(self, raw_data: Dict) -> Dict:
        """
        Xử lý dữ liệu Handwerkskammern thành cấu trúc 3 tầng
        """
        print("🔄 Processing Handwerkskammern data into 3-tier structure...")
        
        # Tầng 1: Lĩnh vực
        domain = {
            "domain_id": "handwerkskammern_deutschland",
            "domain_name": "Deutschlandkarte der Handwerkskammern",
            "domain_description": "German Craft Chambers Directory",
            "country": "Germany",
            "language": "de",
            "created_at": datetime.now().isoformat(),
            "categories": {}
        }
        
        # Lấy danh sách các Handwerk categories từ filter
        filter_data = raw_data.get("lists", {}).get("locations", {}).get("filter", {})
        handwerk_filter = filter_data.get("handwerkid", {})
        handwerk_values = handwerk_filter.get("values", [])
        
        # Tầng 2: Tạo categories từ handwerk values
        categories = {}
        for handwerk in handwerk_values:
            if handwerk.get("$value") != "":  # Skip "Alle" option
                category_id = f"handwerk_{handwerk['$value']}"
                categories[category_id] = {
                    "category_id": category_id,
                    "category_name": handwerk["title"],
                    "handwerk_id": handwerk["$value"],
                    "locations": []
                }
        
        # Tầng 3: Phân loại locations theo handwerk_id
        locations_data = raw_data.get("lists", {}).get("locations", {}).get("$items", [])
        
        location_count = 0
        for location in locations_data:
            # Mỗi location có thể thuộc nhiều handwerk categories
            handwerk_ids = location.get("handwerkid", [])
            
            # Tạo location object chuẩn
            standardized_location = self._standardize_location(location)
            
            # Thêm vào các categories tương ứng
            for handwerk_id in handwerk_ids:
                category_key = f"handwerk_{handwerk_id}"
                if category_key in categories:
                    categories[category_key]["locations"].append(standardized_location)
                    location_count += 1
        
        domain["categories"] = categories
        
        # Thống kê
        total_categories = len([cat for cat in categories.values() if len(cat["locations"]) > 0])
        total_locations = len(locations_data)
        
        print(f"✅ Processed successfully:")
        print(f"   📁 Domain: {domain['domain_name']}")
        print(f"   📂 Categories: {total_categories}")
        print(f"   📍 Locations: {total_locations}")
        print(f"   🔗 Category-Location associations: {location_count}")
        
        return domain
    
    def _standardize_location(self, raw_location: Dict) -> Dict:
        """Chuẩn hóa thông tin location theo format chung"""
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
                "email": self._extract_email_from_link(adresse.get("email_link", "")),
                "website": adresse.get("www", "")
            },
            "metadata": {
                "source": "Handwerkskammer Deutschland", 
                "detail_url": raw_location.get("detailUrl", ""),
                "handwerk_ids": raw_location.get("handwerkid", [])
            }
        }
    
    def _extract_email_from_link(self, email_link: str) -> str:
        """Trích xuất email từ mailto link"""
        if not email_link:
            return ""
        
        # Parse email từ data-mailto-token hoặc href
        import re
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', email_link)
        return email_match.group(1) if email_match else ""
    
    def save_hierarchical_data(self, domain_data: Dict, filename: str = None):
        """Lưu dữ liệu phân cấp ra file"""
        if not filename:
            filename = f"{domain_data['domain_id']}_hierarchical.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(domain_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved hierarchical data to: {filepath}")
        
        # Tạo summary file
        summary = self._create_summary(domain_data)
        summary_path = os.path.join(self.output_dir, f"{domain_data['domain_id']}_summary.json")
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
            
        print(f"📊 Saved summary to: {summary_path}")
        
        return filepath
    
    def _create_summary(self, domain_data: Dict) -> Dict:
        """Tạo tóm tắt thống kê"""
        categories = domain_data.get("categories", {})
        
        category_stats = []
        total_locations = 0
        
        for cat_id, cat_data in categories.items():
            location_count = len(cat_data["locations"])
            total_locations += location_count
            
            if location_count > 0:  # Chỉ include categories có data
                category_stats.append({
                    "category_id": cat_id,
                    "category_name": cat_data["category_name"],
                    "handwerk_id": cat_data["handwerk_id"],
                    "location_count": location_count
                })
        
        # Sort by location count descending
        category_stats.sort(key=lambda x: x["location_count"], reverse=True)
        
        return {
            "domain_summary": {
                "domain_id": domain_data["domain_id"],
                "domain_name": domain_data["domain_name"],
                "total_categories": len(category_stats),
                "total_locations": total_locations,
                "created_at": domain_data["created_at"]
            },
            "category_statistics": category_stats
        }
    
    def load_hierarchical_data(self, filename: str) -> Dict:
        """Load dữ liệu phân cấp từ file"""
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def export_for_map_display(self, domain_data: Dict) -> Dict:
        """Export data ở format phù hợp cho hiển thị bản đồ"""
        map_data = {
            "type": "FeatureCollection",
            "domain": {
                "id": domain_data["domain_id"],
                "name": domain_data["domain_name"]
            },
            "categories": [],
            "features": []
        }
        
        # Tạo danh sách categories cho legend
        for cat_id, cat_data in domain_data["categories"].items():
            if len(cat_data["locations"]) > 0:
                map_data["categories"].append({
                    "id": cat_id,
                    "name": cat_data["category_name"],
                    "count": len(cat_data["locations"]),
                    "color": self._get_category_color(cat_id)
                })
        
        # Tạo GeoJSON features
        for cat_id, cat_data in domain_data["categories"].items():
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
                            "contact": location["contact"],
                            "metadata": location["metadata"]
                        }
                    }
                    map_data["features"].append(feature)
        
        return map_data
    
    def _get_category_color(self, category_id: str) -> str:
        """Tạo màu sắc cho category"""
        colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57",
            "#FF9FF3", "#54A0FF", "#5F27CD", "#00D2D3", "#FF9F43",
            "#74B9FF", "#A29BFE", "#FD79A8", "#FDCB6E", "#6C5CE7"
        ]
        
        # Hash category_id to get consistent color
        hash_val = sum(ord(c) for c in category_id)
        return colors[hash_val % len(colors)]

def main():
    """Test function để xử lý dữ liệu Handwerkskammern"""
    print("🚀 Starting 3-Tier Hierarchical Data Processing")
    print("=" * 60)
    
    # Load raw data
    raw_file = "data_sources/raw/handwerkskammern_raw.json"
    
    if not os.path.exists(raw_file):
        print(f"❌ Raw data file not found: {raw_file}")
        print("Please run: python download_handwerkskammern.py first")
        return
    
    with open(raw_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # Initialize manager
    hierarchy_manager = HierarchicalDataManager()
    
    # Process data
    domain_data = hierarchy_manager.process_handwerkskammern_data(raw_data)
    
    # Save data
    filepath = hierarchy_manager.save_hierarchical_data(domain_data)
    
    # Create map export
    map_data = hierarchy_manager.export_for_map_display(domain_data)
    map_file = os.path.join(hierarchy_manager.output_dir, f"{domain_data['domain_id']}_map.json")
    
    with open(map_file, 'w', encoding='utf-8') as f:
        json.dump(map_data, f, ensure_ascii=False, indent=2)
    
    print(f"🗺️ Map data exported to: {map_file}")
    
    print(f"\n🎉 3-Tier Hierarchical Processing Complete!")
    print(f"📁 Files created in: {hierarchy_manager.output_dir}")

if __name__ == "__main__":
    main()