from django.core.management.base import BaseCommand
from maps.models import Domain, Category, Location


class Command(BaseCommand):
    help = 'Create sample data for Vercel deployment'

    def handle(self, *args, **options):
        try:
            # Check if data already exists
            if Domain.objects.exists():
                self.stdout.write(
                    self.style.WARNING('Sample data already exists. Skipping creation.')
                )
                return

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

            self.stdout.write(
                self.style.SUCCESS('✅ Sample data created successfully!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating sample data: {e}')
            )