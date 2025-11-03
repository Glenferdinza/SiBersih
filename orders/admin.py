from django.contrib import admin
from .models import Service, Order, OrderStatusHistory, Courier, Payment, PaymentIssue

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_price', 'unit', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'mitra', 'service', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at', 'service']
    search_fields = ['order_number', 'user__username', 'mitra__business_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at']

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'changed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number']

@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'vehicle_type', 'vehicle_number', 'mitra', 'is_active']
    list_filter = ['is_active', 'vehicle_type']
    search_fields = ['name', 'phone', 'vehicle_number']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment_method', 'amount', 'status', 'uploaded_at', 'verified_by']
    list_filter = ['status', 'payment_method', 'uploaded_at', 'verified_at']
    search_fields = ['order__order_number', 'order__user__username']
    readonly_fields = ['uploaded_at', 'updated_at']
    
    fieldsets = (
        ('Informasi Order', {
            'fields': ('order', 'payment_method', 'amount')
        }),
        ('Bukti Pembayaran', {
            'fields': ('proof_image',)
        }),
        ('Status Verifikasi', {
            'fields': ('status', 'verified_by', 'verified_at', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PaymentIssue)
class PaymentIssueAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'user', 'order', 'issue_type', 'status', 'created_at', 'responded_by']
    list_filter = ['status', 'issue_type', 'created_at', 'responded_at']
    search_fields = ['ticket_number', 'user__username', 'order__order_number', 'subject', 'description']
    readonly_fields = ['ticket_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informasi Tiket', {
            'fields': ('ticket_number', 'user', 'order', 'status')
        }),
        ('Detail Kendala', {
            'fields': ('issue_type', 'subject', 'description', 'screenshot')
        }),
        ('Tanggapan Admin', {
            'fields': ('admin_response', 'responded_by', 'responded_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

