from django.db import models
from django.conf import settings
from partners.models import MitraProfile, Laundry
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, default='kg')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'services'
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Menunggu Penjemputan'),
        ('picked_up', 'Sudah Dijemput'),
        ('processing', 'Dalam Proses Pencucian'),
        ('ready', 'Siap Diantar'),
        ('delivered', 'Selesai'),
        ('cancelled', 'Dibatalkan'),
    ]
    
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('qris', 'QRIS / QR Code'),
        ('bri', 'Bank BRI'),
        ('bca', 'Bank BCA'),
        ('seabank', 'SeaBank'),
        ('shopee', 'ShopeePay'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    laundry = models.ForeignKey(Laundry, on_delete=models.PROTECT, related_name='orders', null=True, blank=True)
    mitra = models.ForeignKey(MitraProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='orders')
    
    # Voucher (jika digunakan)
    voucher = models.ForeignKey('partners.Voucher', on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='orders', verbose_name='Voucher Digunakan')
    voucher_discount = models.DecimalField(max_digits=10, decimal_places=0, default=0, 
                                          verbose_name='Diskon dari Voucher')
    
    # Detail pesanan
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Berat (KG)',
                                     validators=[MinValueValidator(0.5)], default=2.0)
    pickup_address = models.TextField(verbose_name='Alamat Penjemputan')
    delivery_address = models.TextField(verbose_name='Alamat Pengantaran', blank=True, null=True, default='')
    
    # Waktu
    pickup_time = models.DateTimeField(verbose_name='Waktu Jemput')
    estimated_delivery = models.DateTimeField(null=True, blank=True, verbose_name='Estimasi Selesai')
    actual_delivery = models.DateTimeField(null=True, blank=True, verbose_name='Waktu Antar Aktual')
    
    # Harga breakdown
    laundry_price = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='Harga Laundry')
    cod_fee = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='Biaya COD')
    platform_fee = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='Fee Platform')
    total_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Total Harga')
    
    # Jarak
    distance_km = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Jarak (KM)')
    
    # Status & payment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    payment_proof = models.ImageField(upload_to='payment_proofs/', null=True, blank=True, verbose_name='Bukti Pembayaran')
    is_paid = models.BooleanField(default=False)
    
    notes = models.TextField(blank=True, null=True, verbose_name='Catatan Tambahan')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"SB{uuid.uuid4().hex[:8].upper()}"
        
        # Auto set mitra dari laundry
        if self.laundry and not self.mitra:
            self.mitra = self.laundry.mitra
        
        # Auto calculate total jika belum ada
        if not self.total_price or self.total_price == 0:
            self.calculate_total_price()
        
        super().save(*args, **kwargs)
    
    def calculate_total_price(self):
        """Hitung total harga otomatis"""
        from partners.models import CODRate
        
        # Harga laundry = price_per_kg * weight
        self.laundry_price = float(self.laundry.price_per_kg) * float(self.weight_kg)
        
        # COD fee berdasarkan jarak
        self.cod_fee = CODRate.get_fee_for_distance(float(self.distance_km))
        
        # Platform fee 2.5% - 5% dari laundry price
        fee_percentage = 0.03  # 3%
        self.platform_fee = self.laundry_price * fee_percentage
        
        # Subtotal sebelum voucher
        subtotal = self.laundry_price + self.cod_fee + self.platform_fee
        
        # Apply voucher discount
        if self.voucher and self.voucher.is_valid():
            self.voucher_discount = self.voucher.calculate_discount(
                self.laundry_price,
                float(self.weight_kg),
                self.cod_fee
            )
        else:
            self.voucher_discount = 0
        
        # Total = Subtotal - Voucher Discount
        self.total_price = subtotal - self.voucher_discount
        
        return self.total_price
    
    def __str__(self):
        return f"{self.order_number} - {self.user.username}"
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status}"
    
    class Meta:
        db_table = 'order_status_history'
        verbose_name = 'Order Status History'
        verbose_name_plural = 'Order Status Histories'
        ordering = ['-created_at']

class TransactionLog(models.Model):
    """Log semua transaksi untuk audit"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transaction_logs')
    action = models.CharField(max_length=100, verbose_name='Aksi')
    description = models.TextField(verbose_name='Deskripsi')
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.order.order_number} - {self.action}"
    
    class Meta:
        db_table = 'transaction_logs'
        verbose_name = 'Transaction Log'
        verbose_name_plural = 'Transaction Logs'
        ordering = ['-timestamp']

class Courier(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    vehicle_type = models.CharField(max_length=50)
    vehicle_number = models.CharField(max_length=20)
    mitra = models.ForeignKey(MitraProfile, on_delete=models.CASCADE, related_name='couriers', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.vehicle_number}"
    
    class Meta:
        db_table = 'couriers'
        verbose_name = 'Courier'
        verbose_name_plural = 'Couriers'


class Payment(models.Model):
    """Payment verification for online payment methods"""
    STATUS_CHOICES = [
        ('pending', 'Menunggu Verifikasi'),
        ('verified', 'Terverifikasi'),
        ('rejected', 'Ditolak'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment', verbose_name='Order')
    payment_method = models.CharField(max_length=20, verbose_name='Metode Pembayaran')
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Jumlah Pembayaran')
    proof_image = models.ImageField(upload_to='payment_proofs/', verbose_name='Bukti Pembayaran')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='verified_payments', verbose_name='Diverifikasi Oleh')
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name='Waktu Verifikasi')
    admin_notes = models.TextField(blank=True, null=True, verbose_name='Catatan Admin')
    
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Waktu Upload')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Waktu Update')
    
    def __str__(self):
        return f"Payment {self.order.order_number} - {self.get_status_display()}"
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-uploaded_at']


class PaymentIssue(models.Model):
    """Customer Service - Payment Issues / Kendala Pembayaran"""
    ISSUE_TYPE_CHOICES = [
        ('payment_failed', 'Pembayaran Gagal'),
        ('wrong_amount', 'Nominal Salah'),
        ('not_verified', 'Belum Diverifikasi'),
        ('refund_request', 'Permintaan Refund'),
        ('other', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Baru'),
        ('in_progress', 'Sedang Ditangani'),
        ('resolved', 'Selesai'),
        ('closed', 'Ditutup'),
    ]
    
    # Ticket info
    ticket_number = models.CharField(max_length=50, unique=True, editable=False, verbose_name='No. Tiket')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                            related_name='payment_issues', verbose_name='User')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True,
                             related_name='payment_issues', verbose_name='Order')
    
    # Issue details
    issue_type = models.CharField(max_length=30, choices=ISSUE_TYPE_CHOICES, verbose_name='Jenis Kendala')
    subject = models.CharField(max_length=200, verbose_name='Subjek')
    description = models.TextField(verbose_name='Deskripsi Masalah')
    screenshot = models.ImageField(upload_to='payment_issues/', null=True, blank=True, 
                                  verbose_name='Screenshot/Bukti')
    
    # Status & resolution
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name='Status')
    admin_response = models.TextField(blank=True, null=True, verbose_name='Tanggapan Admin')
    responded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                    null=True, blank=True, related_name='resolved_issues',
                                    verbose_name='Ditangani Oleh')
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name='Waktu Tanggapan')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Dibuat')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Diupdate')
    
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            # Generate ticket number: CS-YYYYMMDD-XXXX
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_ticket = PaymentIssue.objects.filter(
                ticket_number__startswith=f'CS-{date_str}'
            ).order_by('-ticket_number').first()
            
            if last_ticket:
                last_num = int(last_ticket.ticket_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.ticket_number = f'CS-{date_str}-{new_num:04d}'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"
    
    class Meta:
        db_table = 'payment_issues'
        verbose_name = 'Payment Issue'
        verbose_name_plural = 'Payment Issues'
        ordering = ['-created_at']


class Review(models.Model):
    """Review dan Rating untuk Laundry setelah order selesai"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review', verbose_name='Order')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name='User')
    laundry = models.ForeignKey(Laundry, on_delete=models.CASCADE, related_name='reviews', verbose_name='Laundry')
    
    # Rating (1-5 stars)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Rating',
        help_text='Rating 1-5 bintang'
    )
    
    # Review text
    comment = models.TextField(verbose_name='Komentar', help_text='Berikan ulasan Anda')
    
    # Detail ratings (optional)
    service_quality = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
        verbose_name='Kualitas Layanan'
    )
    cleanliness = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
        verbose_name='Kebersihan'
    )
    speed = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
        verbose_name='Kecepatan'
    )
    
    # Photos (optional)
    photo1 = models.ImageField(upload_to='reviews/', null=True, blank=True, verbose_name='Foto 1')
    photo2 = models.ImageField(upload_to='reviews/', null=True, blank=True, verbose_name='Foto 2')
    photo3 = models.ImageField(upload_to='reviews/', null=True, blank=True, verbose_name='Foto 3')
    
    # Admin moderation
    is_approved = models.BooleanField(default=True, verbose_name='Disetujui')
    is_featured = models.BooleanField(default=False, verbose_name='Ditampilkan di Highlight')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Dibuat')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Diupdate')
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Update laundry rating setelah review disimpan
        if is_new or self.is_approved:
            self.laundry.update_rating()
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.laundry.name} - {self.rating}★"
    
    class Meta:
        db_table = 'reviews'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
