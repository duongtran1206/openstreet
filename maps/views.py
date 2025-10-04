from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.text import slugify
from django.core.files.storage import default_storage
from rest_framework import generics, viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Location, MapConfiguration
from .serializers import CategorySerializer, LocationSerializer, LocationMinimalSerializer, MapConfigurationSerializer
from .forms import GeoJSONUploadForm
import json
import os
from decimal import Decimal

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
    """Embeddable map view for iframe"""
    return render(request, 'maps/embed.html')

def admin_map_view(request):
    """Admin map view with management features"""
    return render(request, 'maps/admin_map.html')

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
