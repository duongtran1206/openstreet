from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Location, MapConfiguration

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color_preview', 'icon', 'location_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'
    
    def location_count(self, obj):
        return obj.locations.filter(is_active=True).count()
    location_count.short_description = 'Active Locations'

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'city', 'country', 
        'coordinates_display', 'is_active', 'featured', 'created_at'
    ]
    list_filter = ['category', 'city', 'country', 'is_active', 'featured', 'created_at']
    search_fields = ['name', 'address', 'city', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'featured']
    raw_id_fields = ['category']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Geographic Location', {
            'fields': ('latitude', 'longitude'),
            'description': 'Enter the exact coordinates for this location'
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'website'),
            'classes': ['collapse']
        }),
        ('Additional Details', {
            'fields': ('opening_hours', 'image'),
            'classes': ['collapse']
        }),
        ('Status', {
            'fields': ('is_active', 'featured')
        }),
    )
    
    def coordinates_display(self, obj):
        return f"{obj.latitude}, {obj.longitude}"
    coordinates_display.short_description = 'Coordinates'

@admin.register(MapConfiguration)
class MapConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'center_display', 'zoom_level', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name']
    filter_horizontal = ['categories']
    
    def center_display(self, obj):
        return f"{obj.center_latitude}, {obj.center_longitude}"
    center_display.short_description = 'Map Center'

# Customize admin site
admin.site.site_header = "Business Map Administration"
admin.site.site_title = "Business Map Admin"
admin.site.index_title = "Welcome to Business Map Administration"
