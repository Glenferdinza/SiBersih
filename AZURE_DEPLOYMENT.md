# 🚀 SiBersih - Azure Deployment Guide

Panduan lengkap untuk deploy aplikasi SiBersih ke Azure Web App.

---

## 📋 Prerequisites

1. **Akun Azure** dengan subscription aktif
2. **Azure CLI** terinstall ([Download](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli))
3. **Git** terinstall
4. **Repository GitHub** sudah siap (https://github.com/Glenferdinza/SiBersih.git)

---

## 🎯 Step 1: Login ke Azure

```bash
# Login ke Azure
az login

# Pilih subscription (jika punya lebih dari 1)
az account list --output table
az account set --subscription "SUBSCRIPTION_NAME"
```

---

## 🗄️ Step 2: Buat Azure Database for MySQL

### 2.1 Buat Resource Group
```bash
az group create \
  --name sibersih-rg \
  --location southeastasia
```

### 2.2 Buat MySQL Server
```bash
az mysql flexible-server create \
  --name sibersih-mysql-server \
  --resource-group sibersih-rg \
  --location southeastasia \
  --admin-user adminuser \
  --admin-password "YourStrongPassword123!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 8.0.21 \
  --storage-size 32 \
  --public-access 0.0.0.0
```

**⚠️ PENTING:** Simpan credentials berikut:
- **Server name:** `sibersih-mysql-server.mysql.database.azure.com`
- **Admin username:** `adminuser`
- **Admin password:** `YourStrongPassword123!`

### 2.3 Buat Database
```bash
az mysql flexible-server db create \
  --resource-group sibersih-rg \
  --server-name sibersih-mysql-server \
  --database-name sibersih
```

### 2.4 Konfigurasi Firewall
```bash
# Allow Azure services
az mysql flexible-server firewall-rule create \
  --resource-group sibersih-rg \
  --name sibersih-mysql-server \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Allow your IP (untuk development)
az mysql flexible-server firewall-rule create \
  --resource-group sibersih-rg \
  --name sibersih-mysql-server \
  --rule-name AllowMyIP \
  --start-ip-address YOUR_IP \
  --end-ip-address YOUR_IP
```

---

## 🌐 Step 3: Buat Azure Web App

### 3.1 Buat App Service Plan
```bash
az appservice plan create \
  --name sibersih-plan \
  --resource-group sibersih-rg \
  --location southeastasia \
  --sku B1 \
  --is-linux
```

### 3.2 Buat Web App
```bash
az webapp create \
  --name sibersih-app \
  --resource-group sibersih-rg \
  --plan sibersih-plan \
  --runtime "PYTHON:3.12"
```

**✅ URL Aplikasi:** `https://sibersih-app.azurewebsites.net`

---

## ⚙️ Step 4: Konfigurasi Environment Variables

```bash
# Generate SECRET_KEY baru
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set environment variables
az webapp config appsettings set \
  --resource-group sibersih-rg \
  --name sibersih-app \
  --settings \
    SECRET_KEY="generated-secret-key-here" \
    DEBUG="False" \
    ALLOWED_HOSTS="sibersih-app.azurewebsites.net" \
    DB_NAME="sibersih" \
    DB_USER="adminuser" \
    DB_PASSWORD="YourStrongPassword123!" \
    DB_HOST="sibersih-mysql-server.mysql.database.azure.com" \
    DB_PORT="3306" \
    DB_SSL="True" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    WEBSITES_PORT="8000"
```

---

## 🔗 Step 5: Deploy dari GitHub

### 5.1 Konfigurasi Deployment dari GitHub
```bash
az webapp deployment source config \
  --name sibersih-app \
  --resource-group sibersih-rg \
  --repo-url https://github.com/Glenferdinza/SiBersih.git \
  --branch master \
  --manual-integration
```

### 5.2 Set Startup Command
```bash
az webapp config set \
  --resource-group sibersih-rg \
  --name sibersih-app \
  --startup-file "startup.sh"
```

### 5.3 Enable Logging
```bash
az webapp log config \
  --name sibersih-app \
  --resource-group sibersih-rg \
  --docker-container-logging filesystem \
  --level information
```

---

## 🔄 Step 6: Trigger Deployment

### Option A: Via Azure Portal
1. Buka [Azure Portal](https://portal.azure.com)
2. Pilih **App Services** → **sibersih-app**
3. Pilih **Deployment Center** di menu kiri
4. Klik **Sync** untuk trigger deployment

### Option B: Via Azure CLI
```bash
az webapp deployment source sync \
  --name sibersih-app \
  --resource-group sibersih-rg
```

---

## 🗂️ Step 7: Migrasi Database

### 7.1 SSH ke Web App
```bash
az webapp ssh \
  --name sibersih-app \
  --resource-group sibersih-rg
```

### 7.2 Jalankan Migrasi
```bash
# Di dalam SSH session
cd /home/site/wwwroot
python manage.py migrate
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

### 7.3 Load Initial Data (Optional)
```bash
# Jika punya fixture data
python manage.py loaddata initial_data.json
```

---

## ✅ Step 8: Verifikasi Deployment

### 8.1 Cek Website
Buka: `https://sibersih-app.azurewebsites.net`

### 8.2 Cek Logs
```bash
# Real-time logs
az webapp log tail \
  --name sibersih-app \
  --resource-group sibersih-rg

# Download logs
az webapp log download \
  --name sibersih-app \
  --resource-group sibersih-rg \
  --log-file logs.zip
```

### 8.3 Test Admin Panel
Buka: `https://sibersih-app.azurewebsites.net/admin/`

---

## 🔧 Troubleshooting

### 1. Error: "DisallowedHost"
```bash
# Tambahkan domain ke ALLOWED_HOSTS
az webapp config appsettings set \
  --resource-group sibersih-rg \
  --name sibersih-app \
  --settings ALLOWED_HOSTS="sibersih-app.azurewebsites.net,*.azurewebsites.net"
```

### 2. Static Files tidak muncul
```bash
# SSH ke web app dan jalankan collectstatic
az webapp ssh --name sibersih-app --resource-group sibersih-rg
python manage.py collectstatic --noinput
```

### 3. Database Connection Error
```bash
# Cek firewall rules
az mysql flexible-server firewall-rule list \
  --resource-group sibersih-rg \
  --name sibersih-mysql-server

# Test connection
mysql -h sibersih-mysql-server.mysql.database.azure.com \
  -u adminuser \
  -p sibersih
```

### 4. Restart Web App
```bash
az webapp restart \
  --name sibersih-app \
  --resource-group sibersih-rg
```

---

## 🔄 Update Aplikasi

### Push ke GitHub
```bash
git add .
git commit -m "Update aplikasi"
git push origin master
```

### Trigger Deployment
```bash
az webapp deployment source sync \
  --name sibersih-app \
  --resource-group sibersih-rg
```

---

## 💰 Cost Optimization

### Free Tier (Untuk Testing)
```bash
# Gunakan F1 tier (gratis)
az appservice plan update \
  --name sibersih-plan \
  --resource-group sibersih-rg \
  --sku F1
```

### Production Setup
- **App Service:** B1 tier (~$13/month)
- **MySQL:** Burstable B1ms (~$12/month)
- **Total:** ~$25/month

---

## 📊 Monitoring

### Application Insights
```bash
# Enable Application Insights
az monitor app-insights component create \
  --app sibersih-insights \
  --location southeastasia \
  --resource-group sibersih-rg \
  --application-type web

# Link to Web App
az webapp config appsettings set \
  --resource-group sibersih-rg \
  --name sibersih-app \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="<key-from-previous-command>"
```

---

## 🔒 Security Best Practices

1. **Secret Key:** Gunakan secret key yang kuat dan unik
2. **DEBUG:** Set `DEBUG=False` di production
3. **HTTPS:** Azure Web App sudah include SSL gratis
4. **Database:** Enable SSL connection (`DB_SSL=True`)
5. **Firewall:** Restrict MySQL access hanya dari Azure services

---

## 📚 Resources

- [Azure App Service Docs](https://learn.microsoft.com/en-us/azure/app-service/)
- [Azure Database for MySQL](https://learn.microsoft.com/en-us/azure/mysql/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)

---

## 🆘 Support

Jika ada masalah:
1. Cek logs: `az webapp log tail --name sibersih-app --resource-group sibersih-rg`
2. Review Azure Portal → App Service → Diagnose and solve problems
3. Check GitHub Issues: https://github.com/Glenferdinza/SiBersih/issues

---

**🎉 Selamat! Aplikasi SiBersih sudah deploy di Azure!**

**Live URL:** https://sibersih-app.azurewebsites.net
