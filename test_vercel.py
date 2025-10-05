import requests
import json

BASE_URL = "https://openstreet-ncb1vce5q-duongtranbkas-projects.vercel.app"

def test_endpoint(url, description):
    """Test an endpoint and print results"""
    print(f"\n🔍 Testing: {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS")
            if 'application/json' in response.headers.get('content-type', ''):
                try:
                    data = response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                except:
                    print("Response: Valid JSON response received")
            else:
                print(f"Content length: {len(response.text)} chars")
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - Request took too long")
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR - {str(e)}")

def main():
    print("🚀 Testing Vercel Deployment")
    print("=" * 50)
    
    # Test endpoints
    test_endpoint(f"{BASE_URL}/health/", "Health Check")
    test_endpoint(f"{BASE_URL}/api/status/", "API Status")
    test_endpoint(f"{BASE_URL}/", "Main Page")
    test_endpoint(f"{BASE_URL}/embed/", "Embed Page")
    test_endpoint(f"{BASE_URL}/api/domains/", "Domains API")

if __name__ == "__main__":
    main()