import requests
import json
import os
from pathlib import Path

def fetch_and_save_data():
    """
    Fetch data from the German Handwerkskammern API and save to JSON file
    """
    # URL to fetch data from
    url = "https://www.zdh.de/ueber-uns/organisationen-des-handwerks/handwerkskammern/deutschlandkarte-der-handwerkskammern/wwt3listmap.json?contentUid=19735&cHash=a097bae8dbb5bedcef25ebaea9e5bcc8"
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    output_file = script_dir / "handwerkskammern_data.json"
    
    try:
        print("Fetching data from German Handwerkskammern API...")
        print(f"URL: {url}")
        
        # Send GET request with headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        # Check if request was successful
        response.raise_for_status()
        
        print(f"✅ Successfully fetched data! Status code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        # Try to parse as JSON
        try:
            data = response.json()
            print(f"✅ JSON parsed successfully!")
            
            # Pretty print some info about the data
            if isinstance(data, dict):
                print(f"📊 Data structure: Dictionary with {len(data)} keys")
                if data:
                    print(f"🔑 Keys: {list(data.keys())}")
            elif isinstance(data, list):
                print(f"📊 Data structure: List with {len(data)} items")
                if data and isinstance(data[0], dict):
                    print(f"🔑 First item keys: {list(data[0].keys())}")
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Response is not valid JSON: {e}")
            print("Saving raw content instead...")
            data = response.text
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            if isinstance(data, (dict, list)):
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                f.write(data)
        
        print(f"✅ Data saved to: {output_file}")
        print(f"📁 File size: {output_file.stat().st_size} bytes")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("🗺️  German Handwerkskammern Data Fetcher")
    print("=" * 60)
    
    result = fetch_and_save_data()
    
    if result is not None:
        print("\n🎉 Operation completed successfully!")
    else:
        print("\n💥 Operation failed!")
    
    print("=" * 60)