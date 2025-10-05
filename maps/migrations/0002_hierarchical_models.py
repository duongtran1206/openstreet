"""
Create 3-Tier Hierarchical Models Migration
This migration adds the new hierarchical models while maintaining backward compatibility
"""

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators

class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0001_initial'),  # Adjust this to your latest migration
    ]

    operations = [
        # Create Domain model
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain_id', models.CharField(help_text='Unique identifier for domain', max_length=100, unique=True)),
                ('name', models.CharField(help_text='Domain display name', max_length=200)),
                ('description', models.TextField(blank=True, help_text='Description of the domain')),
                ('country', models.CharField(default='Germany', max_length=100)),
                ('language', models.CharField(default='de', max_length=10)),
                ('color_scheme', models.CharField(default='default', help_text='Color scheme for this domain', max_length=50)),
                ('icon', models.CharField(default='🏢', help_text='Emoji or icon for domain', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('featured', models.BooleanField(default=False, help_text='Show as featured domain')),
                ('source_url', models.URLField(blank=True, help_text='Original data source URL')),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Domain',
                'verbose_name_plural': 'Domains',
                'ordering': ['name'],
            },
        ),
        
        # Create HierarchicalCategory model
        migrations.CreateModel(
            name='HierarchicalCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_id', models.CharField(help_text='Unique identifier within domain', max_length=100)),
                ('name', models.CharField(help_text='Category display name', max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=200)),
                ('external_id', models.CharField(blank=True, help_text='External system ID (e.g., handwerk_id)', max_length=50)),
                ('color', models.CharField(default='#FF6B6B', help_text='Hex color code', max_length=7)),
                ('icon', models.CharField(default='📍', help_text='Icon for category markers', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('display_order', models.IntegerField(default=0, help_text='Order for display')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='maps.domain')),
            ],
            options={
                'verbose_name': 'Hierarchical Category',
                'verbose_name_plural': 'Hierarchical Categories',
                'ordering': ['domain', 'display_order', 'name'],
            },
        ),
        
        # Create HierarchicalLocation model
        migrations.CreateModel(
            name='HierarchicalLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location_id', models.CharField(help_text='Unique identifier from source', max_length=100)),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=200)),
                ('latitude', models.DecimalField(decimal_places=7, max_digits=10, validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)])),
                ('longitude', models.DecimalField(decimal_places=7, max_digits=10, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)])),
                ('street', models.CharField(blank=True, max_length=200)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('postal_code', models.CharField(blank=True, max_length=20)),
                ('country', models.CharField(default='Germany', max_length=100)),
                ('phone', models.CharField(blank=True, max_length=50)),
                ('fax', models.CharField(blank=True, max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('website', models.URLField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('verified', models.BooleanField(default=False, help_text='Data has been verified')),
                ('source_name', models.CharField(blank=True, max_length=200)),
                ('detail_url', models.URLField(blank=True, help_text='URL to detailed information')),
                ('raw_data', models.JSONField(blank=True, help_text='Original raw data', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('categories', models.ManyToManyField(related_name='locations', to='maps.hierarchicalcategory')),
            ],
            options={
                'verbose_name': 'Hierarchical Location',
                'verbose_name_plural': 'Hierarchical Locations',
                'ordering': ['name'],
            },
        ),
        
        # Create DataImportLog model
        migrations.CreateModel(
            name='DataImportLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('import_type', models.CharField(choices=[('full', 'Full Import'), ('update', 'Update Import'), ('partial', 'Partial Import')], max_length=50)),
                ('source_file', models.CharField(help_text='Path to source data file', max_length=500)),
                ('total_categories_processed', models.IntegerField(default=0)),
                ('total_locations_processed', models.IntegerField(default=0)),
                ('categories_created', models.IntegerField(default=0)),
                ('categories_updated', models.IntegerField(default=0)),
                ('locations_created', models.IntegerField(default=0)),
                ('locations_updated', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='import_logs', to='maps.domain')),
            ],
            options={
                'verbose_name': 'Data Import Log',
                'verbose_name_plural': 'Data Import Logs',
                'ordering': ['-started_at'],
            },
        ),
        
        # Add hierarchical links to existing models
        migrations.AddField(
            model_name='category',
            name='hierarchical_category',
            field=models.ForeignKey(blank=True, help_text='Link to hierarchical category if applicable', null=True, on_delete=django.db.models.deletion.SET_NULL, to='maps.hierarchicalcategory'),
        ),
        
        migrations.AddField(
            model_name='location',
            name='hierarchical_location',
            field=models.ForeignKey(blank=True, help_text='Link to hierarchical location if applicable', null=True, on_delete=django.db.models.deletion.SET_NULL, to='maps.hierarchicallocation'),
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='hierarchicalcategory',
            index=models.Index(fields=['domain', 'is_active'], name='maps_hierarchicalcategory_domain_active_idx'),
        ),
        
        migrations.AddIndex(
            model_name='hierarchicalcategory',
            index=models.Index(fields=['external_id'], name='maps_hierarchicalcategory_external_id_idx'),
        ),
        
        migrations.AddIndex(
            model_name='hierarchicallocation',
            index=models.Index(fields=['latitude', 'longitude'], name='maps_hierarchicallocation_lat_lng_idx'),
        ),
        
        migrations.AddIndex(
            model_name='hierarchicallocation',
            index=models.Index(fields=['city', 'is_active'], name='maps_hierarchicallocation_city_active_idx'),
        ),
        
        migrations.AddIndex(
            model_name='hierarchicallocation',
            index=models.Index(fields=['location_id'], name='maps_hierarchicallocation_location_id_idx'),
        ),
        
        # Add unique constraints
        migrations.AddConstraint(
            model_name='hierarchicalcategory',
            constraint=models.UniqueConstraint(fields=('domain', 'category_id'), name='unique_category_per_domain'),
        ),
    ]