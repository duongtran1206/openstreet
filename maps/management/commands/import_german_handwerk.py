import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from maps.models import Category, Location, MapConfiguration

class Command(BaseCommand):
    help = 'Import German Handwerkskammern data - clear existing data and import new'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing database before import',
        )
        parser.add_argument(
            '--file',
            type=str,
            default='test/handwerkskammern_data.json',
            help='Path to JSON data file',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🇩🇪 German Handwerkskammern Data Importer')
        )
        self.stdout.write('=' * 50)

        # Clear database if requested
        if options['clear']:
            self.clear_database()

        # Import data
        json_file = Path(options['file'])
        if not json_file.exists():
            # Try relative to project root
            json_file = Path(__file__).parent.parent.parent.parent / options['file']
        
        if not json_file.exists():
            self.stdout.write(
                self.style.ERROR(f'ERROR: File not found: {options["file"]}')
            )
            return

        self.import_data(json_file)

        # Summary
        self.show_summary()

    def clear_database(self):
        self.stdout.write('Clearing existing database...')
        
        deleted_locations = Location.objects.all().delete()
        self.stdout.write(f'   Deleted {deleted_locations[0]} locations')
        
        deleted_categories = Category.objects.all().delete()
        self.stdout.write(f'   Deleted {deleted_categories[0]} categories')
        
        deleted_configs = MapConfiguration.objects.all().delete()
        self.stdout.write(f'   Deleted {deleted_configs[0]} map configurations')
        
        self.stdout.write(self.style.SUCCESS('Database cleared!'))

    def import_data(self, json_file):
        self.stdout.write(f'\n📥 Loading data from: {json_file}')
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Create handwerk categories mapping
        handwerk_categories = {}
        if 'lists' in data and 'locations' in data['lists'] and 'filter' in data['lists']['locations']:
            filter_data = data['lists']['locations']['filter']
            if 'handwerkid' in filter_data and 'values' in filter_data['handwerkid']:
                for item in filter_data['handwerkid']['values']:
                    if item.get('$value'):
                        handwerk_categories[item['$value']] = item['title']

        self.stdout.write(f'   Found {len(handwerk_categories)} handwerk categories')

        # Create categories
        self.create_categories(handwerk_categories)

        # Import locations
        locations_data = []
        if 'lists' in data and 'locations' in data['lists'] and '$items' in data['lists']['locations']:
            locations_data = data['lists']['locations']['$items']

        self.import_locations(locations_data, handwerk_categories)

        # Create map configuration
        self.create_map_config()

    def create_categories(self, handwerk_categories):
        self.stdout.write('\nCreating categories...')
        
        # Main category
        main_category, created = Category.objects.get_or_create(
            name="Handwerkskammer",
            defaults={
                'slug': "handwerkskammer",
                'color': '#e74c3c',
                'icon': 'industry',
                'description': 'German Chambers of Craft - Phòng Thương mại Thủ công Đức',
                'is_active': True
            }
        )
        self.stdout.write(f'   Main category: {main_category.name}')
        
        # Popular handwerk subcategories
        popular_handwerk = {
            'Bäcker': '#f39c12',
            'Friseure': '#9b59b6',
            'Elektrotechniker': '#3498db',
            'Dachdecker': '#34495e',
            'Glaser': '#1abc9c',
            'Augenoptiker': '#e67e22',
            'Fleischer': '#c0392b',
            'Installateur und Heizungsbauer': '#27ae60'
        }
        
        for handwerk_name, color in popular_handwerk.items():
            if handwerk_name in handwerk_categories.values():
                category, created = Category.objects.get_or_create(
                    name=handwerk_name,
                    defaults={
                        'slug': slugify(handwerk_name),
                        'color': color,
                        'icon': 'tools',
                        'description': f'Handwerk: {handwerk_name}',
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(f'   Created: {handwerk_name}')

    def import_locations(self, locations_data, handwerk_categories):
        self.stdout.write(f'\nImporting {len(locations_data)} locations...')
        
        created_count = 0
        
        # Get categories for assignment
        main_category = Category.objects.get(name="Handwerkskammer")
        subcategories = {cat.name: cat for cat in Category.objects.exclude(name="Handwerkskammer")}
        
        for item in locations_data:
            try:
                title = item.get('title', 'Unknown')
                sort_title = item.get('sortTitle', title)
                latitude = float(item.get('latitude', 0))
                longitude = float(item.get('longitude', 0))
                
                # Address info
                address_info = item.get('adresse', {})
                address = address_info.get('address', '')
                city = address_info.get('city', sort_title)
                zip_code = address_info.get('zip', '')
                phone = address_info.get('phone', '')
                website = address_info.get('www', '')
                
                # Full address
                full_address = f"{address}"
                if zip_code:
                    full_address += f", {zip_code}"
                if city:
                    full_address += f" {city}"
                
                # Assign category
                handwerk_ids = item.get('handwerkid', [])
                selected_category = main_category
                
                # Try to find matching subcategory
                for hid in handwerk_ids:
                    handwerk_name = handwerk_categories.get(hid)
                    if handwerk_name and handwerk_name in subcategories:
                        selected_category = subcategories[handwerk_name]
                        break
                
                # Create description
                handwerk_names = []
                for hid in handwerk_ids[:5]:
                    name = handwerk_categories.get(hid)
                    if name:
                        handwerk_names.append(name)
                
                description = f"Handwerkskammer quản lý: {', '.join(handwerk_names)}"
                if len(handwerk_ids) > 5:
                    description += f" và {len(handwerk_ids) - 5} nghề khác"
                
                # Create location
                location = Location.objects.create(
                    name=title,
                    slug=slugify(f"{title}-{sort_title}"),
                    category=selected_category,
                    latitude=latitude,
                    longitude=longitude,
                    address=full_address,
                    city=city,
                    state="",
                    country="Germany",
                    postal_code=zip_code,
                    phone=phone,
                    website=website,
                    description=description,
                    is_active=True,
                    featured=len(handwerk_ids) > 25
                )
                
                created_count += 1
                if created_count <= 10 or created_count % 10 == 0:
                    self.stdout.write(f'   {created_count:2d}. {title}')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ERROR creating {title}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} locations!')
        )

    def create_map_config(self):
        self.stdout.write('\nCreating map configuration...')
        
        config, created = MapConfiguration.objects.get_or_create(
            name="Germany Handwerkskammern",
            defaults={
                'center_latitude': 51.1657,
                'center_longitude': 10.4515,
                'zoom_level': 6,
                'max_zoom': 18,
                'min_zoom': 5,
                'tile_layer': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                'attribution': '© OpenStreetMap contributors',
                'show_scale': True,
                'show_zoom_control': True,
                'show_layer_control': True,
                'is_default': True
            }
        )
        
        config.categories.set(Category.objects.all())
        
        action = "Created" if created else "Updated"
        self.stdout.write(f'   {action}: {config.name}')

    def show_summary(self):
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('🎉 IMPORT COMPLETED!'))
        self.stdout.write('=' * 50)
        
        total_categories = Category.objects.count()
        total_locations = Location.objects.count()
        total_configs = MapConfiguration.objects.count()
        
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'   Categories: {total_categories}')
        self.stdout.write(f'   Locations: {total_locations}') 
        self.stdout.write(f'   Map Configurations: {total_configs}')
        
        self.stdout.write(f'\n🌐 Access your map at: http://127.0.0.1:8000/')
        self.stdout.write(f'👨‍💼 Admin panel: http://127.0.0.1:8000/admin/')