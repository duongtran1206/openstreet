"""
Handwerkskammern Data Collector
Collects data from German Handwerkskammern API
"""

from .base_collector import BaseDataCollector
from typing import Dict, List, Optional
import re

class HandwerkskammernCollector(BaseDataCollector):
    """Collector for German Handwerkskammern data"""
    
    def __init__(self):
        super().__init__(
            name="handwerkskammern",
            base_url="https://www.handwerkskammern.de"
        )
        self.api_url = "https://www.handwerkskammern.de/api/regional/hwk"
    
    def get_metadata(self) -> Dict:
        """Return metadata about this collector"""
        return {
            "name": "Handwerkskammern Germany",
            "description": "German Craft Chambers",
            "source_url": "https://www.handwerkskammern.de",
            "category": "Professional Organizations",
            "country": "Germany",
            "data_types": ["organizations", "contact_info", "locations"],
            "last_updated": None
        }
    
    def collect_data(self, save_raw: bool = True) -> List[Dict]:
        """Collect Handwerkskammern data"""
        print(f"🔄 Collecting data from {self.name}...")
        
        # Fetch data from API
        raw_data = self.make_request(self.api_url)
        
        if not raw_data:
            print("❌ Failed to fetch Handwerkskammern data")
            return []
        
        if save_raw:
            self.save_raw_data(raw_data, "handwerkskammern_raw")
        
        # Process the data
        processed_data = self.process_handwerkskammern_data(raw_data)
        
        if processed_data:
            self.save_processed_data(processed_data, "handwerkskammern_processed")
        
        return processed_data
    
    def process_handwerkskammern_data(self, raw_data: Dict) -> List[Dict]:
        """Process raw Handwerkskammern data into standardized format"""
        locations = []
        
        if not isinstance(raw_data, list):
            print("❌ Unexpected data format")
            return []
        
        for item in raw_data:
            try:
                location = {
                    "name": item.get("name", "").strip(),
                    "category": "Handwerkskammer",
                    "latitude": float(item.get("lat", 0)),
                    "longitude": float(item.get("lng", 0)),
                    "address": {
                        "street": item.get("street", "").strip(),
                        "postal_code": item.get("zip", "").strip(),
                        "city": item.get("city", "").strip(),
                        "country": "Germany"
                    },
                    "contact": {
                        "phone": item.get("phone", "").strip(),
                        "fax": item.get("fax", "").strip(),
                        "email": item.get("email", "").strip(),
                        "website": item.get("website", "").strip()
                    },
                    "description": item.get("description", "").strip(),
                    "source": "Handwerkskammern.de",
                    "source_id": item.get("id", ""),
                    "raw_data": item
                }
                
                # Validate coordinates
                if location["latitude"] and location["longitude"]:
                    locations.append(location)
                else:
                    print(f"⚠️  Skipping {location['name']} - missing coordinates")
                    
            except Exception as e:
                print(f"❌ Error processing item: {e}")
                continue
        
        print(f"✅ Processed {len(locations)} Handwerkskammern locations")
        return locations