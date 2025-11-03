from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Order, Service, OrderStatusHistory, TransactionLog, Payment, PaymentIssue
from partners.models import MitraProfile, Laundry, CODRate, MitraTransaction
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

@login_required
def create_order(request):
    # Get laundry_id from URL parameter
    laundry_id = request.GET.get('laundry')
    
    # If no laundry selected, redirect to dashboard to choose one
    if not laundry_id:
        messages.info(request, 'Silakan pilih laundry terlebih dahulu')
        return redirect('core:dashboard')
    
    selected_laundry = get_object_or_404(Laundry, id=laundry_id, is_active=True)
    
    if request.method == 'POST':
        laundry_id = request.POST.get('laundry')
        weight_kg = request.POST.get('weight_kg')
        delivery_address = request.POST.get('delivery_address')
        pickup_time = request.POST.get('pickup_time')
        notes = request.POST.get('notes', '')
        payment_method = request.POST.get('payment_method', 'cod')
        
        # Validate required fields
        if not all([laundry_id, weight_kg, delivery_address, pickup_time]):
            messages.error(request, 'Semua field harus diisi')
            return redirect('orders:create_order')
        
        # Validate weight
        try:
            weight = Decimal(weight_kg)
            if weight <= 0:
                messages.error(request, 'Berat harus lebih dari 0 kg')
                return redirect('orders:create_order')
            if weight > 1000:  # Sanity check
                messages.error(request, 'Berat maksimal 1000 kg')
                return redirect('orders:create_order')
        except (ValueError, InvalidOperation):
            messages.error(request, 'Berat tidak valid')
            return redirect('orders:create_order')
        
        # Get user coordinates (for now, use default Yogyakarta city center)
        # TODO: Implement user geolocation
        user_lat = Decimal('-7.797068')  # Yogyakarta city center
        user_lon = Decimal('110.370529')
        
        try:
            laundry = get_object_or_404(Laundry, id=laundry_id, is_active=True)
        except:
            messages.error(request, 'Laundry tidak ditemukan')
            return redirect('orders:create_order')
        
        # Calculate distance
        distance_km = laundry.calculate_distance(user_lat, user_lon)
        
        # Calculate pricing
        laundry_price = laundry.price_per_kg * weight
        cod_fee = Decimal(str(CODRate.get_fee_for_distance(distance_km)))
        platform_fee = laundry_price * Decimal('0.03')  # 3% platform fee
        total_price = laundry_price + cod_fee + platform_fee
        
        # Set estimated delivery (3 days from now)
        estimated_delivery = datetime.now() + timedelta(days=3)
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            laundry=laundry,
            mitra=laundry.mitra,
            weight_kg=weight,
            delivery_address=delivery_address,
            pickup_time=pickup_time,
            distance_km=distance_km,
            laundry_price=laundry_price,
            cod_fee=cod_fee,
            platform_fee=platform_fee,
            total_price=total_price,
            payment_method=payment_method,
            estimated_delivery=estimated_delivery,
            notes=notes,
            status='pending'
        )
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            notes='Pesanan dibuat melalui marketplace',
            changed_by=request.user
        )
        
        # Create transaction log
        TransactionLog.objects.create(
            order=order,
            action='ORDER_CREATED',
            description=f'Order created for {laundry.name} - {weight}kg',
            performed_by=request.user
        )
        
        messages.success(request, f'Pesanan berhasil dibuat! No. Order: {order.order_number}')
        
        # If payment is not COD, redirect to upload payment proof
        if payment_method != 'cod':
            return redirect('orders:upload_payment', order_number=order.order_number)
        
        return redirect('orders:track_order', order_number=order.order_number)
    
    # Get user coordinates (use session or default)
    user_lat = request.session.get('user_latitude', -7.797068)  # Yogyakarta default
    user_lon = request.session.get('user_longitude', 110.370529)
    
    # Calculate distance for selected laundry
    distance = selected_laundry.calculate_distance(float(user_lat), float(user_lon))
    selected_laundry.distance = distance
    
    # Get COD rates for display
    cod_rates = CODRate.objects.filter(is_active=True).order_by('min_distance_km')
    
    context = {
        'selected_laundry': selected_laundry,
        'cod_rates': cod_rates,
        'user_lat': user_lat,
        'user_lon': user_lon,
    }
    return render(request, 'orders/create_order.html', context)

@login_required
def track_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    
    # Authorization check based on role
    if request.user.role == 'user':
        # Users can only view their own orders
        if order.user != request.user:
            messages.error(request, 'Anda tidak memiliki akses ke pesanan ini')
            return redirect('core:dashboard')
    elif request.user.role == 'mitra':
        # Mitras can only view orders from their laundry
        try:
            mitra_profile = request.user.mitra_profile
            if order.mitra != mitra_profile:
                messages.error(request, 'Pesanan ini bukan dari laundry Anda')
                return redirect('core:mitra_dashboard')
        except:
            messages.error(request, 'Akses ditolak')
            return redirect('core:dashboard')
    elif request.user.role != 'admin':
        # Only admin, user, mitra allowed
        messages.error(request, 'Akses ditolak')
        return redirect('core:dashboard')
    
    status_history = order.status_history.all()
    
    context = {
        'order': order,
        'status_history': status_history
    }
    return render(request, 'orders/track_order.html', context)

@login_required
def confirm_delivery(request, order_number):
    """User confirms that their laundry has been delivered"""
    if request.user.role != 'user':
        messages.error(request, 'Unauthorized access')
        return redirect('core:dashboard')
    
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Only allow confirmation if order is ready or in_transit
    if order.status not in ['ready', 'in_transit']:
        messages.error(request, 'Pesanan tidak dapat dikonfirmasi pada status saat ini')
        return redirect('orders:my_orders')
    
    if request.method == 'POST':
        # Update order status to delivered
        order.status = 'delivered'
        order.actual_delivery = timezone.now()
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='delivered',
            notes='Konfirmasi penerimaan oleh customer',
            changed_by=request.user
        )
        
        # Create transaction log
        TransactionLog.objects.create(
            order=order,
            action='DELIVERY_CONFIRMED',
            description=f'Customer confirmed delivery of order {order.order_number}',
            performed_by=request.user
        )
        
        messages.success(request, 'Terima kasih! Pesanan telah dikonfirmasi. Silahkan berikan review untuk laundry ini.')
        return redirect('orders:submit_review', order_number=order.order_number)
    
    context = {'order': order}
    return render(request, 'orders/confirm_delivery.html', context)

@login_required
def my_orders(request):
    """User's orders page with tabs (all, processing, in-transit, completed, cancelled)"""
    if request.user.role != 'user':
        messages.error(request, 'Halaman ini hanya untuk pelanggan')
        return redirect('core:dashboard')
    
    # Get all user orders
    all_orders = Order.objects.filter(user=request.user).select_related('laundry', 'mitra').order_by('-created_at')
    
    # Separate by status for tabs
    orders_processing = all_orders.filter(status__in=['pending', 'processing', 'picked_up'])
    orders_in_transit = all_orders.filter(status__in=['ready', 'in_transit'])
    orders_completed = all_orders.filter(status='delivered')
    orders_cancelled = all_orders.filter(status='cancelled')
    
    context = {
        'all_orders': all_orders,
        'orders_processing': orders_processing,
        'orders_in_transit': orders_in_transit,
        'orders_completed': orders_completed,
        'orders_cancelled': orders_cancelled,
    }
    return render(request, 'orders/my_orders.html', context)


@login_required
def order_history(request):
    """Legacy view - redirect to my_orders for users"""
    if request.user.role == 'user':
        return redirect('orders:my_orders')
    elif request.user.role == 'mitra':
        mitra_profile = request.user.mitra_profile
        orders = Order.objects.filter(mitra=mitra_profile)
    elif request.user.role == 'admin':
        orders = Order.objects.all()
    else:
        orders = Order.objects.none()
    
    context = {'orders': orders}
    return render(request, 'orders/order_history.html', context)

@login_required
def update_order_status(request, order_id):
    if request.user.role not in ['mitra', 'admin']:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        order.status = new_status
        order.save()
        
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            notes=notes,
            changed_by=request.user
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Status berhasil diperbarui',
                'new_status': order.get_status_display()
            })
        
        messages.success(request, 'Status pesanan berhasil diperbarui')
        return redirect('orders:track_order', order_number=order.order_number)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
def upload_payment(request, order_number):
    """Upload payment proof for online payment methods"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Check if payment method is online (not COD)
    if order.payment_method == 'cod':
        messages.error(request, 'Pesanan COD tidak memerlukan upload bukti pembayaran')
        return redirect('orders:track_order', order_number=order.order_number)
    
    # Check if payment already exists
    try:
        payment = order.payment
        if payment.status == 'verified':
            messages.info(request, 'Pembayaran sudah terverifikasi')
            return redirect('orders:track_order', order_number=order.order_number)
    except Payment.DoesNotExist:
        payment = None
    
    if request.method == 'POST':
        proof_image = request.FILES.get('proof_image')
        
        if not proof_image:
            messages.error(request, 'Harap upload bukti pembayaran')
            return redirect('orders:upload_payment', order_number=order_number)
        
        # Validate file size (max 5MB)
        if proof_image.size > 5 * 1024 * 1024:
            messages.error(request, 'Ukuran file terlalu besar (maksimal 5MB)')
            return redirect('orders:upload_payment', order_number=order_number)
        
        # Validate file type (only images)
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if proof_image.content_type not in allowed_types:
            messages.error(request, 'Format file tidak didukung. Gunakan JPG, PNG, atau WEBP')
            return redirect('orders:upload_payment', order_number=order_number)
        
        # Create or update payment
        if payment:
            payment.proof_image = proof_image
            payment.status = 'pending'
            payment.save()
            messages.success(request, 'Bukti pembayaran berhasil diupdate. Menunggu verifikasi admin.')
        else:
            Payment.objects.create(
                order=order,
                payment_method=order.payment_method,
                amount=order.total_price,
                proof_image=proof_image,
                status='pending'
            )
            messages.success(request, 'Bukti pembayaran berhasil diupload. Menunggu verifikasi admin.')
        
        # Create transaction log
        TransactionLog.objects.create(
            order=order,
            action='PAYMENT_PROOF_UPLOADED',
            description=f'Payment proof uploaded for {order.payment_method}',
            performed_by=request.user
        )
        
        return redirect('orders:track_order', order_number=order.order_number)
    
    # Get payment method name
    payment_method_names = {
        'qris': 'QRIS / QR Code',
        'bri': 'Bank BRI',
        'bca': 'Bank BCA',
        'seabank': 'SeaBank',
        'shopee': 'ShopeePay',
    }
    
    context = {
        'order': order,
        'payment': payment,
        'payment_method_name': payment_method_names.get(order.payment_method, order.payment_method.upper())
    }
    return render(request, 'orders/upload_payment.html', context)


@login_required
def admin_verify_payments(request):
    """Admin dashboard to verify payments"""
    if request.user.role != 'admin':
        messages.error(request, 'Akses ditolak. Hanya admin yang dapat mengakses halaman ini.')
        return redirect('core:dashboard')
    
    # Get all pending payments
    pending_payments = Payment.objects.filter(status='pending').select_related('order', 'order__user')
    verified_payments = Payment.objects.filter(status='verified').select_related('order', 'order__user')[:20]
    rejected_payments = Payment.objects.filter(status='rejected').select_related('order', 'order__user')[:20]
    
    context = {
        'pending_payments': pending_payments,
        'verified_payments': verified_payments,
        'rejected_payments': rejected_payments,
    }
    return render(request, 'orders/admin_verify_payments.html', context)


@login_required
def verify_payment(request, payment_id):
    """Admin action to verify or reject payment"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)
    
    payment = get_object_or_404(Payment, id=payment_id)
    action = request.POST.get('action')  # 'verify' or 'reject'
    admin_notes = request.POST.get('admin_notes', '')
    
    if action == 'verify':
        payment.status = 'verified'
        payment.verified_by = request.user
        payment.verified_at = timezone.now()
        payment.admin_notes = admin_notes
        payment.save()
        
        # Mark order as paid
        payment.order.is_paid = True
        payment.order.save()
        
        # Create MitraTransaction for payment distribution
        from partners.models import MitraTransaction
        
        # Get mitra's bank info from verification
        try:
            mitra_verification = payment.order.mitra.user.mitra_verification
            
            # Calculate amounts
            gross_amount = payment.order.total_price
            platform_fee = payment.order.platform_fee
            mitra_earning = gross_amount - platform_fee
            
            # Create transaction
            MitraTransaction.objects.create(
                order=payment.order,
                mitra=payment.order.mitra,
                gross_amount=gross_amount,
                platform_fee=platform_fee,
                mitra_earning=mitra_earning,
                bank_name=mitra_verification.get_bank_name_display(),
                bank_account_number=mitra_verification.bank_account_number,
                bank_account_name=mitra_verification.bank_account_name,
                status='pending'
            )
        except Exception as e:
            # Log error but don't block payment verification
            print(f"Error creating MitraTransaction: {e}")
        
        # Create transaction log
        TransactionLog.objects.create(
            order=payment.order,
            action='PAYMENT_VERIFIED',
            description=f'Payment verified by {request.user.username}',
            performed_by=request.user
        )
        
        messages.success(request, f'Pembayaran untuk order {payment.order.order_number} telah diverifikasi')
        
    elif action == 'reject':
        payment.status = 'rejected'
        payment.verified_by = request.user
        payment.verified_at = timezone.now()
        payment.admin_notes = admin_notes
        payment.save()
        
        # Create transaction log
        TransactionLog.objects.create(
            order=payment.order,
            action='PAYMENT_REJECTED',
            description=f'Payment rejected by {request.user.username}: {admin_notes}',
            performed_by=request.user
        )
        
        messages.warning(request, f'Pembayaran untuk order {payment.order.order_number} ditolak')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Payment updated successfully',
            'status': payment.status
        })
    
    return redirect('orders:admin_verify_payments')


@login_required
def report_payment_issue(request):
    """User form to report payment issues"""
    # Get user's orders for dropdown
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:20]
    
    if request.method == 'POST':
        order_id = request.POST.get('order')
        issue_type = request.POST.get('issue_type')
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        screenshot = request.FILES.get('screenshot')
        
        # Create issue
        order = None
        if order_id:
            order = get_object_or_404(Order, id=order_id, user=request.user)
        
        issue = PaymentIssue.objects.create(
            user=request.user,
            order=order,
            issue_type=issue_type,
            subject=subject,
            description=description,
            screenshot=screenshot
        )
        
        # Send email to CS
        try:
            email_subject = f'[{issue.ticket_number}] {subject}'
            email_body = f"""
Tiket Kendala Baru dari SiBersih

No. Tiket: {issue.ticket_number}
User: {request.user.username} ({request.user.email})
Order: {order.order_number if order else 'Tidak terkait order'}
Jenis Kendala: {issue.get_issue_type_display()}

Subjek: {subject}

Deskripsi:
{description}

---
Tanggapan dapat diberikan melalui dashboard admin SiBersih.
            """
            
            send_mail(
                subject=email_subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['contact.sibersih@gmail.com'],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {e}")
        
        messages.success(request, f'Laporan kendala Anda telah dikirim dengan nomor tiket {issue.ticket_number}. Tim CS kami akan segera merespons.')
        return redirect('orders:my_issues')
    
    context = {
        'user_orders': user_orders,
    }
    return render(request, 'orders/report_payment_issue.html', context)


@login_required
def my_issues(request):
    """User's submitted issues"""
    issues = PaymentIssue.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'issues': issues,
    }
    return render(request, 'orders/my_issues.html', context)


@login_required
def admin_payment_issues(request):
    """Admin dashboard to view and respond to payment issues"""
    if not request.user.is_staff:
        messages.error(request, 'Akses ditolak')
        return redirect('core:home')
    
    # Filter by status
    status_filter = request.GET.get('status', 'all')
    
    if status_filter == 'open':
        issues = PaymentIssue.objects.filter(status='open')
    elif status_filter == 'in_progress':
        issues = PaymentIssue.objects.filter(status='in_progress')
    elif status_filter == 'resolved':
        issues = PaymentIssue.objects.filter(status='resolved')
    elif status_filter == 'closed':
        issues = PaymentIssue.objects.filter(status='closed')
    else:
        issues = PaymentIssue.objects.all()
    
    issues = issues.order_by('-created_at')
    
    # Count by status
    open_count = PaymentIssue.objects.filter(status='open').count()
    in_progress_count = PaymentIssue.objects.filter(status='in_progress').count()
    resolved_count = PaymentIssue.objects.filter(status='resolved').count()
    
    context = {
        'issues': issues,
        'status_filter': status_filter,
        'open_count': open_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
    }
    return render(request, 'orders/admin_payment_issues.html', context)


@login_required
def respond_to_issue(request, issue_id):
    """Admin responds to a payment issue"""
    if not request.user.is_staff:
        messages.error(request, 'Akses ditolak')
        return redirect('core:home')
    
    issue = get_object_or_404(PaymentIssue, id=issue_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_response = request.POST.get('admin_response', '')
        
        if action == 'respond':
            issue.admin_response = admin_response
            issue.status = 'in_progress'
            issue.responded_by = request.user
            issue.responded_at = timezone.now()
            issue.save()
            
            # Send email to user
            try:
                send_mail(
                    subject=f'Re: [{issue.ticket_number}] {issue.subject}',
                    message=f"""
Halo {issue.user.username},

Terima kasih telah menghubungi SiBersih Customer Service.

Tiket Anda: {issue.ticket_number}
Subjek: {issue.subject}

Tanggapan dari Tim CS:
{admin_response}

---
Tim SiBersih
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[issue.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending email: {e}")
            
            messages.success(request, 'Tanggapan telah dikirim ke user')
            
        elif action == 'resolve':
            issue.status = 'resolved'
            issue.save()
            messages.success(request, 'Tiket ditandai sebagai selesai')
            
        elif action == 'close':
            issue.status = 'closed'
            issue.save()
            messages.success(request, 'Tiket ditutup')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return redirect('orders:admin_payment_issues')
    
    return redirect('orders:admin_payment_issues')


@login_required
def submit_review(request, order_number):
    """User submits review after order is delivered"""
    from .models import Review
    
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Check if order is delivered
    if order.status != 'delivered':
        messages.error(request, 'Review hanya dapat diberikan setelah pesanan selesai')
        return redirect('orders:track_order', order_number=order_number)
    
    # Check if review already exists
    try:
        existing_review = order.review
        messages.info(request, 'Anda sudah memberikan review untuk pesanan ini')
        return redirect('orders:my_orders')
    except Review.DoesNotExist:
        pass
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        service_quality = request.POST.get('service_quality', 5)
        cleanliness = request.POST.get('cleanliness', 5)
        speed = request.POST.get('speed', 5)
        
        # Handle photo uploads
        photo1 = request.FILES.get('photo1')
        photo2 = request.FILES.get('photo2')
        photo3 = request.FILES.get('photo3')
        
        # Validate photos
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        for photo in [photo1, photo2, photo3]:
            if photo:
                if photo.size > 5 * 1024 * 1024:  # 5MB
                    messages.error(request, f'File {photo.name} terlalu besar (maksimal 5MB)')
                    return redirect('orders:submit_review', order_number=order_number)
                
                if photo.content_type not in allowed_types:
                    messages.error(request, f'File {photo.name} format tidak didukung. Gunakan JPG, PNG, atau WEBP')
                    return redirect('orders:submit_review', order_number=order_number)
        
        # Create review
        review = Review.objects.create(
            order=order,
            user=request.user,
            laundry=order.laundry,
            rating=rating,
            comment=comment,
            service_quality=service_quality,
            cleanliness=cleanliness,
            speed=speed,
            photo1=photo1,
            photo2=photo2,
            photo3=photo3,
            is_approved=True  # Auto approve for now
        )
        
        # Create transaction log
        TransactionLog.objects.create(
            order=order,
            action='REVIEW_SUBMITTED',
            description=f'Review submitted with rating {rating}/5',
            performed_by=request.user
        )
        
        messages.success(request, 'Terima kasih! Review Anda telah berhasil dikirim.')
        return redirect('orders:my_orders')
    
    context = {
        'order': order,
    }
    return render(request, 'orders/submit_review.html', context)

