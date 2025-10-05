"""
Django management command to collect data from multiple sources
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from data_collectors.data_manager import DataCollectionManager
from maps.models import Category, Location
import json

class Command(BaseCommand):
    help = 'Collect data from multiple sources and import to database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            help='Specific source to collect from (handwerkskammern, caritas, all)',
            default='all'
        )
        parser.add_argument(
            '--max-pages',
            type=int,
            help='Maximum pages to collect (for paginated sources)',
            default=5
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing data before importing',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing',
        )
        
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== Multi-Source Data Collection ===')
        )
        
        # Initialize data manager
        manager = DataCollectionManager()
        
        # Show available sources
        self.show_available_sources(manager)
        
        # Collect data based on source option
        source = options['source']
        max_pages = options['max_pages']
        
        if source == 'all':
            self.stdout.write('\n[INFO] Collecting from all sources...')
            collected_data = manager.collect_from_all_sources(max_pages=max_pages)
        else:
            self.stdout.write(f'\n[INFO] Collecting from {source}...')
            data = manager.collect_from_source(source, max_pages=max_pages)
            collected_data = {source: data} if data else {}
        
        if not collected_data:
            raise CommandError('No data collected')
        
        # Show summary
        summary = manager.get_collection_summary()
        self.show_collection_summary(summary)
        
        # Import to database if not dry run
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('\n[DRY RUN] Would import to database but --dry-run is enabled')
            )
        else:
            self.import_to_database(manager, options['clear_existing'])
        
    def show_available_sources(self, manager):
        """Show available data sources"""
        self.stdout.write('\n[INFO] Available Data Sources:')
        
        collectors_info = manager.list_available_collectors()
        for source_name, metadata in collectors_info.items():
            self.stdout.write(f'  • {source_name}: {metadata["name"]}')
            self.stdout.write(f'    Category: {metadata["category"]}')
            self.stdout.write(f'    Description: {metadata["description"]}')
    
    def show_collection_summary(self, summary):
        """Show collection summary"""
        self.stdout.write('\n[SUMMARY] Collection Results:')
        self.stdout.write(f'  Total sources: {summary["sources"]}')
        self.stdout.write(f'  Total locations: {summary["total_locations"]}')
        
        for source_name, info in summary['collections'].items():
            self.stdout.write(
                f'  • {source_name}: {info["count"]} locations ({info["category"]})'
            )
    
    def import_to_database(self, manager, clear_existing=False):
        """Import collected data to Django database"""
        self.stdout.write('\n[DATABASE] Importing to Django models...')
        
        if clear_existing:
            self.stdout.write('[WARNING] Clearing existing data...')
            Location.objects.all().delete()
            Category.objects.filter(source__in=['caritas', 'handwerkskammern']).delete()
        
        # Get combined data
        combined_data = manager.combine_all_data()
        
        # Track categories and statistics
        category_mapping = {}
        stats = {
            'categories_created': 0,
            'locations_created': 0,
            'locations_updated': 0,
            'errors': 0
        }
        
        for location_data in combined_data:
            try:
                # Get or create category
                category_name = location_data['category']
                source_name = location_data['collection_source']
                
                if category_name not in category_mapping:
                    category, created = Category.objects.get_or_create(
                        name=category_name,
                        defaults={
                            'description': f'{category_name} from {source_name}',
                            'color': self.get_category_color(category_name),
                            'source': source_name
                        }
                    )
                    category_mapping[category_name] = category
                    if created:
                        stats['categories_created'] += 1
                        self.stdout.write(f'    Created category: {category_name}')
                
                category = category_mapping[category_name]
                
                # Create location
                address = location_data.get('address', {})
                contact = location_data.get('contact', {})
                
                location, created = Location.objects.update_or_create(
                    source_id=location_data.get('source_id', ''),
                    source=source_name,
                    defaults={
                        'name': location_data['name'][:255],  # Truncate if too long
                        'category': category,
                        'latitude': location_data['latitude'],
                        'longitude': location_data['longitude'],
                        'address': f"{address.get('street', '')} {address.get('postal_code', '')} {address.get('city', '')}".strip(),
                        'phone': contact.get('phone', '')[:50],
                        'email': contact.get('email', '')[:254],
                        'website': contact.get('website', '')[:200],
                        'description': location_data.get('description', '')[:500],
                        'featured': False,  # You can customize this logic
                    }
                )
                
                if created:
                    stats['locations_created'] += 1
                else:
                    stats['locations_updated'] += 1
                    
            except Exception as e:
                stats['errors'] += 1
                self.stdout.write(
                    self.style.ERROR(f'    Error importing {location_data.get("name", "Unknown")}: {e}')
                )
        
        # Show import results
        self.stdout.write('\n[RESULTS] Import completed:')
        self.stdout.write(f'  Categories created: {stats["categories_created"]}')
        self.stdout.write(f'  Locations created: {stats["locations_created"]}')
        self.stdout.write(f'  Locations updated: {stats["locations_updated"]}')
        
        if stats['errors'] > 0:
            self.stdout.write(
                self.style.WARNING(f'  Errors: {stats["errors"]}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully imported {stats["locations_created"] + stats["locations_updated"]} locations')
        )
    
    def get_category_color(self, category_name):
        """Get color for category based on name"""
        color_mapping = {
            'handwerkskammer': '#FF6B6B',
            'youth migration service': '#4ECDC4', 
            'migration counseling': '#45B7D1',
            'migration counseling adults': '#96CEB4',
            'counseling center': '#FFEAA7',
            'community work': '#DDA0DD',
            'fair integration': '#98D8C8',
            'social services': '#F7DC6F',
        }
        
        category_lower = category_name.lower()
        for key, color in color_mapping.items():
            if key in category_lower:
                return color
        
        # Default color
        return '#95A5A6'