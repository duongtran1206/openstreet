"""
Caritas Data Collector
Collects data from Caritas Germany mapping service
"""

from .base_collector import BaseDataCollector
from typing import Dict, List, Optional
import re
from urllib.parse import urlencode

class CaritasCollector(BaseDataCollector):
    """Collector for Caritas Germany data"""
    
    def __init__(self):
        super().__init__(
            name="caritas",
            base_url="https://www.caritas.de"
        )
        self.api_url = "https://www.caritas.de/Services/MappingService.svc/GetMapContents"
        self.default_params = {
            "datasource": "80c48846275643e0b82b83465979eb70",
            "page": 0,
            "pagesize": 50  # Increased page size
        }
    
    def get_metadata(self) -> Dict:
        """Return metadata about this collector"""
        return {
            "name": "Caritas Germany",
            "description": "Catholic charity organization services in Germany",
            "source_url": "https://www.caritas.de",
            "category": "Social Services",
            "country": "Germany",
            "data_types": ["social_services", "migration_services", "counseling", "locations"],
            "subcategories": [
                "Migrationsberatung",
                "Jugendmigrationsdienst", 
                "Beratungszentrum",
                "Gemeinwesenorientierte Arbeit",
                "IQ - Faire Integration"
            ]
        }
    
    def collect_data(self, max_pages: int = 10, save_raw: bool = True) -> List[Dict]:
        """Collect Caritas data from multiple pages"""
        print(f"[INFO] Collecting data from {self.name}...")
        
        all_locations = []
        all_raw_data = []
        page = 0
        
        while page < max_pages:
            print(f"[PAGE] Fetching page {page + 1}...")
            
            # Build URL with page parameter
            url_parts = [
                self.api_url,
                "ec7e69ee-35b9-45b9-b081-fc7a191a76c0",
                ""
            ]
            url = "/".join(url_parts)
            
            params = self.default_params.copy()
            params["page"] = page
            
            raw_data = self.make_request(url, params)
            
            if not raw_data or not raw_data.get("Contents"):
                print(f"[INFO] No more data on page {page + 1}")
                break
            
            contents = raw_data.get("Contents", [])
            total_count = raw_data.get("TotalCount", 0)
            page_count = raw_data.get("PageCount", 0)
            
            print(f"[DATA] Page {page + 1}: {len(contents)} items (Total: {total_count})")
            
            all_raw_data.extend(contents)
            
            # Process this page's data
            page_locations = self.process_caritas_data(contents)
            all_locations.extend(page_locations)
            
            # Check if we've reached the end
            if page >= page_count - 1:
                print(f"[SUCCESS] Reached last page ({page_count} total pages)")
                break
                
            page += 1
        
        if save_raw:
            self.save_raw_data({
                "total_items": len(all_raw_data),
                "pages_collected": page + 1,
                "contents": all_raw_data
            }, "caritas_raw")
        
        if all_locations:
            self.save_processed_data(all_locations, "caritas_processed")
        
        print(f"[SUCCESS] Collected {len(all_locations)} Caritas locations from {page + 1} pages")
        return all_locations
    
    def process_caritas_data(self, contents: List[Dict]) -> List[Dict]:
        """Process raw Caritas data into standardized format"""
        locations = []
        
        for item in contents:
            try:
                # Extract basic info
                title = item.get("Title", "").strip()
                content_html = item.get("Contents", "")
                popup_html = item.get("Popup", "")
                
                # Clean HTML content
                content_text = self.clean_html(content_html)
                popup_text = self.clean_html(popup_html)
                combined_text = f"{content_text} {popup_text}"
                
                # Extract category from content
                category = self.extract_category(combined_text)
                
                # Extract contact info
                contact_info = self.extract_contact_info(combined_text)
                
                # Extract address
                address_info = self.extract_address(combined_text)
                
                location = {
                    "name": title,
                    "category": category,
                    "latitude": float(item.get("Latitude", 0)),
                    "longitude": float(item.get("Longitude", 0)),
                    "address": {
                        "street": address_info.get("street", ""),
                        "postal_code": address_info.get("postal_code", ""),
                        "city": address_info.get("city", ""),
                        "country": "Germany"
                    },
                    "contact": contact_info,
                    "description": self.clean_description(content_text),
                    "services": self.extract_services(combined_text),
                    "source": "Caritas.de",
                    "source_id": item.get("ContentID", ""),
                    "raw_data": item
                }
                
                # Validate coordinates
                if location["latitude"] and location["longitude"]:
                    locations.append(location)
                else:
                    print(f"[WARN] Skipping {location['name']} - missing coordinates")
                    
            except Exception as e:
                print(f"[ERROR] Error processing Caritas item: {e}")
                continue
        
        return locations
    
    def extract_category(self, text: str) -> str:
        """Extract category from text content"""
        # Look for category indicators in the text
        categories = [
            ("Migrationsberatung für Erwachsene", "Migration Counseling Adults"),
            ("Jugendmigrationsdienst", "Youth Migration Service"),
            ("Migrationsberatung", "Migration Counseling"),
            ("Beratungszentrum", "Counseling Center"),
            ("Gemeinwesenorientierte Arbeit", "Community Work"),
            ("IQ - Faire Integration", "Fair Integration"),
            ("Flüchtlings.*beratung", "Refugee Counseling"),
        ]
        
        for german_term, english_term in categories:
            if re.search(german_term, text, re.IGNORECASE):
                return english_term
        
        return "Social Services"
    
    def extract_services(self, text: str) -> List[str]:
        """Extract services offered from text"""
        services = []
        
        service_indicators = [
            "beratung", "counseling", "integration", "migration", 
            "flüchtling", "refugee", "sozial", "social"
        ]
        
        for indicator in service_indicators:
            if indicator.lower() in text.lower():
                services.append(indicator.capitalize())
        
        return list(set(services))  # Remove duplicates
    
    def clean_description(self, text: str) -> str:
        """Clean and shorten description text"""
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit length
        if len(text) > 200:
            text = text[:197] + "..."
        
        return text