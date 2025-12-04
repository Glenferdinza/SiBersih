# Admin Access Guide

## Accessing Admin Panel

### URL
```
http://127.0.0.1:8000/admin/
```

### Default Credentials
- **Username:** `admin`
- **Password:** `admin123`

**Note:** Change the default password immediately after first login for security.

---

## Admin Panel Features

### 1. User Management
- View and manage all registered users
- Change user roles (User, Mitra, Admin)
- Activate/deactivate user accounts
- Reset user passwords

### 2. Mitra Verification
- Review mitra registration applications
- Verify mitra documents (KTP, business registration)
- Approve or reject mitra applications
- Manage active mitra accounts

### 3. Laundry Management
- View all registered laundries
- Activate/deactivate laundry services
- Verify laundry information
- Monitor laundry ratings and reviews

### 4. Order Management
- View all orders across the platform
- Monitor order statuses
- Handle order disputes
- Generate order reports

### 5. Payment Verification
- Review payment proofs uploaded by users
- Verify bank transfer and QRIS payments
- Approve or reject payment confirmations
- Manage payment-related issues

### 6. Voucher Management
- Review voucher creation requests from mitras
- Approve or reject voucher requests
- Monitor active vouchers
- Deactivate expired or fraudulent vouchers

### 7. COD Rate Configuration
- Set Cash on Delivery (COD) rates based on distance
- Configure delivery fee tiers
- Update pricing structures

### 8. System Settings
- Configure platform fees (default: 3%)
- Manage email templates
- Update system-wide settings

---

## Common Admin Tasks

### Approving a Mitra Application
1. Navigate to **Partners > Mitra Verifications**
2. Click on pending application
3. Review submitted documents
4. Click **Approve** or **Reject** with appropriate notes

### Verifying Payment
1. Go to **Orders > Payments**
2. Filter by **Pending Verification**
3. View uploaded payment proof
4. Verify transaction details
5. Mark as **Verified** or **Rejected**

### Managing Vouchers
1. Access **Partners > Voucher Requests**
2. Review voucher details (discount, validity, terms)
3. Approve if legitimate, reject if fraudulent
4. Approved vouchers become active immediately

### Handling Payment Issues
1. Navigate to **Orders > Payment Issues**
2. Review reported issues
3. Contact user/mitra if needed
4. Resolve and update status

---

## Security Best Practices

1. **Change Default Password:** Never use default credentials in production
2. **Regular Backups:** Ensure database backups are scheduled
3. **Access Logs:** Monitor admin access logs regularly
4. **Two-Factor Authentication:** Enable 2FA if available
5. **Limited Access:** Grant admin access only to trusted personnel

---

## Creating Additional Admin Users

### Via Django Shell
```bash
python manage.py shell
```

```python
from accounts.models import User

# Create admin user
admin = User.objects.create_user(
    username='newadmin',
    email='admin@sibersih.com',
    password='secure_password_here',
    role='admin',
    first_name='Admin',
    last_name='Name'
)
admin.is_staff = True
admin.is_superuser = True
admin.save()
```

### Via Admin Panel
1. Login as superuser
2. Navigate to **Accounts > Users**
3. Click **Add User**
4. Fill in username, email, and password
5. Set **Role** to **Admin**
6. Check **Staff status** and **Superuser status**
7. Click **Save**

---

## Troubleshooting

### Cannot Login
- Verify username and password
- Check if account is active
- Ensure `is_staff=True` for admin access

### Missing Permissions
- Verify user has `is_superuser=True`
- Check role is set to 'admin'
- Re-login after permission changes

### Database Issues
```bash
python manage.py migrate
python manage.py createsuperuser  # Create new admin if needed
```

---

## Support

For technical issues or questions, contact the development team.
