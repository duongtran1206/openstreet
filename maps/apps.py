from django.apps import AppConfig


class MapsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'maps'
    
    def ready(self):
        # Import here to avoid circular import issues
        import os
        if os.environ.get('VERCEL'):
            self.create_sample_data()
    
    def create_sample_data(self):
        try:
            from .models import Domain, Category, Location
            
            # Only create if no data exists
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
                
                print("✅ Sample data created successfully for Vercel!")
        except Exception as e:
            print(f"Note: Could not create sample data: {e}")
