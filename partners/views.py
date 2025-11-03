from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import MitraRequest, Laundry, Voucher, VoucherRequest, LaundryImage, MitraVerification, MitraTransaction
from django.db.models import Sum, Count, Q
import uuid

@login_required
def apply_mitra(request):
    # This is ONLY for applying to become a mitra (not for registering laundry)
    if request.user.role == 'mitra':
        messages.info(request, 'Anda sudah menjadi mitra. Silakan daftarkan laundry Anda.')
        return redirect('partners:register_laundry')
    
    # Check if user has pending request
    pending_request = MitraRequest.objects.filter(user=request.user, status='pending').first()
    if pending_request:
        messages.warning(request, 'Anda sudah memiliki permohonan yang sedang diproses. Mohon menunggu persetujuan admin.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        # Personal/Business Information
        business_name = request.POST.get('business_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        # Bank Account Information
        bank_name = request.POST.get('bank_name')
        account_number = request.POST.get('account_number')
        account_holder = request.POST.get('account_holder')
        
        # Other info
        description = request.POST.get('description', '')
        
        # Create mitra request (simplified - we'll update MitraRequest model later)
        mitra_request = MitraRequest.objects.create(
            user=request.user,
            business_name=business_name,
            location=address,  # Using address for location
            description=description,
            operational_cost=0  # Not needed for mitra application
        )
        
        try:
            send_mail(
                subject='Pendaftaran Mitra Baru - SiBersih',
                message=f'''
Pendaftaran Mitra Baru

Nama Usaha: {business_name}
Pengguna: {request.user.get_full_name()} ({request.user.username})
Email: {request.user.email}
Telepon: {phone}
Alamat: {address}

Informasi Rekening:
Bank: {bank_name}
No Rekening: {account_number}
Atas Nama: {account_holder}

Deskripsi: {description}

Silakan login ke admin panel untuk meninjau dan menyetujui pendaftaran ini.
                ''',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['contact.sibersih@gmail.com'],
                fail_silently=True,
            )
        except:
            pass
        
        messages.success(request, 'Pendaftaran mitra berhasil dikirim. Mohon tunggu persetujuan admin (1-3 hari kerja).')
        return redirect('core:dashboard')
    
    return render(request, 'partners/apply_mitra.html')

@login_required
def register_laundry(request):
    """Register new laundry or edit existing one (for mitra only)"""
    if request.user.role != 'mitra':
        messages.error(request, 'Anda harus menjadi mitra terlebih dahulu')
        return redirect('partners:apply_mitra')
    
    try:
        mitra_profile = request.user.mitra_profile
        existing_laundry = Laundry.objects.filter(mitra=mitra_profile, is_active=True).first()
        
        if request.method == 'POST':
            # Laundry Information
            name = request.POST.get('name')
            address = request.POST.get('address')
            district = request.POST.get('district', 'Yogyakarta')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            
            # Pricing & Service
            price_per_kg = request.POST.get('price_per_kg')
            min_order_kg = request.POST.get('min_order_kg', 2.0)
            
            # Operating Hours
            operating_hours_start = request.POST.get('operating_hours_start', '08:00')
            operating_hours_end = request.POST.get('operating_hours_end', '20:00')
            estimated_pickup_time = request.POST.get('estimated_pickup_time', 60)
            estimated_delivery_time = request.POST.get('estimated_delivery_time', 1440)
            
            # Services Available
            has_regular_wash = request.POST.get('has_regular_wash') == 'on'
            has_dry_clean = request.POST.get('has_dry_clean') == 'on'
            has_express = request.POST.get('has_express') == 'on'
            
            # Validate required fields
            if not all([name, address, latitude, longitude, price_per_kg]):
                messages.error(request, 'Semua field wajib harus diisi')
                return redirect('partners:register_laundry')
            
            # Validate numeric fields
            try:
                from decimal import Decimal, InvalidOperation
                
                lat = Decimal(str(latitude))
                lon = Decimal(str(longitude))
                
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    messages.error(request, 'Koordinat tidak valid')
                    return redirect('partners:register_laundry')
                
                price = Decimal(str(price_per_kg))
                if price <= 0:
                    messages.error(request, 'Harga harus lebih dari 0')
                    return redirect('partners:register_laundry')
                
                min_kg = Decimal(str(min_order_kg))
                if min_kg <= 0:
                    messages.error(request, 'Minimal order harus lebih dari 0')
                    return redirect('partners:register_laundry')
                    
            except (ValueError, InvalidOperation, TypeError):
                messages.error(request, 'Format angka tidak valid')
                return redirect('partners:register_laundry')
            
            if existing_laundry:
                # Update existing laundry
                existing_laundry.name = name
                existing_laundry.address = address
                existing_laundry.district = district
                existing_laundry.latitude = latitude
                existing_laundry.longitude = longitude
                existing_laundry.price_per_kg = price_per_kg
                existing_laundry.min_order_kg = min_order_kg
                existing_laundry.operating_hours_start = operating_hours_start
                existing_laundry.operating_hours_end = operating_hours_end
                existing_laundry.estimated_pickup_time = estimated_pickup_time
                existing_laundry.estimated_delivery_time = estimated_delivery_time
                existing_laundry.has_regular_wash = has_regular_wash
                existing_laundry.has_dry_clean = has_dry_clean
                existing_laundry.has_express = has_express
                existing_laundry.save()
                messages.success(request, 'Informasi laundry berhasil diperbarui!')
            else:
                # Create new laundry
                laundry = Laundry.objects.create(
                    mitra=mitra_profile,
                    name=name,
                    address=address,
                    district=district,
                    latitude=latitude,
                    longitude=longitude,
                    price_per_kg=price_per_kg,
                    min_order_kg=min_order_kg,
                    operating_hours_start=operating_hours_start,
                    operating_hours_end=operating_hours_end,
                    estimated_pickup_time=estimated_pickup_time,
                    estimated_delivery_time=estimated_delivery_time,
                    has_regular_wash=has_regular_wash,
                    has_dry_clean=has_dry_clean,
                    has_express=has_express,
                    city='Yogyakarta',
                    is_active=True
                )
                messages.success(request, 'Laundry berhasil didaftarkan! Sekarang Anda dapat menerima pesanan.')
            
            return redirect('core:mitra_dashboard')
        
        # GET request - show form
        context = {
            'existing_laundry': existing_laundry,
        }
        return render(request, 'partners/register_laundry.html', context)
        
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('core:mitra_dashboard')

@login_required
def edit_laundry(request, laundry_id):
    """Edit existing laundry (alias for register_laundry with specific ID)"""
    return register_laundry(request)

# ==================== VOUCHER VIEWS ====================

@login_required
def voucher_request_list(request):
    """Mitra melihat daftar voucher request mereka"""
    if request.user.role != 'mitra':
        messages.error(request, 'Akses ditolak')
        return redirect('core:dashboard')
    
    mitra_profile = request.user.mitra_profile
    laundries = mitra_profile.laundries.all()
    
    voucher_requests = VoucherRequest.objects.filter(
        mitra=mitra_profile
    ).select_related('laundry', 'created_voucher')
    
    context = {
        'voucher_requests': voucher_requests,
        'laundries': laundries,
    }
    return render(request, 'partners/voucher_request_list.html', context)

@login_required
def create_voucher_request(request):
    """Mitra membuat request voucher baru"""
    if request.user.role != 'mitra':
        messages.error(request, 'Akses ditolak')
        return redirect('core:dashboard')
    
    mitra_profile = request.user.mitra_profile
    laundries = mitra_profile.laundries.all()
    
    if not laundries.exists():
        messages.error(request, 'Anda harus memiliki laundry terlebih dahulu')
        return redirect('core:mitra_dashboard')
    
    if request.method == 'POST':
        laundry_id = request.POST.get('laundry')
        voucher_type = request.POST.get('voucher_type')
        voucher_name = request.POST.get('voucher_name')
        discount_value = request.POST.get('discount_value')
        min_order_kg = request.POST.get('min_order_kg', 0)
        total_quota = request.POST.get('total_quota', 100)
        duration_days = request.POST.get('duration_days', 30)
        reason = request.POST.get('reason')
        
        try:
            laundry = Laundry.objects.get(id=laundry_id, mitra=mitra_profile)
            
            voucher_request = VoucherRequest.objects.create(
                laundry=laundry,
                mitra=mitra_profile,
                voucher_type=voucher_type,
                voucher_name=voucher_name,
                discount_value=discount_value,
                min_order_kg=min_order_kg,
                total_quota=total_quota,
                duration_days=duration_days,
                reason=reason
            )
            
            messages.success(request, 'Request voucher berhasil dikirim. Menunggu persetujuan admin.')
            return redirect('partners:voucher_request_list')
            
        except Laundry.DoesNotExist:
            messages.error(request, 'Laundry tidak ditemukan')
        except Exception as e:
            messages.error(request, f'Gagal membuat request: {str(e)}')
    
    # Preset options untuk voucher
    voucher_presets = {
        'free_shipping': [
            {'name': 'Free Ongkir - Min 3kg', 'value': 0, 'min_kg': 3},
            {'name': 'Free Ongkir - Min 5kg', 'value': 0, 'min_kg': 5},
        ],
        'percentage_discount': [
            {'name': 'Diskon 10%', 'value': 10, 'min_kg': 2},
            {'name': 'Diskon 15%', 'value': 15, 'min_kg': 3},
            {'name': 'Diskon 20%', 'value': 20, 'min_kg': 5},
            {'name': 'Diskon 25%', 'value': 25, 'min_kg': 10},
        ],
        'fixed_discount': [
            {'name': 'Diskon Rp 5.000', 'value': 5000, 'min_kg': 2},
            {'name': 'Diskon Rp 10.000', 'value': 10000, 'min_kg': 3},
            {'name': 'Diskon Rp 15.000', 'value': 15000, 'min_kg': 5},
            {'name': 'Diskon Rp 20.000', 'value': 20000, 'min_kg': 10},
        ],
        'free_kg': [
            {'name': 'Gratis 1 KG', 'value': 1, 'min_kg': 5},
            {'name': 'Gratis 2 KG', 'value': 2, 'min_kg': 10},
        ],
    }
    
    context = {
        'laundries': laundries,
        'voucher_presets': voucher_presets,
    }
    return render(request, 'partners/create_voucher_request.html', context)

@login_required
def admin_voucher_requests(request):
    """Admin melihat semua voucher requests"""
    if request.user.role != 'admin':
        messages.error(request, 'Akses ditolak')
        return redirect('core:dashboard')
    
    status_filter = request.GET.get('status', 'all')
    
    voucher_requests = VoucherRequest.objects.select_related(
        'laundry', 'mitra', 'reviewed_by'
    ).order_by('-created_at')
    
    if status_filter != 'all':
        voucher_requests = voucher_requests.filter(status=status_filter)
    
    pending_count = VoucherRequest.objects.filter(status='pending').count()
    
    context = {
        'voucher_requests': voucher_requests,
        'status_filter': status_filter,
        'pending_count': pending_count,
    }
    return render(request, 'partners/admin_voucher_requests.html', context)

@login_required
def approve_voucher_request(request, request_id):
    """Admin approve voucher request"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Akses ditolak'})
    
    if request.method == 'POST':
        try:
            voucher_request = get_object_or_404(VoucherRequest, id=request_id)
            
            if voucher_request.status != 'pending':
                return JsonResponse({'success': False, 'error': 'Request sudah diproses'})
            
            # Generate voucher code
            voucher_code = f"{voucher_request.laundry.name[:3].upper()}{uuid.uuid4().hex[:6].upper()}"
            
            # Create voucher
            now = timezone.now()
            valid_until = now + timedelta(days=voucher_request.duration_days)
            
            voucher = Voucher.objects.create(
                laundry=voucher_request.laundry,
                code=voucher_code,
                name=voucher_request.voucher_name,
                description=f"Voucher {voucher_request.get_voucher_type_display()} - {voucher_request.laundry.name}",
                voucher_type=voucher_request.voucher_type,
                discount_value=voucher_request.discount_value,
                min_order_kg=voucher_request.min_order_kg,
                total_quota=voucher_request.total_quota,
                valid_from=now,
                valid_until=valid_until,
                is_active=True,
                is_approved=True,
                approved_by=request.user,
                approved_at=now
            )
            
            # Update request
            voucher_request.status = 'approved'
            voucher_request.reviewed_by = request.user
            voucher_request.reviewed_at = now
            voucher_request.created_voucher = voucher
            voucher_request.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Voucher berhasil disetujui',
                'voucher_code': voucher_code
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

@login_required
def reject_voucher_request(request, request_id):
    """Admin reject voucher request"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Akses ditolak'})
    
    if request.method == 'POST':
        try:
            voucher_request = get_object_or_404(VoucherRequest, id=request_id)
            
            if voucher_request.status != 'pending':
                return JsonResponse({'success': False, 'error': 'Request sudah diproses'})
            
            admin_notes = request.POST.get('notes', '')
            
            voucher_request.status = 'rejected'
            voucher_request.reviewed_by = request.user
            voucher_request.reviewed_at = timezone.now()
            voucher_request.admin_notes = admin_notes
            voucher_request.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Request voucher ditolak'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

@login_required
def laundry_detail(request, laundry_id):
    """Preview page laundry dengan pricelist, map, vouchers, reviews"""
    from orders.models import Review
    from django.db.models import Avg, Count
    
    laundry = get_object_or_404(Laundry, id=laundry_id, is_active=True)
    
    # Calculate distance from user location (if provided in session)
    distance = None
    user_lat = request.session.get('user_latitude')
    user_lon = request.session.get('user_longitude')
    
    if user_lat and user_lon and laundry.latitude and laundry.longitude:
        try:
            distance = laundry.calculate_distance(float(user_lat), float(user_lon))
        except (ValueError, TypeError):
            distance = None
    
    # Get active vouchers
    active_vouchers = laundry.vouchers.filter(
        is_active=True,
        is_approved=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now()
    )
    
    # Get images
    images = laundry.images.all()[:15]
    
    # Get approved reviews (don't slice yet - we need to filter for rating breakdown)
    all_reviews = Review.objects.filter(
        laundry=laundry,
        is_approved=True
    ).select_related('user', 'order').order_by('-created_at')
    
    # Calculate rating breakdown using the full queryset
    rating_breakdown = []
    total_reviews = all_reviews.count()
    
    if total_reviews > 0:
        for star in range(5, 0, -1):
            count = all_reviews.filter(rating=star).count()
            percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
            rating_breakdown.append({
                'rating': star,
                'count': count,
                'percentage': percentage
            })
    
    # Now slice the reviews for display (limit to 20)
    reviews = all_reviews[:20]
    
    # Calculate estimated delivery in hours
    estimated_delivery_hours = round(laundry.estimated_delivery_time / 60, 1) if laundry.estimated_delivery_time else 0
    
    context = {
        'laundry': laundry,
        'distance': distance,
        'vouchers': active_vouchers,
        'images': images,
        'reviews': reviews,
        'rating_breakdown': rating_breakdown,
        'total_reviews': total_reviews,
        'estimated_delivery_hours': estimated_delivery_hours,
    }
    return render(request, 'partners/laundry_detail.html', context)

@login_required
def upload_laundry_images(request, laundry_id):
    """Mitra upload images untuk laundry (max 15)"""
    if request.user.role != 'mitra':
        messages.error(request, 'Akses ditolak')
        return redirect('core:dashboard')
    
    laundry = get_object_or_404(
        Laundry, 
        id=laundry_id, 
        mitra=request.user.mitra_profile
    )
    
    if request.method == 'POST':
        files = request.FILES.getlist('images')
        
        # Check current image count
        current_count = laundry.images.count()
        remaining_slots = 15 - current_count
        
        if len(files) > remaining_slots:
            messages.error(request, f'Maksimal {remaining_slots} gambar lagi. Anda memiliki {current_count}/15 gambar.')
            return redirect('partners:upload_laundry_images', laundry_id=laundry_id)
        
        uploaded = 0
        for idx, file in enumerate(files):
            # Validate file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                messages.warning(request, f'{file.name} terlalu besar (max 5MB)')
                continue
            
            # Validate file type - check MIME type AND extension
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            
            if file.content_type not in allowed_types:
                messages.warning(request, f'{file.name} format tidak didukung. Gunakan JPG, PNG, atau WEBP')
                continue
            
            # Double-check extension
            import os
            file_extension = os.path.splitext(file.name)[1].lower()
            if file_extension not in allowed_extensions:
                messages.warning(request, f'{file.name} ekstensi file tidak valid')
                continue
            
            LaundryImage.objects.create(
                laundry=laundry,
                image=file,
                order=current_count + idx,
                is_primary=(current_count == 0 and idx == 0)
            )
            uploaded += 1
        
        if uploaded > 0:
            messages.success(request, f'{uploaded} gambar berhasil diupload')
        
        return redirect('partners:upload_laundry_images', laundry_id=laundry_id)
    
    images = laundry.images.all()
    
    context = {
        'laundry': laundry,
        'images': images,
        'remaining_slots': 15 - images.count(),
    }
    return render(request, 'partners/upload_laundry_images.html', context)

@login_required
def delete_laundry_image(request, image_id):
    """Delete laundry image"""
    if request.user.role != 'mitra':
        return JsonResponse({'success': False, 'error': 'Akses ditolak'})
    
    if request.method == 'POST':
        try:
            image = get_object_or_404(
                LaundryImage, 
                id=image_id,
                laundry__mitra=request.user.mitra_profile
            )
            image.delete()
            
            return JsonResponse({'success': True, 'message': 'Gambar berhasil dihapus'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@login_required
def update_laundry_status(request):
    """Update laundry operational status (Buka/Full/Tutup/Istirahat)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    if request.user.role != 'mitra':
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    try:
        import json
        data = json.loads(request.body)
        new_status = data.get('status')
        
        # Validate status
        valid_statuses = ['buka', 'full', 'tutup', 'istirahat']
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status'})
        
        # Get mitra's laundry
        mitra_profile = request.user.mitra_profile
        laundry = mitra_profile.laundries.first()
        
        if not laundry:
            return JsonResponse({'success': False, 'error': 'Laundry tidak ditemukan'})
        
        # Update status
        laundry.status = new_status
        laundry.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Status berhasil diubah menjadi {new_status}',
            'status': new_status
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def submit_mitra_verification(request):
    """Multi-step form for mitra verification"""
    # Check if user already has verification pending or approved
    try:
        verification = request.user.mitra_verification
        if verification.status == 'approved':
            messages.info(request, 'Verifikasi Anda sudah disetujui')
            return redirect('core:mitra_dashboard')
        elif verification.status == 'pending':
            messages.info(request, 'Verifikasi Anda sedang dalam proses review')
            return redirect('core:dashboard')
    except MitraVerification.DoesNotExist:
        pass
    
    if request.method == 'POST':
        # Personal Identity
        full_name = request.POST.get('full_name')
        ktp_number = request.POST.get('ktp_number')
        ktp_image = request.FILES.get('ktp_image')
        selfie_with_ktp = request.FILES.get('selfie_with_ktp')
        
        # Business Information
        business_name = request.POST.get('business_name')
        business_address = request.POST.get('business_address')
        business_phone = request.POST.get('business_phone')
        store_front_photo = request.FILES.get('store_front_photo')
        store_interior_photo = request.FILES.get('store_interior_photo')
        equipment_photo = request.FILES.get('equipment_photo')
        
        # Bank Account
        bank_name = request.POST.get('bank_name')
        bank_account_number = request.POST.get('bank_account_number')
        bank_account_name = request.POST.get('bank_account_name')
        bank_account_proof = request.FILES.get('bank_account_proof')
        
        # Additional Info
        years_of_experience = request.POST.get('years_of_experience', 0)
        daily_capacity_kg = request.POST.get('daily_capacity_kg', 50.0)
        additional_notes = request.POST.get('additional_notes', '')
        
        # Create verification
        MitraVerification.objects.create(
            user=request.user,
            full_name=full_name,
            ktp_number=ktp_number,
            ktp_image=ktp_image,
            selfie_with_ktp=selfie_with_ktp,
            business_name=business_name,
            business_address=business_address,
            business_phone=business_phone,
            store_front_photo=store_front_photo,
            store_interior_photo=store_interior_photo,
            equipment_photo=equipment_photo,
            bank_name=bank_name,
            bank_account_number=bank_account_number,
            bank_account_name=bank_account_name,
            bank_account_proof=bank_account_proof,
            years_of_experience=years_of_experience,
            daily_capacity_kg=daily_capacity_kg,
            additional_notes=additional_notes,
            status='pending'
        )
        
        messages.success(request, 'Pengajuan verifikasi berhasil dikirim. Mohon tunggu verifikasi admin (maks 3x24 jam)')
        return redirect('core:dashboard')
    
    return render(request, 'partners/submit_verification.html')


@login_required
def admin_mitra_verifications(request):
    """Admin dashboard to verify mitra applications"""
    if request.user.role != 'admin':
        messages.error(request, 'Akses ditolak. Hanya admin yang dapat mengakses halaman ini.')
        return redirect('core:dashboard')
    
    pending_verifications = MitraVerification.objects.filter(status='pending').select_related('user')
    approved_verifications = MitraVerification.objects.filter(status='approved').select_related('user')[:20]
    rejected_verifications = MitraVerification.objects.filter(status='rejected').select_related('user')[:20]
    
    context = {
        'pending_verifications': pending_verifications,
        'approved_verifications': approved_verifications,
        'rejected_verifications': rejected_verifications,
    }
    return render(request, 'partners/admin_mitra_verifications.html', context)


@login_required
def verify_mitra(request, verification_id):
    """Admin action to approve or reject mitra verification"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)
    
    verification = get_object_or_404(MitraVerification, id=verification_id)
    action = request.POST.get('action')  # 'approve' or 'reject'
    admin_notes = request.POST.get('admin_notes', '')
    
    if action == 'approve':
        verification.status = 'approved'
        verification.verified_by = request.user
        verification.verified_at = timezone.now()
        verification.admin_notes = admin_notes
        verification.save()
        
        # Update user role to mitra
        verification.user.role = 'mitra'
        verification.user.save()
        
        # Create MitraProfile if doesn't exist
        from .models import MitraProfile
        if not hasattr(verification.user, 'mitra_profile'):
            MitraProfile.objects.create(
                user=verification.user,
                business_name=verification.business_name,
                location=verification.business_address,
                description=f'Pengalaman {verification.years_of_experience} tahun. Kapasitas {verification.daily_capacity_kg} kg/hari.',
                operational_cost=0
            )
        
        messages.success(request, f'Verifikasi untuk {verification.business_name} telah disetujui')
        
    elif action == 'reject':
        verification.status = 'rejected'
        verification.verified_by = request.user
        verification.verified_at = timezone.now()
        verification.admin_notes = admin_notes
        verification.save()
        
        messages.warning(request, f'Verifikasi untuk {verification.business_name} ditolak')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Verification updated successfully',
            'status': verification.status
        })
    
    return redirect('partners:admin_mitra_verifications')


@login_required
def mitra_earnings(request):
    """Mitra earnings dashboard showing pending and completed transfers"""
    if request.user.role != 'mitra':
        messages.error(request, 'Akses ditolak. Halaman ini hanya untuk mitra.')
        return redirect('core:dashboard')
    
    mitra_profile = request.user.mitra_profile
    
    # Get all transactions
    transactions = MitraTransaction.objects.filter(mitra=mitra_profile).select_related('order')
    
    # Calculate totals
    pending_transactions = transactions.filter(status='pending')
    processing_transactions = transactions.filter(status='processing')
    completed_transactions = transactions.filter(status='completed')
    
    total_pending = pending_transactions.aggregate(total=Sum('mitra_earning'))['total'] or 0
    total_processing = processing_transactions.aggregate(total=Sum('mitra_earning'))['total'] or 0
    total_completed = completed_transactions.aggregate(total=Sum('mitra_earning'))['total'] or 0
    total_earnings = total_completed
    
    context = {
        'pending_transactions': pending_transactions,
        'processing_transactions': processing_transactions,
        'completed_transactions': completed_transactions[:20],  # Latest 20
        'total_pending': total_pending,
        'total_processing': total_processing,
        'total_earnings': total_earnings,
    }
    return render(request, 'partners/mitra_earnings.html', context)


@login_required
def admin_process_transfers(request):
    """Admin dashboard to process mitra transfers"""
    if request.user.role != 'admin':
        messages.error(request, 'Akses ditolak. Hanya admin yang dapat mengakses halaman ini.')
        return redirect('core:dashboard')
    
    pending_transactions = MitraTransaction.objects.filter(
        status='pending'
    ).select_related('order', 'mitra').order_by('-created_at')
    
    processing_transactions = MitraTransaction.objects.filter(
        status='processing'
    ).select_related('order', 'mitra').order_by('-processed_at')[:20]
    
    completed_transactions = MitraTransaction.objects.filter(
        status='completed'
    ).select_related('order', 'mitra').order_by('-completed_at')[:20]
    
    # Calculate totals
    total_pending = pending_transactions.aggregate(total=Sum('mitra_earning'))['total'] or 0
    total_processing = processing_transactions.aggregate(total=Sum('mitra_earning'))['total'] or 0
    total_completed_today = MitraTransaction.objects.filter(
        status='completed',
        completed_at__date=timezone.now().date()
    ).aggregate(total=Sum('mitra_earning'))['total'] or 0
    
    context = {
        'pending_transactions': pending_transactions,
        'processing_transactions': processing_transactions,
        'completed_transactions': completed_transactions,
        'total_pending': total_pending,
        'total_processing': total_processing,
        'total_completed_today': total_completed_today,
    }
    return render(request, 'partners/admin_process_transfers.html', context)


@login_required
def process_transfer(request, transaction_id):
    """Admin action to process or complete transfer"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)
    
    transaction = get_object_or_404(MitraTransaction, id=transaction_id)
    action = request.POST.get('action')  # 'process' or 'complete'
    transfer_reference = request.POST.get('transfer_reference', '')
    transfer_notes = request.POST.get('transfer_notes', '')
    
    if action == 'process':
        transaction.status = 'processing'
        transaction.processed_by = request.user
        transaction.processed_at = timezone.now()
        transaction.transfer_reference = transfer_reference
        transaction.transfer_notes = transfer_notes
        transaction.save()
        
        messages.success(request, f'Transfer untuk order {transaction.order.order_number} sedang diproses')
        
    elif action == 'complete':
        transaction.status = 'completed'
        transaction.completed_at = timezone.now()
        if transfer_reference:
            transaction.transfer_reference = transfer_reference
        if transfer_notes:
            transaction.transfer_notes = transfer_notes
        transaction.save()
        
        messages.success(request, f'Transfer untuk order {transaction.order.order_number} selesai')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Transfer updated successfully',
            'status': transaction.status
        })
    
    return redirect('partners:admin_process_transfers')
