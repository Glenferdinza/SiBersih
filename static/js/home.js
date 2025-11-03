document.addEventListener('DOMContentLoaded', function() {
    gsap.registerPlugin(ScrollTrigger);
    
    const heroTitle = document.getElementById('heroTitle');
    const heroSubtitle = document.getElementById('heroSubtitle');
    
    if (heroTitle && heroSubtitle) {
        gsap.to(heroTitle, {
            opacity: 1,
            duration: 1,
            ease: 'power2.out'
        });
        
        gsap.to(heroSubtitle, {
            opacity: 1,
            duration: 1,
            delay: 0.5,
            ease: 'power2.out'
        });
    }
    
    const featureBoxes = document.querySelectorAll('.feature-box');
    featureBoxes.forEach((box, index) => {
        gsap.to(box, {
            scrollTrigger: {
                trigger: box,
                start: 'top 80%',
                end: 'top 50%',
                scrub: 1,
            },
            opacity: 1,
            y: 0,
            duration: 1,
            delay: index * 0.2
        });
    });
    
    const ctaSection = document.querySelector('.cta-section');
    if (ctaSection) {
        gsap.from('.cta-content', {
            scrollTrigger: {
                trigger: ctaSection,
                start: 'top 80%',
                end: 'top 50%',
                scrub: 1,
            },
            opacity: 0,
            y: 50,
            duration: 1
        });
    }

    // Testimonial Slider - Infinite Loop
    const sliderTrack = document.querySelector('.testimonials-track');
    const prevBtn = document.querySelector('.slider-btn-prev');
    const nextBtn = document.querySelector('.slider-btn-next');
    const dots = document.querySelectorAll('.dot');
    const testimonialCards = document.querySelectorAll('.testimonial-card');
    
    if (sliderTrack && testimonialCards.length > 0) {
        let currentIndex = 0;
        let cardsToShow = 3; // Always show 3 cards
        let autoPlayInterval;
        const totalCards = testimonialCards.length;
        
        // Clone cards for infinite loop
        testimonialCards.forEach(card => {
            const clone = card.cloneNode(true);
            sliderTrack.appendChild(clone);
        });
        
        // Update cards to show based on screen width
        function updateCardsToShow() {
            const width = window.innerWidth;
            if (width <= 768) {
                cardsToShow = 1;
            } else if (width <= 1024) {
                cardsToShow = 2;
            } else {
                cardsToShow = 3;
            }
            updateSlider();
        }
        
        // Update slider position
        function updateSlider(smooth = true) {
            const allCards = document.querySelectorAll('.testimonial-card');
            const cardWidth = allCards[0].offsetWidth;
            const gap = 32; // 2rem gap
            const offset = -(currentIndex * (cardWidth + gap));
            
            sliderTrack.style.transition = smooth ? 'transform 0.5s ease-in-out' : 'none';
            sliderTrack.style.transform = `translateX(${offset}px)`;
            
            // Update dots (loop back to start)
            const dotIndex = currentIndex % totalCards;
            dots.forEach((dot, index) => {
                dot.classList.toggle('active', index === dotIndex);
            });
        }
        
        // Next slide with infinite loop
        function nextSlide() {
            currentIndex++;
            updateSlider();
            
            // Reset to start after reaching clones
            if (currentIndex >= totalCards) {
                setTimeout(() => {
                    currentIndex = 0;
                    updateSlider(false);
                }, 500);
            }
        }
        
        // Previous slide with infinite loop
        function prevSlide() {
            if (currentIndex === 0) {
                currentIndex = totalCards;
                updateSlider(false);
                setTimeout(() => {
                    currentIndex--;
                    updateSlider();
                }, 20);
            } else {
                currentIndex--;
                updateSlider();
            }
        }
        
        // Go to specific slide
        function goToSlide(index) {
            currentIndex = index;
            updateSlider();
            resetAutoPlay();
        }
        
        // Auto-play
        function startAutoPlay() {
            autoPlayInterval = setInterval(() => {
                nextSlide();
            }, 5000); // Change every 5 seconds
        }
        
        function resetAutoPlay() {
            clearInterval(autoPlayInterval);
            startAutoPlay();
        }
        
        // Event listeners
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                nextSlide();
                resetAutoPlay();
            });
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                prevSlide();
                resetAutoPlay();
            });
        }
        
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => goToSlide(index));
        });
        
        // Touch support for mobile
        let touchStartX = 0;
        let touchEndX = 0;
        
        sliderTrack.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        });
        
        sliderTrack.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        });
        
        function handleSwipe() {
            if (touchEndX < touchStartX - 50) {
                nextSlide();
                resetAutoPlay();
            }
            if (touchEndX > touchStartX + 50) {
                prevSlide();
                resetAutoPlay();
            }
        }
        
        // Initialize
        window.addEventListener('resize', updateCardsToShow);
        updateCardsToShow();
        startAutoPlay();
        
        // Pause auto-play on hover
        sliderTrack.addEventListener('mouseenter', () => {
            clearInterval(autoPlayInterval);
        });
        
        sliderTrack.addEventListener('mouseleave', () => {
            startAutoPlay();
        });
    }
});
