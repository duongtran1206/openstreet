from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from maps.models import Category, Location, MapConfiguration
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create sample data for the business map'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Set admin password
        try:
            admin_user = User.objects.get(username='admin')
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Admin password set to: admin123'))
        except User.DoesNotExist:
            pass
        
        # Create categories
        categories_data = [
            {
                'name': 'Cửa hàng',
                'slug': 'cua-hang',
                'color': '#ff6b6b',
                'icon': 'store',
                'description': 'Các cửa hàng bán lẻ'
            },
            {
                'name': 'Kho hàng',
                'slug': 'kho-hang',
                'color': '#4ecdc4',
                'icon': 'warehouse',
                'description': 'Kho lưu trữ và phân phối'
            },
            {
                'name': 'Văn phòng',
                'slug': 'van-phong',
                'color': '#45b7d1',
                'icon': 'office',
                'description': 'Văn phòng làm việc và hành chính'
            },
            {
                'name': 'Trung tâm dịch vụ',
                'slug': 'trung-tam-dich-vu',
                'color': '#96ceb4',
                'icon': 'service',
                'description': 'Trung tâm bảo hành và dịch vụ'
            },
            {
                'name': 'Đại lý',
                'slug': 'dai-ly',
                'color': '#feca57',
                'icon': 'partner',
                'description': 'Đại lý và đối tác kinh doanh'
            }
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create sample locations
        locations_data = [
            # Cửa hàng ở Hà Nội
            {
                'name': 'Cửa hàng Hoàn Kiếm',
                'slug': 'cua-hang-hoan-kiem',
                'category': 'cua-hang',
                'latitude': Decimal('21.0285'),
                'longitude': Decimal('105.8542'),
                'address': '123 Phố Hàng Bạc, Hoàn Kiếm',
                'city': 'Hà Nội',
                'country': 'Vietnam',
                'phone': '+84 24 3826 1234',
                'email': 'hoankiem@company.com',
                'description': 'Cửa hàng flagship tại trung tâm Hà Nội',
                'featured': True
            },
            {
                'name': 'Cửa hàng Ba Đình',
                'slug': 'cua-hang-ba-dinh',
                'category': 'cua-hang',
                'latitude': Decimal('21.0245'),
                'longitude': Decimal('105.8412'),
                'address': '456 Đường Nguyễn Thái Học, Ba Đình',
                'city': 'Hà Nội',
                'country': 'Vietnam',
                'phone': '+84 24 3733 5678',
                'email': 'badinh@company.com',
                'description': 'Cửa hàng gần các cơ quan chính phủ',
                'featured': False
            },
            {
                'name': 'Cửa hàng Cầu Giấy',
                'slug': 'cua-hang-cau-giay',
                'category': 'cua-hang',
                'latitude': Decimal('21.0285'),
                'longitude': Decimal('105.7938'),
                'address': '789 Xuân Thủy, Cầu Giấy',
                'city': 'Hà Nội',
                'country': 'Vietnam',
                'phone': '+84 24 3754 9012',
                'email': 'caugiay@company.com',
                'description': 'Cửa hàng trong khu đại học',
                'featured': False
            },
            
            # Kho hàng
            {
                'name': 'Kho trung tâm Hà Nội',
                'slug': 'kho-trung-tam-ha-noi',
                'category': 'kho-hang',
                'latitude': Decimal('21.0185'),
                'longitude': Decimal('105.8642'),
                'address': '321 Đường Láng, Đống Đa',
                'city': 'Hà Nội',
                'country': 'Vietnam',
                'phone': '+84 24 3514 7890',
                'email': 'kho-hanoi@company.com',
                'description': 'Kho phân phối chính cho khu vực miền Bắc',
                'featured': True
            },
            {
                'name': 'Kho Gia Lâm',
                'slug': 'kho-gia-lam',
                'category': 'kho-hang',
                'latitude': Decimal('21.0385'),
                'longitude': Decimal('105.8742'),
                'address': '654 Đại lộ Thăng Long, Gia Lâm',
                'city': 'Hà Nội',
                'country': 'Vietnam',
                'phone': '+84 24 3827 3456',
                'email': 'gialm@company.com',
                'description': 'Kho lưu trữ quy mô lớn gần sân bay',
                'featured': False
            },
            
            # Văn phòng
            {
                'name': 'Trụ sở chính',
                'slug': 'tru-so-chinh',
                'category': 'van-phong',
                'latitude': Decimal('21.0485'),
                'longitude': Decimal('105.8442'),
                'address': '987 Phố Hai Bà Trưng, Hai Bà Trưng',
                'city': 'Hà Nội',
                'country': 'Vietnam',
                'phone': '+84 24 3943 1111',
                'email': 'headquarters@company.com',
                'website': 'https://company.com',
                'description': 'Văn phòng trụ sở chính của công ty',
                'opening_hours': 'T2-T6: 8:00-17:30, T7: 8:00-12:00',
                'featured': True
            },
            
            # Trung tâm dịch vụ
            {
                'name': 'Trung tâm bảo hành Thanh Xuân',
                'slug': 'trung-tam-bao-hanh-thanh-xuan',
                'category': 'trung-tam-dich-vu',
                'latitude': Decimal('20.9985'),
                'longitude': Decimal('105.8045'),
                'address': '147 Nguyễn Tuân, Thanh Xuân',
                'city': 'Hà Nội',
                'country': 'Vietnam',
                'phone': '+84 24 3557 8901',
                'email': 'service-thanhxuan@company.com',
                'description': 'Trung tâm bảo hành và sửa chữa',
                'opening_hours': 'T2-CN: 8:00-20:00',
                'featured': False
            },
            
            # Đại lý
            {
                'name': 'Đại lý Tây Hồ',
                'slug': 'dai-ly-tay-ho',
                'category': 'dai-ly',
                'latitude': Decimal('21.0645'),
                'longitude': Decimal('105.8242'),
                'address': '258 Lạc Long Quân, Tây Hồ',
                'city': 'Hà Nội',
                'country': 'Vietnam',
                'phone': '+84 24 3718 2345',
                'email': 'tayho-agency@company.com',
                'description': 'Đại lý ủy quyền khu vực Tây Hồ',
                'featured': False
            },
            
            # Locations ở TP.HCM
            {
                'name': 'Cửa hàng Quận 1',
                'slug': 'cua-hang-quan-1',
                'category': 'cua-hang',
                'latitude': Decimal('10.7769'),
                'longitude': Decimal('106.7009'),
                'address': '123 Đường Nguyễn Huệ, Quận 1',
                'city': 'TP. Hồ Chí Minh',
                'country': 'Vietnam',
                'phone': '+84 28 3821 1234',
                'email': 'quan1@company.com',
                'description': 'Cửa hàng trung tâm TP.HCM',
                'featured': True
            },
            {
                'name': 'Kho miền Nam',
                'slug': 'kho-mien-nam',
                'category': 'kho-hang',
                'latitude': Decimal('10.8231'),
                'longitude': Decimal('106.6297'),
                'address': '789 Quốc lộ 1A, Bình Tân',
                'city': 'TP. Hồ Chí Minh',
                'country': 'Vietnam',
                'phone': '+84 28 3756 7890',
                'email': 'kho-hcm@company.com',
                'description': 'Kho phân phối khu vực miền Nam',
                'featured': True
            }
        ]
        
        for loc_data in locations_data:
            category = categories[loc_data['category']]
            loc_data['category'] = category
            
            location, created = Location.objects.get_or_create(
                slug=loc_data['slug'],
                defaults=loc_data
            )
            if created:
                self.stdout.write(f'Created location: {location.name}')
        
        # Create default map configuration
        config_data = {
            'name': 'Default Business Map',
            'center_latitude': Decimal('21.0285'),
            'center_longitude': Decimal('105.8542'),
            'zoom_level': 10,
            'is_default': True,
            'tile_layer': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            'attribution': '© OpenStreetMap contributors'
        }
        
        config, created = MapConfiguration.objects.get_or_create(
            name=config_data['name'],
            defaults=config_data
        )
        
        if created:
            # Add all categories to the default configuration
            config.categories.set(categories.values())
            self.stdout.write(f'Created map configuration: {config.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSample data created successfully!\n'
                f'Categories: {Category.objects.count()}\n'
                f'Locations: {Location.objects.count()}\n'
                f'Map Configurations: {MapConfiguration.objects.count()}\n\n'
                f'Admin login:\n'
                f'Username: admin\n'
                f'Password: admin123\n'
            )
        )