# 🚀 Deploy SiBersih ke Sevalla

Panduan lengkap deployment aplikasi SiBersih Django ke Sevalla hosting.

## 📋 Prerequisites

1. **Akun Sevalla** - Daftar di https://sevalla.com
2. **GitHub Repository** - https://github.com/Glenferdinza/SiBersih.git
3. **Python 3.12** installed locally
4. **MySQL Database** (akan dibuat di Sevalla)

---

## 🔧 Step 1: Persiapan Lokal

### 1.1 Generate SECRET_KEY Baru

```bash
python generate_secret_key.py
```

Copy output SECRET_KEY yang dihasilkan.

### 1.2 Test Locally dengan Production Settings

Buat file `.env` di root project:

```env
SECRET_KEY=<paste-secret-key-from-step-1.1>
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.mysql
DB_NAME=sibersih
DB_USER=root
DB_PASSWORD=asya2105
DB_HOST=localhost
DB_PORT=3306
```

### 1.3 Test Static Files Collection

```bash
python manage.py collectstatic --noinput
```

### 1.4 Test dengan Gunicorn

```bash
gunicorn config.wsgi:application
```

Buka http://localhost:8000 - pastikan aplikasi jalan dengan baik.

---

## 📦 Step 2: Push ke GitHub

### 2.1 Commit Semua Perubahan

```bash
git status
git add .
git commit -m "Prepare for Sevalla deployment - Add production configs"
```

### 2.2 Push ke GitHub

```bash
git push origin main
```

Atau jika branch Anda `master`:

```bash
git push origin master
```

---

## 🌐 Step 3: Setup di Sevalla

### 3.1 Login ke Sevalla Dashboard

1. Login di https://sevalla.com
2. Pilih "Create New Application" atau "Deploy"

### 3.2 Connect GitHub Repository

1. Pilih "GitHub" sebagai deployment method
2. Authorize Sevalla untuk akses GitHub Anda
3. Pilih repository: **Glenferdinza/SiBersih**
4. Pilih branch: **main** (atau master)

### 3.3 Configure Build Settings

**Build Command:**
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**Start Command:**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

**Python Version:** 3.12

---

## 🗄️ Step 4: Setup Database di Sevalla

### 4.1 Create MySQL Database

1. Di Sevalla Dashboard, go to "Databases"
2. Click "Create Database"
3. Select **MySQL**
4. Database Name: **sibersih_production**
5. Create database

### 4.2 Catat Database Credentials

Sevalla akan memberikan:
- **Host**: `mysql-xxx.sevalla.com`
- **Database Name**: `sibersih_production`
- **Username**: `user_xxxxx`
- **Password**: `xxxxxxxxx`
- **Port**: `3306`

---

## ⚙️ Step 5: Configure Environment Variables

Di Sevalla Dashboard, tambahkan Environment Variables:

```
SECRET_KEY=<paste-your-secret-key-here>
DEBUG=False
ALLOWED_HOSTS=.sevalla.com,yourdomain.com

DB_ENGINE=django.db.backends.mysql
DB_NAME=sibersih_production
DB_USER=<from-step-4.2>
DB_PASSWORD=<from-step-4.2>
DB_HOST=<from-step-4.2>
DB_PORT=3306

STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media
```

**PENTING:** Ganti `yourdomain.com` dengan domain actual Anda jika ada.

---

## 🚀 Step 6: Deploy!

### 6.1 Trigger Deployment

Click "Deploy" button di Sevalla dashboard.

Monitor build logs - pastikan tidak ada error.

### 6.2 Run Database Migrations

Setelah deployment selesai, jalankan migrations via Sevalla console:

```bash
python manage.py migrate
```

### 6.3 Create Superuser

```bash
python manage.py createsuperuser
```

Ikuti prompt untuk create admin account.

### 6.4 Load Initial Data (Optional)

Jika ada fixture data:

```bash
python manage.py loaddata partners/fixtures/cod_rates.json
```

---

## ✅ Step 7: Verify Deployment

### 7.1 Test Website

1. Buka URL yang diberikan Sevalla (contoh: `https://sibersih.sevalla.com`)
2. Test halaman home
3. Test login/register
4. Test order flow
5. Test admin panel: `/admin`

### 7.2 Check Logs

Monitor logs di Sevalla dashboard untuk error.

### 7.3 Test Static Files

Pastikan CSS, JavaScript, dan images load dengan benar.

---

## 🔐 Step 8: Security Checklist

- [ ] `DEBUG=False` di production
- [ ] SECRET_KEY unik dan aman
- [ ] Database credentials secure
- [ ] ALLOWED_HOSTS configured correctly
- [ ] SSL/HTTPS enabled (biasanya otomatis di Sevalla)
- [ ] Media files upload tested
- [ ] Admin panel accessible dan secure

---

## 📝 Step 9: Custom Domain (Optional)

Jika Anda punya domain sendiri:

### 9.1 Di Sevalla

1. Go to application settings
2. Add custom domain: `sibersih.com`
3. Sevalla akan kasih DNS records

### 9.2 Di Domain Registrar

Tambahkan DNS records yang diberikan Sevalla:

```
Type: A
Name: @
Value: <sevalla-ip-address>

Type: CNAME
Name: www
Value: <sevalla-cname>
```

### 9.3 Update ALLOWED_HOSTS

```
ALLOWED_HOSTS=.sevalla.com,sibersih.com,www.sibersih.com
```

Redeploy aplikasi.

---

## 🐛 Troubleshooting

### Issue: Static files tidak load

**Solusi:**
```bash
python manage.py collectstatic --noinput --clear
```

### Issue: Database connection error

**Solusi:**
- Check environment variables di Sevalla
- Pastikan DB credentials benar
- Cek IP whitelist di database settings

### Issue: 500 Internal Server Error

**Solusi:**
- Check logs di Sevalla console
- Set `DEBUG=True` temporarily untuk lihat error detail
- Pastikan semua migrations sudah run

### Issue: Media files upload error

**Solusi:**
- Pastikan `MEDIA_ROOT` directory writeable
- Check file upload size limits di Sevalla

---

## 📞 Support

Jika ada masalah:

1. **Sevalla Support**: https://sevalla.com/support
2. **Django Docs**: https://docs.djangoproject.com/en/5.2/howto/deployment/
3. **GitHub Issues**: https://github.com/Glenferdinza/SiBersih/issues

---

## 🎉 Selamat!

Aplikasi SiBersih Anda sekarang live di production! 🚀

**Next Steps:**
- Setup backup strategy
- Monitor application performance
- Setup error tracking (Sentry)
- Configure CDN for static files
- Setup SSL certificate renewal
- Create deployment pipeline (CI/CD)

---

Made with ❤️ by SiBersih Team
