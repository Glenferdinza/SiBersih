from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('track/<str:order_number>/', views.track_order, name='track_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('history/', views.order_history, name='order_history'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    
    # Delivery confirmation
    path('confirm-delivery/<str:order_number>/', views.confirm_delivery, name='confirm_delivery'),
    
    # Reviews
    path('review/<str:order_number>/', views.submit_review, name='submit_review'),
    
    # Payment verification
    path('upload-payment/<str:order_number>/', views.upload_payment, name='upload_payment'),
    path('admin/verify-payments/', views.admin_verify_payments, name='admin_verify_payments'),
    path('admin/verify-payment/<int:payment_id>/', views.verify_payment, name='verify_payment'),
    
    # Payment issues / Customer Service
    path('report-issue/', views.report_payment_issue, name='report_payment_issue'),
    path('my-issues/', views.my_issues, name='my_issues'),
    path('admin/payment-issues/', views.admin_payment_issues, name='admin_payment_issues'),
    path('admin/respond-issue/<int:issue_id>/', views.respond_to_issue, name='respond_to_issue'),
]
