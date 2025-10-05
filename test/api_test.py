#!/usr/bin/env python3
"""
API Test Script - Kiểm tra tất cả endpoints của Hierarchical Map System
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

class APITester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def test_endpoint(self, method, endpoint, description, expected_status=200, params=None, data=None):
        """Test một API endpoint"""
        self.total_tests += 1
        url = f"{BASE_URL}{endpoint}"
        
        try:
            print(f"\n🧪 Testing: {description}")
            print(f"   URL: {method} {url}")
            
            if params:
                print(f"   Params: {params}")
            
            start_time = time.time()
            
            if method.upper() == 'GET':
                response = requests.get(url, params=params, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, timeout=10)
            
            elapsed = time.time() - start_time
            
            # Check status code
            if response.status_code == expected_status:
                print(f"   ✅ Status: {response.status_code} (Expected: {expected_status})")
                self.passed_tests += 1
                status = "PASS"
            else:
                print(f"   ❌ Status: {response.status_code} (Expected: {expected_status})")
                status = "FAIL"
            
            # Check response content
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                try:
                    json_data = response.json()
                    if isinstance(json_data, list):
                        print(f"   📊 Data: List with {len(json_data)} items")
                    elif isinstance(json_data, dict):
                        if 'features' in json_data:  # GeoJSON
                            features = len(json_data.get('features', []))
                            print(f"   🗺️  Data: GeoJSON with {features} features")
                        else:
                            keys = list(json_data.keys())[:5]  # First 5 keys
                            print(f"   📋 Data: Object with keys: {keys}")
                    print(f"   ⚡ Response Time: {elapsed:.3f}s")
                except Exception as e:
                    print(f"   ⚠️  JSON Parse Error: {e}")
            else:
                print(f"   📄 Content-Type: {content_type}")
                print(f"   📏 Content Length: {len(response.text)} chars")
            
            # Store result
            self.results.append({
                'endpoint': endpoint,
                'description': description,
                'status_code': response.status_code,
                'expected_status': expected_status,
                'passed': status == "PASS",
                'response_time': elapsed,
                'content_type': content_type
            })
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request Error: {e}")
            self.results.append({
                'endpoint': endpoint,
                'description': description,
                'error': str(e),
                'passed': False
            })
    
    def run_all_tests(self):
        """Chạy tất cả tests"""
        print("🚀 HIERARCHICAL MAP API TESTING")
        print("=" * 50)
        print(f"Base URL: {BASE_URL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test Web Pages
        print("\n📱 WEB INTERFACE TESTS")
        self.test_endpoint("GET", "/", "Main Map View", 200)
        self.test_endpoint("GET", "/embed/", "Embed Map (PRIMARY)", 200)
        self.test_endpoint("GET", "/embed-debug/", "Debug Embed Page", 200)
        self.test_endpoint("GET", "/hierarchical/", "Hierarchical Map Interface", 200)
        self.test_endpoint("GET", "/admin-map/", "Admin Map View", 200)
        
        # Test Hierarchical APIs
        print("\n🏗️ HIERARCHICAL API TESTS")
        self.test_endpoint("GET", "/api/hierarchical/domains/", "Get All Domains", 200)
        
        self.test_endpoint("GET", "/api/hierarchical/categories/", 
                          "Get Categories (Caritas)", 200, 
                          params={"domain": "caritas_deutschland"})
        
        self.test_endpoint("GET", "/api/hierarchical/categories/", 
                          "Get Categories (Handwerk)", 200, 
                          params={"domain": "handwerkskammern_deutschland"})
        
        self.test_endpoint("GET", "/api/hierarchical/locations/", 
                          "Get Locations (All Caritas)", 200, 
                          params={"domain": "caritas_deutschland"})
        
        self.test_endpoint("GET", "/api/hierarchical/locations/", 
                          "Get Locations (Caritas Jugendmigration)", 200, 
                          params={
                              "domain": "caritas_deutschland",
                              "categories[0]": "jugendmigrationsdienst"
                          })
        
        self.test_endpoint("GET", "/api/hierarchical/search/", 
                          "Search Locations (Dresden)", 200, 
                          params={"q": "Dresden", "domain": "caritas_deutschland"})
        
        # Test Legacy APIs
        print("\n🗺️ LEGACY API TESTS")
        self.test_endpoint("GET", "/api/map-data/", "Legacy Map Data", 200)
        self.test_endpoint("GET", "/api/map-config/", "Map Configuration", 200)
        self.test_endpoint("GET", "/api/categories/", "Legacy Categories", 200)
        self.test_endpoint("GET", "/api/locations/", "Legacy Locations", 200)
        
        # Test Data Collection APIs
        print("\n📊 DATA COLLECTION API TESTS")
        self.test_endpoint("GET", "/api/collection-sources/", "Collection Sources", 200)
        self.test_endpoint("GET", "/api/collection-stats/", "Collection Stats", 200)
        
        # Test Error Cases
        print("\n❌ ERROR HANDLING TESTS")
        self.test_endpoint("GET", "/api/hierarchical/categories/", 
                          "Invalid Domain", 200, 
                          params={"domain": "invalid_domain"})
        
        self.test_endpoint("GET", "/nonexistent-url/", 
                          "404 Not Found Test", 404)
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """In tổng kết test results"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in self.results if r.get('passed', False))
        failed = self.total_tests - passed
        success_rate = (passed / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if not result.get('passed', False):
                    endpoint = result['endpoint']
                    desc = result['description']
                    if 'error' in result:
                        print(f"   • {endpoint} - {desc} - Error: {result['error']}")
                    else:
                        expected = result.get('expected_status', 'N/A')
                        actual = result.get('status_code', 'N/A')
                        print(f"   • {endpoint} - {desc} - Status: {actual} (Expected: {expected})")
        
        # Performance stats
        response_times = [r.get('response_time', 0) for r in self.results if 'response_time' in r]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            print(f"\n⚡ PERFORMANCE:")
            print(f"   Average Response Time: {avg_time:.3f}s")
            print(f"   Fastest: {min_time:.3f}s")
            print(f"   Slowest: {max_time:.3f}s")
        
        print(f"\n🎉 {'ALL SYSTEMS OPERATIONAL!' if failed == 0 else 'SOME ISSUES DETECTED'}")
        print(f"🌐 Primary URL: {BASE_URL}/embed/")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()