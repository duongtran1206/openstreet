"""
🎉 DJANGO 3-TIER INTEGRATION COMPLETE! 🎉

Demo script để show kết quả Django integration
"""

import os
import sys
import json

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapproject.settings')
    
    # Add project root to path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    import django
    django.setup()

def show_import_results():
    """Hiển thị kết quả import vào Django"""
    
    setup_django()
    
    from maps.hierarchical_models import Domain, HierarchicalCategory, HierarchicalLocation, DataImportLog
    from django.db.models import Count, Q
    
    print("🎉 DJANGO 3-TIER INTEGRATION SUCCESS!")
    print("=" * 70)
    
    # Database statistics
    total_domains = Domain.objects.count()
    total_categories = HierarchicalCategory.objects.count()
    total_locations = HierarchicalLocation.objects.count()
    total_import_logs = DataImportLog.objects.count()
    
    print(f"📊 DATABASE STATISTICS:")
    print(f"   🏢 Domains: {total_domains}")
    print(f"   📂 Categories: {total_categories}")
    print(f"   📍 Locations: {total_locations}")
    print(f"   📋 Import Logs: {total_import_logs}")
    
    # Domain details
    handwerk_domain = Domain.objects.filter(domain_id='handwerkskammern_deutschland').first()
    
    if handwerk_domain:
        print(f"\n🏢 DOMAIN: {handwerk_domain.name}")
        print(f"   🆔 ID: {handwerk_domain.domain_id}")
        print(f"   🌍 Country: {handwerk_domain.country}")
        print(f"   🗣️ Language: {handwerk_domain.language}")
        print(f"   📈 Status: {'✅ Active' if handwerk_domain.is_active else '❌ Inactive'}")
        print(f"   ⭐ Featured: {'✅ Yes' if handwerk_domain.featured else '❌ No'}")
        print(f"   📅 Created: {handwerk_domain.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📅 Updated: {handwerk_domain.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Categories statistics
        categories = handwerk_domain.categories.annotate(
            location_count=Count('locations', filter=Q(locations__is_active=True))
        ).filter(is_active=True).order_by('-location_count')
        
        print(f"\n📂 CATEGORIES ({categories.count()} total):")
        print(f"   🔝 Top 10 by Location Count:")
        
        for i, cat in enumerate(categories[:10], 1):
            print(f"      {i:2d}. {cat.name:<35} ({cat.location_count:2d} locations)")
        
        # Location statistics by city
        locations_by_city = HierarchicalLocation.objects.filter(
            categories__domain=handwerk_domain,
            is_active=True
        ).values('city').annotate(
            location_count=Count('id')
        ).order_by('-location_count')
        
        print(f"\n📍 LOCATIONS BY CITY:")
        for i, city_stat in enumerate(locations_by_city[:10], 1):
            print(f"      {i:2d}. {city_stat['city']:<25} ({city_stat['location_count']:2d} locations)")
        
        # Sample locations
        sample_locations = HierarchicalLocation.objects.filter(
            categories__domain=handwerk_domain,
            is_active=True
        ).distinct()[:5]
        
        print(f"\n📍 SAMPLE LOCATIONS:")
        for i, loc in enumerate(sample_locations, 1):
            categories_list = [cat.name for cat in loc.categories.all()[:2]]
            categories_str = ", ".join(categories_list)
            if loc.categories.count() > 2:
                categories_str += f" (+{loc.categories.count() - 2} more)"
            
            print(f"   {i}. {loc.name}")
            print(f"      🏠 {loc.full_address}")
            print(f"      📞 {loc.phone or 'N/A'}")
            print(f"      🌐 {loc.website or 'N/A'}")
            print(f"      📍 ({loc.latitude}, {loc.longitude})")
            print(f"      📂 Categories: {categories_str}")
            print()
    
    # Import logs
    latest_log = DataImportLog.objects.order_by('-started_at').first()
    
    if latest_log:
        print(f"📋 LATEST IMPORT LOG:")
        print(f"   🏢 Domain: {latest_log.domain.name}")
        print(f"   📁 Type: {latest_log.import_type.title()}")
        print(f"   📊 Status: {latest_log.status.title()}")
        print(f"   📂 Categories: {latest_log.categories_created} created, {latest_log.categories_updated} updated")
        print(f"   📍 Locations: {latest_log.locations_created} created, {latest_log.locations_updated} updated")
        print(f"   ⏱️ Started: {latest_log.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if latest_log.completed_at:
            print(f"   ✅ Completed: {latest_log.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   ⏳ Duration: {latest_log.duration}")
    
    print(f"\n🌐 WEB INTERFACE ACCESS:")
    print(f"   🔧 Django Admin: http://127.0.0.1:8000/admin/")
    print(f"   📁 Domains: http://127.0.0.1:8000/admin/maps/domain/")
    print(f"   📂 Categories: http://127.0.0.1:8000/admin/maps/hierarchicalcategory/")
    print(f"   📍 Locations: http://127.0.0.1:8000/admin/maps/hierarchicallocation/")
    print(f"   📋 Import Logs: http://127.0.0.1:8000/admin/maps/dataimportlog/")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. 🌐 Create map views to display hierarchical data")
    print(f"   2. 🔍 Add search and filtering by categories")
    print(f"   3. 📱 Create REST API endpoints")
    print(f"   4. 🎨 Design category-based map styling")
    print(f"   5. 📊 Build analytics dashboard")
    
    return True

def create_sample_views():
    """Tạo sample Django views cho hierarchical data"""
    
    view_content = '''"""
Sample Django Views for 3-Tier Hierarchical Data
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Q
from .hierarchical_models import Domain, HierarchicalCategory, HierarchicalLocation

def hierarchical_map(request):
    """Main map view with hierarchical data"""
    
    # Get all active domains
    domains = Domain.objects.filter(is_active=True)
    
    # Get domain from URL parameter or use first domain
    domain_id = request.GET.get('domain', domains.first().domain_id if domains else None)
    
    if not domain_id:
        return render(request, 'maps/no_data.html')
    
    domain = get_object_or_404(Domain, domain_id=domain_id, is_active=True)
    
    # Get categories for this domain
    categories = domain.categories.filter(is_active=True).annotate(
        location_count=Count('locations', filter=Q(locations__is_active=True))
    ).order_by('-location_count')
    
    context = {
        'domain': domain,
        'domains': domains,
        'categories': categories,
        'total_locations': domain.total_locations
    }
    
    return render(request, 'maps/hierarchical_map.html', context)

def api_locations(request):
    """API endpoint for location data"""
    
    domain_id = request.GET.get('domain')
    category_ids = request.GET.getlist('categories')
    
    if not domain_id:
        return JsonResponse({'error': 'domain parameter required'}, status=400)
    
    # Base query
    locations = HierarchicalLocation.objects.filter(
        categories__domain__domain_id=domain_id,
        is_active=True
    ).distinct()
    
    # Filter by categories if specified
    if category_ids:
        locations = locations.filter(categories__category_id__in=category_ids)
    
    # Prepare GeoJSON response
    features = []
    
    for location in locations:
        # Get primary category (first one)
        primary_category = location.categories.first()
        
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [float(location.longitude), float(location.latitude)]
            },
            'properties': {
                'id': location.id,
                'name': location.name,
                'address': location.full_address,
                'phone': location.phone,
                'email': location.email,
                'website': location.website,
                'category': {
                    'id': primary_category.category_id if primary_category else None,
                    'name': primary_category.name if primary_category else None,
                    'color': primary_category.color if primary_category else '#95A5A6'
                },
                'categories': [
                    {
                        'id': cat.category_id,
                        'name': cat.name,
                        'color': cat.color
                    }
                    for cat in location.categories.all()
                ]
            }
        }
        
        features.append(feature)
    
    geojson = {
        'type': 'FeatureCollection',
        'features': features,
        'count': len(features)
    }
    
    return JsonResponse(geojson)

def api_categories(request):
    """API endpoint for category data"""
    
    domain_id = request.GET.get('domain')
    
    if not domain_id:
        return JsonResponse({'error': 'domain parameter required'}, status=400)
    
    domain = get_object_or_404(Domain, domain_id=domain_id, is_active=True)
    
    categories = domain.categories.filter(is_active=True).annotate(
        location_count=Count('locations', filter=Q(locations__is_active=True))
    ).order_by('-location_count')
    
    category_data = [
        {
            'id': cat.category_id,
            'name': cat.name,
            'color': cat.color,
            'icon': cat.icon,
            'location_count': cat.location_count,
            'external_id': cat.external_id
        }
        for cat in categories
    ]
    
    return JsonResponse({
        'domain': {
            'id': domain.domain_id,
            'name': domain.name
        },
        'categories': category_data,
        'count': len(category_data)
    })
'''
    
    # Save view file
    view_file = os.path.join(os.path.dirname(__file__), '..', 'maps', 'hierarchical_views.py')
    
    with open(view_file, 'w', encoding='utf-8') as f:
        f.write(view_content)
    
    print(f"📁 Created sample views: {view_file}")
    
    # Create URL patterns
    url_content = '''"""
URL patterns for hierarchical views
Add these to your main urls.py
"""

from django.urls import path
from maps import hierarchical_views

hierarchical_patterns = [
    path('map/hierarchical/', hierarchical_views.hierarchical_map, name='hierarchical_map'),
    path('api/locations/', hierarchical_views.api_locations, name='api_locations'),
    path('api/categories/', hierarchical_views.api_categories, name='api_categories'),
]
'''
    
    url_file = os.path.join(os.path.dirname(__file__), 'hierarchical_urls.py')
    
    with open(url_file, 'w', encoding='utf-8') as f:
        f.write(url_content)
    
    print(f"🔗 Created sample URLs: {url_file}")

def main():
    """Main demo function"""
    
    print("🚀 DJANGO 3-TIER HIERARCHICAL SYSTEM DEMO")
    print("=" * 70)
    
    try:
        show_import_results()
        
        print(f"\n📁 CREATING SAMPLE FILES...")
        create_sample_views()
        
        print(f"\n🎉 DJANGO INTEGRATION DEMO COMPLETE!")
        print(f"💡 The 3-tier hierarchical data system is now fully integrated with Django!")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()