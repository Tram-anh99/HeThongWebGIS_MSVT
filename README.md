# Hệ Thống WebGIS - Mã Số Vùng Trồng (MSVT)

Hệ thống WebGIS quản lý mã số vùng trồng với Frontend Vue 3 và Backend FastAPI.

## 📋 Mục Lục
- [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
- [Cài Đặt](#cài-đặt)
- [Cấu Hình](#cấu-hình)
- [Chạy Dự Án](#chạy-dự-án)
- [Cấu Trúc Dự Án](#cấu-trúc-dự-án)

---

## 🔧 Yêu Cầu Hệ Thống

Trước khi bắt đầu, đảm bảo máy tính của bạn đã cài đặt:

### 1. **PostgreSQL** (với PostGIS)
- PostgreSQL 13+ 
- PostGIS extension

**Cài đặt trên macOS:**
```bash
# Sử dụng Homebrew
brew install postgresql@15 postgis
brew services start postgresql@15
```

**Cài đặt trên Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis
sudo systemctl start postgresql
```

**Cài đặt trên Windows:**
- Tải PostgreSQL từ: https://www.postgresql.org/download/windows/
- Chọn cài đặt PostGIS extension khi cài đặt

### 2. **Python 3.8+**
```bash
# Kiểm tra phiên bản Python
python3 --version
```

### 3. **Node.js 16+** và **npm**
```bash
# Kiểm tra phiên bản
node --version
npm --version
```

**Cài đặt Node.js:**
- macOS: `brew install node`
- Ubuntu/Debian: `sudo apt install nodejs npm`
- Windows: Tải từ https://nodejs.org/

---

## 📥 Cài Đặt

### Bước 1: Clone Repository
```bash
# Clone dự án từ GitHub
git clone https://github.com/Tram-anh99/HeThongWebGIS_MSVT.git

# Di chuyển vào thư mục dự án
cd HeThongWebGIS_MSVT
```

### Bước 2: Thiết Lập Database

#### 2.1. Tạo Database PostgreSQL
```bash
# Di chuyển vào thư mục Database
cd Database

# Chạy script thiết lập database
chmod +x setup-database.sh
./setup-database.sh
```

Script sẽ tự động:
- Tạo database `webgis_msvt`
- Kích hoạt PostGIS extension
- Cấu hình schema

**Lưu ý:** Nếu bạn đã có database với tên `webgis_msvt`, script sẽ hỏi có muốn xóa và tạo lại không.

#### 2.2. Import Dữ Liệu (Nếu có)
```bash
# Nếu có file backup trong thư mục Database/backups
# Kiểm tra các file backup có sẵn
ls -la Database/backups/

# Restore từ file backup (nếu có)
psql -U postgres -d webgis_msvt -f Database/backups/your_backup_file.sql
```

### Bước 3: Cài Đặt Backend (FastAPI)

```bash
# Di chuyển vào thư mục Backend
cd Backend

# Cấp quyền thực thi cho script
chmod +x start_server.sh

# Script sẽ tự động tạo virtual environment và cài đặt dependencies
# Nhưng bạn cũng có thể cài thủ công:
python3 -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Bước 4: Cài Đặt Frontend (Vue 3)

```bash
# Di chuyển vào thư mục Frontend
cd Frontend

# Cài đặt dependencies
npm install
```

---

## ⚙️ Cấu Hình

### Cấu Hình Backend

1. Copy file `.env.example` thành `.env`:
```bash
cd Backend
cp .env.example .env
```

2. Chỉnh sửa file `.env` với thông tin của bạn:
```bash
# Mở file .env và điều chỉnh các giá trị sau
nano .env  # hoặc dùng editor bất kỳ
```

**Các thông số quan trọng cần kiểm tra:**
```env
# Database Settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=webgis_msvt
DB_USER=postgres          # Thay đổi nếu bạn dùng user khác
DB_PASSWORD=postgres      # Thay đổi theo password của bạn
DB_SCHEMA=public

# JWT Settings
JWT_SECRET_KEY=your-secret-key-please-change-this-in-production

# CORS Settings (nếu chạy frontend trên port khác)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🚀 Chạy Dự Án

Có 2 cách để chạy dự án:

### Cách 1: Chạy Tự Động (Khuyến Nghị)

Chạy cả Backend và Frontend cùng lúc:

```bash
# Từ thư mục gốc của dự án
chmod +x start_all.sh
./start_all.sh
```

Hệ thống sẽ tự động khởi động:
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **Frontend:** http://localhost:5173

Nhấn `Ctrl+C` để dừng tất cả servers.

### Cách 2: Chạy Thủ Công

#### Chạy Backend
```bash
# Mở Terminal/Cmd window 1
cd Backend
chmod +x start_server.sh
./start_server.sh
```

Hoặc chạy trực tiếp:
```bash
cd Backend
source venv/bin/activate  # Trên Windows: venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Chạy Frontend
```bash
# Mở Terminal/Cmd window 2
cd Frontend
chmod +x start_frontend.sh
./start_frontend.sh
```

Hoặc chạy trực tiếp:
```bash
cd Frontend
npm run dev
```

---

## 📁 Cấu Trúc Dự Án

```
HeThongWebGIS_MSVT/
├── Backend/                 # FastAPI Backend
│   ├── models/             # SQLAlchemy Models
│   ├── routes/             # API Routes
│   ├── schemas/            # Pydantic Schemas
│   ├── utils/              # Utility functions
│   ├── main.py             # FastAPI Application
│   ├── database.py         # Database connection
│   ├── config.py           # Configuration
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   └── start_server.sh     # Script khởi động backend
│
├── Frontend/               # Vue 3 Frontend
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   ├── package.json       # Node dependencies
│   └── start_frontend.sh  # Script khởi động frontend
│
├── Database/              # Database files
│   ├── data/             # CSV/GeoJSON data files
│   ├── scripts/          # Database scripts
│   ├── backups/          # Backup files
│   ├── migrations/       # Migration files
│   └── setup-database.sh # Script thiết lập database
│
├── docs/                 # Documentation
├── scripts/              # Utility scripts
└── start_all.sh          # Script khởi động toàn bộ hệ thống
```

---

## 🔍 Kiểm Tra Hệ Thống

### Kiểm tra Backend
```bash
# Kiểm tra API đang chạy
curl http://localhost:8000

# Mở API documentation
open http://localhost:8000/docs  # macOS
# hoặc truy cập: http://localhost:8000/docs trong browser
```

### Kiểm tra Frontend
Truy cập http://localhost:5173 trong trình duyệt.

### Kiểm tra Database
```bash
# Kết nối vào PostgreSQL
psql -U postgres -d webgis_msvt

# Kiểm tra tables
\dt

# Kiểm tra PostGIS
SELECT PostGIS_Version();

# Thoát
\q
```

---

## ❗ Xử Lý Lỗi Thường Gặp

### Lỗi 1: PostgreSQL connection refused
**Nguyên nhân:** PostgreSQL chưa được khởi động.

**Giải pháp:**
```bash
# macOS
brew services start postgresql@15

# Ubuntu/Debian
sudo systemctl start postgresql

# Kiểm tra trạng thái
pg_isready -U postgres
```

### Lỗi 2: Port 8000 hoặc 5173 đã được sử dụng
**Giải pháp:**
```bash
# Tìm process đang sử dụng port
lsof -i :8000  # hoặc :5173

# Kill process
kill -9 <PID>
```

### Lỗi 3: ModuleNotFoundError (Python)
**Giải pháp:**
```bash
cd Backend
source venv/bin/activate
pip install -r requirements.txt
```

### Lỗi 4: npm install failed
**Giải pháp:**
```bash
cd Frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Lỗi 5: Database authentication failed
Kiểm tra lại username/password trong file `Backend/.env`:
```bash
# Chỉnh sửa file .env
nano Backend/.env

# Đảm bảo DB_USER và DB_PASSWORD đúng với PostgreSQL của bạn
```

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra logs trong terminal
2. Xem API docs tại http://localhost:8000/docs
3. Kiểm tra file `.env` đã được cấu hình đúng chưa
4. Đảm bảo PostgreSQL, Python, và Node.js đã được cài đặt đúng phiên bản

---

## 📝 Lưu Ý

- **Môi trường Development:** Các script `start_*.sh` được thiết kế cho môi trường phát triển với hot-reload
- **Production:** Cần build frontend (`npm run build`) và cấu hình server production cho backend
- **Security:** Nhớ thay đổi `JWT_SECRET_KEY` trong file `.env` trước khi deploy production
- **Data Files:** Các file dữ liệu CSV/GeoJSON lớn nằm trong `Database/data/` sẽ không được đẩy lên GitHub (đã được gitignore)

---

## 🎯 Bắt Đầu Nhanh

**TL;DR - Chạy ngay sau khi clone:**

```bash
# 1. Clone repo
git clone https://github.com/Tram-anh99/HeThongWebGIS_MSVT.git
cd HeThongWebGIS_MSVT

# 2. Setup database
cd Database && chmod +x setup-database.sh && ./setup-database.sh && cd ..

# 3. Cấu hình Backend
cd Backend && cp .env.example .env && cd ..
# (Chỉnh sửa Backend/.env nếu cần)

# 4. Chạy toàn bộ hệ thống
chmod +x start_all.sh
./start_all.sh
```

Truy cập:
- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/docs

---

**Chúc bạn code vui vẻ! 🚀**
