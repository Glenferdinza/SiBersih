from django.contrib import admin
from .models import MitraRequest, MitraProfile, MitraVerification, MitraTransaction

@admin.register(MitraRequest)
class MitraRequestAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['business_name', 'user__username', 'location']
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        for req in queryset:
            if req.status == 'pending':
                req.status = 'approved'
                req.save()
                
                req.user.role = 'mitra'
                req.user.save()
                
                MitraProfile.objects.create(
                    user=req.user,
                    business_name=req.business_name,
                    location=req.location,
                    description=req.description,
                    operational_cost=req.operational_cost
                )
        self.message_user(request, f"{queryset.count()} requests approved")
    approve_requests.short_description = "Approve selected requests"
    
    def reject_requests(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} requests rejected")
    reject_requests.short_description = "Reject selected requests"

@admin.register(MitraProfile)
class MitraProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'rating', 'total_orders', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['business_name', 'user__username', 'location']


@admin.register(MitraVerification)
class MitraVerificationAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'full_name', 'status', 'submitted_at', 'verified_by']
    list_filter = ['status', 'bank_name', 'submitted_at', 'verified_at']
    search_fields = ['business_name', 'full_name', 'ktp_number', 'user__username']
    readonly_fields = ['submitted_at', 'updated_at']
    
    fieldsets = (
        ('Informasi Personal', {
            'fields': ('user', 'full_name', 'ktp_number', 'ktp_image', 'selfie_with_ktp')
        }),
        ('Informasi Usaha', {
            'fields': ('business_name', 'business_address', 'business_phone', 
                      'store_front_photo', 'store_interior_photo', 'equipment_photo')
        }),
        ('Informasi Rekening Bank', {
            'fields': ('bank_name', 'bank_account_number', 'bank_account_name', 'bank_account_proof')
        }),
        ('Informasi Tambahan', {
            'fields': ('years_of_experience', 'daily_capacity_kg', 'additional_notes')
        }),
        ('Status Verifikasi', {
            'fields': ('status', 'verified_by', 'verified_at', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MitraTransaction)
class MitraTransactionAdmin(admin.ModelAdmin):
    list_display = ['order', 'mitra', 'mitra_earning', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at', 'completed_at']
    search_fields = ['order__order_number', 'mitra__business_name', 'transfer_reference']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informasi Order', {
            'fields': ('order', 'mitra')
        }),
        ('Rincian Pembayaran', {
            'fields': ('gross_amount', 'platform_fee', 'mitra_earning')
        }),
        ('Informasi Rekening', {
            'fields': ('bank_name', 'bank_account_number', 'bank_account_name')
        }),
        ('Status Transfer', {
            'fields': ('status', 'transfer_reference', 'transfer_notes', 
                      'processed_by', 'processed_at', 'completed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

