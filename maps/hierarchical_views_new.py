"""
Django Views for 3-Tier Hierarchical Map Interface
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Q
from django.views.decorators.http import require_http_methods
from django.views import View
import json
import logging

try:
    from .hierarchical_models import Domain, HierarchicalCategory, HierarchicalLocation
except ImportError:
    Domain = HierarchicalCategory = HierarchicalLocation = None

logger = logging.getLogger(__name__)

class HierarchicalMapView(View):
    """Main view for 3-tier hierarchical map interface"""
    
    def get(self, request):
        """Render the hierarchical map with domain selection"""
        
        if not all([Domain, HierarchicalCategory, HierarchicalLocation]):
            return JsonResponse({'error': 'Hierarchical models not available'}, status=500)
        
        # Get all available domains
        domains = Domain.objects.annotate(
            location_count=Count('categories__locations')
        ).order_by('name')
        
        # Get selected domain (default to first)
        domain_id = request.GET.get('domain')
        if domain_id:
            domain = get_object_or_404(Domain, domain_id=domain_id)
        else:
            domain = domains.first()
        
        # Get categories for selected domain
        categories = []
        categories_json = "[]"
        
        if domain:
            categories = HierarchicalCategory.objects.filter(
                domain=domain
            ).annotate(
                location_count=Count('locations')
            ).order_by('name')
            
            # Prepare categories data for JavaScript
            categories_data = []
            for cat in categories:
                categories_data.append({
                    'category_id': cat.category_id,
                    'name': cat.name,
                    'icon': cat.icon or 'Category',
                    'color': cat.color or '#3388ff',
                    'location_count': cat.location_count,
                })
            categories_json = json.dumps(categories_data)
        
        context = {
            'domains': domains,
            'domain': domain,
            'categories': categories,
            'categories_json': categories_json,
        }
        
        return render(request, 'maps/hierarchical_map.html', context)

class HierarchicalLocationsAPI(View):
    """API endpoint to provide locations data for map"""
    
    def get(self, request):
        """Return GeoJSON format locations for selected domain/categories"""
        
        if not all([Domain, HierarchicalCategory, HierarchicalLocation]):
            return JsonResponse({'error': 'Hierarchical models not available'}, status=500)
        
        try:
            domain_id = request.GET.get('domain')
            category_ids = request.GET.getlist('categories[]')
            
            print(f"DEBUG: domain_id={domain_id}, category_ids={category_ids}")
            
            # Build query
            query = Q()
            
            if domain_id:
                query &= Q(categories__domain__domain_id=domain_id)
            
            if category_ids:
                query &= Q(categories__category_id__in=category_ids)
            
            print(f"DEBUG: Query built: {query}")
            
            # Get locations
            locations = HierarchicalLocation.objects.filter(query).distinct().prefetch_related(
                'categories__domain'
            )
            print(f"DEBUG: Query successful, found {locations.count()} locations")
        except Exception as e:
            print(f"DEBUG: Error in API: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
        
        # Build GeoJSON features
        features = []
        for location in locations:
            # Get location categories
            location_categories = []
            for category in location.categories.all():
                location_categories.append({
                    'id': category.category_id,
                    'name': category.name,
                    'color': category.color or '#3388ff',
                    'icon': category.icon or 'Category'
                })
            
            # Create feature
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [float(location.longitude), float(location.latitude)]
                },
                'properties': {
                    'id': location.location_id,
                    'name': location.name,
                    'address': location.full_address,  # Use the full_address property
                    'street': location.street,
                    'city': location.city,
                    'postal_code': location.postal_code,
                    'country': location.country,
                    'phone': location.phone,
                    'email': location.email,
                    'website': location.website,
                    'categories': location_categories,
                    'category': location_categories[0] if location_categories else None,
                    'raw_data': location.raw_data
                }
            }
            features.append(feature)
        
        # Return GeoJSON
        geojson = {
            'type': 'FeatureCollection',
            'features': features,
            'meta': {
                'total_locations': len(features),
                'domain_id': domain_id,
                'categories_requested': category_ids
            }
        }
        
        return JsonResponse(geojson)

@require_http_methods(["GET"])
def search_locations_api(request):
    """Search locations by name or address"""
    
    if not HierarchicalLocation:
        return JsonResponse({'error': 'Location model not available'}, status=500)
    
    query = request.GET.get('q', '').strip()
    domain_id = request.GET.get('domain')
    limit = int(request.GET.get('limit', 20))
    
    if not query:
        return JsonResponse({'locations': []})
    
    # Build search query
    search_query = Q(name__icontains=query) | Q(address__icontains=query)
    
    if domain_id:
        search_query &= Q(categories__domain_id=domain_id)
    
    locations = HierarchicalLocation.objects.filter(
        search_query
    ).distinct().prefetch_related('categories')[:limit]
    
    location_list = []
    for location in locations:
        categories = list(location.categories.values('category_id', 'name', 'color', 'icon'))
        
        location_list.append({
            'location_id': location.location_id,
            'name': location.name,
            'address': location.address,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'phone': location.phone,
            'email': location.email,
            'website': location.website,
            'categories': categories
        })
    
    return JsonResponse({
        'locations': location_list,
        'query': query,
        'total_found': len(location_list)
    })

@require_http_methods(["GET"])
def domain_list_api(request):
    """Simple API to list all domains"""
    
    if not Domain:
        return JsonResponse({'error': 'Domain model not available'}, status=500)
    
    domains = Domain.objects.annotate(
        category_count=Count('categories'),
        location_count=Count('categories__locations')
    ).order_by('name')
    
    domain_list = []
    for domain in domains:
        domain_list.append({
            'domain_id': domain.domain_id,
            'name': domain.name,
            'country': domain.country,
            'language': domain.language,
            'icon': domain.icon or 'Domain',
            'category_count': domain.category_count,
            'location_count': domain.location_count
        })
    
    return JsonResponse({'domains': domain_list})

@require_http_methods(["GET"])
def category_list_api(request):
    """API to list categories for a domain"""
    
    if not HierarchicalCategory:
        return JsonResponse({'error': 'Category model not available'}, status=500)
    
    domain_id = request.GET.get('domain')
    
    categories = HierarchicalCategory.objects.annotate(
        location_count=Count('locations')
    )
    
    if domain_id:
        categories = categories.filter(domain__domain_id=domain_id)
    
    categories = categories.order_by('name')
    
    category_list = []
    for category in categories:
        category_list.append({
            'category_id': category.category_id,
            'name': category.name,
            'color': category.color or '#3388ff',
            'icon': category.icon or 'Category',
            'location_count': category.location_count,
            'domain_id': category.domain_id
        })
    
    return JsonResponse({'categories': category_list})

# Legacy compatibility functions
def hierarchical_map(request):
    """Function-based view wrapper for compatibility"""
    return HierarchicalMapView.as_view()(request)

def api_locations(request):
    """Legacy function-based API endpoint - redirects to new class-based view"""
    return HierarchicalLocationsAPI.as_view()(request)