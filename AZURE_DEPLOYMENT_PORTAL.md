# 🌐 SiBersih - Azure Deployment via Portal (GUI)

Panduan lengkap deploy SiBersih ke Azure menggunakan Azure Portal (Web Browser) - **Lebih Mudah untuk Pemula!**

---

## 📋 Yang Anda Butuhkan

1. ✅ **Akun Microsoft/Azure** - Sudah Anda punya (glenferdinzaaghis.2024@student.uny.ac.id)
2. ✅ **Repository GitHub** - Sudah siap (https://github.com/Glenferdinza/SiBersih)
3. ✅ **Browser** - Chrome, Edge, atau Firefox
4. ⏱️ **Waktu** - Sekitar 30-45 menit

---

## 🚀 STEP-BY-STEP DEPLOYMENT

---

## 📦 PART 1: Buat MySQL Database (15 menit)

### Step 1.1: Login ke Azure Portal

1. Buka browser, kunjungi: **https://portal.azure.com**
2. Login dengan akun: `glenferdinzaaghis.2024@student.uny.ac.id`
3. Jika ada warning "Device management", klik **OK** (tidak masalah)

### Step 1.2: Create Resource Group

1. Di Azure Portal, klik **"Create a resource"** (pojok kiri atas)
2. Search: **"Resource Group"** → Klik **Create**
3. Isi form:
   ```
   Subscription: [Pilih subscription Anda]
   Resource group name: sibersih-rg
   Region: Southeast Asia (Singapore)
   ```
4. Klik **Review + Create** → **Create**
5. Tunggu ~10 detik sampai muncul "Deployment complete"

### Step 1.3: Create MySQL Database

1. Klik **"Create a resource"** lagi
2. Search: **"Azure Database for MySQL Flexible Server"**
3. Klik **Create** → Pilih **Flexible server**

**BASICS TAB:**
```
Subscription: [Subscription Anda]
Resource group: sibersih-rg
Server name: sibersih-mysql-server
Region: Southeast Asia
MySQL version: 8.0.21
Workload type: Development (untuk testing)
   atau: Production (untuk live)

Compute + storage: Klik Configure server
  → Pilih "Burstable" (paling murah)
  → Compute size: Standard_B1ms (1 vCore, 2 GiB)
  → Storage: 32 GiB
  → Klik Save
```

**AUTHENTICATION TAB:**
```
Authentication method: MySQL authentication only
Admin username: adminuser
Password: SiBersih2024!Strong
Confirm password: SiBersih2024!Strong
```

⚠️ **PENTING:** Simpan password ini! Akan dibutuhkan nanti.

**NETWORKING TAB:**
```
Connectivity method: Public access (allowed IP addresses)
Firewall rules:
  ✅ Allow public access from any Azure service
  ✅ Add current client IP address (centang ini)
```

4. Klik **Review + Create** → **Create**
5. ⏳ Tunggu **10-15 menit** (MySQL provisioning memakan waktu lama)
6. Setelah selesai, klik **Go to resource**

### Step 1.4: Create Database (sibersih)

1. Dari MySQL server page, di menu kiri klik **"Databases"**
2. Klik **"+ Add"**
3. Database name: **sibersih**
4. Charset: **utf8mb4**
5. Collation: **utf8mb4_unicode_ci**
6. Klik **Save**

### Step 1.5: Catat Connection String

1. Di MySQL server page, klik **"Connect"** (menu kiri)
2. Copy informasi berikut (simpan di Notepad):
   ```
   Server name: sibersih-mysql-server.mysql.database.azure.com
   Username: adminuser
   Password: SiBersih2024!Strong
   Database: sibersih
   Port: 3306
   ```

✅ **MySQL Database sudah siap!**

---

## 🌐 PART 2: Deploy Web App (15 menit)

### Step 2.1: Create Web App

1. Klik **"Create a resource"**
2. Search: **"Web App"** → Klik **Create**

**BASICS TAB:**
```
Subscription: [Subscription Anda]
Resource group: sibersih-rg
Name: sibersih-app
   (Catatan: Harus unik global. Jika sibersih-app sudah terpakai,
    coba: sibersih-app-glen atau sibersih-app-2024)

Publish: Code
Runtime stack: Python 3.12
Operating System: Linux
Region: Southeast Asia

Pricing plans:
  Linux Plan: Klik Create new → Nama: sibersih-plan
  Pricing plan: Klik Change size
    → Pilih "Dev/Test" tab
    → Pilih "B1" (Basic) - ~$13/month
    → Atau "F1" (Free) untuk testing - $0/month
    → Klik Apply
```

**DEPLOYMENT TAB:**
```
GitHub Actions settings:
  Continuous deployment: Enable
  
  GitHub account:
    → Klik Authorize
    → Login GitHub dengan akun Glenferdinza
    → Authorize Azure App Service
  
  Organization: Glenferdinza
  Repository: SiBersih
  Branch: master
```

⚠️ **PENTING:** Jika diminta authorize GitHub, klik **Authorize** dan login.

**NETWORKING TAB:**
```
Enable public access: Yes
```

**MONITORING TAB:**
```
Enable Application Insights: Yes (recommended)
  Application Insights Name: sibersih-insights
  Region: Southeast Asia
```

3. Klik **Review + Create** → **Create**
4. ⏳ Tunggu **3-5 menit**
5. Setelah selesai, klik **Go to resource**

### Step 2.2: Configure Environment Variables

1. Di Web App page, menu kiri klik **"Configuration"**
2. Di tab **Application settings**, klik **"+ New application setting"**
3. Tambahkan satu per satu:

**Setting 1:**
```
Name: SECRET_KEY
Value: [Generate baru - lihat cara di bawah]
```

**Cara Generate SECRET_KEY:**
- Buka terminal PowerShell di folder project
- Jalankan: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- Copy hasil output dan paste ke Value

**Setting 2:**
```
Name: DEBUG
Value: False
```

**Setting 3:**
```
Name: ALLOWED_HOSTS
Value: sibersih-app.azurewebsites.net
```
(Ganti `sibersih-app` dengan nama app Anda jika berbeda)

**Setting 4:**
```
Name: DB_NAME
Value: sibersih
```

**Setting 5:**
```
Name: DB_USER
Value: adminuser
```

**Setting 6:**
```
Name: DB_PASSWORD
Value: SiBersih2024!Strong
```

**Setting 7:**
```
Name: DB_HOST
Value: sibersih-mysql-server.mysql.database.azure.com
```

**Setting 8:**
```
Name: DB_PORT
Value: 3306
```

**Setting 9:**
```
Name: DB_SSL
Value: True
```

**Setting 10:**
```
Name: SCM_DO_BUILD_DURING_DEPLOYMENT
Value: true
```

**Setting 11:**
```
Name: WEBSITES_PORT
Value: 8000
```

4. Setelah semua setting ditambahkan, klik **Save** (atas)
5. Klik **Continue** pada konfirmasi restart

### Step 2.3: Configure Startup Command

1. Di menu kiri, klik **"Configuration"**
2. Tab **General settings**
3. Scroll ke **Startup Command**
4. Isi dengan: `startup.sh`
5. Klik **Save** (atas)

✅ **Web App Configuration sudah siap!**

---

## 🔄 PART 3: Deploy & Verify (10 menit)

### Step 3.1: Trigger Deployment

Deployment seharusnya otomatis berjalan karena kita enable GitHub Actions.

**Cara Cek Status Deployment:**

1. Di Web App page, menu kiri klik **"Deployment Center"**
2. Lihat tab **Logs**
3. Anda akan lihat deployment dari GitHub Actions
4. Status bisa: **Building** → **Running** → **Success** (atau **Failed** jika error)
5. ⏳ Tunggu ~5-10 menit sampai status **Success**

**Atau cek di GitHub:**
1. Buka: https://github.com/Glenferdinza/SiBersih
2. Klik tab **Actions**
3. Lihat workflow yang sedang running
4. Tunggu sampai ✅ hijau (success)

### Step 3.2: Run Database Migration

Setelah deployment sukses:

1. Di Web App page, menu kiri klik **"SSH"** atau **"Advanced Tools"** → **"Go"**
2. Di Kudu console, klik **SSH** atau **Debug console** → **SSH**
3. Jalankan command berikut:

```bash
cd /home/site/wwwroot
python -m venv antenv
source antenv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

**Atau lebih sederhana (jika startup.sh sudah jalan):**
```bash
cd /home/site/wwwroot
python manage.py migrate
python manage.py createsuperuser
```

Isi superuser:
```
Username: admin
Email: admin@sibersih.com
Password: Admin123!Strong
Password (again): Admin123!Strong
```

### Step 3.3: Restart Web App

1. Kembali ke Web App page
2. Klik **Restart** (toolbar atas)
3. Klik **Yes** untuk confirm
4. Tunggu ~30 detik

### Step 3.4: Test Website!

1. Buka browser baru
2. Kunjungi: **https://sibersih-app.azurewebsites.net**
   (Ganti dengan nama app Anda)

**Yang harus muncul:**
- ✅ Homepage SiBersih tampil normal
- ✅ Tidak ada error 500/404
- ✅ Styling (CSS) muncul
- ✅ Bisa klik menu navigasi

**Test Admin:**
- URL: **https://sibersih-app.azurewebsites.net/admin**
- Login dengan superuser tadi
- ✅ Admin panel harus bisa diakses

### Step 3.5: Test Registration & Login

1. Klik **Daftar** di website
2. Buat akun baru (user biasa)
3. Login dengan akun tersebut
4. ✅ Dashboard user harus muncul

---

## 🎉 DEPLOYMENT COMPLETE!

Your live website: **https://sibersih-app.azurewebsites.net**

---

## 📊 Monitoring & Maintenance

### View Logs

1. Di Web App page, menu kiri klik **"Log stream"**
2. Atau klik **"Diagnose and solve problems"**

### Check Metrics

1. Menu kiri klik **"Metrics"**
2. Lihat:
   - Response time
   - Request count
   - Errors
   - CPU/Memory usage

### Application Insights

1. Menu kiri klik **"Application Insights"**
2. View:
   - Live metrics
   - Failures
   - Performance
   - Users analytics

---

## 🐛 Troubleshooting

### Problem 1: Website shows "Application Error"

**Solution:**
1. Klik **Log stream** untuk lihat error
2. Pastikan semua environment variables sudah benar
3. Pastikan `startup.sh` ada dan executable
4. Restart Web App

### Problem 2: Static files (CSS) tidak muncul

**Solution:**
1. SSH ke web app
2. Jalankan: `python manage.py collectstatic --noinput`
3. Restart app

### Problem 3: Database connection error

**Solution:**
1. Cek MySQL firewall rules
2. Pastikan DB_HOST, DB_USER, DB_PASSWORD benar
3. Pastikan MySQL server running
4. Test connection dari SSH console:
   ```bash
   mysql -h sibersih-mysql-server.mysql.database.azure.com -u adminuser -p sibersih
   ```

### Problem 4: GitHub Actions deployment failed

**Solution:**
1. Buka GitHub → Actions → Lihat error log
2. Biasanya karena requirements.txt error
3. Fix di local, push ke GitHub
4. Deployment akan auto-retry

---

## 🔄 Update Aplikasi

Setiap kali Anda push ke GitHub master branch, deployment otomatis terjadi!

```bash
# Di local
git add .
git commit -m "Update feature"
git push origin master

# Azure akan auto-deploy dalam 5-10 menit
```

---

## 💰 Cost Management

### Current Setup Cost (~$25/month)
- Web App (B1): ~$13/month
- MySQL (B1ms): ~$12/month
- Application Insights: Free tier

### Reduce Cost (Free Tier for Testing)
1. Web App → Scale up → F1 Free ($0)
2. MySQL → Compute + Storage → Burstable B1s ($7/month)
   
**Total Free/Minimal:** $0-7/month

### Stop Resources (When Not Using)
1. Web App → **Stop**
2. MySQL → **Stop** (tidak dikenakan biaya saat stopped)

---

## 🔒 Security Checklist

- [x] ✅ DEBUG = False
- [x] ✅ SECRET_KEY unique dan strong
- [x] ✅ MySQL password strong
- [x] ✅ HTTPS enabled (otomatis dari Azure)
- [x] ✅ Database SSL enabled
- [ ] ⏳ Setup custom domain (optional)
- [ ] ⏳ Enable Azure AD authentication (optional)

---

## 📚 Resources

- **Your Web App:** https://portal.azure.com → App Services → sibersih-app
- **Your Database:** https://portal.azure.com → Azure Database for MySQL → sibersih-mysql-server
- **GitHub Repo:** https://github.com/Glenferdinza/SiBersih
- **Azure Documentation:** https://learn.microsoft.com/en-us/azure/app-service/

---

## 🆘 Need Help?

1. **Check Logs:** Web App → Log stream
2. **Diagnose Issues:** Web App → Diagnose and solve problems
3. **Azure Support:** Portal → Help + support
4. **GitHub Issues:** https://github.com/Glenferdinza/SiBersih/issues

---

**🎊 Congratulations! SiBersih is now live on Azure!** 🎊

**Share your link:** `https://sibersih-app.azurewebsites.net`
