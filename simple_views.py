from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Django is running successfully',
        'debug': True
    })

@csrf_exempt
def simple_test(request):
    """Simple test endpoint without database"""
    try:
        return JsonResponse({
            'status': 'success',
            'message': 'Simple test passed',
            'method': request.method,
            'path': request.path
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt 
def create_sample_data(request):
    """Create sample data for the map"""
    try:
        from maps.models import Domain, Category, Location
        
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
            ("Migrationsdienst", "Migration services"),
            ("Suchtberatung", "Addiction counseling")
        ]
        
        categories_created = 0
        locations_created = 0
        
        for cat_name, cat_desc in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_name,
                domain=caritas_domain,
                defaults={'description': cat_desc}
            )
            
            if created:
                categories_created += 1
            
            # Create sample locations for each category
            locations_data = [
                (f"Caritas {cat_name} Berlin", 52.5200, 13.4050, "Berlin"),
                (f"Caritas {cat_name} München", 48.1351, 11.5820, "Munich"),
            ]
            
            for loc_name, lat, lon, city in locations_data:
                location, created = Location.objects.get_or_create(
                    name=loc_name,
                    defaults={
                        'latitude': lat,
                        'longitude': lon,
                        'address': f"{loc_name}, {city}",
                        'description': f"Sample {cat_name} location in {city}"
                    }
                )
                if created:
                    location.categories.add(category)
                    locations_created += 1
        
        total_domains = Domain.objects.count()
        total_categories = Category.objects.count()
        total_locations = Location.objects.count()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Sample data created successfully',
            'created': {
                'categories': categories_created,
                'locations': locations_created
            },
            'totals': {
                'domains': total_domains,
                'categories': total_categories,
                'locations': total_locations
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)