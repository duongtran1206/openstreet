"""
WSGI config for mapproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vercel_settings')

application = get_wsgi_application()

# Auto-create sample data for Vercel deployment
try:
    from django.conf import settings
    if getattr(settings, 'AUTO_CREATE_SAMPLE_DATA', False):
        from maps.models import Domain, Category, Location
        
        # Check if data exists
        if not Domain.objects.exists():
            # Create Caritas domain
            caritas_domain = Domain.objects.create(
                name="Caritas Deutschland",
                description='Caritas charitable organization locations across Germany',
                color='#FF6B35'
            )
            
            # Create sample categories and locations
            categories_data = [
                ("Beratungsstellen", "Counseling centers"),
                ("Altenhilfe", "Elder care"),
                ("Kinder- und Jugendhilfe", "Child & youth services"),
                ("Migrationsdienst", "Migration services"),
                ("Suchtberatung", "Addiction counseling")
            ]
            
            for cat_name, cat_desc in categories_data:
                category = Category.objects.create(
                    name=cat_name,
                    domain=caritas_domain,
                    description=cat_desc
                )
                
                # Sample locations
                locations_data = [
                    (f"Caritas {cat_name} Berlin", 52.5200, 13.4050, "Berlin"),
                    (f"Caritas {cat_name} München", 48.1351, 11.5820, "Munich"),
                ]
                
                for loc_name, lat, lon, city in locations_data:
                    location = Location.objects.create(
                        name=loc_name,
                        latitude=lat,
                        longitude=lon,
                        address=f"{loc_name}, {city}",
                        description=f"Sample {cat_name} location in {city}"
                    )
                    location.categories.add(category)
            
            print("✅ Sample data created successfully for Vercel deployment!")
except Exception as e:
    print(f"Note: Could not auto-create sample data: {e}")
