# 3-Tier Hierarchical Map System with OpenStreetMap# Django OpenStreetMap Business Map



🌍 **Interactive hierarchical mapping system with real German business data**A Django web application for creating and embedding interactive maps using OpenStreetMap with multi-category business location management capabilities.



A Django-based web application that provides interactive maps with 3-tier hierarchical data structure:## ✨ Key Features

- **Domain** → **Categories** → **Locations**

- Real data from Caritas Deutschland (516 migration services) and Handwerkskammern (53 craft chambers)- 🗺️ **Interactive Maps** powered by Leaflet.js and OpenStreetMap

- Embeddable interface for external websites- 📱 **Responsive Design** optimized for mobile and desktop  

- RESTful API for data access- 🏷️ **Category Management** supports 20+ categories

- 🔍 **Search & Filter** locations by name and category

## 📊 Current Data- 📤 **Data Import** from GeoJSON files

- 🎯 **Embeddable** - can be embedded in other websites

- **2 Domains**: Caritas Deutschland, Handwerkskammern Deutschland  - ⚡ **REST API** for system integration

- **320 Categories**: Migration services, craft trades, social services- 👨‍💼 **Admin Interface** for easy data management

- **569 Locations**: Across Germany with complete address and contact information- **Completely Free** - no Google Maps API key required

- **Updated**: October 5, 2025

# OpenStreetMap Business Map

## 🚀 Quick Start

A Django web application for creating and embedding interactive maps using OpenStreetMap with multi-category business location management capabilities.

### 1. Clone & Setup

```bash## Key Features

git clone https://github.com/duongtran1206/openstreet.git

cd openstreet- **Interactive Maps** using Leaflet.js and OpenStreetMap

python -m venv .venv- **Responsive Design** optimized for mobile and desktop  

source .venv/bin/activate  # Linux/Mac- **Category Management** supporting 20+ categories

pip install -r requirements.txt- **Search and Filter** locations by name and category

```- **Data Import** from GeoJSON files

- **Embeddable** - can be embedded in other websites

### 2. Database Setup- **REST API** for system integration

```bash- **Admin Interface** for easy data management

python manage.py migrate- **Completely Free** - no Google Maps API Key required

python manage.py loaddata final_hierarchical_fixtures.json

```## 🚀 Installation & Setup



### 3. Run Application### Prerequisites

```bash

python manage.py runserver- Python 3.8+

```- Django 4.2+

- Virtual environment (recommended)

### 4. Access Points

- **Map Interface**: http://127.0.0.1:8000/embed/### Installation Steps

- **API Root**: http://127.0.0.1:8000/api/hierarchical/domains/

- **Admin Panel**: http://127.0.0.1:8000/admin/1. **Clone the repository**

```bash

## 🏗️ Architecturegit clone https://github.com/duongtran1206/openstreet.git

cd openstreet

### 3-Tier Hierarchical Structure```

```

Domain (Lĩnh vực)2. **Create virtual environment**

├── HierarchicalCategory (Danh mục)```bash

│   └── HierarchicalLocation (Địa điểm)python -m venv .venv

└── HierarchicalCategorysource .venv/bin/activate  # macOS/Linux

    ├── HierarchicalLocation# or

    └── HierarchicalLocation.venv\Scripts\activate     # Windows

``````



### Technology Stack3. **Install dependencies**

- **Backend**: Django 4.2.25 + Django REST Framework```bash

- **Frontend**: Leaflet.js 1.9.4 + OpenStreetMap tilespip install -r requirements.txt

- **Database**: SQLite with complete fixtures```

- **API**: RESTful endpoints with CORS support

4. **Setup database**

## 📡 API Usage```bash

python manage.py migrate

### Get Domainspython manage.py createsuperuser

```javascript```

fetch('/api/hierarchical/domains/')

  .then(response => response.json())5. **Load sample data (optional)**

  .then(domains => {```bash

    // domains = [{"domain_id": "caritas_deutschland", "name": "Caritas Deutschland", ...}]python manage.py seed_data

  });```

```

6. **Run development server**

### Get Categories for Domain```bash

```javascriptpython manage.py runserver

fetch('/api/hierarchical/categories/?domain=caritas_deutschland')```

  .then(response => response.json()) 

  .then(categories => {### 2. Access URLs

    // categories = [{"category_id": "jugendmigrationsdienst", "name": "Jugendmigrationsdienst", ...}]

  });#### **Main Map:**

```- http://127.0.0.1:8000/ - Full map with controls



### Get Locations#### **Admin Panel:**

```javascript- http://127.0.0.1:8000/admin/

fetch('/api/hierarchical/locations/?domain=caritas_deutschland&categories[]=jugendmigrationsdienst')- Default: Username `admin`, Password `admin123`

  .then(response => response.json())

  .then(locations => {#### **Embed Map:**

    // locations = [{"name": "JMD Berlin", "latitude": 52.5200, "longitude": 13.4050, ...}]- http://127.0.0.1:8000/embed/

  });

```#### **GeoJSON Upload:**

- http://127.0.0.1:8000/upload-geojson/

## 🗄️ Database Management

#### **API Endpoints:**

### Export Current Data- http://127.0.0.1:8000/api/locations/ - Locations list

```bash- http://127.0.0.1:8000/api/categories/ - Categories list

python manage.py dumpdata maps.Domain maps.HierarchicalCategory maps.HierarchicalLocation --indent=2 > backup.json- http://127.0.0.1:8000/api/map-data/ - Optimized map data

```- http://127.0.0.1:8000/api/map-config/ - Map configuration



### Update Caritas Data## 🎯 Usage

```bash

python update_caritas_data.py### 1. Data Management via Admin

```1. Access http://127.0.0.1:8000/admin/

2. Login with admin credentials

### View Database Status3. Add/Edit Categories and Locations

```bash4. Customize colors and icons for each category

python manage.py shell -c "

from maps.hierarchical_models import *### 2. GeoJSON Import

print('Domains:', Domain.objects.count())

print('Categories:', HierarchicalCategory.objects.count())  #### Via Web Interface

print('Locations:', HierarchicalLocation.objects.count())1. Access `/upload-geojson/`

"2. Select GeoJSON file

```3. Choose category for locations

4. Upload

## 🌐 Embedding

#### Via Command Line

The map interface is designed to be embedded in external websites:```bash

python manage.py import_geojson data.geojson --category "Category Name" --clear

```html```

<iframe src="http://your-domain.com/embed/" width="100%" height="600" frameborder="0"></iframe>

```### 3. Embed in Website



Features:#### **Method 1: Iframe (Easiest)**

- Responsive design```html

- Domain/category filtering<iframe 

- Interactive markers with popups    src="http://your-domain.com/embed/" 

- Hierarchical controls    width="100%" 

    height="500"

## 📂 Project Structure    frameborder="0">

</iframe>

``````

openstreet/

├── maps/                                    # Main Django app#### **Method 2: JavaScript Widget**

│   ├── hierarchical_models.py             # 3-tier data models  ```html

│   ├── hierarchical_views.py              # API views<div id="business-map"></div>

│   ├── hierarchical_urls.py               # URL routing<script src="http://your-domain.com/static/js/map.js"></script>

│   ├── templates/maps/embed.html          # Embeddable interface<script>

│   └── migrations/                        # Database migrationsnew BusinessMapViewer('business-map', {

├── static/    apiEndpoint: 'http://your-domain.com/api/map-data/',

│   ├── css/hierarchical-controls.css      # Styling    configEndpoint: 'http://your-domain.com/api/map-config/'

│   └── js/hierarchical-controls.js        # Frontend logic});

├── data_collectors/                       # API import scripts</script>

├── final_hierarchical_fixtures.json      # Complete database (2.4MB)```

├── requirements.txt                       # Python dependencies

└── manage.py                              # Django management#### **Method 3: Customized with URL Parameters**

``````html

<!-- Show only specific category -->

## 🔄 Data Sources<iframe src="http://your-domain.com/embed/?category=1"></iframe>



### Caritas Deutschland<!-- Show only featured locations -->

- **Source**: https://www.caritas.de/Services/MappingService.svc/GetMapData/<iframe src="http://your-domain.com/embed/?featured=true"></iframe>

- **Type**: Migration and integration services```

- **Locations**: 516 across Germany

- **Categories**: 227 service types## 📊 Sample Data



### Handwerkskammern Deutschland  The system comes pre-loaded with:

- **Source**: Handwerkskammern website- **25 Categories**: Stores, Warehouses, Offices, Service Centers, Dealers, etc.

- **Type**: Craft trade chambers- **140+ Locations**: Distributed across major Vietnamese cities

- **Locations**: 53 chambers- **Different colors** for each location type

- **Categories**: 93 craft trades

## 🔧 Customization

## 🛠️ Development

### Add New Category:

### Add New Domain1. Go to Admin → Categories → Add Category

1. Create Domain object2. Set name, color (#hex), icon

2. Import data with categories and locations3. Locations will automatically display with new color

3. Update frontend controls

4. Test API endpoints### Add New Location:

1. Go to Admin → Locations → Add Location

### Extend API2. Enter coordinates (latitude, longitude)

- Add new endpoints in `hierarchical_views.py`3. Choose category, add contact information

- Update URL routing in `hierarchical_urls.py` 

- Document new endpoints### Customize Map:

1. Go to Admin → Map Configurations

See [DATABASE_INFO.md](DATABASE_INFO.md) for detailed database information.2. Change map center, zoom level

3. Select categories to display

## 📝 License

## 🌐 API Documentation

This project contains real data from German organizations. Please respect data usage terms and provide appropriate attribution.
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