"""
Test Django Import for 3-Tier Hierarchical Data
Test script để import dữ liệu Handwerkskammern vào Django
"""

import os
import sys
import json
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapproject.settings')
    
    # Add project root to path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    import django
    django.setup()

def test_import_handwerkskammern():
    """Test import của dữ liệu Handwerkskammern"""
    
    print("🚀 TESTING DJANGO 3-TIER DATA IMPORT")
    print("=" * 60)
    
    # Setup Django
    setup_django()
    
    # Import Django models
    from maps.hierarchical_models import Domain, HierarchicalCategory, HierarchicalLocation
    from django.db import models
    
    print(f"📊 Current Database State:")
    print(f"   Domains: {Domain.objects.count()}")
    print(f"   Categories: {HierarchicalCategory.objects.count()}")
    print(f"   Locations: {HierarchicalLocation.objects.count()}")
    
    # Check if hierarchical data exists
    hierarchical_file = "data_sources/hierarchical/handwerkskammern_deutschland_hierarchical.json"
    
    if not os.path.exists(hierarchical_file):
        print(f"❌ Hierarchical data file not found: {hierarchical_file}")
        print("Please run: python hierarchical_manager.py first")
        return False
    
    print(f"\n📁 Found hierarchical data file: {hierarchical_file}")
    
    # Test dry run first
    print(f"\n🔍 Running DRY RUN to test import...")
    
    try:
        execute_from_command_line([
            'manage.py', 
            'import_hierarchical_data', 
            'handwerkskammern_deutschland',
            '--dry-run',
            '--mode=create'
        ])
        
        print(f"\n✅ Dry run completed successfully!")
        
        # Ask for confirmation for real import
        confirm = input(f"\n❓ Proceed with actual import? (y/n): ").lower()
        
        if confirm == 'y':
            print(f"\n💾 Running ACTUAL IMPORT...")
            
            execute_from_command_line([
                'manage.py',
                'import_hierarchical_data', 
                'handwerkskammern_deutschland',
                '--mode=create'
            ])
            
            # Show final statistics
            print(f"\n📊 Final Database State:")
            print(f"   Domains: {Domain.objects.count()}")
            print(f"   Categories: {HierarchicalCategory.objects.count()}")
            print(f"   Locations: {HierarchicalLocation.objects.count()}")
            
            # Show sample data
            handwerk_domain = Domain.objects.filter(domain_id='handwerkskammern_deutschland').first()
            if handwerk_domain:
                print(f"\n📂 Domain: {handwerk_domain.name}")
                print(f"   Total Categories: {handwerk_domain.total_categories}")
                print(f"   Total Locations: {handwerk_domain.total_locations}")
                
                # Show top categories
                top_categories = handwerk_domain.categories.annotate(
                    location_count=models.Count('locations', filter=models.Q(locations__is_active=True))
                ).filter(is_active=True).order_by('-location_count')[:5]
                
                print(f"\n🔝 Top 5 Categories:")
                for i, cat in enumerate(top_categories, 1):
                    print(f"   {i}. {cat.name}: {cat.location_count} locations")
                
                # Show sample locations
                sample_locations = HierarchicalLocation.objects.filter(
                    categories__domain=handwerk_domain,
                    is_active=True
                ).distinct()[:3]
                
                print(f"\n📍 Sample Locations:")
                for i, loc in enumerate(sample_locations, 1):
                    categories = ", ".join([cat.name for cat in loc.categories.all()[:2]])
                    print(f"   {i}. {loc.name} ({loc.city})")
                    print(f"      Categories: {categories}")
                    print(f"      Coordinates: ({loc.latitude}, {loc.longitude})")
            
            print(f"\n🎉 IMPORT COMPLETED SUCCESSFULLY!")
            print(f"🌐 Data is now ready for web interface!")
            print(f"🔧 Access Django Admin to manage the data")
            
            return True
        else:
            print(f"❌ Import cancelled by user")
            return False
            
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def show_admin_urls():
    """Show admin URLs for managing imported data"""
    print(f"\n🔧 DJANGO ADMIN URLS:")
    print(f"   📁 Domains: /admin/maps/domain/")
    print(f"   📂 Categories: /admin/maps/hierarchicalcategory/")
    print(f"   📍 Locations: /admin/maps/hierarchicallocation/")
    print(f"   📊 Import Logs: /admin/maps/dataimportlog/")
    print(f"\n💡 Start Django server: python manage.py runserver")

def main():
    """Main test function"""
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    try:
        success = test_import_handwerkskammern()
        
        if success:
            show_admin_urls()
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()