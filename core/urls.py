from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('mitra-dashboard/', views.mitra_dashboard, name='mitra_dashboard'),
    path('admin/export/orders/excel/', views.export_orders_excel, name='export_orders_excel'),
    path('admin/export/orders/csv/', views.export_orders_csv, name='export_orders_csv'),
]
