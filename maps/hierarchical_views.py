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
            total_locations=Count('hierarchicalcategory__hierarchicallocation')
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
                location_count=Count('hierarchicallocation')
            ).order_by('name')
            
            # Prepare categories data for JavaScript
            categories_data = []
            for cat in categories:
                categories_data.append({
                    'category_id': cat.category_id,
                    'name': cat.name,
                    'icon': cat.icon or '📂',
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

def hierarchical_map(request):
    """Function-based view wrapper for compatibility"""
    return HierarchicalMapView.as_view()(request)

class HierarchicalLocationsAPI(View):
    """API endpoint to provide locations data for map"""
    
    def get(self, request):
        """Return GeoJSON format locations for selected domain/categories"""
        
        if not all([Domain, HierarchicalCategory, HierarchicalLocation]):
            return JsonResponse({'error': 'Hierarchical models not available'}, status=500)
        
        domain_id = request.GET.get('domain')
        category_ids = request.GET.getlist('categories[]')
        
        # Build query
        query = Q()
        
        if domain_id:
            query &= Q(categories__domain_id=domain_id)
        
        if category_ids:
            query &= Q(categories__category_id__in=category_ids)
        
        # Get locations
        locations = HierarchicalLocation.objects.filter(query).distinct().prefetch_related(
            'categories__domain'
        )
        
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
                    'icon': category.icon or '📂'
                })
            
            # Create feature
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [location.longitude, location.latitude]
                },
                'properties': {
                    'id': location.location_id,
                    'name': location.name,
                    'address': location.address,
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

def api_locations(request):
    """Legacy function-based API endpoint - redirects to new class-based view"""
    return HierarchicalLocationsAPI.as_view()(request)
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
