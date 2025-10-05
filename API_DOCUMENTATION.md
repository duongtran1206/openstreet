# 📋 API DOCUMENTATION - Hierarchical Map System

## 🌐 **BASE URL:** `http://127.0.0.1:8000/`

---

## 🎯 **WEB INTERFACE ENDPOINTS**

### 📍 **Main Pages**
| URL | Chức năng | Mô tả |
|-----|-----------|-------|
| `/` | Main Map View | Giao diện bản đồ chính với legacy controls |
| `/embed/` | **Embed Map (PRIMARY)** | Giao diện nhúng với hierarchical controls |
| `/embed-debug/` | Debug Embed | Debug version của embed page |
| `/embed-test/` | Test Embed | Test page cho embedded map |
| `/hierarchical/` | Hierarchical Map | Full hierarchical map interface |
| `/admin-map/` | Admin Map | Giao diện quản trị bản đồ |
| `/admin/` | Django Admin | Django admin interface |

### 📤 **Data Management**
| URL | Chức năng | Mô tả |
|-----|-----------|-------|
| `/upload-geojson/` | Upload GeoJSON | Upload và import GeoJSON files |
| `/data-collection/` | Data Collection Interface | Giao diện thu thập dữ liệu multi-source |

---

## 🚀 **REST API ENDPOINTS**

### 🏗️ **3-Tier Hierarchical System APIs**

#### **📊 Domains API (Tier 1)**
```
GET /api/hierarchical/domains/
```
**Chức năng:** Lấy danh sách tất cả domains (lĩnh vực)
**Response:**
```json
[
  {
    "domain_id": "caritas_deutschland",
    "name": "Caritas Deutschland", 
    "description": "Social services & migration consulting",
    "country": "Germany",
    "language": "de",
    "category_count": 7,
    "location_count": 5
  },
  {
    "domain_id": "handwerkskammern_deutschland",
    "name": "Deutschlandkarte der Handwerkskammern",
    "country": "Germany", 
    "language": "de",
    "category_count": 93,
    "location_count": 53
  }
]
```

#### **🏷️ Categories API (Tier 2)**
```
GET /api/hierarchical/categories/?domain={domain_id}
```
**Chức năng:** Lấy categories thuộc một domain
**Parameters:**
- `domain` (required): Domain ID (vd: `caritas_deutschland`)

**Response:**
```json
[
  {
    "category_id": "jugendmigrationsdienst",
    "name": "Jugendmigrationsdienst",
    "description": "Youth migration service",
    "color": "#e74c3c",
    "icon": "fas fa-hands-helping", 
    "location_count": 2
  }
]
```

#### **📍 Locations API (Tier 3)**
```
GET /api/hierarchical/locations/?domain={domain_id}&categories[]={category_id}
```
**Chức năng:** Lấy locations với filtering
**Parameters:**
- `domain` (required): Domain ID
- `categories[]` (optional): Array of category IDs to filter
- `search` (optional): Text search trong tên/địa chỉ

**Response GeoJSON:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "id": "caritas_1",
        "name": "Kath. Jugendmigrationsdienst Dresden",
        "address": "Schönbrunnstraße 10, 01097 Dresden",
        "phone": "+49 351 32023810",
        "email": "jmd@caritas-dresden.de",
        "categories": [
          {
            "id": "jugendmigrationsdienst",
            "name": "Jugendmigrationsdienst",
            "color": "#e74c3c"
          }
        ]
      },
      "geometry": {
        "type": "Point",
        "coordinates": [13.7373, 51.0504]
      }
    }
  ]
}
```

#### **🔍 Search API**
```
GET /api/hierarchical/search/?q={query}&domain={domain_id}
```
**Chức năng:** Tìm kiếm locations theo text
**Parameters:**
- `q` (required): Search query
- `domain` (optional): Limit search to domain

---

### 🗺️ **Legacy Map APIs**

#### **📊 Map Data**
```
GET /api/map-data/
```
**Chức năng:** Lấy tất cả data cho legacy map
**Response:** GeoJSON với tất cả locations

#### **⚙️ Map Configuration**
```
GET /api/map-config/
GET /api/map-config/{config_name}/
```
**Chức năng:** Lấy cấu hình bản đồ
**Response:**
```json
{
  "center": {"lat": 52.52, "lng": 13.4050},
  "zoom": 6,
  "max_zoom": 18,
  "tile_layer": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
}
```

#### **🏷️ Categories (Legacy)**
```
GET /api/categories/
```
**Chức năng:** DRF ViewSet cho legacy categories
**Methods:** GET, POST, PUT, DELETE (với permissions)

#### **📍 Locations (Legacy)**
```
GET /api/locations/
```
**Chức năng:** DRF ViewSet cho legacy locations  
**Methods:** GET, POST, PUT, DELETE (với permissions)

---

### 📊 **Data Collection APIs**

#### **📥 Collect Data**
```
POST /api/collect-data/
```
**Chức năng:** Thu thập dữ liệu từ external sources
**Body:**
```json
{
  "source_type": "handwerk_chambers",
  "limit": 100
}
```

#### **📋 Collection Sources**
```
GET /api/collection-sources/
```
**Chức năng:** Lấy danh sách available data sources

#### **📈 Collection Stats**
```
GET /api/collection-stats/
```
**Chức năng:** Thống kê về data collection

---

## 🎯 **USAGE EXAMPLES**

### **Load Embed Page với Caritas Data:**
```javascript
// 1. Load domains
fetch('/api/hierarchical/domains/')
  .then(r => r.json())
  .then(domains => console.log(domains));

// 2. Load Caritas categories  
fetch('/api/hierarchical/categories/?domain=caritas_deutschland')
  .then(r => r.json())
  .then(categories => console.log(categories));

// 3. Load Caritas locations
fetch('/api/hierarchical/locations/?domain=caritas_deutschland')
  .then(r => r.json()) 
  .then(geojson => console.log(geojson));
```

### **Search Locations:**
```javascript
// Tìm kiếm "Dresden" trong domain Caritas
fetch('/api/hierarchical/search/?q=Dresden&domain=caritas_deutschland')
  .then(r => r.json())
  .then(results => console.log(results));
```

### **Filter by Categories:**
```javascript
// Lấy chỉ locations thuộc Jugendmigrationsdienst
fetch('/api/hierarchical/locations/?domain=caritas_deutschland&categories[0]=jugendmigrationsdienst')
  .then(r => r.json())
  .then(geojson => console.log(geojson));
```

---

## 📊 **CURRENT DATA STATUS**

### **📈 Statistics:**
- **Total Domains:** 2
  - Caritas Deutschland (7 categories, 5 locations)
  - Handwerkskammern Deutschland (93 categories, 53 locations)
- **Total Categories:** 100
- **Total Locations:** 58
- **Geographic Coverage:** Germany

### **🎯 Primary Workflow:**
1. **Access:** `http://127.0.0.1:8000/embed/`
2. **Select Domain:** Dropdown Tier 1  
3. **Choose Categories:** Checkboxes Tier 2
4. **View Locations:** List + Map Tier 3
5. **Interact:** Click locations to zoom + view details

---

## 🔧 **DEVELOPMENT & DEBUG**

### **Debug URLs:**
- `/embed-debug/` - Enhanced debug info
- Browser DevTools Console - Real-time logs
- Django Admin - `/admin/` - Data management

### **Cache Busting:**
- CSS/JS files include `?v={timestamp}` 
- Force refresh: Ctrl+F5 in browser

### **API Testing:**
- Use browser DevTools Network tab
- Test endpoints directly in browser
- Check Django server logs for DEBUG info

---

## 🚀 **PERFORMANCE & FEATURES**

### **✅ Optimizations:**
- **Responsive Design** - Mobile/desktop adaptive
- **Auto-refresh** - 30-second intervals  
- **Connection Monitoring** - Online/offline status
- **Lazy Loading** - Data loaded on demand
- **Cache Management** - Timestamp-based cache busting

### **🎨 UI Features:**
- **Clean Interface** - No icons/emojis per request
- **Keyboard Shortcuts** - Ctrl+F (search), Escape (toggle)
- **Hover Effects** - Interactive feedback
- **Collapsible Controls** - Space optimization
- **Location List** - Detailed view with click-to-zoom

### **🔐 Security:**
- **CSRF Protection** - Django built-in
- **Input Validation** - API parameter validation  
- **Error Handling** - Graceful degradation
- **CORS Ready** - For iframe embedding

Tất cả APIs đã được test và hoạt động ổn định! 🎉