# Setup Guide untuk SiBersih

## Langkah-langkah Setup Database MySQL

1. Pastikan MySQL Server sudah berjalan di port 3306

2. Buat database dengan nama `sibersih`:

Buka MySQL Command Line atau MySQL Workbench, lalu jalankan:

```sql
CREATE DATABASE sibersih CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. Update password MySQL di file `config/settings.py`:

Cari bagian DATABASES dan ubah PASSWORD sesuai dengan password MySQL Anda:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sibersih',
        'USER': 'root',
        'PASSWORD': 'YOUR_MYSQL_PASSWORD_HERE',  # <-- Ubah ini
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}
```

4. Aktifkan virtual environment (jika belum):

```bash
.venv\Scripts\Activate.ps1
```

5. Jalankan migrasi database:

```bash
python manage.py migrate
```

6. Buat superuser untuk admin:

```bash
python manage.py createsuperuser
```

Ikuti instruksi untuk membuat username, email, dan password admin.

7. Setup data awal (services):

```bash
python manage.py setup_initial_data
```

8. Jalankan server:

```bash
python manage.py runserver
```

9. Akses website di browser:

- Homepage: http://127.0.0.1:8000
- Admin Panel: http://127.0.0.1:8000/admin

## Troubleshooting

### Error: Access denied for user 'root'@'localhost'

Pastikan password MySQL sudah diupdate dengan benar di `config/settings.py`

### Error: Unknown database 'sibersih'

Buat database terlebih dahulu dengan perintah SQL di langkah 2

### Error: mysqlclient installation failed

Untuk Windows, download dan install Visual C++ Build Tools atau install precompiled mysqlclient

## Struktur User Roles

1. User (default): Bisa pesan laundry, track pesanan, lihat riwayat
2. Mitra: Bisa kelola pesanan yang masuk, update status
3. Admin: Akses penuh ke semua fitur termasuk approval mitra

## Cara Mengubah User Menjadi Admin

Setelah membuat user baru, Anda bisa mengubahnya menjadi admin melalui Django admin panel:

1. Login ke http://127.0.0.1:8000/admin
2. Klik "Users"
3. Pilih user yang ingin diubah
4. Ubah field "Role" menjadi "Admin"
5. Centang "Staff status" dan "Superuser status" jika diperlukan
6. Save

## Email Configuration (Optional)

Untuk mengaktifkan email notification saat pendaftaran mitra, update di `config/settings.py`:

```python
EMAIL_HOST_USER = 'contact.sibersih@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password_here'
```

Note: Untuk Gmail, gunakan App Password bukan password biasa.
