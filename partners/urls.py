from django.urls import path
from . import views

app_name = 'partners'

urlpatterns = [
    # Mitra application
    path('apply/', views.apply_mitra, name='apply_mitra'),
    
    # Laundry Registration & Edit (for existing mitra)
    path('laundry/register/', views.register_laundry, name='register_laundry'),
    path('laundry/edit/<int:laundry_id>/', views.edit_laundry, name='edit_laundry'),
    
    # Voucher Management (Mitra)
    path('vouchers/', views.voucher_request_list, name='voucher_request_list'),
    path('vouchers/create/', views.create_voucher_request, name='create_voucher_request'),
    
    # Voucher Management (Admin)
    path('admin/vouchers/', views.admin_voucher_requests, name='admin_voucher_requests'),
    path('admin/vouchers/<int:request_id>/approve/', views.approve_voucher_request, name='approve_voucher_request'),
    path('admin/vouchers/<int:request_id>/reject/', views.reject_voucher_request, name='reject_voucher_request'),
    
    # Laundry Detail & Images
    path('laundry/<int:laundry_id>/', views.laundry_detail, name='laundry_detail'),
    path('laundry/<int:laundry_id>/images/', views.upload_laundry_images, name='upload_laundry_images'),
    path('images/<int:image_id>/delete/', views.delete_laundry_image, name='delete_laundry_image'),
    
    # Laundry Status Control
    path('update-laundry-status/', views.update_laundry_status, name='update_laundry_status'),
    
    # Mitra Verification
    path('verification/submit/', views.submit_mitra_verification, name='submit_mitra_verification'),
    path('admin/verifications/', views.admin_mitra_verifications, name='admin_mitra_verifications'),
    path('admin/verify-mitra/<int:verification_id>/', views.verify_mitra, name='verify_mitra'),
    
    # Mitra Earnings & Transfers
    path('earnings/', views.mitra_earnings, name='mitra_earnings'),
    path('admin/transfers/', views.admin_process_transfers, name='admin_process_transfers'),
    path('admin/process-transfer/<int:transaction_id>/', views.process_transfer, name='process_transfer'),
]
