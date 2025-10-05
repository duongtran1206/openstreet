"""
Django Models for 3-Tier Hierarchical Data Structure
Mở rộng models hiện có để hỗ trợ cấu trúc 3 tầng
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import json

class Domain(models.Model):
    """
    TẦNG 1: LĨNH VỰC (DOMAIN)
    Đại diện cho một lĩnh vực dữ liệu lớn (VD: Handwerkskammern, Caritas...)
    """
    domain_id = models.CharField(max_length=100, unique=True, help_text='Unique identifier for domain')
    name = models.CharField(max_length=200, help_text='Domain display name')
    description = models.TextField(blank=True, help_text='Description of the domain')
    
    # Geographic info
    country = models.CharField(max_length=100, default='Germany')
    language = models.CharField(max_length=10, default='de')
    
    # Visual settings
    color_scheme = models.CharField(max_length=50, default='default', help_text='Color scheme for this domain')
    icon = models.CharField(max_length=50, default='Domain', help_text='Icon or label for domain')
    
    # Status
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False, help_text='Show as featured domain')
    
    # Metadata
    source_url = models.URLField(blank=True, help_text='Original data source URL')
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Domain'
        verbose_name_plural = 'Domains'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def total_categories(self):
        """Tổng số categories trong domain"""
        return self.categories.filter(is_active=True).count()
    
    @property
    def total_locations(self):
        """Tổng số locations trong domain"""
        return HierarchicalLocation.objects.filter(
            categories__domain=self,
            is_active=True
        ).distinct().count()

class HierarchicalCategory(models.Model):
    """
    TẦNG 2: DANH MỤC/MẢNG (CATEGORIES)  
    Các danh mục con trong một lĩnh vực (VD: Augenoptiker, Kraftfahrzeugtechniker...)
    """
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='categories')
    
    category_id = models.CharField(max_length=100, help_text='Unique identifier within domain')
    name = models.CharField(max_length=200, help_text='Category display name')
    slug = models.SlugField(max_length=200, blank=True)
    
    # Category-specific data
    external_id = models.CharField(max_length=50, blank=True, help_text='External system ID (e.g., handwerk_id)')
    
    # Visual settings
    color = models.CharField(max_length=7, default='#FF6B6B', help_text='Hex color code')
    icon = models.CharField(max_length=50, default='Category', help_text='Icon or label for category markers')
    
    # Status
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0, help_text='Order for display')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Hierarchical Category'
        verbose_name_plural = 'Hierarchical Categories'
        ordering = ['domain', 'display_order', 'name']
        unique_together = [['domain', 'category_id']]
        indexes = [
            models.Index(fields=['domain', 'is_active']),
            models.Index(fields=['external_id']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.domain.name} → {self.name}"
    
    def get_location_count(self):
        """Số lượng locations trong category này"""
        return self.locations.filter(is_active=True).count()

class HierarchicalLocation(models.Model):
    """
    TẦNG 3: ĐỊA ĐIỂM (LOCATIONS)
    Các địa điểm cụ thể có thể thuộc nhiều categories
    """
    # Basic info
    location_id = models.CharField(max_length=100, help_text='Unique identifier from source')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    
    # Many-to-Many với categories (1 location có thể thuộc nhiều categories)
    categories = models.ManyToManyField(HierarchicalCategory, related_name='locations')
    
    # Geographic coordinates
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    
    # Address information
    street = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Germany')
    
    # Contact information
    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Additional info
    description = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    verified = models.BooleanField(default=False, help_text='Data has been verified')
    
    # Metadata
    source_name = models.CharField(max_length=200, blank=True)
    detail_url = models.URLField(blank=True, help_text='URL to detailed information')
    raw_data = models.JSONField(blank=True, null=True, help_text='Original raw data')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Hierarchical Location'
        verbose_name_plural = 'Hierarchical Locations'
        ordering = ['name']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['city', 'is_active']),
            models.Index(fields=['location_id']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.city}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.city})"
    
    @property
    def coordinates(self):
        """Return coordinates as [lat, lng] for JavaScript"""
        return [float(self.latitude), float(self.longitude)]
    
    @property
    def full_address(self):
        """Return formatted full address"""
        parts = []
        if self.street:
            parts.append(self.street)
        if self.postal_code and self.city:
            parts.append(f"{self.postal_code} {self.city}")
        elif self.city:
            parts.append(self.city)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)
    
    @property
    def primary_domain(self):
        """Get primary domain (first category's domain)"""
        first_category = self.categories.first()
        return first_category.domain if first_category else None

class DataImportLog(models.Model):
    """
    Log để theo dõi quá trình import dữ liệu
    """
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='import_logs')
    
    # Import info
    import_type = models.CharField(max_length=50, choices=[
        ('full', 'Full Import'),
        ('update', 'Update Import'),
        ('partial', 'Partial Import')
    ])
    source_file = models.CharField(max_length=500, help_text='Path to source data file')
    
    # Statistics
    total_categories_processed = models.IntegerField(default=0)
    total_locations_processed = models.IntegerField(default=0)
    categories_created = models.IntegerField(default=0)
    categories_updated = models.IntegerField(default=0)
    locations_created = models.IntegerField(default=0)
    locations_updated = models.IntegerField(default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    
    error_message = models.TextField(blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Data Import Log'
        verbose_name_plural = 'Data Import Logs'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.domain.name} - {self.import_type} ({self.status})"
    
    @property
    def duration(self):
        """Calculate import duration"""
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None

# Note: Category and Location models are kept in models.py to avoid conflicts
# The hierarchical system extends the existing models with foreign key links