"""
Django Admin interface for 3-Tier Hierarchical Data
Enhanced admin with hierarchical views and statistics
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.safestring import mark_safe

# Import models
from .hierarchical_models import (
    Domain, HierarchicalCategory, HierarchicalLocation, DataImportLog
)

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'domain_id', 'country', 'language', 
        'total_categories_display', 'total_locations_display',
        'is_active', 'featured', 'last_updated'
    ]
    list_filter = ['country', 'language', 'is_active', 'featured', 'created_at']
    search_fields = ['name', 'domain_id', 'description']
    readonly_fields = ['created_at', 'last_updated', 'statistics_display']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('domain_id', 'name', 'description')
        }),
        ('Geographic & Language', {
            'fields': ('country', 'language')
        }),
        ('Visual Settings', {
            'fields': ('color_scheme', 'icon')
        }),
        ('Status', {
            'fields': ('is_active', 'featured')
        }),
        ('Metadata', {
            'fields': ('source_url', 'created_at', 'last_updated')
        }),
        ('Statistics', {
            'fields': ('statistics_display',),
            'classes': ('collapse',)
        })
    )
    
    def total_categories_display(self, obj):
        count = obj.categories.filter(is_active=True).count()
        url = reverse('admin:maps_hierarchicalcategory_changelist') + f'?domain__id__exact={obj.id}'
        return format_html(
            '<a href="{}">{} categories</a>',
            url, count
        )
    total_categories_display.short_description = 'Categories'
    
    def total_locations_display(self, obj):
        count = HierarchicalLocation.objects.filter(
            categories__domain=obj, is_active=True
        ).distinct().count()
        url = reverse('admin:maps_hierarchicallocation_changelist') + f'?categories__domain__id__exact={obj.id}'
        return format_html(
            '<a href="{}">{} locations</a>',
            url, count
        )
    total_locations_display.short_description = 'Locations'
    
    def statistics_display(self, obj):
        if not obj.id:
            return "Save domain first to see statistics"
        
        # Get category statistics
        categories = obj.categories.annotate(
            location_count=Count('locations', filter=Q(locations__is_active=True))
        ).filter(is_active=True).order_by('-location_count')[:10]
        
        stats_html = f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            <h4>📊 Domain Statistics</h4>
            <p><strong>Total Categories:</strong> {obj.total_categories}</p>
            <p><strong>Total Locations:</strong> {obj.total_locations}</p>
            
            <h4>🔝 Top Categories by Locations:</h4>
            <ul>
        """
        
        for cat in categories:
            stats_html += f"<li>{cat.name}: {cat.location_count} locations</li>"
        
        stats_html += "</ul></div>"
        
        return mark_safe(stats_html)
    statistics_display.short_description = 'Statistics'

class LocationInline(admin.TabularInline):
    model = HierarchicalLocation.categories.through
    extra = 0
    readonly_fields = ['location_link']
    
    def location_link(self, obj):
        if obj.hierarchicallocation:
            url = reverse('admin:maps_hierarchicallocation_change', args=[obj.hierarchicallocation.id])
            return format_html(
                '<a href="{}">{}</a>',
                url, obj.hierarchicallocation.name
            )
        return "-"
    location_link.short_description = 'Location'

@admin.register(HierarchicalCategory)
class HierarchicalCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'domain', 'external_id', 'location_count_display',
        'color_display', 'is_active', 'display_order'
    ]
    list_filter = ['domain', 'is_active', 'created_at']
    search_fields = ['name', 'category_id', 'external_id']
    list_editable = ['display_order', 'is_active']
    readonly_fields = ['created_at', 'updated_at', 'category_id']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('domain', 'category_id', 'name', 'slug', 'external_id')
        }),
        ('Visual Settings', {
            'fields': ('color', 'icon')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'display_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [LocationInline]
    
    def location_count_display(self, obj):
        count = obj.locations.filter(is_active=True).count()
        url = reverse('admin:maps_hierarchicallocation_changelist') + f'?categories__id__exact={obj.id}'
        return format_html(
            '<a href="{}">{} locations</a>',
            url, count
        )
    location_count_display.short_description = 'Locations'
    
    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background: {}; border-radius: 3px; display: inline-block;"></div> {}',
            obj.color, obj.color
        )
    color_display.short_description = 'Color'

class CategoryInline(admin.TabularInline):
    model = HierarchicalLocation.categories.through
    extra = 0
    readonly_fields = ['category_link']
    
    def category_link(self, obj):
        if obj.hierarchicalcategory:
            url = reverse('admin:maps_hierarchicalcategory_change', args=[obj.hierarchicalcategory.id])
            return format_html(
                '<a href="{}">{}</a>',
                url, obj.hierarchicalcategory.name
            )
        return "-"
    category_link.short_description = 'Category'

@admin.register(HierarchicalLocation)
class HierarchicalLocationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'city', 'country', 'categories_display',
        'coordinates_display', 'contact_display', 'is_active', 'verified'
    ]
    list_filter = [
        'country', 'is_active', 'verified', 'created_at',
        ('categories__domain', admin.RelatedOnlyFieldListFilter),
        ('categories', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = ['name', 'city', 'location_id', 'street', 'phone', 'email']
    list_editable = ['is_active', 'verified']
    readonly_fields = [
        'created_at', 'updated_at', 'coordinates_display', 
        'full_address_display', 'raw_data_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('location_id', 'name', 'slug')
        }),
        ('Geographic Coordinates', {
            'fields': ('latitude', 'longitude', 'coordinates_display')
        }),
        ('Address', {
            'fields': ('street', 'city', 'postal_code', 'country', 'full_address_display')
        }),
        ('Contact Information', {
            'fields': ('phone', 'fax', 'email', 'website')
        }),
        ('Additional Info', {
            'fields': ('description', 'source_name', 'detail_url')
        }),
        ('Status', {
            'fields': ('is_active', 'verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Raw Data', {
            'fields': ('raw_data_display',),
            'classes': ('collapse',)
        })
    )
    
    inlines = [CategoryInline]
    
    def categories_display(self, obj):
        categories = obj.categories.all()[:3]  # Show first 3
        total = obj.categories.count()
        
        category_links = []
        for cat in categories:
            url = reverse('admin:maps_hierarchicalcategory_change', args=[cat.id])
            category_links.append(f'<a href="{url}">{cat.name}</a>')
        
        result = ', '.join(category_links)
        if total > 3:
            result += f' (+{total - 3} more)'
        
        return format_html(result)
    categories_display.short_description = 'Categories'
    
    def coordinates_display(self, obj):
        return format_html(
            '<a href="https://www.google.com/maps?q={},{}" target="_blank">📍 {:.4f}, {:.4f}</a>',
            obj.latitude, obj.longitude, obj.latitude, obj.longitude
        )
    coordinates_display.short_description = 'Coordinates'
    
    def full_address_display(self, obj):
        return obj.full_address
    full_address_display.short_description = 'Full Address'
    
    def contact_display(self, obj):
        contact_info = []
        if obj.phone:
            contact_info.append(f'📞 {obj.phone}')
        if obj.email:
            contact_info.append(f'📧 {obj.email}')
        if obj.website:
            contact_info.append(f'🌐 <a href="{obj.website}" target="_blank">Website</a>')
        
        return format_html('<br>'.join(contact_info)) if contact_info else '-'
    contact_display.short_description = 'Contact'
    
    def raw_data_display(self, obj):
        if obj.raw_data:
            import json
            formatted_data = json.dumps(obj.raw_data, indent=2, ensure_ascii=False)
            return format_html(
                '<pre style="background: #f8f9fa; padding: 10px; border-radius: 5px; max-height: 300px; overflow-y: auto;">{}</pre>',
                formatted_data
            )
        return "No raw data"
    raw_data_display.short_description = 'Raw Data'

@admin.register(DataImportLog)
class DataImportLogAdmin(admin.ModelAdmin):
    list_display = [
        'domain', 'import_type', 'status', 'total_locations_processed',
        'locations_created', 'locations_updated', 'started_at', 'duration_display'
    ]
    list_filter = ['import_type', 'status', 'started_at', 'domain']
    search_fields = ['domain__name', 'source_file']
    readonly_fields = [
        'started_at', 'completed_at', 'duration_display',
        'statistics_display'
    ]
    
    fieldsets = (
        ('Import Information', {
            'fields': ('domain', 'import_type', 'source_file', 'status')
        }),
        ('Statistics', {
            'fields': (
                'total_categories_processed', 'total_locations_processed',
                'categories_created', 'categories_updated',
                'locations_created', 'locations_updated'
            )
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'duration_display')
        }),
        ('Error Info', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Summary', {
            'fields': ('statistics_display',),
            'classes': ('collapse',)
        })
    )
    
    def duration_display(self, obj):
        if obj.duration:
            return str(obj.duration)
        return "-"
    duration_display.short_description = 'Duration'
    
    def statistics_display(self, obj):
        if obj.status == 'completed':
            success_rate = (obj.locations_created + obj.locations_updated) / max(obj.total_locations_processed, 1) * 100
            
            stats_html = f"""
            <div style="background: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745;">
                <h4>✅ Import Summary</h4>
                <p><strong>Success Rate:</strong> {success_rate:.1f}%</p>
                <p><strong>Categories:</strong> {obj.categories_created} created, {obj.categories_updated} updated</p>
                <p><strong>Locations:</strong> {obj.locations_created} created, {obj.locations_updated} updated</p>
                <p><strong>Duration:</strong> {obj.duration or 'Unknown'}</p>
            </div>
            """
        else:
            stats_html = f"""
            <div style="background: #f8d7da; padding: 15px; border-radius: 5px; border-left: 4px solid #dc3545;">
                <h4>❌ Import Status: {obj.status.title()}</h4>
                {f'<p><strong>Error:</strong> {obj.error_message}</p>' if obj.error_message else ''}
            </div>
            """
        
        return mark_safe(stats_html)
    statistics_display.short_description = 'Summary'

# Override existing admin if needed
from django.contrib import admin as django_admin
from .models import Category, Location

# Enhance existing Category admin
if Category in django_admin.site._registry:
    django_admin.site.unregister(Category)

@admin.register(Category)
class EnhancedCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'hierarchical_link', 'color', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    def hierarchical_link(self, obj):
        if obj.hierarchical_category:
            url = reverse('admin:maps_hierarchicalcategory_change', args=[obj.hierarchical_category.id])
            return format_html(
                '<a href="{}">🔗 {}</a>',
                url, obj.hierarchical_category.name
            )
        return "Not linked"
    hierarchical_link.short_description = 'Hierarchical Category'

# Enhance existing Location admin  
if Location in django_admin.site._registry:
    django_admin.site.unregister(Location)

@admin.register(Location)
class EnhancedLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'hierarchical_link', 'city', 'is_active', 'featured']
    list_filter = ['category', 'is_active', 'featured', 'created_at']
    search_fields = ['name', 'city', 'address']
    readonly_fields = ['created_at', 'updated_at']
    
    def hierarchical_link(self, obj):
        if obj.hierarchical_location:
            url = reverse('admin:maps_hierarchicallocation_change', args=[obj.hierarchical_location.id])
            return format_html(
                '<a href="{}">🔗 {}</a>',
                url, obj.hierarchical_location.name
            )
        return "Not linked"
    hierarchical_link.short_description = 'Hierarchical Location'