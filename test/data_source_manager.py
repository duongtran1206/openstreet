"""
Data Source Manager - CRUD operations for multiple data sources
Supports downloading, processing, and importing data from various APIs
"""

import json
import requests
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import time
from bs4 import BeautifulSoup
import re

class DataSourceManager:
    """Manages multiple data sources for map application"""
    
    def __init__(self, config_file: str = "test/data_sources/sources_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def load_config(self) -> Dict:
        """Load data sources configuration"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Config file not found: {self.config_file}")
            return {"data_sources": {}, "database_config": {}}
    
    def save_config(self):
        """Save configuration back to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] Configuration saved to {self.config_file}")
    
    def list_sources(self) -> Dict[str, Dict]:
        """List all available data sources"""
        return self.config.get("data_sources", {})
    
    def get_source(self, source_id: str) -> Optional[Dict]:
        """Get specific data source configuration"""
        return self.config["data_sources"].get(source_id)
    
    def add_source(self, source_id: str, source_config: Dict):
        """Add new data source"""
        self.config["data_sources"][source_id] = source_config
        self.save_config()
        print(f"[SUCCESS] Added data source: {source_id}")
    
    def update_source(self, source_id: str, updates: Dict):
        """Update existing data source"""
        if source_id in self.config["data_sources"]:
            self.config["data_sources"][source_id].update(updates)
            self.save_config()
            print(f"[SUCCESS] Updated data source: {source_id}")
        else:
            print(f"[ERROR] Data source not found: {source_id}")
    
    def remove_source(self, source_id: str):
        """Remove data source"""
        if source_id in self.config["data_sources"]:
            del self.config["data_sources"][source_id]
            self.save_config()
            print(f"[SUCCESS] Removed data source: {source_id}")
        else:
            print(f"[ERROR] Data source not found: {source_id}")
    
    def download_raw_data(self, source_id: str, max_pages: int = None) -> bool:
        """Download raw data from source"""
        source_config = self.get_source(source_id)
        if not source_config:
            print(f"[ERROR] Source not found: {source_id}")
            return False
        
        if not source_config.get("enabled", True):
            print(f"[INFO] Source disabled: {source_id}")
            return False
        
        print(f"[INFO] Downloading data from {source_config['name']}...")
        
        try:
            if source_config["type"] in ["json_direct", "json_nested"]:
                return self._download_direct_json(source_id, source_config)
            elif source_config["type"] == "paginated_api":
                return self._download_paginated_api(source_id, source_config, max_pages)
            else:
                print(f"[ERROR] Unknown source type: {source_config['type']}")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to download {source_id}: {e}")
            return False
    
    def _download_direct_json(self, source_id: str, config: Dict) -> bool:
        """Download JSON directly from URL"""
        response = self.session.get(config["url"])
        response.raise_for_status()
        
        raw_data = response.json()
        
        # Save raw data
        raw_file = f"test/data_sources/raw/{source_id}_raw.json"
        os.makedirs(os.path.dirname(raw_file), exist_ok=True)
        
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        
        print(f"[SUCCESS] Downloaded {len(raw_data) if isinstance(raw_data, list) else 1} records")
        print(f"[SUCCESS] Raw data saved to: {raw_file}")
        
        # Update config
        self.update_source(source_id, {
            "last_updated": datetime.now().isoformat(),
            "total_records": len(raw_data) if isinstance(raw_data, list) else 1
        })
        
        return True
    
    def _download_paginated_api(self, source_id: str, config: Dict, max_pages: int = None) -> bool:
        """Download data from paginated API"""
        pagination = config["pagination"]
        base_url = config["url"]
        all_data = []
        page = 0
        
        while True:
            if max_pages and page >= max_pages:
                print(f"[INFO] Reached max pages limit: {max_pages}")
                break
            
            # Build URL with pagination parameters
            if "?" in base_url:
                url = f"{base_url}&{pagination['page_param']}={page}"
            else:
                url = f"{base_url}?{pagination['page_param']}={page}"
            
            print(f"[INFO] Fetching page {page + 1}...")
            
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Extract content based on configuration
            content_field = pagination.get("content_field", "Contents")
            page_data = data.get(content_field, [])
            
            if not page_data:
                print(f"[INFO] No more data on page {page + 1}")
                break
            
            all_data.extend(page_data)
            
            total_count = data.get(pagination.get("total_count_field", "TotalCount"), 0)
            page_count = data.get(pagination.get("page_count_field", "PageCount"), 0)
            
            print(f"[INFO] Page {page + 1}: {len(page_data)} items (Total: {total_count})")
            
            # Check if we've reached the end
            if page >= page_count - 1:
                print(f"[SUCCESS] Downloaded all {page_count} pages")
                break
            
            page += 1
            time.sleep(1)  # Rate limiting
        
        # Save raw data
        raw_file = f"test/data_sources/raw/{source_id}_raw.json"
        os.makedirs(os.path.dirname(raw_file), exist_ok=True)
        
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_items": len(all_data),
                "pages_downloaded": page + 1,
                "download_timestamp": datetime.now().isoformat(),
                "data": all_data
            }, f, ensure_ascii=False, indent=2)
        
        print(f"[SUCCESS] Downloaded {len(all_data)} total records")
        print(f"[SUCCESS] Raw data saved to: {raw_file}")
        
        # Update config
        self.update_source(source_id, {
            "last_updated": datetime.now().isoformat(),
            "total_records": len(all_data)
        })
        
        return True
    
    def process_raw_data(self, source_id: str) -> bool:
        """Process raw data into standardized format"""
        source_config = self.get_source(source_id)
        if not source_config:
            print(f"[ERROR] Source not found: {source_id}")
            return False
        
        raw_file = f"test/data_sources/raw/{source_id}_raw.json"
        if not os.path.exists(raw_file):
            print(f"[ERROR] Raw data file not found: {raw_file}")
            return False
        
        print(f"[INFO] Processing data for {source_config['name']}...")
        
        try:
            with open(raw_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            if source_config["type"] == "json_direct":
                processed_data = self._process_direct_json(raw_data, source_config)
            elif source_config["type"] == "json_nested":
                processed_data = self._process_nested_json(raw_data, source_config)
            elif source_config["type"] == "paginated_api":
                processed_data = self._process_paginated_data(raw_data["data"], source_config)
            else:
                print(f"[ERROR] Unknown source type: {source_config['type']}")
                return False
            
            # Save processed data
            processed_file = f"test/data_sources/processed/{source_id}_processed.json"
            os.makedirs(os.path.dirname(processed_file), exist_ok=True)
            
            with open(processed_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "source_id": source_id,
                    "source_name": source_config["name"],
                    "category": source_config["category"],
                    "processed_timestamp": datetime.now().isoformat(),
                    "total_locations": len(processed_data),
                    "locations": processed_data
                }, f, ensure_ascii=False, indent=2)
            
            print(f"[SUCCESS] Processed {len(processed_data)} locations")
            print(f"[SUCCESS] Processed data saved to: {processed_file}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to process {source_id}: {e}")
            return False
    
    def _process_direct_json(self, raw_data: List[Dict], config: Dict) -> List[Dict]:
        """Process direct JSON data"""
        processed_locations = []
        fields_mapping = config["fields_mapping"]
        
        for item in raw_data:
            try:
                location = {
                    "name": item.get(fields_mapping.get("name", "name"), "").strip(),
                    "category": config["category"],
                    "latitude": float(item.get(fields_mapping.get("latitude", "lat"), 0)),
                    "longitude": float(item.get(fields_mapping.get("longitude", "lng"), 0)),
                    "address": {
                        "street": item.get(fields_mapping.get("address", "street"), "").strip(),
                        "city": item.get(fields_mapping.get("city", "city"), "").strip(),
                        "postal_code": item.get(fields_mapping.get("postal_code", "zip"), "").strip(),
                        "country": config.get("country", "")
                    },
                    "contact": {
                        "phone": item.get(fields_mapping.get("phone", "phone"), "").strip(),
                        "fax": item.get(fields_mapping.get("fax", "fax"), "").strip(), 
                        "email": item.get(fields_mapping.get("email", "email"), "").strip(),
                        "website": item.get(fields_mapping.get("website", "website"), "").strip()
                    },
                    "metadata": {
                        "source": config["name"],
                        "color": config.get("color", "#95A5A6"),
                        "icon": config.get("icon", "📍"),
                        "source_id": item.get("id", "")
                    },
                    "raw_data": item
                }
                
                # Validate coordinates
                if self._validate_coordinates(location["latitude"], location["longitude"]):
                    processed_locations.append(location)
                else:
                    print(f"[WARN] Invalid coordinates for {location['name']}")
                    
            except Exception as e:
                print(f"[ERROR] Error processing item: {e}")
                continue
        
        return processed_locations
    
    def _get_nested_value(self, data: Dict, key_path: str):
        """Get value from nested dictionary using dot notation"""
        if not key_path:
            return None
            
        keys = key_path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _process_nested_json(self, raw_data: Dict, config: Dict) -> List[Dict]:
        """Process nested JSON data (like Handwerkskammern)"""
        processed_locations = []
        fields_mapping = config["fields_mapping"]
        
        # Extract nested data array
        data_path = config.get("data_path", "")
        if data_path:
            items = self._get_nested_value(raw_data, data_path)
            if not isinstance(items, list):
                print(f"[ERROR] Data path '{data_path}' does not point to a list")
                return []
        else:
            items = raw_data if isinstance(raw_data, list) else []
        
        for item in items:
            try:
                # Extract fields using nested access
                name = self._get_nested_value(item, fields_mapping.get("name", "name")) or ""
                street = self._get_nested_value(item, fields_mapping.get("address", "address")) or ""
                city = self._get_nested_value(item, fields_mapping.get("city", "city")) or ""
                postal_code = self._get_nested_value(item, fields_mapping.get("postal_code", "zip")) or ""
                phone = self._get_nested_value(item, fields_mapping.get("phone", "phone")) or ""
                website = self._get_nested_value(item, fields_mapping.get("website", "website")) or ""
                
                # Get coordinates
                latitude = self._get_nested_value(item, fields_mapping.get("latitude", "latitude")) or 0
                longitude = self._get_nested_value(item, fields_mapping.get("longitude", "longitude")) or 0
                
                location = {
                    "name": str(name).strip(),
                    "category": config["category"],
                    "latitude": float(latitude) if latitude else 0,
                    "longitude": float(longitude) if longitude else 0,
                    "address": {
                        "street": str(street).strip(),
                        "city": str(city).strip(),
                        "postal_code": str(postal_code).strip(),
                        "country": config.get("country", "")
                    },
                    "contact": {
                        "phone": str(phone).strip(),
                        "fax": "",
                        "email": "",
                        "website": str(website).strip()
                    },
                    "metadata": {
                        "source": config["name"],
                        "color": config.get("color", "#95A5A6"),
                        "icon": config.get("icon", "📍"),
                        "source_id": item.get("id", ""),
                        "detail_url": self._get_nested_value(item, fields_mapping.get("detail_url", "")) or ""
                    },
                    "raw_data": item
                }
                
                # Validate coordinates
                if self._validate_coordinates(location["latitude"], location["longitude"]):
                    processed_locations.append(location)
                else:
                    print(f"[WARN] Invalid coordinates for {location['name']}: ({latitude}, {longitude})")
                    
            except Exception as e:
                print(f"[ERROR] Error processing item: {e}")
                continue
        
        return processed_locations
    
    def _process_paginated_data(self, raw_data: List[Dict], config: Dict) -> List[Dict]:
        """Process paginated API data (like Caritas)"""
        processed_locations = []
        fields_mapping = config["fields_mapping"]
        
        for item in raw_data:
            try:
                # Extract basic fields
                name = item.get(fields_mapping.get("name", "Title"), "").strip()
                content_html = item.get(fields_mapping.get("contents", "Contents"), "")
                popup_html = item.get(fields_mapping.get("popup", "Popup"), "")
                
                # Clean HTML and extract information
                content_text = self._clean_html(content_html)
                popup_text = self._clean_html(popup_html)
                combined_text = f"{content_text} {popup_text}"
                
                # Extract contact info and address
                contact_info = self._extract_contact_info(combined_text)
                address_info = self._extract_address_info(combined_text)
                
                location = {
                    "name": name,
                    "category": config["category"],
                    "latitude": float(item.get(fields_mapping.get("latitude", "Latitude"), 0)),
                    "longitude": float(item.get(fields_mapping.get("longitude", "Longitude"), 0)),
                    "address": address_info,
                    "contact": contact_info,
                    "description": self._clean_text(content_text)[:500],  # Limit description
                    "metadata": {
                        "source": config["name"],
                        "color": config.get("color", "#95A5A6"),
                        "icon": config.get("icon", "📍"),
                        "source_id": item.get(fields_mapping.get("content_id", "ContentID"), "")
                    },
                    "raw_data": item
                }
                
                # Validate coordinates
                if self._validate_coordinates(location["latitude"], location["longitude"]):
                    processed_locations.append(location)
                else:
                    print(f"[WARN] Invalid coordinates for {location['name']}")
                    
            except Exception as e:
                print(f"[ERROR] Error processing item: {e}")
                continue
        
        return processed_locations
    
    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content and extract text"""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean whitespace
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information from text"""
        contact_info = {"phone": "", "fax": "", "email": "", "website": ""}
        
        # Phone patterns
        phone_patterns = [
            r'(?:Fon|Tel|Phone)[:\s]+([+\d\s\-\(\)]+)',
            r'(\+49[^\s,<]+)',
            r'(\(\d{2,5}\)[^\s,<]+)',
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                contact_info['phone'] = matches[0].strip()
                break
        
        # Fax patterns
        fax_patterns = [r'(?:Fax)[:\s]+([+\d\s\-\(\)]+)']
        for pattern in fax_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                contact_info['fax'] = matches[0].strip()
                break
        
        # Email patterns
        email_pattern = r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        matches = re.findall(email_pattern, text)
        if matches:
            contact_info['email'] = matches[0]
        
        # Website patterns
        website_patterns = [
            r'href=["\']?(https?://[^"\'>\s]+)',
            r'(www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        ]
        
        for pattern in website_patterns:
            matches = re.findall(pattern, text)
            if matches:
                website = matches[0]
                if not website.startswith('http'):
                    website = 'http://' + website
                contact_info['website'] = website
                break
        
        return contact_info
    
    def _extract_address_info(self, text: str) -> Dict:
        """Extract address information from text"""
        address_info = {"street": "", "postal_code": "", "city": "", "country": "Germany"}
        
        # German postal code pattern
        postal_pattern = r'(\d{5})\s+([A-Za-zäöüß\s-]+)'
        matches = re.findall(postal_pattern, text)
        
        if matches:
            postal_code, city = matches[0]
            address_info['postal_code'] = postal_code.strip()
            address_info['city'] = city.strip()
        
        # Street address pattern (before postal code)
        street_pattern = r'([A-Za-zäöüß\.\s\-]+\s+\d+[a-zA-Z]?)\s*(?:\d{5}|<br>)'
        street_matches = re.findall(street_pattern, text)
        
        if street_matches:
            address_info['street'] = street_matches[0].strip()
        
        return address_info
    
    def _validate_coordinates(self, lat: float, lng: float) -> bool:
        """Validate coordinates are within reasonable bounds"""
        db_config = self.config.get("database_config", {})
        
        min_lat = db_config.get("min_latitude", -90)
        max_lat = db_config.get("max_latitude", 90)
        min_lng = db_config.get("min_longitude", -180)
        max_lng = db_config.get("max_longitude", 180)
        
        return (min_lat <= lat <= max_lat and min_lng <= lng <= max_lng and 
                lat != 0 and lng != 0)
    
    def get_summary(self) -> Dict:
        """Get summary of all data sources"""
        summary = {
            "total_sources": len(self.config["data_sources"]),
            "enabled_sources": 0,
            "sources": {}
        }
        
        for source_id, source_config in self.config["data_sources"].items():
            if source_config.get("enabled", True):
                summary["enabled_sources"] += 1
            
            # Check if files exist
            raw_file = f"test/data_sources/raw/{source_id}_raw.json"
            processed_file = f"test/data_sources/processed/{source_id}_processed.json"
            
            summary["sources"][source_id] = {
                "name": source_config["name"],
                "category": source_config["category"],
                "enabled": source_config.get("enabled", True),
                "last_updated": source_config.get("last_updated"),
                "total_records": source_config.get("total_records"),
                "has_raw_data": os.path.exists(raw_file),
                "has_processed_data": os.path.exists(processed_file)
            }
        
        return summary