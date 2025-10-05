# Database Information

## 📊 Current Database Status

**Updated: October 5, 2025**

### Domains & Data Sources

#### 1. Caritas Deutschland
- **Categories**: 227 
- **Locations**: 516
- **API Source**: `https://www.caritas.de/Services/MappingService.svc/GetMapData/ec7e69ee-35b9-45b9-b081-fc7a191a76c0/?datasource=80c48846275643e0b82b83465979eb70`
- **Data Type**: Migration and integration services
- **Last Updated**: October 5, 2025

#### 2. Deutschlandkarte der Handwerkskammern
- **Categories**: 93
- **Locations**: 53  
- **API Source**: Handwerkskammern Deutschland website
- **Data Type**: Craft trades and chambers
- **Last Updated**: Previous import

### 📋 Totals
- **Domains**: 2
- **Categories**: 320
- **Locations**: 569

## 🗄️ Database Files

### Production Data
- `final_hierarchical_fixtures.json` (2.4MB) - Complete database with all domains, categories, and locations

### Import Scripts
- `import_caritas_real.py` - Original Caritas import script
- `update_caritas_data.py` - Updated script for new Caritas API endpoint
- `debug_caritas_api.py` - Debug tools for Caritas API
- `debug_caritas_location.py` - Debug tools for location processing

## 🚀 Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/duongtran1206/openstreet.git
cd openstreet
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Create new database
python manage.py migrate

# Load all data
python manage.py loaddata final_hierarchical_fixtures.json
```

### 5. Run Server
```bash
python manage.py runserver
```

### 6. Access Application
- **Main Interface**: http://127.0.0.1:8000/embed/
- **API Domains**: http://127.0.0.1:8000/api/hierarchical/domains/
- **Admin Interface**: http://127.0.0.1:8000/admin/

## 🌐 API Endpoints

### Hierarchical API Structure

#### Get Domains
```http
GET /api/hierarchical/domains/
```

#### Get Categories for Domain
```http
GET /api/hierarchical/categories/?domain={domain_id}
```

#### Get Locations
```http
GET /api/hierarchical/locations/?domain={domain_id}&categories[]={category_id}
```

### Example Usage
```javascript
// Get all domains
fetch('/api/hierarchical/domains/')
  .then(response => response.json())
  .then(domains => console.log(domains));

// Get Caritas categories  
fetch('/api/hierarchical/categories/?domain=caritas_deutschland')
  .then(response => response.json())
  .then(categories => console.log(categories));
```

## 📁 Project Structure

```
openstreet/
├── maps/                           # Django app
│   ├── hierarchical_models.py     # 3-tier data models
│   ├── hierarchical_views.py      # API views
│   ├── hierarchical_urls.py       # URL routing
│   └── templates/maps/embed.html  # Frontend interface
├── static/
│   ├── css/hierarchical-controls.css
│   └── js/hierarchical-controls.js
├── final_hierarchical_fixtures.json # Complete database
├── requirements.txt               # Dependencies
└── manage.py                     # Django management
```

## 🔄 Data Updates

### Update Caritas Data
```bash
python update_caritas_data.py
```

### Create New Fixtures
```bash
python manage.py dumpdata maps.Domain maps.HierarchicalCategory maps.HierarchicalLocation --indent=2 > new_fixtures.json
```

## 🛠️ Development Notes

- **Framework**: Django 4.2.25 + Django REST Framework
- **Frontend**: Leaflet.js 1.9.4 + OpenStreetMap
- **Database**: SQLite (included in fixtures)
- **Architecture**: 3-tier hierarchical structure (Domain → Category → Location)
- **CORS**: Enabled for embedding in external websites

## 📝 License & Usage

This project contains real data from:
- Caritas Deutschland (migration services)
- Handwerkskammern Deutschland (craft trades)

Please respect data sources and usage terms.