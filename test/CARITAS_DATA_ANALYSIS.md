# 🛠️ Caritas Data Processing Tool

## 📊 **Phân tích dữ liệu Caritas:**

Từ API: `https://www.caritas.de/Services/MappingService.svc/GetMapContents/...`

### **Cấu trúc dữ liệu hiện có:**

```json
{
  "Contents": [
    {
      "ContentID": "...",
      "Title": "...",
      "Latitude": 51.04707,
      "Longitude": 13.7592301,
      "Contents": "HTML content with details",
      "Popup": "HTML for map popup",
      "DataSourceID": "..."
    }
  ],
  "Count": 10,
  "Page": 0,
  "PageCount": 52,
  "TotalCount": 516
}
```

### **🎯 Mục tiêu chuyển đổi thành 3 tầng:**

#### **TẦNG 1 - DOMAIN:**
- **Domain ID:** `caritas_deutschland`
- **Name:** `Caritas Deutschland`
- **Description:** `Các dịch vụ xã hội và tư vấn di cư của Caritas`

#### **TẦNG 2 - CATEGORIES:**
Dựa trên `<h2 class="kicker">` trong HTML content:
- `jugendmigrationsdienst` - Jugendmigrationsdienst
- `migrationsberatung_erwachsene` - Migrationsberatung für Erwachsene
- `migrationsberatung` - Migrationsberatung
- `gemeinwesenorientierte_arbeit` - Gemeinwesenorientierte Arbeit
- `iq_faire_integration` - IQ - Faire Integration
- `beratungszentrum` - Beratungszentrum
- `fluechtlingsberatung` - Flüchtlings- und Migrationsberatung

#### **TẦNG 3 - LOCATIONS:**
Mỗi địa điểm từ API với:
- **Coordinates:** Latitude, Longitude
- **Name:** Title từ JSON
- **Address:** Parse từ HTML content  
- **Phone/Email:** Parse từ HTML content
- **Categories:** Xác định từ service type

### **🔧 Kế hoạch xử lý:**

1. **Download toàn bộ data** (516 records, 52 pages)
2. **Parse HTML content** để trích xuất thông tin
3. **Phân loại categories** theo service type
4. **Chuẩn hóa địa chỉ** và thông tin liên hệ
5. **Generate Django fixtures** để import vào database