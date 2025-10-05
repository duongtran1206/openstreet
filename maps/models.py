from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Import hierarchical models
from .hierarchical_models import (
    Domain, HierarchicalCategory, HierarchicalLocation, DataImportLog
)

class Category(models.Model):
    """Category for grouping locations (e.g., stores, warehouses, offices)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#ff6b6b', help_text='Hex color code')
    icon = models.CharField(max_length=50, default='marker', help_text='Icon name for markers')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Link to hierarchical system (optional)
    hierarchical_category = models.ForeignKey(
        'HierarchicalCategory', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        help_text='Link to hierarchical category if applicable'
    )

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Location(models.Model):
    """Location model to store business locations"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='locations')
    
    # Geographic coordinates
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text='Latitude coordinate (-90 to 90)'
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text='Longitude coordinate (-180 to 180)'
    )
    
    # Address information
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Vietnam')
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Additional info
    description = models.TextField(blank=True)
    opening_hours = models.TextField(blank=True, help_text='Operating hours')
    image = models.URLField(blank=True, help_text='Image URL')
    
    # Status
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False, help_text='Show as featured location')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Link to hierarchical system (optional)
    hierarchical_location = models.ForeignKey(
        'HierarchicalLocation',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text='Link to hierarchical location if applicable'
    )

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        ordering = ['name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    @property
    def coordinates(self):
        """Return coordinates as [lat, lng] for JavaScript"""
        return [float(self.latitude), float(self.longitude)]

class MapConfiguration(models.Model):
    """Configuration for map display"""
    name = models.CharField(max_length=100, unique=True)
    center_latitude = models.DecimalField(max_digits=9, decimal_places=6, default=21.0285)
    center_longitude = models.DecimalField(max_digits=9, decimal_places=6, default=105.8542)
    zoom_level = models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(18)])
    
    # Map settings
    max_zoom = models.IntegerField(default=18)
    min_zoom = models.IntegerField(default=1)
    
    # Style settings
    tile_layer = models.URLField(
        default='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        help_text='Tile layer URL for map background'
    )
    attribution = models.CharField(
        max_length=200,
        default='© OpenStreetMap contributors'
    )
    
    # Display options
    show_scale = models.BooleanField(default=True)
    show_zoom_control = models.BooleanField(default=True)
    show_layer_control = models.BooleanField(default=True)
    
    # Categories to display
    categories = models.ManyToManyField(Category, blank=True)
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Map Configuration'
        verbose_name_plural = 'Map Configurations'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default configuration
            MapConfiguration.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
