from rest_framework import serializers
from .models import Category, Location, MapConfiguration

class CategorySerializer(serializers.ModelSerializer):
    location_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'color', 'icon', 'description', 'is_active', 'location_count']
    
    def get_location_count(self, obj):
        return obj.locations.filter(is_active=True).count()

class LocationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    coordinates = serializers.ReadOnlyField()
    
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'slug', 'category', 'category_name', 'category_color', 'category_icon',
            'latitude', 'longitude', 'coordinates', 'address', 'city', 'state', 'country',
            'postal_code', 'phone', 'email', 'website', 'description', 'opening_hours',
            'image', 'is_active', 'featured', 'created_at', 'updated_at'
        ]

class LocationMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for map display"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    coordinates = serializers.ReadOnlyField()
    
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'category', 'category_name', 'category_color', 'category_icon',
            'latitude', 'longitude', 'coordinates', 'address', 'city', 'description', 'image'
        ]

class MapConfigurationSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = MapConfiguration
        fields = [
            'id', 'name', 'center_latitude', 'center_longitude', 'zoom_level',
            'max_zoom', 'min_zoom', 'tile_layer', 'attribution',
            'show_scale', 'show_zoom_control', 'show_layer_control',
            'categories', 'is_default'
        ]