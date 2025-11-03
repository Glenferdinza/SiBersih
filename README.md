# 🧺 SiBersih - Sistem Manajemen Laundry

[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

SiBersih adalah sistem manajemen laundry berbasis web yang dibangun menggunakan Django. Platform modern untuk mengelola pesanan laundry dengan fitur tracking real-time, sistem mitra, dan dashboard interaktif.

**🌐 Live Demo:** [sibersih-app.azurewebsites.net](https://sibersih-app.azurewebsites.net) *(coming soon)*

---

## ✨ Fitur Utama

### 👥 User Features
- ✅ Pemesanan laundry online dengan berbagai jenis layanan
- 📍 Pencarian laundry terdekat berdasarkan lokasi
- 📊 Tracking pesanan real-time dengan timeline status
- 💳 Multiple payment methods (COD, Transfer Bank, QRIS)
- 🎟️ Sistem voucher dan diskon
- ⭐ Review dan rating laundry
- 📱 Responsive design untuk mobile & desktop

### 🏪 Mitra Features
- 📝 Pendaftaran mitra dengan approval system
- 📦 Kelola pesanan masuk
- 🖼️ Upload foto laundry (max 15 gambar)
- 💰 Tracking pendapatan dan statistik
- 🎫 Request voucher untuk promosi
- 📈 Dashboard dengan analytics

### 👨‍💼 Admin Features
- ✅ Approve/reject pendaftaran mitra
- 🎫 Approve voucher requests
- 📊 Monitoring semua transaksi
- 👥 User management
- 📈 Laporan dan statistik keseluruhan

---

## 🛠️ Teknologi

| Stack | Technology |
|-------|-----------|
| **Backend** | Django 5.2.7 |
| **Database** | MySQL 8.0 / Azure MySQL |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Maps** | Leaflet.js (OpenStreetMap) |
| **Styling** | Custom CSS with Clean Aqua Theme |
| **Deployment** | Azure Web App + WhiteNoise |
| **Image Processing** | Pillow |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ ([Download](https://www.python.org/downloads/))
- MySQL 8.0+ ([Download](https://dev.mysql.com/downloads/))
- Git ([Download](https://git-scm.com/downloads/))

### Installation

1. **Clone repository**
```bash
git clone https://github.com/Glenferdinza/SiBersih.git
cd SiBersih
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create MySQL database**
```sql
CREATE DATABASE sibersih CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. **Configure environment**
```bash
cp .env.example .env
# Edit .env dengan database credentials Anda
```

6. **Run migrations**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Run development server**
```bash
python manage.py runserver
```

9. **Access the app**
- Website: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8000/admin

---

## 📁 Project Structure

```
SiBersih/
├── accounts/          # User authentication & profiles
├── core/              # Homepage & dashboards
├── orders/            # Order management
├── partners/          # Partner/Mitra system
├── vouchers/          # Voucher management
├── config/            # Django settings
├── static/            # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
├── templates/         # HTML templates
├── media/             # User uploads
├── staticfiles/       # Collected static files
├── .env.example       # Environment template
├── requirements.txt   # Python dependencies
├── manage.py
├── startup.sh         # Azure startup script
└── AZURE_DEPLOYMENT.md  # Deployment guide
```

---

## 🌐 Deployment ke Azure

Kami menyediakan panduan lengkap untuk deploy ke Azure Web App:

📖 **[Baca Panduan Deployment](AZURE_DEPLOYMENT.md)**

### Quick Deploy
```bash
# Login to Azure
az login

# Deploy dengan Azure CLI
az webapp up \
  --name sibersih-app \
  --resource-group sibersih-rg \
  --runtime "PYTHON:3.12" \
  --sku B1
```

---

## 🧪 Testing

### Run Tests
```bash
python manage.py test
```

### Test Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 📊 Database Schema

### Main Models
- **User** (Custom user model dengan roles)
- **Laundry** (Partner laundry info)
- **Order** (Pesanan laundry)
- **Review** (Rating & review)
- **Voucher** (Discount vouchers)
- **Payment** (Payment tracking)

---

## 🎨 Design System

### Color Palette
- **Primary:** `#14b8a6` (Teal)
- **Secondary:** `#0d9488` (Dark Teal)
- **Accent:** `#f59e0b` (Amber)
- **Background:** `#f8fafc` (Light Gray)
- **Text:** `#0f172a` (Dark Blue)

### Typography
- **Headings:** Bold 700-800
- **Body:** Regular 400-600
- **Font:** System fonts (optimal performance)

---

## 🔒 Security Features

- ✅ CSRF Protection
- ✅ XSS Prevention
- ✅ SQL Injection Protection (Django ORM)
- ✅ Secure Password Hashing (PBKDF2)
- ✅ File Upload Validation
- ✅ Role-based Access Control
- ✅ HTTPS Enforcement (Production)
- ✅ Security Headers Middleware

---

## 📝 Environment Variables

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Database
DB_NAME=sibersih
DB_USER=your-username
DB_PASSWORD=your-password
DB_HOST=your-host
DB_PORT=3306
DB_SSL=True
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 👨‍💻 Authors

**SiBersih Development Team**
- GitHub: [@Glenferdinza](https://github.com/Glenferdinza)

---

## 🆘 Support

- 📧 Email: contact.sibersih@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/Glenferdinza/SiBersih/issues)
- 📚 Docs: [Wiki](https://github.com/Glenferdinza/SiBersih/wiki)

---

## 🙏 Acknowledgments

- Django Framework
- OpenStreetMap & Leaflet.js
- Azure Cloud Platform
- MySQL Database

---

**⭐ Star this repo if you find it helpful!**

## Fitur Utama

- Sistem autentikasi user dengan role (User, Mitra, Admin)
- Pemesanan laundry online dengan berbagai jenis layanan
- Tracking pesanan real-time dengan timeline status
- Dashboard khusus untuk User, Mitra, dan Admin
- Sistem pendaftaran mitra dengan approval admin
- Responsive design dengan Clean Aqua color theme
- Scroll-driven animations menggunakan GSAP
- Integrasi MySQL database
- Email notification untuk pendaftaran mitra

## Teknologi

- Backend: Django 5.2.7
- Database: MySQL 8.4.3
- Frontend: HTML5, CSS3, JavaScript
- Animation: GSAP & ScrollTrigger
- Image Processing: Pillow

## Instalasi

### Prerequisites

- Python 3.8 atau lebih tinggi
- MySQL Server 8.4.3
- Git

### Langkah Instalasi

1. Clone repository

```bash
git clone <repository-url>
cd Django
```

2. Buat dan aktifkan virtual environment

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Konfigurasi database

Buat database MySQL dengan nama `sibersih`:

```sql
CREATE DATABASE sibersih;
```

5. Update konfigurasi database di `config/settings.py` jika diperlukan

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sibersih',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

6. Jalankan migrasi

```bash
python manage.py migrate
```

7. Buat superuser untuk admin

```bash
python manage.py createsuperuser
```

8. Buat data services awal (opsional)

```bash
python manage.py shell
```

```python
from orders.models import Service
Service.objects.create(name="Cuci Setrika", description="Layanan cuci dan setrika lengkap", base_price=8000, unit="kg")
Service.objects.create(name="Dry Clean", description="Pembersihan kering untuk pakaian khusus", base_price=15000, unit="pcs")
Service.objects.create(name="Cuci Ekspres", description="Layanan cuci cepat dalam 24 jam", base_price=12000, unit="kg")
exit()
```

9. Jalankan development server

```bash
python manage.py runserver
```

10. Akses website di `http://127.0.0.1:8000`

## Struktur Project

```
Django/
├── .venv/
├── accounts/          # App untuk autentikasi dan user management
├── core/              # App untuk homepage dan dashboards
├── orders/            # App untuk manajemen pesanan
├── partners/          # App untuk sistem mitra
├── config/            # Konfigurasi Django project
├── static/            # File CSS, JS, images
├── templates/         # Template HTML
├── media/             # User uploaded files
└── manage.py
```

## Quick Start

Untuk memudahkan setup, Anda bisa menggunakan script otomatis:

```bash
run_server.bat
```

Script ini akan:
- Mengaktifkan virtual environment
- Install dependencies
- Menjalankan migrasi
- Setup data awal
- Menjalankan server

Atau lihat `SETUP_GUIDE.md` untuk panduan lengkap step-by-step.

## Penggunaan

### User

1. Daftar akun baru atau login
2. Buat pesanan laundry melalui menu "Pesan Laundry"
3. Lacak status pesanan secara real-time
4. Lihat riwayat transaksi

### Mitra

1. Daftar sebagai mitra melalui halaman pendaftaran
2. Tunggu approval dari admin
3. Kelola pesanan yang masuk
4. Update status pesanan
5. Lihat statistik dan pendapatan

### Admin

1. Login ke admin panel di `/admin`
2. Kelola user, mitra, dan pesanan
3. Approve/reject pendaftaran mitra
4. Lihat laporan dan statistik keseluruhan

## Created By

SiBersih Development Team

## License

MIT Licensed

Copyright 2025 SiBersih

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files, to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
