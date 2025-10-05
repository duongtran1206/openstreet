# 🧪 Tests Directory

Thư mục này chứa tất cả các file test được tổ chức gọn gàng theo chức năng.

## 📁 Cấu trúc thư mục:

### **📂 `/tests/api/`**
Chứa các test liên quan đến API endpoints:
- `test_api.py` - Test basic API functionality
- `test_geojson.py` - Test GeoJSON API logic

### **📂 `/tests/hierarchical/`** 
Chứa các test cho hệ thống hierarchical map:
- `test_hierarchical_demo.py` - Demo hierarchical system

### **📂 `/tests/embed/`**
Chứa các test cho tính năng embed:
- `embed_test.html` - Demo trang embed trong iframe

### **📂 `/tests/temp/`**
Thư mục tạm thời cho các file test không cần thiết

## 🚀 Cách sử dụng:

### **Chạy test API:**
```bash
cd tests/api
python test_api.py
python test_geojson.py
```

### **Xem demo hierarchical:**
```bash
cd tests/hierarchical  
python test_hierarchical_demo.py
```

### **Test embed:**
- Mở trực tiếp: `http://127.0.0.1:8000/embed-test/`
- Hoặc file local: `tests/embed/embed_test.html`

## 📝 Ghi chú:

- Tất cả test cần Django server chạy ở `127.0.0.1:8000`
- Đảm bảo database có dữ liệu hierarchical
- API endpoints phải hoạt động bình thường

## 🔧 Maintenance:

- ✅ **Đã dọn dẹp:** Files test được tổ chức theo chức năng
- ✅ **Cấu trúc rõ ràng:** Dễ tìm kiếm và bảo trì
- ✅ **Tách biệt:** Mỗi loại test có thư mục riêng