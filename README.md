# SiBersih

SiBersih adalah sistem manajemen laundry berbasis web yang dibangun menggunakan Django. Website ini menyediakan platform modern untuk mengelola pesanan laundry dengan fitur tracking real-time, sistem mitra, dan dashboard interaktif.

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
