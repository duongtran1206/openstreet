"""
3-Tier Data Structure Visualization and Analytics
Hiển thị và phân tích dữ liệu phân cấp 3 tầng
"""

import json
import os
from typing import Dict, List

def visualize_3tier_structure(hierarchical_file: str):
    """Hiển thị cấu trúc 3 tầng một cách trực quan"""
    
    print("🏗️  3-TIER HIERARCHICAL DATA STRUCTURE")
    print("=" * 70)
    
    with open(hierarchical_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # TẦNG 1: LĨNH VỰC (DOMAIN)
    print(f"📁 TẦNG 1 - LĨNH VỰC:")
    print(f"   🎯 Domain ID: {data['domain_id']}")
    print(f"   📋 Domain Name: {data['domain_name']}")
    print(f"   📝 Description: {data['domain_description']}")
    print(f"   🌍 Country: {data['country']}")
    print(f"   🗣️ Language: {data['language']}")
    
    categories = data['categories']
    total_categories = len([cat for cat in categories.values() if len(cat['locations']) > 0])
    total_locations = sum(len(cat['locations']) for cat in categories.values())
    
    print(f"\n📂 TẦNG 2 - DANH MỤC/MẢNG:")
    print(f"   📊 Total Categories: {total_categories}")
    
    # Hiển thị top 10 categories có nhiều locations nhất
    category_stats = []
    for cat_id, cat_data in categories.items():
        if len(cat_data['locations']) > 0:
            category_stats.append({
                'id': cat_id,
                'name': cat_data['category_name'],
                'count': len(cat_data['locations'])
            })
    
    category_stats.sort(key=lambda x: x['count'], reverse=True)
    
    print(f"   🔝 Top 10 Categories by Location Count:")
    for i, cat in enumerate(category_stats[:10], 1):
        print(f"      {i:2d}. {cat['name']:<40} ({cat['count']:2d} locations)")
    
    print(f"\n📍 TẦNG 3 - ĐỊA ĐIỂM:")
    print(f"   📊 Total Locations: {total_locations}")
    print(f"   🔗 Total Category-Location Associations: {sum(cat['count'] for cat in category_stats)}")
    
    # Hiển thị mẫu locations từ category đầu tiên
    if category_stats:
        sample_category = category_stats[0]
        sample_cat_id = sample_category['id']
        sample_locations = categories[sample_cat_id]['locations'][:3]
        
        print(f"\n   📍 Sample Locations from '{sample_category['name']}':")
        for i, loc in enumerate(sample_locations, 1):
            print(f"      {i}. {loc['name']}")
            print(f"         📧 {loc['address']['street']}, {loc['address']['postal_code']} {loc['address']['city']}")
            print(f"         📞 {loc['contact']['phone']}")
            print(f"         🌐 {loc['contact']['website']}")
            print(f"         📍 ({loc['coordinates']['latitude']:.4f}, {loc['coordinates']['longitude']:.4f})")
    
    return {
        'domain': data['domain_name'],
        'categories': total_categories,
        'locations': total_locations,
        'top_categories': category_stats[:5]
    }

def analyze_data_distribution(hierarchical_file: str):
    """Phân tích phân phối dữ liệu"""
    
    print(f"\n📊 DATA DISTRIBUTION ANALYSIS")
    print("=" * 70)
    
    with open(hierarchical_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    categories = data['categories']
    
    # Thống kê phân phối locations theo category
    location_counts = [len(cat['locations']) for cat in categories.values() if len(cat['locations']) > 0]
    
    avg_locations = sum(location_counts) / len(location_counts) if location_counts else 0
    max_locations = max(location_counts) if location_counts else 0
    min_locations = min(location_counts) if location_counts else 0
    
    print(f"📈 Location Distribution Statistics:")
    print(f"   Average locations per category: {avg_locations:.2f}")
    print(f"   Maximum locations in a category: {max_locations}")
    print(f"   Minimum locations in a category: {min_locations}")
    
    # Categories theo tầng phân phối
    ranges = [
        (1, 10, "1-10"),
        (11, 20, "11-20"),  
        (21, 30, "21-30"),
        (31, 40, "31-40"),
        (41, 50, "41-50"),
        (51, 100, "51+")
    ]
    
    print(f"\n📊 Categories by Location Count Ranges:")
    for min_range, max_range, label in ranges:
        count = len([c for c in location_counts if min_range <= c <= max_range])
        if count > 0:
            print(f"   {label:<10}: {count:2d} categories")
    
    # Phân tích coverage địa lý
    all_locations = []
    for cat in categories.values():
        all_locations.extend(cat['locations'])
    
    cities = set()
    states = set()
    
    for loc in all_locations:
        cities.add(loc['address']['city'])
        # Extract state from location name (simple heuristic)
        name = loc['name']
        if 'Hamburg' in name:
            states.add('Hamburg')
        elif 'Berlin' in name:
            states.add('Berlin')
        elif 'München' in name or 'Munich' in name:
            states.add('Bayern')
        # Add more state detection logic as needed
    
    print(f"\n🗺️ Geographic Coverage:")
    print(f"   Unique cities: {len(cities)}")
    print(f"   Sample cities: {', '.join(list(cities)[:10])}")

def create_category_index(hierarchical_file: str, output_file: str = None):
    """Tạo index cho tìm kiếm nhanh theo category"""
    
    print(f"\n🔍 CREATING CATEGORY INDEX")
    print("=" * 70)
    
    with open(hierarchical_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Tạo index cho tìm kiếm nhanh
    category_index = {}
    location_index = {}
    
    for cat_id, cat_data in data['categories'].items():
        if len(cat_data['locations']) > 0:
            # Category index
            category_index[cat_id] = {
                'name': cat_data['category_name'],
                'handwerk_id': cat_data['handwerk_id'],
                'location_count': len(cat_data['locations']),
                'location_ids': [loc['location_id'] for loc in cat_data['locations']]
            }
            
            # Location index
            for loc in cat_data['locations']:
                loc_id = loc['location_id']
                if loc_id not in location_index:
                    location_index[loc_id] = {
                        'name': loc['name'],
                        'city': loc['address']['city'],
                        'coordinates': loc['coordinates'],
                        'categories': []
                    }
                location_index[loc_id]['categories'].append(cat_id)
    
    index_data = {
        'domain_info': {
            'domain_id': data['domain_id'],
            'domain_name': data['domain_name'],
            'created_at': data['created_at']
        },
        'category_index': category_index,
        'location_index': location_index,
        'stats': {
            'total_categories': len(category_index),
            'total_locations': len(location_index)
        }
    }
    
    if not output_file:
        output_file = hierarchical_file.replace('_hierarchical.json', '_index.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"📇 Category index saved to: {output_file}")
    print(f"   📂 {len(category_index)} categories indexed")
    print(f"   📍 {len(location_index)} locations indexed")
    
    return index_data

def main():
    """Main function to demonstrate 3-tier structure"""
    
    hierarchical_file = "data_sources/hierarchical/handwerkskammern_deutschland_hierarchical.json"
    
    if not os.path.exists(hierarchical_file):
        print(f"❌ File not found: {hierarchical_file}")
        print("Please run: python hierarchical_manager.py first")
        return
    
    # Visualize structure
    stats = visualize_3tier_structure(hierarchical_file)
    
    # Analyze distribution 
    analyze_data_distribution(hierarchical_file)
    
    # Create index
    index_data = create_category_index(hierarchical_file)
    
    print(f"\n🎉 3-TIER STRUCTURE ANALYSIS COMPLETE!")
    print(f"📊 Summary:")
    print(f"   🏗️ Structure: {stats['domain']} → {stats['categories']} categories → {stats['locations']} locations")
    print(f"   🔝 Top category: {stats['top_categories'][0]['name']} ({stats['top_categories'][0]['count']} locations)")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"   1. 🌐 Web interface to browse by category")
    print(f"   2. 🗺️ Interactive map with category filtering")
    print(f"   3. 🔍 Search functionality using the index")
    print(f"   4. 📊 Analytics dashboard")

if __name__ == "__main__":
    main()