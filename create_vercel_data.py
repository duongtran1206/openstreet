import os
import django
import sys

# Add the project directory to the Python path
sys.path.insert(0, '/var/task')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vercel_settings')

# Configure Django
django.setup()

from maps.models import Domain, Category, Location
from django.contrib.auth import get_user_model

def create_sample_data():
    """Create sample data for the map"""
    
    # Create Caritas domain
    caritas_domain, created = Domain.objects.get_or_create(
        name="Caritas Deutschland",
        defaults={
            'description': 'Caritas charitable organization locations across Germany',
            'color': '#FF6B35'
        }
    )
    
    # Create categories for Caritas
    categories_data = [
        ("Beratungsstellen", "Counseling and advice centers"),
        ("Altenhilfe", "Elder care services"),
        ("Kinder- und Jugendhilfe", "Child and youth services"),
        ("Behindertenhilfe", "Disability support services"),
        ("Familienhilfe", "Family support services"),
        ("Suchtberatung", "Addiction counseling"),
        ("Migrationsdienst", "Migration services")
    ]
    
    for cat_name, cat_desc in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_name,
            domain=caritas_domain,
            defaults={'description': cat_desc}
        )
        
        # Create sample locations for each category
        locations_data = [
            (f"Caritas {cat_name} Berlin", 52.5200, 13.4050),
            (f"Caritas {cat_name} München", 48.1351, 11.5820),
            (f"Caritas {cat_name} Hamburg", 53.5511, 9.9937),
        ]
        
        for loc_name, lat, lon in locations_data:
            location, created = Location.objects.get_or_create(
                name=loc_name,
                defaults={
                    'latitude': lat,
                    'longitude': lon,
                    'address': f"{loc_name} Address",
                    'description': f"Sample {cat_name} location"
                }
            )
            if created:
                location.categories.add(category)

if __name__ == '__main__':
    create_sample_data()
    print("Sample data created successfully!")