#!/usr/bin/env python3
"""
Final Caritas Fixtures Creator
Tạo fixtures hoàn chỉnh với tất cả required fields
"""

import json
from datetime import datetime

def create_final_fixtures():
    """Tạo fixtures hoàn chỉnh"""
    print("🔧 Creating complete Caritas fixtures...")
    
    current_time = datetime.now().isoformat()
    
    fixtures = []
    
    # 1. DOMAIN
    domain_fixture = {
        "model": "maps.domain",
        "fields": {
            "domain_id": "caritas_deutschland",
            "name": "Caritas Deutschland",
            "description": "Caritas Deutschland - Soziale Dienste und Migrationsberatung",
            "country": "Germany",
            "language": "de",
            "color_scheme": "caritas_red",
            "icon": "Caritas",
            "is_active": True,
            "featured": True,
            "source_url": "https://www.caritas.de",
            "last_updated": current_time,
            "created_at": current_time
        }
    }
    fixtures.append(domain_fixture)
    
    # 2. CATEGORIES
    categories = [
        {
            "category_id": "caritas_jugendmigrationsdienst",
            "name": "Jugendmigrationsdienst",
            "color": "#FF6B6B",
            "icon": "Jugend"
        },
        {
            "category_id": "caritas_migrationsberatung_fuer_erwachsene",
            "name": "Migrationsberatung für Erwachsene", 
            "color": "#4ECDC4",
            "icon": "Erwachsene"
        },
        {
            "category_id": "caritas_migrationsberatung",
            "name": "Migrationsberatung",
            "color": "#45B7D1",
            "icon": "Beratung"
        },
        {
            "category_id": "caritas_gemeinwesenorientierte_arbeit",
            "name": "Gemeinwesenorientierte Arbeit",
            "color": "#96CEB4", 
            "icon": "Gemeinwesen"
        },
        {
            "category_id": "caritas_iq_faire_integration",
            "name": "IQ - Faire Integration",
            "color": "#FFEAA7",
            "icon": "Integration"
        },
        {
            "category_id": "caritas_beratungszentrum",
            "name": "Beratungszentrum",
            "color": "#DDA0DD",
            "icon": "Zentrum"
        },
        {
            "category_id": "caritas_allgemein",
            "name": "Allgemeine Beratung",
            "color": "#F7DC6F",
            "icon": "Caritas"
        }
    ]
    
    for cat in categories:
        category_fixture = {
            "model": "maps.hierarchicalcategory",
            "fields": {
                "category_id": cat["category_id"],
                "name": cat["name"], 
                "domain_id": "caritas_deutschland",
                "color": cat["color"],
                "icon": cat["icon"],
                "description": f"Caritas {cat['name']} Services",
                "is_active": True,
                "source_identifier": cat["category_id"].replace("caritas_", "")
            }
        }
        fixtures.append(category_fixture)
    
    # 3. Sample LOCATIONS (chỉ tạo vài location để test)
    sample_locations = [
        {
            "location_id": "caritas_dresden_jmd",
            "name": "Kath. Jugendmigrationsdienst Dresden", 
            "latitude": 51.04707,
            "longitude": 13.7592301,
            "street": "Canalettostraße 10",
            "city": "Dresden",
            "postal_code": "01307",
            "phone": "+49 (0351) 4984-746",
            "email": "jmd@caritas-dresden.de",
            "category": "caritas_jugendmigrationsdienst"
        },
        {
            "location_id": "caritas_freital_jmd",
            "name": "Jugendmigrationsdienst Freital",
            "latitude": 51.00217,
            "longitude": 13.65205,
            "street": "Dresdner Straße 162", 
            "city": "Freital",
            "postal_code": "01705",
            "phone": "+49 (0176) 39255033",
            "email": "jmd-freital@caritas-dresden.de",
            "category": "caritas_jugendmigrationsdienst"
        },
        {
            "location_id": "caritas_bautzen_mbe",
            "name": "Caritasverband Oberlausitz e.V Migrationsberatung",
            "latitude": 51.1806236,
            "longitude": 14.4289502,
            "street": "Kirchplatz 2",
            "city": "Bautzen", 
            "postal_code": "02625",
            "phone": "+49 (3591) 498250",
            "email": "meb@caritas-oberlausitz.de",
            "category": "caritas_migrationsberatung_fuer_erwachsene"
        }
    ]
    
    for loc in sample_locations:
        location_fixture = {
            "model": "maps.hierarchicallocation",
            "fields": {
                "location_id": loc["location_id"],
                "name": loc["name"],
                "latitude": loc["latitude"],
                "longitude": loc["longitude"],
                "street": loc["street"],
                "city": loc["city"],
                "postal_code": loc["postal_code"],
                "country": "Germany",
                "phone": loc["phone"],
                "fax": "",
                "email": loc["email"],
                "website": "",
                "description": f"Caritas {loc['name']}",
                "is_active": True,
                "verified": False,
                "source_name": "Caritas Deutschland API",
                "raw_data": {
                    "category": loc["category"],
                    "import_source": "caritas_api"
                }
            }
        }
        fixtures.append(location_fixture)
    
    # Save fixtures
    with open('caritas_minimal_fixtures.json', 'w', encoding='utf-8') as f:
        json.dump(fixtures, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Created {len(fixtures)} fixtures:")
    print(f"   - 1 Domain")
    print(f"   - {len(categories)} Categories") 
    print(f"   - {len(sample_locations)} Locations")
    print("💾 Saved as: caritas_minimal_fixtures.json")

def main():
    """Main function"""
    print("🚀 Caritas Minimal Fixtures Creator")
    print("="*50)
    
    create_final_fixtures()
    
    print("="*50)
    print("✅ Ready to import!")
    print("\n🔧 To import into Django:")
    print("   python manage.py loaddata caritas_minimal_fixtures.json")
    print("\n📍 Note: This creates sample data for testing")
    print("   Use the full caritas_processor.py for complete data")

if __name__ == "__main__":
    main()