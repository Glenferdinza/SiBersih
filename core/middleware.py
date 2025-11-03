from django.utils.deprecation import MiddlewareMixin

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https: http:; "
            "frame-src https://www.google.com; "
            "connect-src 'self' https://*.tile.openstreetmap.org https://unpkg.com https://nominatim.openstreetmap.org;"
        )
        
        return response

class RoleBasedAccessMiddleware(MiddlewareMixin):
    """Enforce role-based access control"""
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip for non-authenticated requests
        if not request.user.is_authenticated:
            return None
        
        path = request.path
        user_role = getattr(request.user, 'role', 'user')
        
        # Admin-only paths
        admin_paths = ['/admin-dashboard/', '/admin/export/']
        if any(path.startswith(p) for p in admin_paths):
            if user_role != 'admin':
                from django.shortcuts import redirect
                from django.contrib import messages
                messages.error(request, 'Unauthorized access')
                return redirect('core:dashboard')
        
        # Mitra-only paths
        mitra_paths = ['/mitra-dashboard/']
        if any(path.startswith(p) for p in mitra_paths):
            if user_role != 'mitra':
                from django.shortcuts import redirect
                from django.contrib import messages
                messages.error(request, 'Unauthorized access')
                return redirect('core:dashboard')
        
        return None
