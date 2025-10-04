from django import forms
from .models import Category

class GeoJSONUploadForm(forms.Form):
    geojson_file = forms.FileField(
        label='GeoJSON File',
        help_text='Select a GeoJSON file to upload (.json or .geojson)',
        widget=forms.FileInput(attrs={'accept': '.json,.geojson'})
    )
    
    category_name = forms.CharField(
        label='Category Name',
        max_length=100,
        help_text='Name for the category (will be created if not exists)'
    )
    
    category_color = forms.CharField(
        label='Category Color',
        max_length=7,
        initial='#3498db',
        widget=forms.TextInput(attrs={'type': 'color'}),
        help_text='Choose color for markers'
    )
    
    clear_existing = forms.BooleanField(
        label='Clear existing data',
        required=False,
        help_text='Check to remove all existing locations before import'
    )
    
    def clean_geojson_file(self):
        file = self.cleaned_data['geojson_file']
        if file:
            if not file.name.endswith(('.json', '.geojson')):
                raise forms.ValidationError('Please upload a valid GeoJSON file (.json or .geojson)')
            
            # Basic file size check (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size too large. Please upload files smaller than 10MB.')
        
        return file