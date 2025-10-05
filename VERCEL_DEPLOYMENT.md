# Hướng dẫn Deploy Django lên Vercel

## Bước 1: Cài đặt Vercel CLI

Mở PowerShell và chạy lệnh:
```powershell
npm install -g vercel
```

## Bước 2: Đăng nhập Vercel

```powershell
vercel login
```

Chọn cách đăng nhập (GitHub, GitLab, Bitbucket, hoặc Email)

## Bước 3: Deploy dự án

Trong thư mục dự án, chạy:
```powershell
cd "c:\Users\Uyen\Documents\geomap\openstreet"
vercel
```

Khi được hỏi:
- **Set up and deploy**: Chọn `Y`  
- **Which scope**: Chọn scope của bạn
- **Link to existing project**: Chọn `N`
- **What's your project's name**: Nhập tên (vd: `geomap-openstreet`)
- **In which directory**: Chọn `./` (thư mục hiện tại)
- **Want to override settings**: Chọn `N`

## Bước 4: Thiết lập Environment Variables

Sau khi deploy, truy cập Vercel Dashboard để thêm biến môi trường:
- `SECRET_KEY`: Tạo secret key mới cho production
- `DEBUG`: Đặt `False`

## Bước 5: Redeploy với settings mới

```powershell
vercel --prod
```

## Files đã tạo sẵn:

1. **vercel.json**: Cấu hình Vercel cho Django
2. **build_files.sh**: Script build static files  
3. **vercel_settings.py**: Settings tối ưu cho production
4. **wsgi.py**: Đã cập nhật để dùng vercel_settings

## Lưu ý:
- Database SQLite sẽ reset sau mỗi lần deploy (Vercel serverless)
- Cần migrate dữ liệu mỗi lần deploy hoặc dùng external database
- Static files sẽ được serve từ Vercel CDN

## Sau khi deploy thành công:
Vercel sẽ cung cấp URL như: `https://your-project.vercel.app`

URL embed sẽ là: `https://your-project.vercel.app/embed/`