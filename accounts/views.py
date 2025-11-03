from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User

def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        if password != password2:
            messages.error(request, 'Password tidak cocok')
            return redirect('accounts:register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan')
            return redirect('accounts:register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah digunakan')
            return redirect('accounts:register')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            address=address
        )
        
        messages.success(request, 'Registrasi berhasil! Silakan login.')
        return redirect('accounts:login')
    
    return render(request, 'accounts/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'core:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Username atau password salah')
            return redirect('accounts:login')
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logout berhasil')
    return redirect('core:home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.address = request.POST.get('address', user.address)
        
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        messages.success(request, 'Profil berhasil diperbarui')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile.html')

@login_required
def settings_view(request):
    # Import di sini untuk menghindari circular import
    from partners.models import MitraRequest
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        user = request.user
        
        # Jika user ingin jadi mitra
        if new_role == 'mitra' and user.role == 'user':
            # Cek apakah ada request yang approved
            approved_request = MitraRequest.objects.filter(
                user=user, 
                status='approved'
            ).first()
            
            if approved_request:
                # Jika sudah approved, langsung ubah role
                user.role = 'mitra'
                user.save()
                messages.success(request, 'Role berhasil diubah ke Mitra. Selamat datang!')
                return redirect('core:dashboard')
            else:
                # Jika belum approved, redirect ke form apply
                messages.info(request, 'Silakan lengkapi formulir pendaftaran mitra terlebih dahulu.')
                return redirect('partners:apply_mitra')
        
        # Jika mitra ingin jadi user (downgrade), langsung ijinkan
        if new_role == 'user' and user.role == 'mitra':
            user.role = 'user'
            user.save()
            messages.success(request, 'Role berhasil diubah ke User')
            return redirect('core:dashboard')
        
        # Jika tidak ada perubahan atau invalid
        messages.error(request, 'Tidak ada perubahan role atau role tidak valid')
        return redirect('accounts:settings')
    
    # Cek status aplikasi mitra jika ada
    from partners.models import MitraRequest
    mitra_request = None
    if request.user.role == 'user':
        mitra_request = MitraRequest.objects.filter(user=request.user).order_by('-created_at').first()
    
    context = {
        'mitra_request': mitra_request
    }
    
    return render(request, 'accounts/settings.html', context)

