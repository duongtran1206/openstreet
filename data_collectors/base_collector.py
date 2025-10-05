"""
Base Data Collector Class
Provides common functionality for all data collectors
"""

import json
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import time
import re
from bs4 import BeautifulSoup

class BaseDataCollector(ABC):
    """Base class for all data collectors"""
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def save_raw_data(self, data: Any, filename: str):
        """Save raw data to JSON file"""
        output_path = f"data_collectors/raw_data/{self.name}_{filename}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] Saved raw data to {output_path}")
    
    def save_processed_data(self, data: List[Dict], filename: str):
        """Save processed data to JSON file"""
        output_path = f"data_collectors/processed_data/{self.name}_{filename}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] Saved processed data to {output_path}")
        
    def make_request(self, url: str, params: Optional[Dict] = None, delay: float = 1.0) -> Optional[Dict]:
        """Make HTTP request with error handling and rate limiting"""
        try:
            time.sleep(delay)
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # Try to parse as JSON first
            try:
                return response.json()
            except:
                # If not JSON, return text content
                return {'content': response.text, 'url': response.url}
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error fetching {url}: {e}")
            return None
    
    def extract_coordinates(self, text: str) -> Optional[tuple]:
        """Extract latitude and longitude from text"""
        # Common coordinate patterns
        patterns = [
            r'(?:lat|latitude)["\s:=]+([+-]?\d+\.?\d*)',
            r'(?:lng|lon|longitude)["\s:=]+([+-]?\d+\.?\d*)',
            r'"Latitude":([+-]?\d+\.?\d*)',
            r'"Longitude":([+-]?\d+\.?\d*)',
        ]
        
        coords = {}
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches and 'lat' in pattern.lower():
                coords['lat'] = float(matches[0])
            elif matches:
                coords['lng'] = float(matches[0])
                
        if 'lat' in coords and 'lng' in coords:
            return coords['lat'], coords['lng']
        return None
    
    def clean_html(self, html_content: str) -> str:
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
    
    def extract_contact_info(self, text: str) -> Dict:
        """Extract contact information from text"""
        contact_info = {}
        
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
        fax_patterns = [
            r'(?:Fax)[:\s]+([+\d\s\-\(\)]+)',
        ]
        
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
    
    def extract_address(self, text: str) -> Dict:
        """Extract address information from text"""
        address_info = {}
        
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
    
    @abstractmethod
    def collect_data(self, **kwargs) -> List[Dict]:
        """
        Abstract method to collect data from the specific source.
        Must be implemented by each collector.
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict:
        """
        Abstract method to return metadata about the collector.
        Must be implemented by each collector.
        """
        pass