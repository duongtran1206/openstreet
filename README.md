# Django OpenStreetMap Business Map

Một ứng dụng web Django cho phép tạo và nhúng bản đồ tương tác sử dụng OpenStreetMap với khả năng quản lý nhiều danh mục địa điểm kinh doanh.

## ✨ Tính năng chính

- 🗺️ **Bản đồ tương tác** sử dụng Leaflet.js và OpenStreetMap
- � **Responsive design** tối ưu cho mobile và desktop  
- �️ **Quản lý danh mục** hỗ trợ 20+ categories
- � **Tìm kiếm và lọc** địa điểm theo tên và danh mục
- 📤 **Import dữ liệu** từ file GeoJSON
- 🎯 **Embeddable** - có thể nhúng vào website khác
- ⚡ **API REST** cho tích hợp với hệ thống khác
- 👨‍💼 **Admin interface** quản lý dữ liệu dễ dàng
- 🆓 **Hoàn toàn miễn phí** - không cần Google Maps API Key

## 🚀 Cài đặt và chạy

### 1. Khởi động server (đã sẵn sàng)
```bash
# Server đang chạy tại: http://127.0.0.1:8000/
source .venv/bin/activate
python manage.py runserver
```

### 2. Truy cập các URL

#### **Bản đồ chính:**
- http://127.0.0.1:8000/ - Bản đồ đầy đủ với controls

#### **Admin Panel:**
- http://127.0.0.1:8000/admin/
- Username: `admin`
- Password: `admin123`

#### **Embed Map (để nhúng vào website):**
- http://127.0.0.1:8000/embed/

#### **API Endpoints:**
- http://127.0.0.1:8000/api/locations/ - Danh sách locations
- http://127.0.0.1:8000/api/categories/ - Danh sách categories
- http://127.0.0.1:8000/api/map-data/ - Dữ liệu tối ưu cho bản đồ
- http://127.0.0.1:8000/api/map-config/ - Cấu hình bản đồ

## 🎯 Cách sử dụng

### 1. Quản lý dữ liệu qua Admin
1. Truy cập http://127.0.0.1:8000/admin/
2. Đăng nhập với admin/admin123
3. Thêm/sửa Categories và Locations
4. Tùy chỉnh màu sắc và icon cho từng category

### 2. Nhúng vào website khách hàng

#### **Cách 1: Iframe (Dễ nhất)**
```html
<iframe 
    src="http://127.0.0.1:8000/embed/" 
    width="100%" 
    height="500"
    frameborder="0">
</iframe>
```

#### **Cách 2: JavaScript Widget**
```html
<div id="business-map"></div>
<script src="http://127.0.0.1:8000/static/js/map.js"></script>
<script>
new BusinessMapViewer('business-map', {
    apiEndpoint: 'http://127.0.0.1:8000/api/map-data/',
    configEndpoint: 'http://127.0.0.1:8000/api/map-config/'
});
</script>
```

#### **Cách 3: Tùy chỉnh với tham số URL**
```html
<!-- Chỉ hiển thị cửa hàng -->
<iframe src="http://127.0.0.1:8000/embed/?category=1"></iframe>

<!-- Chỉ hiển thị featured locations -->
<iframe src="http://127.0.0.1:8000/embed/?featured=true"></iframe>
```

## 📊 Dữ liệu mẫu

Hệ thống đã được tạo sẵn với:
- **5 Categories**: Cửa hàng, Kho hàng, Văn phòng, Trung tâm dịch vụ, Đại lý
- **10 Locations**: Phân bố tại Hà Nội và TP.HCM
- **Màu sắc khác nhau** cho từng loại địa điểm

## 🔧 Tùy chỉnh

### Thêm Category mới:
1. Vào Admin → Categories → Add Category
2. Đặt tên, màu sắc (#hex), icon
3. Locations sẽ tự động hiển thị với màu mới

### Thêm Location mới:
1. Vào Admin → Locations → Add Location
2. Nhập tọa độ (latitude, longitude)
3. Chọn category, thêm thông tin liên hệ

### Tùy chỉnh bản đồ:
1. Vào Admin → Map Configurations
2. Thay đổi trung tâm bản đồ, zoom level
3. Chọn categories hiển thị

## 🌐 API Documentation

### GET /api/map-data/
Trả về dữ liệu tối ưu cho bản đồ:
```json
{
  "locations": [...],
  "categories": [...],
  "locations_by_category": {...},
  "total_locations": 10
}
```

### Filtering:
- `/api/map-data/?category=1,2` - Chỉ category 1 và 2
- `/api/map-data/?featured=true` - Chỉ featured locations

### GET /api/locations/
CRUD đầy đủ cho locations với filtering:
- `/api/locations/?city=Hà Nội`
- `/api/locations/?search=cửa hàng`

## 💰 Ưu điểm so với Google Maps

- ✅ **Miễn phí hoàn toàn** - không giới hạn requests
- ✅ **Không cần API key** - setup nhanh chóng  
- ✅ **Tùy chỉnh hoàn toàn** - branding riêng
- ✅ **SEO friendly** - tốt hơn cho search engine
- ✅ **Open source** - không bị vendor lock-in
- ✅ **Nhẹ và nhanh** - performance tối ưu

## 🔧 Công nghệ sử dụng

- **Backend**: Django + Django REST Framework
- **Frontend**: Leaflet.js + OpenStreetMap
- **Database**: SQLite (có thể dễ dàng chuyển PostgreSQL/MySQL)
- **Styling**: CSS3 + Responsive Design

## 📱 Responsive & Cross-browser

- ✅ Desktop: Chrome, Firefox, Safari, Edge
- ✅ Mobile: iOS Safari, Android Chrome
- ✅ Tablet: iPad, Android tablets
- ✅ Embed: Hoạt động trong iframe trên mọi website

## 🚀 Triển khai Production

Để triển khai lên production:

1. **Cập nhật settings:**
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
```

2. **Sử dụng database production:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # ... config PostgreSQL
    }
}
```

3. **Setup static files:**
```bash
python manage.py collectstatic
```

4. **Deploy lên server** (Heroku, DigitalOcean, AWS, etc.)

## 📞 Hỗ trợ

Dự án này bao gồm:
- ✅ Source code đầy đủ
- ✅ Database với dữ liệu mẫu
- ✅ Admin interface
- ✅ API documentation
- ✅ Responsive templates
- ✅ Embed code examples

**Mọi thứ đã sẵn sàng để nhúng vào website khách hàng!** 🎉