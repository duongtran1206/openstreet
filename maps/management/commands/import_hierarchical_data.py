"""
Django Management Command to Import 3-Tier Hierarchical Data
Usage: python manage.py import_hierarchical_data <source_id> [options]
"""

import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from maps.hierarchical_models import (
    Domain, HierarchicalCategory, HierarchicalLocation, DataImportLog
)

class Command(BaseCommand):
    help = 'Import 3-tier hierarchical data into Django models'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'source_id',
            type=str,
            help='Source ID (e.g., handwerkskammern_deutschland)'
        )
        
        parser.add_argument(
            '--file',
            type=str,
            help='Path to hierarchical JSON file (optional, auto-detected if not provided)'
        )
        
        parser.add_argument(
            '--mode',
            type=str,
            choices=['create', 'update', 'replace'],
            default='create',
            help='Import mode: create (skip existing), update (update existing), replace (delete and recreate)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate import without making changes'
        )
        
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Batch size for bulk operations'
        )
    
    def handle(self, *args, **options):
        source_id = options['source_id']
        file_path = options.get('file')
        mode = options['mode']
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Starting 3-Tier Data Import: {source_id}')
        )
        
        # Auto-detect file path if not provided
        if not file_path:
            file_path = f'test/data_sources/hierarchical/{source_id}_hierarchical.json'
        
        if not os.path.exists(file_path):
            raise CommandError(f'File not found: {file_path}')
        
        # Load hierarchical data
        self.stdout.write(f'📁 Loading data from: {file_path}')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise CommandError(f'Error reading file: {e}')
        
        # Start import process
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be made'))
        
        try:
            with transaction.atomic():
                result = self._import_data(data, mode, dry_run, batch_size)
                
                if dry_run:
                    # Rollback transaction for dry run
                    transaction.set_rollback(True)
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Import failed: {e}')
            )
            raise
        
        # Display results
        self._display_results(result, dry_run)
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'🎉 Import completed successfully!')
            )
    
    def _import_data(self, data, mode, dry_run, batch_size):
        """Main import logic"""
        
        # Extract domain info
        domain_info = {
            'domain_id': data['domain_id'],
            'name': data['domain_name'],
            'description': data.get('domain_description', ''),
            'country': data.get('country', 'Germany'),
            'language': data.get('language', 'de')
        }
        
        self.stdout.write(f"📂 Domain: {domain_info['name']}")
        
        # Create/get domain
        if not dry_run:
            domain, domain_created = Domain.objects.get_or_create(
                domain_id=domain_info['domain_id'],
                defaults=domain_info
            )
            
            if not domain_created and mode == 'update':
                for key, value in domain_info.items():
                    setattr(domain, key, value)
                domain.save()
        else:
            domain = None
            domain_created = not Domain.objects.filter(
                domain_id=domain_info['domain_id']
            ).exists()
        
        # Create import log
        if not dry_run:
            import_log = DataImportLog.objects.create(
                domain=domain,
                import_type='full' if mode == 'replace' else mode,
                source_file=f"hierarchical/{data['domain_id']}_hierarchical.json",
                status='processing'
            )
        
        # Statistics
        stats = {
            'domain_created': domain_created,
            'categories_processed': 0,
            'categories_created': 0,
            'categories_updated': 0,
            'locations_processed': 0,
            'locations_created': 0,
            'locations_updated': 0,
            'associations_created': 0
        }
        
        # Process categories and locations
        categories_data = data.get('categories', {})
        
        self.stdout.write(f"📊 Processing {len(categories_data)} categories...")
        
        if mode == 'replace' and not dry_run:
            # Delete existing data for this domain
            HierarchicalCategory.objects.filter(domain=domain).delete()
            self.stdout.write(self.style.WARNING('🗑️ Deleted existing categories'))
        
        # Process categories
        category_objects = {}
        
        for cat_id, cat_data in categories_data.items():
            if len(cat_data['locations']) == 0:
                continue  # Skip empty categories
                
            stats['categories_processed'] += 1
            
            category_info = {
                'domain': domain,
                'category_id': cat_data['category_id'],
                'name': cat_data['category_name'],
                'external_id': str(cat_data.get('handwerk_id', '')),
                'color': self._get_category_color(cat_id),
                'icon': '🏭' if 'handwerk' in cat_id else '📍'
            }
            
            if not dry_run:
                category, cat_created = HierarchicalCategory.objects.get_or_create(
                    domain=domain,
                    category_id=cat_data['category_id'],
                    defaults=category_info
                )
                
                if not cat_created and mode in ['update', 'replace']:
                    for key, value in category_info.items():
                        if key != 'domain':  # Don't update domain
                            setattr(category, key, value)
                    category.save()
                    stats['categories_updated'] += 1
                else:
                    stats['categories_created'] += 1
                    
                category_objects[cat_id] = category
            else:
                # For dry run, create a fake domain to check
                fake_domain = type('Domain', (), {'domain_id': domain_info['domain_id']})()
                cat_created = True  # In dry run, assume it would be created
                
                if cat_created:
                    stats['categories_created'] += 1
                else:
                    stats['categories_updated'] += 1
            
            # Process locations in this category
            self._process_locations_batch(
                cat_data['locations'], 
                category_objects.get(cat_id), 
                stats, 
                dry_run, 
                mode,
                batch_size
            )
        
        # Update import log
        if not dry_run:
            import_log.total_categories_processed = stats['categories_processed']
            import_log.total_locations_processed = stats['locations_processed']
            import_log.categories_created = stats['categories_created']
            import_log.categories_updated = stats['categories_updated']
            import_log.locations_created = stats['locations_created']
            import_log.locations_updated = stats['locations_updated']
            import_log.status = 'completed'
            import_log.completed_at = timezone.now()
            import_log.save()
        
        return stats
    
    def _process_locations_batch(self, locations_data, category, stats, dry_run, mode, batch_size):
        """Process locations in batches"""
        
        locations_to_create = []
        locations_to_update = []
        
        for location_data in locations_data:
            stats['locations_processed'] += 1
            
            location_info = {
                'location_id': str(location_data['location_id']),
                'name': location_data['name'],
                'latitude': location_data['coordinates']['latitude'],
                'longitude': location_data['coordinates']['longitude'],
                'street': location_data['address'].get('street', ''),
                'city': location_data['address'].get('city', ''),
                'postal_code': location_data['address'].get('postal_code', ''),
                'country': location_data['address'].get('country', 'Germany'),
                'phone': location_data['contact'].get('phone', ''),
                'fax': location_data['contact'].get('fax', ''),
                'email': location_data['contact'].get('email', ''),
                'website': location_data['contact'].get('website', ''),
                'source_name': location_data['metadata'].get('source', ''),
                'detail_url': location_data['metadata'].get('detail_url', ''),
                'raw_data': location_data
            }
            
            if not dry_run:
                # Check if location exists
                existing_location = HierarchicalLocation.objects.filter(
                    location_id=location_info['location_id']
                ).first()
                
                if existing_location:
                    if mode in ['update', 'replace']:
                        for key, value in location_info.items():
                            setattr(existing_location, key, value)
                        existing_location.save()
                        
                        # Add to category if not already associated
                        existing_location.categories.add(category)
                        stats['locations_updated'] += 1
                        stats['associations_created'] += 1
                else:
                    # Create new location
                    location = HierarchicalLocation.objects.create(**location_info)
                    location.categories.add(category)
                    stats['locations_created'] += 1
                    stats['associations_created'] += 1
            else:
                # Dry run - just count
                exists = HierarchicalLocation.objects.filter(
                    location_id=location_info['location_id']
                ).exists()
                
                if exists:
                    stats['locations_updated'] += 1
                else:
                    stats['locations_created'] += 1
                stats['associations_created'] += 1
    
    def _get_category_color(self, category_id):
        """Get color for category"""
        colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57",
            "#FF9FF3", "#54A0FF", "#5F27CD", "#00D2D3", "#FF9F43",
            "#74B9FF", "#A29BFE", "#FD79A8", "#FDCB6E", "#6C5CE7"
        ]
        
        hash_val = sum(ord(c) for c in category_id)
        return colors[hash_val % len(colors)]
    
    def _display_results(self, stats, dry_run):
        """Display import results"""
        mode_text = "WOULD BE" if dry_run else "WERE"
        
        self.stdout.write(f"\n📊 IMPORT RESULTS:")
        self.stdout.write(f"   📁 Domain: {'CREATED' if stats['domain_created'] else 'UPDATED'}")
        self.stdout.write(f"   📂 Categories processed: {stats['categories_processed']}")
        self.stdout.write(f"   📂 Categories {mode_text.lower()} created: {stats['categories_created']}")
        self.stdout.write(f"   📂 Categories {mode_text.lower()} updated: {stats['categories_updated']}")
        self.stdout.write(f"   📍 Locations processed: {stats['locations_processed']}")
        self.stdout.write(f"   📍 Locations {mode_text.lower()} created: {stats['locations_created']}")
        self.stdout.write(f"   📍 Locations {mode_text.lower()} updated: {stats['locations_updated']}")
        self.stdout.write(f"   🔗 Category associations {mode_text.lower()} created: {stats['associations_created']}")
        
        if not dry_run:
            self.stdout.write(f"\n💾 Data successfully imported into Django models!")
            self.stdout.write(f"🌐 Ready for web interface integration!")