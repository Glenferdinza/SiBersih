from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import re

class MitraRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mitra_requests')
    business_name = models.CharField(max_length=200)
    location = models.TextField()
    description = models.TextField()
    operational_cost = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.business_name} - {self.user.username}"
    
    class Meta:
        db_table = 'mitra_requests'
        verbose_name = 'Mitra Request'
        verbose_name_plural = 'Mitra Requests'

class MitraProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mitra_profile')
    business_name = models.CharField(max_length=200)
    location = models.TextField()
    description = models.TextField()
    operational_cost = models.DecimalField(max_digits=12, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_orders = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.business_name}"
    
    class Meta:
        db_table = 'mitra_profiles'
        verbose_name = 'Mitra Profile'
        verbose_name_plural = 'Mitra Profiles'

class Laundry(models.Model):
    """Detail laundry dari mitra - marketplace listing"""
    mitra = models.ForeignKey(MitraProfile, on_delete=models.CASCADE, related_name='laundries')
    name = models.CharField(max_length=200, verbose_name='Nama Laundry')
    address = models.TextField(verbose_name='Alamat Lengkap')
    district = models.CharField(max_length=100, verbose_name='Kecamatan', default='Yogyakarta')
    city = models.CharField(max_length=100, default='Yogyakarta')
    
    # Koordinat untuk Maps
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    map_link = models.URLField(max_length=500, blank=True, null=True, verbose_name='Link Google Maps')
    
    # Harga & Layanan
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Harga per KG',
                                       validators=[MinValueValidator(1000)])
    min_order_kg = models.DecimalField(max_digits=5, decimal_places=1, default=2.0, verbose_name='Min Order (KG)')
    
    # Operasional
    operating_hours_start = models.TimeField(default='08:00')
    operating_hours_end = models.TimeField(default='20:00')
    estimated_pickup_time = models.IntegerField(default=60, verbose_name='Estimasi Waktu Jemput (menit)')
    estimated_delivery_time = models.IntegerField(default=1440, verbose_name='Estimasi Pengiriman (menit)')
    
    # Status Operasional
    STATUS_CHOICES = [
        ('buka', 'Buka'),
        ('full', 'Full Booked'),
        ('istirahat', 'Istirahat'),
        ('tutup', 'Tutup'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='buka', verbose_name='Status')
    
    # Rating & Status
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0,
                                validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_reviews = models.IntegerField(default=0)
    total_orders_completed = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_open_now = models.BooleanField(default=True)
    
    # Layanan tersedia
    has_regular_wash = models.BooleanField(default=True, verbose_name='Cuci Setrika')
    has_dry_clean = models.BooleanField(default=True, verbose_name='Dry Clean')
    has_express = models.BooleanField(default=True, verbose_name='Express')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.district}"
    
    def save(self, *args, **kwargs):
        """Auto-extract coordinates from Google Maps link"""
        if self.map_link and not self.latitude:
            coords = self.extract_coordinates_from_map_link(self.map_link)
            if coords:
                self.latitude, self.longitude = coords
        super().save(*args, **kwargs)
    
    @staticmethod
    def extract_coordinates_from_map_link(link):
        """Extract lat/lon from Google Maps URL"""
        # Pattern untuk berbagai format Google Maps URL
        patterns = [
            r'@(-?\d+\.\d+),(-?\d+\.\d+)',  # @lat,lon
            r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)',  # !3dlat!4dlon
            r'll=(-?\d+\.\d+),(-?\d+\.\d+)',  # ll=lat,lon
            r'q=(-?\d+\.\d+),(-?\d+\.\d+)',  # q=lat,lon
        ]
        
        for pattern in patterns:
            match = re.search(pattern, link)
            if match:
                lat, lon = float(match.group(1)), float(match.group(2))
                # Validasi koordinat untuk area Yogyakarta (rough bounds)
                if -8.0 <= lat <= -7.5 and 110.0 <= lon <= 111.0:
                    return (lat, lon)
        return None
    
    def calculate_distance(self, user_lat, user_lon):
        """Hitung jarak dari user (simplified - nanti bisa pakai haversine)"""
        if self.latitude and self.longitude:
            from math import radians, sin, cos, sqrt, atan2
            R = 6371  # Radius bumi dalam km
            
            lat1, lon1 = radians(user_lat), radians(user_lon)
            lat2, lon2 = radians(float(self.latitude)), radians(float(self.longitude))
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance = R * c
            
            return round(distance, 2)
        return 0
    
    def update_rating(self):
        """Update rating laundry berdasarkan reviews"""
        from django.db.models import Avg, Count
        
        # Hitung average rating dari reviews yang approved
        stats = self.reviews.filter(is_approved=True).aggregate(
            avg_rating=Avg('rating'),
            total=Count('id')
        )
        
        if stats['total'] > 0:
            self.rating = round(stats['avg_rating'], 1)
            self.total_reviews = stats['total']
        else:
            # Jika belum ada review, set default 0
            self.rating = 0.0
            self.total_reviews = 0
        
        self.save(update_fields=['rating', 'total_reviews'])
    
    class Meta:
        db_table = 'laundries'
        verbose_name = 'Laundry'
        verbose_name_plural = 'Laundries'
        ordering = ['-rating', '-total_orders_completed']

class CODRate(models.Model):
    """Tarif COD berdasarkan jarak"""
    min_distance_km = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Jarak Min (KM)')
    max_distance_km = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Jarak Max (KM)')
    fee = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Biaya COD')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.min_distance_km}-{self.max_distance_km} km: Rp{self.fee}"
    
    @classmethod
    def get_fee_for_distance(cls, distance_km):
        """Get COD fee berdasarkan jarak"""
        rate = cls.objects.filter(
            min_distance_km__lte=distance_km,
            max_distance_km__gte=distance_km,
            is_active=True
        ).first()
        return float(rate.fee) if rate else 5000.0
    
    class Meta:
        db_table = 'cod_rates'
        verbose_name = 'COD Rate'
        verbose_name_plural = 'COD Rates'
        ordering = ['min_distance_km']

class LaundryImage(models.Model):
    """Gambar-gambar laundry (max 15)"""
    laundry = models.ForeignKey(Laundry, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='laundry_images/%Y/%m/', verbose_name='Gambar')
    caption = models.CharField(max_length=200, blank=True, null=True)
    order = models.IntegerField(default=0, verbose_name='Urutan')
    is_primary = models.BooleanField(default=False, verbose_name='Gambar Utama')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.laundry.name} - Image {self.order}"
    
    class Meta:
        db_table = 'laundry_images'
        verbose_name = 'Laundry Image'
        verbose_name_plural = 'Laundry Images'
        ordering = ['order', '-is_primary']

class Voucher(models.Model):
    """Voucher yang dibuat oleh Mitra dan di-approve Admin"""
    VOUCHER_TYPE_CHOICES = [
        ('free_shipping', 'Free Ongkir'),
        ('percentage_discount', 'Diskon Persentase'),
        ('fixed_discount', 'Diskon Nominal'),
        ('free_kg', 'Gratis KG'),
    ]
    
    laundry = models.ForeignKey(Laundry, on_delete=models.CASCADE, related_name='vouchers')
    code = models.CharField(max_length=50, unique=True, verbose_name='Kode Voucher')
    name = models.CharField(max_length=200, verbose_name='Nama Voucher')
    description = models.TextField(verbose_name='Deskripsi')
    
    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPE_CHOICES)
    
    # Nilai voucher
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                        help_text='Persentase (1-100) atau Nominal (Rupiah) atau KG')
    max_discount = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True,
                                      help_text='Maksimal diskon untuk persentase')
    
    # Syarat & Ketentuan
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0,
                                          verbose_name='Min Pembelian (Rp)')
    min_order_kg = models.DecimalField(max_digits=5, decimal_places=1, default=0,
                                      verbose_name='Min Order (KG)')
    max_usage_per_user = models.IntegerField(default=1, verbose_name='Max Pemakaian per User')
    total_quota = models.IntegerField(default=100, verbose_name='Total Kuota')
    used_count = models.IntegerField(default=0, verbose_name='Sudah Dipakai')
    
    # Periode berlaku
    valid_from = models.DateTimeField(verbose_name='Berlaku Dari')
    valid_until = models.DateTimeField(verbose_name='Berlaku Sampai')
    
    # Status
    is_active = models.BooleanField(default=False, verbose_name='Aktif')
    is_approved = models.BooleanField(default=False, verbose_name='Disetujui Admin')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                   null=True, blank=True, related_name='approved_vouchers')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def is_valid(self):
        """Cek apakah voucher masih valid"""
        now = timezone.now()
        return (
            self.is_active and 
            self.is_approved and 
            self.valid_from <= now <= self.valid_until and
            self.used_count < self.total_quota
        )
    
    def can_be_used_by(self, user):
        """Cek apakah user bisa pakai voucher ini"""
        if not self.is_valid():
            return False
        
        # Cek usage per user
        from orders.models import Order
        user_usage = Order.objects.filter(
            customer=user,
            voucher=self
        ).count()
        
        return user_usage < self.max_usage_per_user
    
    def calculate_discount(self, order_amount, order_kg, shipping_fee):
        """Hitung diskon berdasarkan tipe voucher"""
        if not self.is_valid():
            return 0
        
        # Cek minimum order
        if order_amount < float(self.min_order_amount):
            return 0
        if order_kg < float(self.min_order_kg):
            return 0
        
        if self.voucher_type == 'free_shipping':
            return float(shipping_fee)
        
        elif self.voucher_type == 'percentage_discount':
            discount = order_amount * (float(self.discount_value) / 100)
            if self.max_discount:
                discount = min(discount, float(self.max_discount))
            return discount
        
        elif self.voucher_type == 'fixed_discount':
            return float(self.discount_value)
        
        elif self.voucher_type == 'free_kg':
            # Gratis KG dihitung dari harga per kg laundry
            price_per_kg = order_amount / order_kg if order_kg > 0 else 0
            return price_per_kg * float(self.discount_value)
        
        return 0
    
    class Meta:
        db_table = 'vouchers'
        verbose_name = 'Voucher'
        verbose_name_plural = 'Vouchers'
        ordering = ['-created_at']

class VoucherRequest(models.Model):
    """Request voucher dari Mitra ke Admin"""
    STATUS_CHOICES = [
        ('pending', 'Menunggu Persetujuan'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
    ]
    
    VOUCHER_TYPE_CHOICES = [
        ('free_shipping', 'Free Ongkir'),
        ('percentage_discount', 'Diskon Persentase'),
        ('fixed_discount', 'Diskon Nominal'),
        ('free_kg', 'Gratis KG'),
    ]
    
    laundry = models.ForeignKey(Laundry, on_delete=models.CASCADE, related_name='voucher_requests')
    mitra = models.ForeignKey(MitraProfile, on_delete=models.CASCADE, related_name='voucher_requests')
    
    # Data voucher yang diminta
    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPE_CHOICES)
    voucher_name = models.CharField(max_length=200)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_kg = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    total_quota = models.IntegerField(default=100)
    duration_days = models.IntegerField(default=30, verbose_name='Durasi (Hari)')
    
    # Alasan & Catatan
    reason = models.TextField(verbose_name='Alasan Pengajuan')
    admin_notes = models.TextField(blank=True, null=True, verbose_name='Catatan Admin')
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='reviewed_voucher_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Voucher yang dihasilkan (jika approved)
    created_voucher = models.OneToOneField(Voucher, on_delete=models.SET_NULL, 
                                          null=True, blank=True, related_name='request_origin')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.laundry.name} - {self.get_voucher_type_display()} - {self.status}"
    
    class Meta:
        db_table = 'voucher_requests'
        verbose_name = 'Voucher Request'
        verbose_name_plural = 'Voucher Requests'
        ordering = ['-created_at']


class MitraVerification(models.Model):
    """Verification for mitra applications - KTP, business docs, bank account"""
    STATUS_CHOICES = [
        ('pending', 'Menunggu Verifikasi'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
    ]
    
    BANK_CHOICES = [
        ('bri', 'Bank BRI'),
        ('bca', 'Bank BCA'),
        ('mandiri', 'Bank Mandiri'),
        ('bni', 'Bank BNI'),
        ('seabank', 'SeaBank'),
        ('other', 'Lainnya'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                               related_name='mitra_verification', verbose_name='User')
    
    # Personal Identity
    full_name = models.CharField(max_length=200, verbose_name='Nama Lengkap (sesuai KTP)')
    ktp_number = models.CharField(max_length=16, verbose_name='Nomor KTP')
    ktp_image = models.ImageField(upload_to='mitra_verifications/ktp/', verbose_name='Foto KTP')
    selfie_with_ktp = models.ImageField(upload_to='mitra_verifications/selfie/', 
                                        verbose_name='Foto Selfie dengan KTP')
    
    # Business Information
    business_name = models.CharField(max_length=200, verbose_name='Nama Usaha Laundry')
    business_address = models.TextField(verbose_name='Alamat Usaha')
    business_phone = models.CharField(max_length=15, verbose_name='Nomor Telepon Usaha')
    
    # Business Photos (multiple)
    store_front_photo = models.ImageField(upload_to='mitra_verifications/business/', 
                                         verbose_name='Foto Depan Toko')
    store_interior_photo = models.ImageField(upload_to='mitra_verifications/business/', 
                                            verbose_name='Foto Interior Toko')
    equipment_photo = models.ImageField(upload_to='mitra_verifications/business/', 
                                       verbose_name='Foto Peralatan Laundry', blank=True, null=True)
    
    # Bank Account Information
    bank_name = models.CharField(max_length=20, choices=BANK_CHOICES, verbose_name='Nama Bank')
    bank_account_number = models.CharField(max_length=20, verbose_name='Nomor Rekening')
    bank_account_name = models.CharField(max_length=200, verbose_name='Nama Pemilik Rekening')
    bank_account_proof = models.ImageField(upload_to='mitra_verifications/bank/', 
                                          verbose_name='Foto Buku Tabungan/Bukti Rekening')
    
    # Additional Information
    years_of_experience = models.IntegerField(verbose_name='Pengalaman (Tahun)', default=0)
    daily_capacity_kg = models.DecimalField(max_digits=6, decimal_places=1, 
                                           verbose_name='Kapasitas Harian (KG)', default=50.0)
    additional_notes = models.TextField(blank=True, null=True, 
                                       verbose_name='Catatan Tambahan')
    
    # Verification Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', 
                            verbose_name='Status Verifikasi')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                   null=True, blank=True, related_name='verified_mitras',
                                   verbose_name='Diverifikasi Oleh')
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name='Waktu Verifikasi')
    admin_notes = models.TextField(blank=True, null=True, verbose_name='Catatan Admin')
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Waktu Submit')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Waktu Update')
    
    def __str__(self):
        return f"{self.business_name} - {self.get_status_display()}"
    
    class Meta:
        db_table = 'mitra_verifications'
        verbose_name = 'Mitra Verification'
        verbose_name_plural = 'Mitra Verifications'
        ordering = ['-submitted_at']


class MitraTransaction(models.Model):
    """Track payments/transfers to mitra from completed orders"""
    STATUS_CHOICES = [
        ('pending', 'Menunggu Transfer'),
        ('processing', 'Sedang Diproses'),
        ('completed', 'Transfer Selesai'),
        ('failed', 'Transfer Gagal'),
    ]
    
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, 
                                related_name='mitra_transaction', verbose_name='Order')
    mitra = models.ForeignKey(MitraProfile, on_delete=models.CASCADE, 
                             related_name='transactions', verbose_name='Mitra')
    
    # Amount breakdown
    gross_amount = models.DecimalField(max_digits=12, decimal_places=0, 
                                      verbose_name='Total Pembayaran Pelanggan')
    platform_fee = models.DecimalField(max_digits=12, decimal_places=0, 
                                      verbose_name='Fee Platform (3%)')
    mitra_earning = models.DecimalField(max_digits=12, decimal_places=0, 
                                       verbose_name='Pendapatan Mitra')
    
    # Bank details (from MitraVerification)
    bank_name = models.CharField(max_length=50, verbose_name='Bank Tujuan')
    bank_account_number = models.CharField(max_length=20, verbose_name='No. Rekening')
    bank_account_name = models.CharField(max_length=200, verbose_name='Nama Pemilik Rekening')
    
    # Transfer status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', 
                            verbose_name='Status Transfer')
    transfer_reference = models.CharField(max_length=100, blank=True, null=True, 
                                         verbose_name='Referensi Transfer')
    transfer_notes = models.TextField(blank=True, null=True, 
                                     verbose_name='Catatan Transfer')
    
    # Processing details
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                    null=True, blank=True, related_name='processed_transactions',
                                    verbose_name='Diproses Oleh')
    processed_at = models.DateTimeField(null=True, blank=True, 
                                       verbose_name='Waktu Proses')
    completed_at = models.DateTimeField(null=True, blank=True, 
                                       verbose_name='Waktu Selesai')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Dibuat')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Update Terakhir')
    
    def __str__(self):
        return f"{self.order.order_number} - {self.mitra.business_name} - Rp {self.mitra_earning}"
    
    class Meta:
        db_table = 'mitra_transactions'
        verbose_name = 'Mitra Transaction'
        verbose_name_plural = 'Mitra Transactions'
        ordering = ['-created_at']
