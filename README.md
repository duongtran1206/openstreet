# Django OpenStreetMap Business Map

A Django web application for creating and embedding interactive maps using OpenStreetMap with multi-category business location management capabilities.

## ✨ Key Features

- 🗺️ **Interactive Maps** powered by Leaflet.js and OpenStreetMap
- 📱 **Responsive Design** optimized for mobile and desktop  
- 🏷️ **Category Management** supports 20+ categories
- 🔍 **Search & Filter** locations by name and category
- 📤 **Data Import** from GeoJSON files
- 🎯 **Embeddable** - can be embedded in other websites
- ⚡ **REST API** for system integration
- 👨‍💼 **Admin Interface** for easy data management
- **Completely Free** - no Google Maps API key required

# OpenStreetMap Business Map

A Django web application for creating and embedding interactive maps using OpenStreetMap with multi-category business location management capabilities.

## Key Features

- **Interactive Maps** using Leaflet.js and OpenStreetMap
- **Responsive Design** optimized for mobile and desktop  
- **Category Management** supporting 20+ categories
- **Search and Filter** locations by name and category
- **Data Import** from GeoJSON files
- **Embeddable** - can be embedded in other websites
- **REST API** for system integration
- **Admin Interface** for easy data management
- **Completely Free** - no Google Maps API Key required

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- Django 4.2+
- Virtual environment (recommended)

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/duongtran1206/openstreet.git
cd openstreet
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup database**
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. **Load sample data (optional)**
```bash
python manage.py seed_data
```

6. **Run development server**
```bash
python manage.py runserver
```

### 2. Access URLs

#### **Main Map:**
- http://127.0.0.1:8000/ - Full map with controls

#### **Admin Panel:**
- http://127.0.0.1:8000/admin/
- Default: Username `admin`, Password `admin123`

#### **Embed Map:**
- http://127.0.0.1:8000/embed/

#### **GeoJSON Upload:**
- http://127.0.0.1:8000/upload-geojson/

#### **API Endpoints:**
- http://127.0.0.1:8000/api/locations/ - Locations list
- http://127.0.0.1:8000/api/categories/ - Categories list
- http://127.0.0.1:8000/api/map-data/ - Optimized map data
- http://127.0.0.1:8000/api/map-config/ - Map configuration

## 🎯 Usage

### 1. Data Management via Admin
1. Access http://127.0.0.1:8000/admin/
2. Login with admin credentials
3. Add/Edit Categories and Locations
4. Customize colors and icons for each category

### 2. GeoJSON Import

#### Via Web Interface
1. Access `/upload-geojson/`
2. Select GeoJSON file
3. Choose category for locations
4. Upload

#### Via Command Line
```bash
python manage.py import_geojson data.geojson --category "Category Name" --clear
```

### 3. Embed in Website

#### **Method 1: Iframe (Easiest)**
```html
<iframe 
    src="http://your-domain.com/embed/" 
    width="100%" 
    height="500"
    frameborder="0">
</iframe>
```

#### **Method 2: JavaScript Widget**
```html
<div id="business-map"></div>
<script src="http://your-domain.com/static/js/map.js"></script>
<script>
new BusinessMapViewer('business-map', {
    apiEndpoint: 'http://your-domain.com/api/map-data/',
    configEndpoint: 'http://your-domain.com/api/map-config/'
});
</script>
```

#### **Method 3: Customized with URL Parameters**
```html
<!-- Show only specific category -->
<iframe src="http://your-domain.com/embed/?category=1"></iframe>

<!-- Show only featured locations -->
<iframe src="http://your-domain.com/embed/?featured=true"></iframe>
```

## 📊 Sample Data

The system comes pre-loaded with:
- **25 Categories**: Stores, Warehouses, Offices, Service Centers, Dealers, etc.
- **140+ Locations**: Distributed across major Vietnamese cities
- **Different colors** for each location type

## 🔧 Customization

### Add New Category:
1. Go to Admin → Categories → Add Category
2. Set name, color (#hex), icon
3. Locations will automatically display with new color

### Add New Location:
1. Go to Admin → Locations → Add Location
2. Enter coordinates (latitude, longitude)
3. Choose category, add contact information

### Customize Map:
1. Go to Admin → Map Configurations
2. Change map center, zoom level
3. Select categories to display

## 🌐 API Documentation

### GET /api/map-data/
Returns optimized data for map:
```json
{
  "locations": [...],
  "categories": [...],
  "locations_by_category": {...},
  "total_locations": 141
}
```

### Filtering:
- `/api/map-data/?category=1,2` - Only categories 1 and 2
- `/api/map-data/?featured=true` - Only featured locations

### GET /api/locations/
Full CRUD for locations with filtering:
- `/api/locations/?city=Hanoi`
- `/api/locations/?search=store`

## 💰 Advantages over Google Maps

- ✅ **Completely Free** - no request limits
- ✅ **Fully customizable** - your own branding
- ✅ **SEO friendly** - better for search engines
- ✅ **Open source** - no vendor lock-in
- ✅ **Fast and lightweight** - optimized performance

## �️ Tech Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Frontend**: Leaflet.js 1.9.4 + OpenStreetMap
- **Database**: SQLite (easily switchable to PostgreSQL/MySQL)
- **Styling**: CSS3 + Responsive Design
- **Icons**: Font Awesome

## 📱 Browser Support & Responsiveness

- ✅ **Desktop**: Chrome, Firefox, Safari, Edge
- ✅ **Mobile**: iOS Safari, Android Chrome
- ✅ **Tablet**: iPad, Android tablets
- ✅ **Embed**: Works in iframe on any website

## 🚀 Production Deployment

To deploy to production:

1. **Update settings:**
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = 'your-secret-key'
```

2. **Use production database:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # ... PostgreSQL config
    }
}
```

3. **Setup static files:**
```bash
python manage.py collectstatic
```

4. **Deploy to server** (Heroku, DigitalOcean, AWS, etc.)

## �️ Project Structure

```
mapproject/
├── maps/                   # Main Django app
│   ├── models.py          # Category, Location, MapConfiguration
│   ├── views.py           # API views and web views
│   ├── serializers.py     # DRF serializers
│   ├── admin.py           # Admin configuration
│   ├── forms.py           # GeoJSON upload forms
│   ├── templates/maps/    # HTML templates
│   └── management/        # Management commands
├── static/                # Static files
│   ├── css/map.css       # Map styles
│   └── js/map.js         # Map JavaScript
├── requirements.txt       # Python dependencies
└── manage.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

This project includes:
- ✅ Complete source code
- ✅ Database with sample data (25 categories, 140+ locations)
- ✅ Admin interface
- ✅ API documentation
- ✅ Responsive templates
- ✅ Embed code examples
- ✅ GeoJSON import functionality

**Everything is ready to embed into client websites!** 🎉