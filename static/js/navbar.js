// Navbar Scroll Effect - Transparent to Solid
window.addEventListener('scroll', function() {
    const navbar = document.getElementById('mainNav');
    if (navbar && window.scrollY > 50) {
        navbar.classList.add('navbar-scrolled');
    } else if (navbar) {
        navbar.classList.remove('navbar-scrolled');
    }
});

// Mobile Menu Toggle
const navToggle = document.getElementById('navToggle');
const navMenu = document.getElementById('navMenu');

if (navToggle) {
    navToggle.addEventListener('click', function() {
        navToggle.classList.toggle('active');
        navMenu.classList.toggle('active');
        document.body.classList.toggle('menu-open');
    });
}

// Close menu when clicking outside
document.addEventListener('click', function(event) {
    if (!navMenu || !navToggle) return; // Guard clause
    
    const isClickInsideNav = navMenu.contains(event.target) || navToggle.contains(event.target);
    
    if (!isClickInsideNav && navMenu.classList.contains('active')) {
        navToggle.classList.remove('active');
        navMenu.classList.remove('active');
        document.body.classList.remove('menu-open');
    }
});

// Close menu on link click (mobile)
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
    link.addEventListener('click', function() {
        if (navToggle && navMenu && window.innerWidth <= 768) {
            navToggle.classList.remove('active');
            navMenu.classList.remove('active');
            document.body.classList.remove('menu-open');
        }
    });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
