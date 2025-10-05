from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'OK',
        'message': 'Django server is running on Vercel',
        'debug': False
    })


@csrf_exempt  
@require_http_methods(["GET"])
def api_status(request):
    """API status check"""
    try:
        from .models import Domain, Category, Location
        
        domain_count = Domain.objects.count()
        category_count = Category.objects.count()
        location_count = Location.objects.count()
        
        return JsonResponse({
            'status': 'OK',
            'database': 'Connected',
            'data': {
                'domains': domain_count,
                'categories': category_count,
                'locations': location_count
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'ERROR',
            'message': str(e)
        }, status=500)