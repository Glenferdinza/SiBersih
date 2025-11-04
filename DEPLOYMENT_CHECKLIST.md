# 📋 SiBersih Azure Deployment - Quick Checklist

Gunakan checklist ini saat deploy via Azure Portal.

---

## ✅ PRE-DEPLOYMENT CHECKLIST

- [ ] Akun Azure sudah login (https://portal.azure.com)
- [ ] Repository GitHub sudah ter-push (https://github.com/Glenferdinza/SiBersih)
- [ ] Punya waktu 30-45 menit
- [ ] Siapkan Notepad untuk catat credentials

---

## 📦 PART 1: MySQL DATABASE (15 min)

### ☑️ Step 1: Resource Group
```
Portal → Create a resource → Resource Group
Nama: sibersih-rg
Region: Southeast Asia
→ Create
```

### ☑️ Step 2: MySQL Server (⏳ 10-15 menit)
```
Portal → Create a resource → Azure Database for MySQL Flexible Server

BASICS:
  Server name: sibersih-mysql-server
  Region: Southeast Asia
  MySQL version: 8.0.21
  Compute: Burstable B1ms (1 vCore, 2 GiB)
  Storage: 32 GiB

AUTHENTICATION:
  Username: adminuser
  Password: SiBersih2024!Strong
  ⚠️ SIMPAN PASSWORD INI!

NETWORKING:
  ✅ Allow public access from any Azure service
  ✅ Add current client IP address

→ Create (tunggu 10-15 menit)
```

### ☑️ Step 3: Create Database
```
MySQL server → Databases → + Add
Name: sibersih
Charset: utf8mb4
Collation: utf8mb4_unicode_ci
→ Save
```

### ☑️ Step 4: Catat Connection Info
```
📝 SIMPAN DI NOTEPAD:
Server: sibersih-mysql-server.mysql.database.azure.com
Username: adminuser
Password: SiBersih2024!Strong
Database: sibersih
Port: 3306
```

---

## 🌐 PART 2: WEB APP (15 min)

### ☑️ Step 5: Create Web App
```
Portal → Create a resource → Web App

BASICS:
  Name: sibersih-app (atau sibersih-app-glen jika sudah terpakai)
  Publish: Code
  Runtime: Python 3.12
  OS: Linux
  Region: Southeast Asia
  Plan: B1 Basic (~$13/mo) atau F1 Free ($0)

DEPLOYMENT:
  ✅ Enable continuous deployment
  GitHub account: Authorize → Login Glenferdinza
  Repo: SiBersih
  Branch: master

MONITORING:
  ✅ Enable Application Insights

→ Create (tunggu 3-5 menit)
```

### ☑️ Step 6: Environment Variables (11 settings)
```
Web App → Configuration → Application settings → + New

1. SECRET_KEY = [Generate: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"]
2. DEBUG = False
3. ALLOWED_HOSTS = sibersih-app.azurewebsites.net
4. DB_NAME = sibersih
5. DB_USER = adminuser
6. DB_PASSWORD = SiBersih2024!Strong
7. DB_HOST = sibersih-mysql-server.mysql.database.azure.com
8. DB_PORT = 3306
9. DB_SSL = True
10. SCM_DO_BUILD_DURING_DEPLOYMENT = true
11. WEBSITES_PORT = 8000

→ Save (app akan restart)
```

### ☑️ Step 7: Startup Command
```
Configuration → General settings
Startup Command: startup.sh
→ Save
```

---

## 🔄 PART 3: DEPLOY & TEST (10 min)

### ☑️ Step 8: Monitor Deployment
```
Option 1: Azure Portal
  Web App → Deployment Center → Logs
  Tunggu status: Success ✅

Option 2: GitHub
  https://github.com/Glenferdinza/SiBersih → Actions
  Tunggu workflow: ✅ hijau
```

### ☑️ Step 9: Database Migration
```
Web App → SSH (atau Advanced Tools → SSH)

Jalankan:
  cd /home/site/wwwroot
  python manage.py migrate
  python manage.py createsuperuser
  
Isi superuser:
  Username: admin
  Email: admin@sibersih.com
  Password: Admin123!Strong
```

### ☑️ Step 10: Restart & Test
```
Web App → Restart → Yes

Test:
1. ✅ Homepage: https://sibersih-app.azurewebsites.net
2. ✅ Admin: https://sibersih-app.azurewebsites.net/admin
3. ✅ Register user baru
4. ✅ Login & lihat dashboard
```

---

## 🎉 DEPLOYMENT COMPLETE!

### Your Live URLs:
```
🌐 Website: https://sibersih-app.azurewebsites.net
👨‍💼 Admin: https://sibersih-app.azurewebsites.net/admin
```

### Login Credentials:
```
Admin:
  Username: admin
  Password: Admin123!Strong

Database:
  Host: sibersih-mysql-server.mysql.database.azure.com
  User: adminuser
  Pass: SiBersih2024!Strong
  DB: sibersih
```

---

## 🔍 QUICK TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Application Error | Check Log stream, verify env vars |
| CSS tidak muncul | SSH: `python manage.py collectstatic --noinput` |
| DB connection error | Check firewall rules, verify DB credentials |
| Deployment failed | Check GitHub Actions logs |
| 404 Not Found | Check ALLOWED_HOSTS setting |

---

## 💰 COST TRACKING

| Resource | Tier | Cost/Month |
|----------|------|------------|
| Web App | B1 Basic | ~$13 |
| Web App | F1 Free | $0 |
| MySQL | B1ms Burstable | ~$12 |
| MySQL | B1s Burstable | ~$7 |
| App Insights | Free tier | $0 |
| **TOTAL** | B1 + B1ms | **~$25** |
| **MINIMAL** | F1 + B1s | **~$7** |

**Stop resources saat tidak dipakai untuk save cost!**

---

## 📊 MONITORING DASHBOARD

```
Web App → Overview:
  ✅ Status: Running
  ✅ URL: Responding
  ✅ Health check: Healthy

Metrics to watch:
  📈 Response time: < 2s
  📊 Requests: Normal traffic
  ⚠️ HTTP errors: Should be 0
  💻 CPU: < 70%
  💾 Memory: < 80%
```

---

## 🔄 UPDATE WORKFLOW

```
Local changes → git push → GitHub Actions → Azure Auto-Deploy

1. Edit code di local
2. git add .
3. git commit -m "Update"
4. git push origin master
5. ⏳ Wait 5-10 min (auto-deploy)
6. ✅ Website updated!
```

---

## 🆘 SUPPORT LINKS

- **Azure Portal:** https://portal.azure.com
- **Resource Group:** Portal → sibersih-rg
- **Web App:** Portal → App Services → sibersih-app
- **MySQL:** Portal → Azure Database for MySQL → sibersih-mysql-server
- **GitHub Repo:** https://github.com/Glenferdinza/SiBersih
- **Documentation:** [AZURE_DEPLOYMENT_PORTAL.md](AZURE_DEPLOYMENT_PORTAL.md)

---

**Print checklist ini dan centang setiap step yang sudah selesai!** ✅
