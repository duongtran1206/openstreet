#!/usr/bin/env python3
"""
Fix Caritas Fixtures for Django Models
Sửa lại fixtures để phù hợp với Django model structure
"""

import json

def fix_caritas_fixtures():
    """Sửa lại fixtures file để phù hợp với model"""
    print("🔧 Fixing Caritas fixtures...")
    
    # Load original fixtures
    with open('caritas_fixtures.json', 'r', encoding='utf-8') as f:
        fixtures = json.load(f)
    
    fixed_fixtures = []
    
    for fixture in fixtures:
        model = fixture['model']
        
        if model == 'maps.domain':
            # Domain model không cần pk, sử dụng domain_id trong fields
            fixed_fixture = {
                "model": "maps.domain",
                "fields": {
                    "domain_id": fixture['pk'],  # Move pk to domain_id field
                    **fixture['fields']
                }
            }
            fixed_fixtures.append(fixed_fixture)
            
        elif model == 'maps.hierarchicalcategory':
            # Category model có category_id, không cần pk integer
            fixed_fixture = {
                "model": "maps.hierarchicalcategory", 
                "fields": {
                    "category_id": fixture['pk'],  # Move pk to category_id field
                    **fixture['fields']
                }
            }
            fixed_fixtures.append(fixed_fixture)
            
        elif model == 'maps.hierarchicallocation':
            # Location model có location_id, không cần pk integer  
            fixed_fixture = {
                "model": "maps.hierarchicallocation",
                "fields": {
                    "location_id": fixture['pk'],  # Move pk to location_id field
                    **fixture['fields']
                }
            }
            fixed_fixtures.append(fixed_fixture)
            
        else:
            # Giữ nguyên các model khác
            fixed_fixtures.append(fixture)
    
    # Save fixed fixtures
    with open('caritas_fixtures_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(fixed_fixtures, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Fixed {len(fixed_fixtures)} fixtures")
    print("💾 Saved as: caritas_fixtures_fixed.json")

def create_many_to_many_fixtures():
    """Tạo fixtures cho many-to-many relationships"""
    print("\n🔗 Creating many-to-many relationship fixtures...")
    
    # Load fixed fixtures để tìm relationships
    with open('caritas_fixtures_fixed.json', 'r', encoding='utf-8') as f:
        fixtures = json.load(f)
    
    # Tìm locations và categories để tạo relationships
    locations = [f for f in fixtures if f['model'] == 'maps.hierarchicallocation']
    
    m2m_fixtures = []
    
    # Tạo fixtures cho ManyToMany relationships giữa locations và categories
    for location in locations:
        location_id = location['fields']['location_id']
        
        # Lấy category từ raw_data hoặc suy đoán
        raw_data = location['fields'].get('raw_data', {})
        service_type = raw_data.get('service_type', '')
        
        # Determine category based on service type
        category_id = get_category_id_for_service(service_type)
        
        # Tạo through table entry (nếu cần)
        # Note: Django auto-handles ManyToMany, chỉ cần set trong fixtures
        # Nhưng vì model có categories field, cần set đúng format
        if 'categories' not in location['fields']:
            location['fields']['categories'] = [category_id]
    
    # Update fixtures with relationships
    with open('caritas_fixtures_final.json', 'w', encoding='utf-8') as f:
        json.dump(fixtures, f, ensure_ascii=False, indent=2)
    
    print("✅ Updated fixtures with relationships")
    print("💾 Saved as: caritas_fixtures_final.json")

def get_category_id_for_service(service_type):
    """Convert service type to category ID"""
    if not service_type:
        return 'caritas_allgemein'
    
    service_type = service_type.lower().strip()
    
    mappings = {
        'jugendmigrationsdienst': 'caritas_jugendmigrationsdienst',
        'migrationsberatung für erwachsene': 'caritas_migrationsberatung_fuer_erwachsene',
        'migrationsberatung': 'caritas_migrationsberatung',
        'gemeinwesenorientierte arbeit': 'caritas_gemeinwesenorientierte_arbeit',
        'iq - faire integration': 'caritas_iq_faire_integration',
        'beratungszentrum': 'caritas_beratungszentrum'
    }
    
    # Direct match
    if service_type in mappings:
        return mappings[service_type]
    
    # Partial matches
    for service_key, category_id in mappings.items():
        if service_key in service_type:
            return category_id
    
    return 'caritas_allgemein'

def main():
    """Main function"""
    print("🛠️ Caritas Fixtures Fixer")
    print("="*50)
    
    # Fix basic fixtures structure
    fix_caritas_fixtures()
    
    # Create M2M relationships
    create_many_to_many_fixtures()
    
    print("="*50)
    print("✅ All fixes completed!")
    print("\n🔧 To import into Django:")
    print("   python manage.py loaddata caritas_fixtures_final.json")
    
    print("\n📋 Files created:")
    print("   - caritas_fixtures_fixed.json (basic fixes)")
    print("   - caritas_fixtures_final.json (with relationships)")

if __name__ == "__main__":
    main()