#!/usr/bin/env python3
"""
Django Direct Import Script for Caritas Data
Sử dụng Django ORM trực tiếp để tạo dữ liệu
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapproject.settings')
django.setup()

from maps.hierarchical_models import Domain, HierarchicalCategory, HierarchicalLocation

def create_caritas_data():
    """Tạo dữ liệu Caritas trực tiếp qua Django ORM"""
    print("🚀 Creating Caritas data via Django ORM...")
    
    # 1. Tạo Domain
    domain, created = Domain.objects.get_or_create(
        domain_id='caritas_deutschland',
        defaults={
            'name': 'Caritas Deutschland',
            'description': 'Caritas Deutschland - Soziale Dienste und Migrationsberatung',
            'country': 'Germany',
            'language': 'de',
            'color_scheme': 'caritas_red',
            'icon': 'Caritas',
            'is_active': True,
            'featured': True,
            'source_url': 'https://www.caritas.de'
        }
    )
    
    if created:
        print(f"✅ Created domain: {domain.name}")
    else:
        print(f"📍 Domain already exists: {domain.name}")
    
    # 2. Tạo Categories
    categories_data = [
        {
            'category_id': 'jugendmigrationsdienst',
            'name': 'Jugendmigrationsdienst',
            'color': '#FF6B6B',
            'icon': 'Jugend'
        },
        {
            'category_id': 'migrationsberatung_erwachsene',
            'name': 'Migrationsberatung für Erwachsene',
            'color': '#4ECDC4', 
            'icon': 'Erwachsene'
        },
        {
            'category_id': 'migrationsberatung',
            'name': 'Migrationsberatung',
            'color': '#45B7D1',
            'icon': 'Beratung'
        },
        {
            'category_id': 'gemeinwesenorientierte_arbeit',
            'name': 'Gemeinwesenorientierte Arbeit',
            'color': '#96CEB4',
            'icon': 'Gemeinwesen'
        },
        {
            'category_id': 'iq_faire_integration',
            'name': 'IQ - Faire Integration',
            'color': '#FFEAA7',
            'icon': 'Integration'
        },
        {
            'category_id': 'beratungszentrum',
            'name': 'Beratungszentrum',
            'color': '#DDA0DD',
            'icon': 'Zentrum'
        },
        {
            'category_id': 'allgemein',
            'name': 'Allgemeine Beratung',
            'color': '#F7DC6F',
            'icon': 'Caritas'
        }
    ]
    
    created_categories = []
    for cat_data in categories_data:
        category, created = HierarchicalCategory.objects.get_or_create(
            category_id=cat_data['category_id'],
            domain=domain,
            defaults={
                'name': cat_data['name'],
                'color': cat_data['color'],
                'icon': cat_data['icon'],
                'external_id': cat_data['category_id'],
                'is_active': True,
                'display_order': 0
            }
        )
        
        if created:
            print(f"✅ Created category: {category.name}")
        else:
            print(f"📍 Category already exists: {category.name}")
        
        created_categories.append(category)
    
    # 3. Tạo Sample Locations
    locations_data = [
        {
            'location_id': 'dresden_jmd',
            'name': 'Kath. Jugendmigrationsdienst Dresden',
            'latitude': 51.04707,
            'longitude': 13.7592301,
            'street': 'Canalettostraße 10',
            'city': 'Dresden',
            'postal_code': '01307',
            'phone': '+49 (0351) 4984-746',
            'email': 'jmd@caritas-dresden.de',
            'category_id': 'jugendmigrationsdienst'
        },
        {
            'location_id': 'freital_jmd',
            'name': 'Jugendmigrationsdienst Freital',
            'latitude': 51.00217,
            'longitude': 13.65205,
            'street': 'Dresdner Straße 162',
            'city': 'Freital',
            'postal_code': '01705',
            'phone': '+49 (0176) 39255033',
            'email': 'jmd-freital@caritas-dresden.de',
            'category_id': 'jugendmigrationsdienst'
        },
        {
            'location_id': 'bautzen_mbe',
            'name': 'Caritasverband Oberlausitz e.V Migrationsberatung',
            'latitude': 51.1806236,
            'longitude': 14.4289502,
            'street': 'Kirchplatz 2',
            'city': 'Bautzen',
            'postal_code': '02625',
            'phone': '+49 (3591) 498250',
            'email': 'meb@caritas-oberlausitz.de',
            'category_id': 'migrationsberatung_erwachsene'
        },
        {
            'location_id': 'goerlitz_migration',
            'name': 'Caritas-Region Görlitz',
            'latitude': 51.1500422,
            'longitude': 14.9858229,
            'street': 'Wilhelmsplatz 2',
            'city': 'Görlitz',
            'postal_code': '02826',
            'phone': '+49 (3581) 420028',
            'email': 'migration.goerlitz@caritas-goerlitz.de',
            'category_id': 'migrationsberatung'
        },
        {
            'location_id': 'cottbus_gemeinwesen',
            'name': 'Caritas-Region Cottbus',
            'latitude': 51.7520649,
            'longitude': 14.3334005,
            'street': 'Straße der Jugend 23',
            'city': 'Cottbus',
            'postal_code': '03046',
            'phone': '+49 (355) 38003735',
            'email': '',
            'category_id': 'gemeinwesenorientierte_arbeit'
        }
    ]
    
    created_locations = []
    for loc_data in locations_data:
        # Tìm category
        category = next((cat for cat in created_categories if cat.category_id == loc_data['category_id']), None)
        
        if not category:
            print(f"❌ Category not found for location: {loc_data['name']}")
            continue
        
        location, created = HierarchicalLocation.objects.get_or_create(
            location_id=loc_data['location_id'],
            defaults={
                'name': loc_data['name'],
                'latitude': loc_data['latitude'],
                'longitude': loc_data['longitude'],
                'street': loc_data['street'],
                'city': loc_data['city'],
                'postal_code': loc_data['postal_code'],
                'country': 'Germany',
                'phone': loc_data['phone'],
                'email': loc_data['email'],
                'description': f"Caritas {loc_data['name']}",
                'is_active': True,
                'verified': False,
                'source_name': 'Caritas Deutschland API',
                'raw_data': {
                    'category': loc_data['category_id'],
                    'import_source': 'caritas_api'
                }
            }
        )
        
        if created:
            print(f"✅ Created location: {location.name}")
            # Thêm category vào location
            location.categories.add(category)
        else:
            print(f"📍 Location already exists: {location.name}")
        
        created_locations.append(location)
    
    print(f"\n📊 Summary:")
    print(f"   - Domain: 1 ({domain.name})")
    print(f"   - Categories: {len(created_categories)}")  
    print(f"   - Locations: {len(created_locations)}")
    
    return domain, created_categories, created_locations

def verify_data():
    """Kiểm tra dữ liệu đã tạo"""
    print("\n🔍 Verifying created data...")
    
    # Kiểm tra Domain
    domain_count = Domain.objects.filter(domain_id='caritas_deutschland').count()
    print(f"   Domains: {domain_count}")
    
    # Kiểm tra Categories
    categories = HierarchicalCategory.objects.filter(domain__domain_id='caritas_deutschland')
    print(f"   Categories: {categories.count()}")
    
    # Kiểm tra Locations
    locations = HierarchicalLocation.objects.filter(categories__domain__domain_id='caritas_deutschland')
    print(f"   Locations: {locations.distinct().count()}")
    
    # Test API endpoint
    if locations.exists():
        print(f"\n🌐 Test API:")
        print(f"   Domain ID to use: caritas_deutschland")
        print(f"   Categories available: {list(categories.values_list('category_id', flat=True))}")

def main():
    """Main function"""
    print("🚀 Caritas Django Direct Import")
    print("="*50)
    
    try:
        domain, categories, locations = create_caritas_data()
        verify_data()
        
        print("="*50)
        print("✅ Import completed successfully!")
        print("\n🎯 Next steps:")
        print("   1. Check hierarchical map: http://127.0.0.1:8000/hierarchical/")
        print("   2. Check embed map: http://127.0.0.1:8000/embed/")
        print("   3. Test API: http://127.0.0.1:8000/api/hierarchical/locations/?domain=caritas_deutschland")
        
    except Exception as e:
        print(f"❌ Error during import: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()