from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.text import slugify
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from rest_framework import generics, viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Location, MapConfiguration
from .serializers import CategorySerializer, LocationSerializer, LocationMinimalSerializer, MapConfigurationSerializer
from .forms import GeoJSONUploadForm
import json
import os
import sys
import time
from decimal import Decimal
from io import StringIO

# Add path for data collectors
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    from data_collectors.data_manager import DataCollectionManager
except ImportError:
    DataCollectionManager = None

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for locations with filtering"""
    queryset = Location.objects.filter(is_active=True).select_related('category')
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'city', 'country', 'featured']
    search_fields = ['name', 'address', 'city', 'description']
    lookup_field = 'slug'

@api_view(['GET'])
def map_data(request):
    """
    API endpoint to get all map data for frontend
    Optimized for map display with minimal data
    """
    # Get query parameters
    category_ids = request.GET.getlist('category')
    featured_only = request.GET.get('featured', 'false').lower() == 'true'
    
    # Filter locations
    locations = Location.objects.filter(is_active=True).select_related('category')
    
    if category_ids:
        locations = locations.filter(category__id__in=category_ids)
    
    if featured_only:
        locations = locations.filter(featured=True)
    
    # Get categories
    categories = Category.objects.filter(is_active=True)
    if category_ids:
        categories = categories.filter(id__in=category_ids)
    
    # Serialize data
    locations_data = LocationMinimalSerializer(locations, many=True).data
    categories_data = CategorySerializer(categories, many=True).data
    
    # Group locations by category for frontend
    locations_by_category = {}
    for location in locations_data:
        category_id = location['category']
        if category_id not in locations_by_category:
            locations_by_category[category_id] = []
        locations_by_category[category_id].append(location)
    
    return Response({
        'locations': locations_data,
        'categories': categories_data,
        'locations_by_category': locations_by_category,
        'total_locations': len(locations_data)
    })

@api_view(['GET'])
def map_config(request, config_name=None):
    """Get map configuration"""
    if config_name:
        config = get_object_or_404(MapConfiguration, name=config_name)
    else:
        config = MapConfiguration.objects.filter(is_default=True).first()
        if not config:
            config = MapConfiguration.objects.first()
    
    if not config:
        # Return default configuration
        return Response({
            'center_latitude': 21.0285,
            'center_longitude': 105.8542,
            'zoom_level': 10,
            'tile_layer': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            'attribution': '© OpenStreetMap contributors'
        })
    
    return Response(MapConfigurationSerializer(config).data)

def map_view(request):
    """Main map view"""
    return render(request, 'maps/map.html')

def embed_map_view(request):
    """Embeddable map view for iframe with hierarchical controls"""
    # Import hierarchical models
    try:
        from .hierarchical_models import Domain, HierarchicalCategory
        
        # Get hierarchical data
        domains = Domain.objects.filter(is_active=True).annotate(
            category_count=Count('categories', filter=Q(categories__is_active=True)),
            location_count=Count('categories__locations', filter=Q(categories__is_active=True))
        ).order_by('name')
        
        # Get default domain (first one)
        domain = domains.first()
        
        # Get categories for default domain
        categories = []
        categories_json = "[]"
        
        if domain:
            categories = HierarchicalCategory.objects.filter(
                domain=domain, is_active=True
            ).annotate(
                location_count=Count('locations', filter=Q(locations__is_active=True))
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
            'is_embed': True,
            'timestamp': int(time.time()),  # Cache busting timestamp
        }
        
        return render(request, 'maps/embed.html', context)
    except ImportError:
        # Fallback to regular embed if hierarchical models not available
        return render(request, 'maps/embed.html', {
            'is_embed': True, 
            'timestamp': int(time.time())
        })

def admin_map_view(request):
    """Admin map view with management features"""
    return render(request, 'maps/admin_map.html')

def embed_debug_view(request):
    """Debug page for embedded map"""
    return render(request, 'maps/embed_debug.html', {
        'is_debug': True,
        'timestamp': int(time.time())
    })

def embed_test_view(request):
    """Test page for embedded map demo"""
    from django.http import HttpResponse
    
    # Read the test HTML file
    test_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'embed_test.html')
    try:
        with open(test_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse('<h1>Test file not found</h1><p>embed_test.html not available</p>')

def upload_geojson(request):
    """Upload and import GeoJSON file"""
    if request.method == 'POST':
        form = GeoJSONUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save uploaded file temporarily
                geojson_file = request.FILES['geojson_file']
                file_path = default_storage.save(f'temp/{geojson_file.name}', geojson_file)
                full_path = default_storage.path(file_path)
                
                # Process the file
                result = process_geojson_upload(
                    full_path,
                    form.cleaned_data['category_name'],
                    form.cleaned_data['category_color'],
                    form.cleaned_data['clear_existing']
                )
                
                # Clean up temp file
                default_storage.delete(file_path)
                
                if result['success']:
                    messages.success(request, f"Successfully imported {result['imported']} locations!")
                    if result['skipped'] > 0:
                        messages.warning(request, f"Skipped {result['skipped']} invalid features.")
                else:
                    messages.error(request, f"Import failed: {result['error']}")
                    
                return redirect('upload_geojson')
                
            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
    else:
        form = GeoJSONUploadForm()
    
    stats = {
        'categories': Category.objects.count(),
        'locations': Location.objects.count(),
        'featured': Location.objects.filter(featured=True).count()
    }
    
    return render(request, 'maps/upload_geojson.html', {
        'form': form,
        'stats': stats
    })

def process_geojson_upload(file_path, category_name, category_color, clear_existing):
    """Process uploaded GeoJSON file"""
    try:
        if clear_existing:
            Location.objects.all().delete()
            Category.objects.all().delete()
        
        # Create or get category
        category, created = Category.objects.get_or_create(
            slug=slugify(category_name),
            defaults={
                'name': category_name,
                'color': category_color,
                'icon': 'marker',
                'description': f'Imported from GeoJSON'
            }
        )
        
        # Load GeoJSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data.get('type') != 'FeatureCollection':
            return {'success': False, 'error': 'Invalid GeoJSON format'}
        
        features = data.get('features', [])
        imported_count = 0
        skipped_count = 0
        
        for i, feature in enumerate(features):
            try:
                # Extract geometry
                geometry = feature.get('geometry', {})
                if geometry.get('type') != 'Point':
                    skipped_count += 1
                    continue
                
                coordinates = geometry.get('coordinates', [])
                if len(coordinates) < 2:
                    skipped_count += 1
                    continue
                
                longitude, latitude = coordinates[0], coordinates[1]
                
                # Extract properties
                properties = feature.get('properties', {})
                name = properties.get('name') or properties.get('Name') or f'Location {i+1}'
                
                # Generate unique slug
                base_slug = slugify(name)
                slug = base_slug
                counter = 1
                while Location.objects.filter(slug=slug).exists():
                    slug = f'{base_slug}-{counter}'
                    counter += 1
                
                # Create location
                Location.objects.create(
                    name=name,
                    slug=slug,
                    category=category,
                    latitude=Decimal(str(latitude)),
                    longitude=Decimal(str(longitude)),
                    address=properties.get('address', '') or properties.get('Address', ''),
                    city=properties.get('city', '') or properties.get('City', ''),
                    state=properties.get('state', '') or properties.get('State', ''),
                    country=properties.get('country', 'Vietnam'),
                    postal_code=properties.get('postal_code', '') or properties.get('PostalCode', ''),
                    phone=properties.get('phone', '') or properties.get('Phone', ''),
                    email=properties.get('email', '') or properties.get('Email', ''),
                    website=properties.get('website', '') or properties.get('Website', ''),
                    description=properties.get('description', '') or properties.get('Description', ''),
                    opening_hours=properties.get('opening_hours', '') or properties.get('OpeningHours', ''),
                    image=properties.get('image', '') or properties.get('Image', ''),
                    featured=properties.get('featured', False) or properties.get('Featured', False),
                    is_active=True
                )
                
                imported_count += 1
                
            except Exception:
                skipped_count += 1
                continue
        
        return {
            'success': True,
            'imported': imported_count,
            'skipped': skipped_count
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


# Multi-Source Data Collection Views
def data_collection_interface(request):
    """Show data collection interface"""
    if not DataCollectionManager:
        messages.error(request, "Data collection system not available")
        return redirect('map')
    
    manager = DataCollectionManager()
    interface_data = manager.get_user_selection_interface()
    
    # Get current stats
    current_stats = {
        'total_locations': Location.objects.count(),
        'categories': Category.objects.count(),
        'sources': Location.objects.values('source').distinct().count(),
    }
    
    # Get recent collections (if any files exist)
    recent_files = []
    try:
        import glob
        pattern = "data_collectors/processed_data/*.json"
        files = glob.glob(pattern)
        files.sort(key=os.path.getmtime, reverse=True)
        recent_files = [os.path.basename(f) for f in files[:5]]
    except:
        pass
    
    context = {
        'interface_data': interface_data,
        'current_stats': current_stats,
        'recent_files': recent_files,
    }
    
    return render(request, 'maps/data_collection.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def collect_data_ajax(request):
    """AJAX endpoint to collect data from selected sources"""
    if not DataCollectionManager:
        return JsonResponse({
            'success': False,
            'error': 'Data collection system not available'
        })
    
    try:
        data = json.loads(request.body)
        source = data.get('source', 'all')
        max_pages = int(data.get('max_pages', 3))
        clear_existing = data.get('clear_existing', False)
        
        # Capture Django command output
        output = StringIO()
        
        # Build command arguments
        args = [
            '--source', source,
            '--max-pages', str(max_pages)
        ]
        
        if clear_existing:
            args.append('--clear-existing')
        
        # Run the collection command
        try:
            call_command('collect_multi_source_data', *args, stdout=output)
            
            # Get updated stats
            new_stats = {
                'total_locations': Location.objects.count(),
                'categories': Category.objects.count(),
                'sources': Location.objects.values('source').distinct().count(),
            }
            
            return JsonResponse({
                'success': True,
                'message': 'Data collection completed successfully',
                'output': output.getvalue(),
                'stats': new_stats
            })
            
        except Exception as cmd_error:
            return JsonResponse({
                'success': False,
                'error': f'Collection command failed: {str(cmd_error)}',
                'output': output.getvalue()
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@api_view(['GET'])
def get_collection_sources(request):
    """API endpoint to get available data collection sources"""
    if not DataCollectionManager:
        return Response({
            'success': False,
            'error': 'Data collection system not available'
        })
    
    try:
        manager = DataCollectionManager()
        sources = manager.list_available_collectors()
        
        return Response({
            'success': True,
            'sources': sources
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        })


@api_view(['GET'])
def get_collection_stats(request):
    """API endpoint to get current database stats"""
    try:
        stats = {
            'total_locations': Location.objects.count(),
            'categories': Category.objects.count(),
            'sources': list(Location.objects.values_list('source', flat=True).distinct()),
            'categories_breakdown': {},
            'sources_breakdown': {}
        }
        
        # Category breakdown
        for category in Category.objects.all():
            count = Location.objects.filter(category=category).count()
            stats['categories_breakdown'][category.name] = count
        
        # Sources breakdown  
        for source in stats['sources']:
            if source:
                count = Location.objects.filter(source=source).count()
                stats['sources_breakdown'][source] = count
        
        return Response({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        })
