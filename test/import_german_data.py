import json
import os
import sys
import django
from pathlib import Path

# Thêm project path vào sys.path
project_path = Path(__file__).parent.parent
sys.path.insert(0, str(project_path))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapproject.settings')
django.setup()

from django.utils.text import slugify

from maps.models import Category, Location, MapConfiguration

def clear_database():
    """Xóa toàn bộ dữ liệu cũ"""
    print("Đang xóa database cũ...")
    
    # Xóa locations trước (vì có foreign key)
    deleted_locations = Location.objects.all().delete()
    print(f"Đã xóa {deleted_locations[0]} locations")
    
    # Xóa categories
    deleted_categories = Category.objects.all().delete()
    print(f"Đã xóa {deleted_categories[0]} categories")
    
    # Xóa map configurations
    deleted_configs = MapConfiguration.objects.all().delete()
    print(f"Đã xóa {deleted_configs[0]} map configurations")
    
    print("✅ Đã xóa toàn bộ database cũ!")

def load_handwerk_data():
    """Load dữ liệu German Handwerkskammern"""
    
    # Path to JSON file
    json_file = Path(__file__).parent / "handwerkskammern_data.json"
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Tạo mapping từ handwerk ID đến tên category
    handwerk_categories = {}
    if 'lists' in data and 'locations' in data['lists'] and 'filter' in data['lists']['locations']:
        filter_data = data['lists']['locations']['filter']
        if 'handwerkid' in filter_data and 'values' in filter_data['handwerkid']:
            for item in filter_data['handwerkid']['values']:
                if item.get('$value'):  # Bỏ qua "Alle" (empty value)
                    handwerk_categories[item['$value']] = item['title']
    
    print(f"Tìm thấy {len(handwerk_categories)} handwerk categories")
    
    # Tạo categories
    print("\nĐang tạo categories...")
    created_categories = {}
    
    # Tạo category chính cho Handwerkskammer
    main_category, created = Category.objects.get_or_create(
        name="Handwerkskammer",
        defaults={
            'slug': "handwerkskammer",
            'color': '#e74c3c',
            'icon': 'industry',
            'description': 'German Chambers of Craft - Phòng Thương mại Thủ công Đức',
            'is_active': True
        }
    )
    print(f"✅ Category chính: {main_category.name}")
    
    # Tạo các categories con cho từng handwerk type (chỉ tạo những cái phổ biến)
    popular_handwerk_colors = {
        'Bäcker': '#f39c12',           # Thợ làm bánh - màu vàng
        'Friseure': '#9b59b6',         # Thợ cắt tóc - màu tím
        'Elektrotechniker': '#3498db', # Thợ điện - màu xanh
        'Dachdecker': '#34495e',       # Thợ lợp mái - màu xám
        'Glaser': '#1abc9c',           # Thợ thủy tinh - màu xanh lá
        'Augenoptiker': '#e67e22',     # Thợ kính mắt - màu cam
        'Fleischer': '#c0392b',        # Thợ thịt - màu đỏ đậm
        'Installateur und Heizungsbauer': '#27ae60'  # Thợ ống nước - màu xanh lá
    }
    
    for handwerk_name, color in popular_handwerk_colors.items():
        if handwerk_name in handwerk_categories.values():
            category, created = Category.objects.get_or_create(
                name=handwerk_name,
                defaults={
                    'slug': slugify(handwerk_name),
                    'color': color,
                    'icon': 'tools',
                    'description': f'Handwerk: {handwerk_name}',
                    'is_active': True
                }
            )
            created_categories[handwerk_name] = category
            if created:
                print(f"  ✅ Tạo category: {handwerk_name}")
    
    # Load locations data
    locations_data = []
    if 'lists' in data and 'locations' in data['lists'] and '$items' in data['lists']['locations']:
        locations_data = data['lists']['locations']['$items']
    
    print(f"\nĐang import {len(locations_data)} locations...")
    
    # Import locations
    created_locations = 0
    for item in locations_data:
        try:
            # Lấy thông tin cơ bản
            title = item.get('title', 'Unknown')
            sort_title = item.get('sortTitle', title)
            latitude = float(item.get('latitude', 0))
            longitude = float(item.get('longitude', 0))
            
            # Lấy thông tin địa chỉ
            address_info = item.get('adresse', {})
            address = address_info.get('address', '')
            city = address_info.get('city', sort_title)
            zip_code = address_info.get('zip', '')
            phone = address_info.get('phone', '')
            website = address_info.get('www', '')
            
            # Tạo địa chỉ đầy đủ
            full_address = f"{address}"
            if zip_code:
                full_address += f", {zip_code}"
            if city:
                full_address += f" {city}"
            
            # Lấy handwerk categories của location này
            handwerk_ids = item.get('handwerkid', [])
            
            # Chọn category (ưu tiên category con nếu có, không thì dùng category chính)
            selected_category = main_category
            
            # Tìm category con phù hợp
            for hid in handwerk_ids:
                handwerk_name = handwerk_categories.get(hid)
                if handwerk_name and handwerk_name in created_categories:
                    selected_category = created_categories[handwerk_name]
                    break
            
            # Tạo description từ handwerk categories
            handwerk_names = []
            for hid in handwerk_ids[:5]:  # Chỉ lấy 5 cái đầu
                name = handwerk_categories.get(hid)
                if name:
                    handwerk_names.append(name)
            
            description = f"Handwerkskammer quản lý: {', '.join(handwerk_names)}"
            if len(handwerk_ids) > 5:
                description += f" và {len(handwerk_ids) - 5} nghề khác"
            
            # Tạo location
            location = Location.objects.create(
                name=title,
                slug=slugify(f"{title}-{sort_title}"),
                category=selected_category,
                latitude=latitude,
                longitude=longitude,
                address=full_address,
                city=city,
                state="",  # Sẽ thêm sau nếu cần
                country="Germany",
                postal_code=zip_code,
                phone=phone,
                website=website,
                description=description,
                is_active=True,
                featured=len(handwerk_ids) > 25  # Featured nếu quản lý nhiều nghề
            )
            
            created_locations += 1
            print(f"  ✅ {created_locations:2d}. {title} ({city})")
            
        except Exception as e:
            print(f"  ❌ Lỗi tạo location {title}: {e}")
    
    print(f"\n✅ Đã tạo {created_locations} locations thành công!")
    
    # Tạo map configuration cho Germany
    print("\nĐang tạo map configuration...")
    
    config, created = MapConfiguration.objects.get_or_create(
        name="Germany Handwerkskammern",
        defaults={
            'center_latitude': 51.1657,   # Trung tâm nước Đức
            'center_longitude': 10.4515,
            'zoom_level': 6,              # Zoom để nhìn thấy toàn nước Đức
            'max_zoom': 18,
            'min_zoom': 5,
            'tile_layer': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            'attribution': '© OpenStreetMap contributors',
            'show_scale': True,
            'show_zoom_control': True,
            'show_layer_control': True,
            'is_default': True
        }
    )
    
    # Thêm tất cả categories vào config
    config.categories.set(Category.objects.all())
    
    if created:
        print(f"✅ Tạo map configuration: {config.name}")
    else:
        print(f"✅ Cập nhật map configuration: {config.name}")

def main():
    print("=" * 60)
    print("🗑️  XÓA DATABASE CŨ VÀ IMPORT DỮ LIỆU GERMAN HANDWERKSKAMMERN")
    print("=" * 60)
    
    try:
        # Bước 1: Xóa database cũ
        clear_database()
        
        # Bước 2: Import dữ liệu mới
        print("\n" + "=" * 40)
        print("📥 IMPORT DỮ LIỆU MỚI")
        print("=" * 40)
        
        load_handwerk_data()
        
        print("\n" + "=" * 60)
        print("🎉 HOÀN TẤT! DATABASE ĐÃ ĐƯỢC CẬP NHẬT")
        print("=" * 60)
        
        # Thống kê cuối
        total_categories = Category.objects.count()
        total_locations = Location.objects.count()
        total_configs = MapConfiguration.objects.count()
        
        print(f"\n📊 THỐNG KÊ:")
        print(f"   - Categories: {total_categories}")
        print(f"   - Locations: {total_locations}")
        print(f"   - Map Configurations: {total_configs}")
        print(f"\n🌐 Truy cập: http://127.0.0.1:8000/")
        print(f"👨‍💼 Admin: http://127.0.0.1:8000/admin/")
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())