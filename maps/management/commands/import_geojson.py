from django.core.management.base import BaseCommand
from django.utils.text import slugify
from maps.models import Category, Location
from decimal import Decimal
import json
import os

class Command(BaseCommand):
    help = 'Import locations from GeoJSON file'

    def add_arguments(self, parser):
        parser.add_argument('geojson_file', type=str, help='Path to GeoJSON file')
        parser.add_argument('--category', type=str, help='Category name for all locations')
        parser.add_argument('--clear', action='store_true', help='Clear existing data before import')

    def handle(self, *args, **options):
        geojson_file = options['geojson_file']
        category_name = options.get('category', 'Imported Locations')
        
        if not os.path.exists(geojson_file):
            self.stdout.write(self.style.ERROR(f'File not found: {geojson_file}'))
            return
        
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Location.objects.all().delete()
            Category.objects.all().delete()
        
        # Create or get category
        category, created = Category.objects.get_or_create(
            slug=slugify(category_name),
            defaults={
                'name': category_name,
                'color': '#3498db',
                'icon': 'marker',
                'description': f'Imported from {os.path.basename(geojson_file)}'
            }
        )
        
        if created:
            self.stdout.write(f'✓ Created category: {category.name}')
        else:
            self.stdout.write(f'✓ Using existing category: {category.name}')
        
        # Load and parse GeoJSON
        try:
            with open(geojson_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading file: {e}'))
            return
        
        if data.get('type') != 'FeatureCollection':
            self.stdout.write(self.style.ERROR('Invalid GeoJSON: Expected FeatureCollection'))
            return
        
        features = data.get('features', [])
        imported_count = 0
        skipped_count = 0
        
        self.stdout.write(f'Processing {len(features)} features...')
        
        for i, feature in enumerate(features):
            try:
                # Extract geometry
                geometry = feature.get('geometry', {})
                if geometry.get('type') != 'Point':
                    self.stdout.write(f'⚠ Skipping feature {i+1}: Only Point geometry supported')
                    skipped_count += 1
                    continue
                
                coordinates = geometry.get('coordinates', [])
                if len(coordinates) < 2:
                    self.stdout.write(f'⚠ Skipping feature {i+1}: Invalid coordinates')
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
                location_data = {
                    'name': name,
                    'slug': slug,
                    'category': category,
                    'latitude': Decimal(str(latitude)),
                    'longitude': Decimal(str(longitude)),
                    'address': properties.get('address', '') or properties.get('Address', ''),
                    'city': properties.get('city', '') or properties.get('City', ''),
                    'state': properties.get('state', '') or properties.get('State', ''),
                    'country': properties.get('country', 'Vietnam'),
                    'postal_code': properties.get('postal_code', '') or properties.get('PostalCode', ''),
                    'phone': properties.get('phone', '') or properties.get('Phone', ''),
                    'email': properties.get('email', '') or properties.get('Email', ''),
                    'website': properties.get('website', '') or properties.get('Website', ''),
                    'description': properties.get('description', '') or properties.get('Description', ''),
                    'opening_hours': properties.get('opening_hours', '') or properties.get('OpeningHours', ''),
                    'image': properties.get('image', '') or properties.get('Image', ''),
                    'featured': properties.get('featured', False) or properties.get('Featured', False),
                    'is_active': True
                }
                
                location = Location.objects.create(**location_data)
                imported_count += 1
                
                if imported_count % 10 == 0:
                    self.stdout.write(f'  Processed {imported_count} locations...')
                
            except Exception as e:
                self.stdout.write(f'⚠ Error processing feature {i+1}: {e}')
                skipped_count += 1
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 GeoJSON import completed!\n'
                f'✅ Imported: {imported_count} locations\n'
                f'⚠️ Skipped: {skipped_count} features\n'
                f'📁 Category: {category.name}\n'
                f'📍 Total locations in DB: {Location.objects.count()}\n'
            )
        )

    def create_sample_geojson(self):
        """Helper method to show GeoJSON format example"""
        sample = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [105.8542, 21.0285]
                    },
                    "properties": {
                        "name": "Cửa hàng Hoàn Kiếm",
                        "address": "123 Phố Hàng Bạc, Hoàn Kiếm",
                        "city": "Hà Nội",
                        "country": "Vietnam",
                        "phone": "+84 24 3826 1234",
                        "email": "hoankiem@company.com",
                        "description": "Cửa hàng flagship tại trung tâm Hà Nội",
                        "featured": True
                    }
                }
            ]
        }
        return json.dumps(sample, indent=2, ensure_ascii=False)