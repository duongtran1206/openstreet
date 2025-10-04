from django.core.management.base import BaseCommand
from maps.models import Category, Location, MapConfiguration
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Create 20+ categories with sample locations for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating 20+ categories with locations...')
        
        # Clear existing data
        Location.objects.all().delete()
        Category.objects.all().delete()
        
        # 25 different business categories with Vietnamese names
        categories_data = [
            {'name': 'Nhà máy sản xuất', 'slug': 'nha-may-san-xuat', 'color': '#e74c3c', 'icon': 'factory'},
            {'name': 'Cửa hàng bán lẻ', 'slug': 'cua-hang-ban-le', 'color': '#3498db', 'icon': 'store'},
            {'name': 'Kho vận chuyển', 'slug': 'kho-van-chuyen', 'color': '#f39c12', 'icon': 'warehouse'},
            {'name': 'Văn phòng đại diện', 'slug': 'van-phong-dai-dien', 'color': '#9b59b6', 'icon': 'office'},
            {'name': 'Trạm xăng dầu', 'slug': 'tram-xang-dau', 'color': '#1abc9c', 'icon': 'gas-station'},
            {'name': 'Nhà hàng khách sạn', 'slug': 'nha-hang-khach-san', 'color': '#e67e22', 'icon': 'restaurant'},
            {'name': 'Trung tâm thương mại', 'slug': 'trung-tam-thuong-mai', 'color': '#34495e', 'icon': 'mall'},
            {'name': 'Bệnh viện y tế', 'slug': 'benh-vien-y-te', 'color': '#e74c3c', 'icon': 'hospital'},
            {'name': 'Trường học giáo dục', 'slug': 'truong-hoc-giao-duc', 'color': '#f1c40f', 'icon': 'school'},
            {'name': 'Ngân hàng tài chính', 'slug': 'ngan-hang-tai-chinh', 'color': '#2ecc71', 'icon': 'bank'},
            {'name': 'Trạm dịch vụ xe', 'slug': 'tram-dich-vu-xe', 'color': '#95a5a6', 'icon': 'service'},
            {'name': 'Công viên giải trí', 'slug': 'cong-vien-giai-tri', 'color': '#27ae60', 'icon': 'park'},
            {'name': 'Trung tâm thể thao', 'slug': 'trung-tam-the-thao', 'color': '#e67e22', 'icon': 'sports'},
            {'name': 'Rạp chiếu phim', 'slug': 'rap-chieu-phim', 'color': '#8e44ad', 'icon': 'cinema'},
            {'name': 'Siêu thị điện máy', 'slug': 'sieu-thi-dien-may', 'color': '#3498db', 'icon': 'electronics'},
            {'name': 'Cửa hàng thời trang', 'slug': 'cua-hang-thoi-trang', 'color': '#e91e63', 'icon': 'fashion'},
            {'name': 'Tiệm cắt tóc làm đẹp', 'slug': 'tiem-cat-toc-lam-dep', 'color': '#ff5722', 'icon': 'beauty'},
            {'name': 'Phòng khám nha khoa', 'slug': 'phong-kham-nha-khoa', 'color': '#00bcd4', 'icon': 'dental'},
            {'name': 'Cửa hàng sách văn phòng phẩm', 'slug': 'cua-hang-sach-van-phong-pham', 'color': '#607d8b', 'icon': 'bookstore'},
            {'name': 'Trung tâm sửa chữa điện thoại', 'slug': 'trung-tam-sua-chua-dien-thoai', 'color': '#795548', 'icon': 'phone-repair'},
            {'name': 'Cửa hàng bánh kẹo', 'slug': 'cua-hang-banh-keo', 'color': '#ffc107', 'icon': 'bakery'},
            {'name': 'Trạm rửa xe ô tô', 'slug': 'tram-rua-xe-oto', 'color': '#2196f3', 'icon': 'car-wash'},
            {'name': 'Cửa hàng hoa tươi', 'slug': 'cua-hang-hoa-tuoi', 'color': '#e91e63', 'icon': 'flower'},
            {'name': 'Trung tâm massage spa', 'slug': 'trung-tam-massage-spa', 'color': '#9c27b0', 'icon': 'spa'},
            {'name': 'Cửa hàng xe máy', 'slug': 'cua-hang-xe-may', 'color': '#ff9800', 'icon': 'motorbike'}
        ]
        
        # Define location areas for variety
        location_areas = [
            # Hà Nội areas
            {'name': 'Hoàn Kiếm', 'lat_base': 21.0285, 'lng_base': 105.8542, 'city': 'Hà Nội'},
            {'name': 'Ba Đình', 'lat_base': 21.0245, 'lng_base': 105.8412, 'city': 'Hà Nội'},
            {'name': 'Cầu Giấy', 'lat_base': 21.0285, 'lng_base': 105.7938, 'city': 'Hà Nội'},
            {'name': 'Đống Đa', 'lat_base': 21.0185, 'lng_base': 105.8642, 'city': 'Hà Nội'},
            {'name': 'Hai Bà Trưng', 'lat_base': 21.0485, 'lng_base': 105.8442, 'city': 'Hà Nội'},
            {'name': 'Thanh Xuân', 'lat_base': 20.9985, 'lng_base': 105.8045, 'city': 'Hà Nội'},
            {'name': 'Tây Hồ', 'lat_base': 21.0645, 'lng_base': 105.8242, 'city': 'Hà Nội'},
            
            # TP.HCM areas  
            {'name': 'Quận 1', 'lat_base': 10.7769, 'lng_base': 106.7009, 'city': 'TP. Hồ Chí Minh'},
            {'name': 'Quận 3', 'lat_base': 10.7756, 'lng_base': 106.6947, 'city': 'TP. Hồ Chí Minh'},
            {'name': 'Quận 7', 'lat_base': 10.7379, 'lng_base': 106.7196, 'city': 'TP. Hồ Chí Minh'},
            {'name': 'Bình Thạnh', 'lat_base': 10.8014, 'lng_base': 106.7109, 'city': 'TP. Hồ Chí Minh'},
            {'name': 'Thủ Đức', 'lat_base': 10.8505, 'lng_base': 106.7717, 'city': 'TP. Hồ Chí Minh'},
            
            # Đà Nẵng
            {'name': 'Hải Châu', 'lat_base': 16.0544, 'lng_base': 108.2022, 'city': 'Đà Nẵng'},
            {'name': 'Sơn Trà', 'lat_base': 16.0833, 'lng_base': 108.2500, 'city': 'Đà Nẵng'},
            
            # Hải Phòng
            {'name': 'Hồng Bàng', 'lat_base': 20.8525, 'lng_base': 106.6807, 'city': 'Hải Phòng'},
            {'name': 'Lê Chân', 'lat_base': 20.8447, 'lng_base': 106.6839, 'city': 'Hải Phòng'},
        ]
        
        # Create categories
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(f'✓ Created category: {category.name}')
        
        # Generate locations for each category
        total_locations = 0
        for cat_slug, category in categories.items():
            # Each category gets 3-8 random locations
            num_locations = random.randint(3, 8)
            
            for i in range(num_locations):
                # Pick random area
                area = random.choice(location_areas)
                
                # Generate random coordinates around the base point
                lat_offset = random.uniform(-0.01, 0.01)
                lng_offset = random.uniform(-0.01, 0.01)
                
                location_data = {
                    'name': f'{category.name} {area["name"]} {i+1}',
                    'slug': f'{cat_slug}-{area["name"].lower()}-{i+1}',
                    'category': category,
                    'latitude': Decimal(str(area['lat_base'] + lat_offset)),
                    'longitude': Decimal(str(area['lng_base'] + lng_offset)),
                    'address': f'{random.randint(1, 999)} Đường {random.choice(["Nguyễn Huệ", "Lê Lợi", "Trần Hưng Đạo", "Hai Bà Trưng", "Ba Tháng Hai"])}, {area["name"]}',
                    'city': area['city'],
                    'country': 'Vietnam',
                    'phone': f'+84 {random.randint(20, 99)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}',
                    'email': f'{cat_slug}-{area["name"].lower()}@company.com',
                    'description': f'{category.name} tại khu vực {area["name"]}, {area["city"]}',
                    'featured': random.choice([True, False, False]),  # 1/3 chance to be featured
                    'is_active': True
                }
                
                location, created = Location.objects.get_or_create(
                    slug=location_data['slug'],
                    defaults=location_data
                )
                
                if created:
                    total_locations += 1
        
        # Update default map configuration
        config, created = MapConfiguration.objects.get_or_create(
            name='Default Business Map',
            defaults={
                'center_latitude': Decimal('16.0544'),  # Center around Vietnam
                'center_longitude': Decimal('108.2022'),
                'zoom_level': 6,
                'is_default': True
            }
        )
        
        # Add all categories to configuration
        config.categories.set(categories.values())
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Test data created successfully!\n'
                f'📁 Categories: {len(categories)}\n'
                f'📍 Locations: {total_locations}\n'
                f'🏙️  Cities: Hà Nội, TP.HCM, Đà Nẵng, Hải Phòng\n'
                f'🎯 Featured locations: {Location.objects.filter(featured=True).count()}\n\n'
                f'🌐 Test URLs:\n'
                f'   Main map: http://127.0.0.1:8000/\n'
                f'   Embed map: http://127.0.0.1:8000/embed/\n'
                f'   Admin: http://127.0.0.1:8000/admin/ (admin/admin123)\n'
            )
        )