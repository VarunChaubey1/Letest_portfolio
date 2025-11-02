document.addEventListener('DOMContentLoaded', () => {
    let isMobile = window.innerWidth <= 768;

    window.addEventListener('resize', () => {
        isMobile = window.innerWidth <= 768;
    });

    // Loader
    window.addEventListener('load', () => {
        const loader = document.querySelector('.loader');
        if (loader) {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.style.display = 'none';
            }, 300);
        }
    });

    // Navbar Scroll Effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Hamburger Menu
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('open');
            navLinks.classList.toggle('active');
        });
    }

    // Smooth Scroll for Nav Links
    document.querySelectorAll('.nav-links a').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            gsap.to(window, { duration: 1, scrollTo: { y: targetId, offsetY: 70 } });
            if (navLinks && navLinks.classList.contains('active')) {
                hamburger.classList.remove('open');
                navLinks.classList.remove('active');
            }
        });
    });

    // GSAP Animations
    if (typeof gsap !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);

        gsap.from('.hero-text', {
            opacity: 0,
            x: -100,
            duration: 1,
            ease: 'power2.out',
            delay: 0.5
        });

        gsap.from('.hero-visual', {
            opacity: 0,
            scale: 0.8,
            duration: 1,
            ease: 'power2.out',
            delay: 0.7
        });

        gsap.utils.toArray('.section-title').forEach(title => {
            gsap.from(title, {
                scrollTrigger: {
                    trigger: title,
                    start: 'top 80%',
                    toggleActions: 'play none none none'
                },
                opacity: 0,
                y: 50,
                duration: 0.8,
                ease: 'power2.out'
            });
        });

        gsap.utils.toArray('.exp-card').forEach(card => {
            gsap.from(card, {
                scrollTrigger: {
                    trigger: card,
                    start: 'top 85%',
                    toggleActions: 'play none none none'
                },
                opacity: 0,
                y: 50,
                duration: 0.8,
                ease: 'power2.out'
            });
        });

        gsap.utils.toArray('.skill-card').forEach(card => {
            gsap.from(card, {
                scrollTrigger: {
                    trigger: card,
                    start: 'top 85%',
                    toggleActions: 'play none none none'
                },
                opacity: 0,
                y: 50,
                duration: 0.8,
                ease: 'power2.out'
            });

            const progressBar = card.querySelector('.progress-bar');
            const progressFill = card.querySelector('.progress-fill');
            const percentage = card.querySelector('.progress-percentage');
            if (progressBar && progressFill && percentage) {
                const percentageValue = parseInt(progressBar.getAttribute('data-percentage'));
                gsap.fromTo(progressFill, 
                    { width: 0 }, 
                    {
                        scrollTrigger: {
                            trigger: card,
                            start: 'top 85%',
                            toggleActions: 'play none none none'
                        },
                        width: `${percentageValue}%`,
                        duration: 1.5,
                        ease: 'power2.out',
                        onUpdate: function() {
                            const progress = Math.round(this.progress() * percentageValue);
                            percentage.textContent = `${progress}%`;
                        },
                        onComplete: function() {
                            percentage.textContent = `${percentageValue}%`;
                        }
                    }
                );
            }
        });

        gsap.utils.toArray('.cert-card').forEach(card => {
            gsap.from(card, {
                scrollTrigger: {
                    trigger: card,
                    start: 'top 85%',
                    toggleActions: 'play none none none'
                },
                opacity: 0,
                y: 50,
                duration: 0.8,
                ease: 'power2.out'
            });
        });

        gsap.utils.toArray('.project-card, .achievement-card').forEach((card, index) => {
            gsap.from(card, {
                scrollTrigger: {
                    trigger: card.parentElement,
                    start: 'top 85%',
                    toggleActions: 'play none none none'
                },
                opacity: 0,
                x: 50,
                duration: 0.8,
                delay: index * 0.1,
                ease: 'power2.out'
            });
        });

        gsap.from('.connect-container', {
            scrollTrigger: {
                trigger: '.connect-container',
                start: 'top 85%',
                toggleActions: 'play none none none'
            },
            opacity: 0,
            y: 50,
            duration: 0.8,
            ease: 'power2.out'
        });
    }

    function getCardWidth(slider, cards, container) {
        if (!cards || cards.length === 0) return 320;
        if (isMobile) {
            return window.innerWidth;
        }
        const firstCard = cards[0];
        if (firstCard) {
            const style = window.getComputedStyle(firstCard);
            return firstCard.offsetWidth + parseInt(style.marginRight || 32);
        }
        return 320;
    }

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    function initSlider(sliderSelector) {
        const slider = document.querySelector(sliderSelector);
        if (!slider) {
            console.warn(`Slider ${sliderSelector} not found`);
            return;
        }
        const cards = slider.querySelectorAll('.project-card, .achievement-card');
        if (cards.length === 0) {
            console.warn(`No cards found in ${sliderSelector}`);
            return;
        }
        const container = slider.parentElement;
        const prevBtn = container.querySelector('.prev-btn');
        const nextBtn = container.querySelector('.next-btn');
        let currentIndex = 0;
        let cardWidth = getCardWidth(slider, cards, container);

        const updateCardWidth = debounce(() => {
            cardWidth = getCardWidth(slider, cards, container);
            if (isMobile) {
                slider.scrollLeft = 0;
            } else if (typeof gsap !== 'undefined') {
                gsap.set(slider, { x: 0 });
            }
            currentIndex = 0;
            cards.forEach(card => card.style.opacity = '1');
        }, 250);
        window.addEventListener('resize', updateCardWidth);

        function slideTo(index) {
            const maxIndex = cards.length - 1;
            currentIndex = Math.max(0, Math.min(index, maxIndex));
            if (!isMobile && typeof gsap !== 'undefined') {
                const translateX = -currentIndex * cardWidth;
                gsap.to(slider, {
                    x: translateX,
                    duration: 0.5,
                    ease: 'power2.out'
                });
            } else if (isMobile) {
                const scrollPos = currentIndex * cardWidth;
                slider.scrollTo({
                    left: scrollPos,
                    behavior: 'smooth'
                });
            }
        }

        // FIXED: Button events - Ensure buttons exist and add if not (fallback)
        if (prevBtn && nextBtn && !isMobile) {
            prevBtn.style.display = 'flex'; // Force display
            nextBtn.style.display = 'flex';
            prevBtn.addEventListener('click', (e) => {
                e.preventDefault();
                slideTo(currentIndex - 1);
            });
            nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                slideTo(currentIndex + 1);
            });
        } else if (!isMobile) {
            // Fallback: Create buttons if missing (rare)
            console.warn('Buttons missing, creating fallback');
            const createBtn = (className, icon) => {
                const btn = document.createElement('button');
                btn.className = `slider-btn ${className}`;
                btn.innerHTML = icon;
                btn.style.display = 'flex';
                container.appendChild(btn);
                return btn;
            };
            const prev = createBtn('prev-btn', '<i class="fas fa-chevron-left"></i>');
            const next = createBtn('next-btn', '<i class="fas fa-chevron-right"></i>');
            prev.addEventListener('click', (e) => { e.preventDefault(); slideTo(currentIndex - 1); });
            next.addEventListener('click', (e) => { e.preventDefault(); slideTo(currentIndex + 1); });
        }

        // Mouse Drag for Desktop
        if (!isMobile) {
            let isDragging = false;
            let startX = 0;
            let startTranslate = 0;
            slider.addEventListener('mousedown', (e) => {
                isDragging = true;
                startX = e.clientX;
                startTranslate = gsap ? gsap.getProperty(slider, 'x') : 0;
                slider.style.cursor = 'grabbing';
                e.preventDefault();
            });

            slider.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                const deltaX = e.clientX - startX;
                const newTranslate = startTranslate - deltaX;
                if (gsap) gsap.set(slider, { x: newTranslate });
            });

            slider.addEventListener('mouseup', (e) => {
                if (!isDragging) return;
                isDragging = false;
                slider.style.cursor = 'grab';
                const deltaX = e.clientX - startX;
                if (Math.abs(deltaX) > 50) {
                    slideTo(currentIndex + (deltaX > 0 ? -1 : 1));
                } else {
                    slideTo(currentIndex);
                }
            });

            slider.addEventListener('mouseleave', () => {
                if (isDragging) {
                    isDragging = false;
                    slider.style.cursor = 'default';
                    slideTo(currentIndex);
                }
            });
        }

        // Touch for Mobile
        if (isMobile) {
            let touchStartX = 0;
            let touchStartScroll = 0;
            slider.addEventListener('touchstart', (e) => {
                touchStartX = e.touches[0].clientX;
                touchStartScroll = slider.scrollLeft;
            }, { passive: true });

            slider.addEventListener('touchmove', (e) => {
                if (touchStartX === 0) return;
                const deltaX = touchStartX - e.touches[0].clientX;
                slider.scrollLeft = touchStartScroll + deltaX;
            }, { passive: false });

            slider.addEventListener('touchend', (e) => {
                const deltaX = touchStartX - (e.changedTouches[0].clientX || 0);
                if (Math.abs(deltaX) > 50) {
                    const direction = deltaX > 0 ? 1 : -1;
                    slideTo(currentIndex + direction);
                }
                touchStartX = 0;
            }, { passive: false });

            slider.addEventListener('scroll', () => {
                currentIndex = Math.round(slider.scrollLeft / cardWidth);
            });
        }

        slider.style.userSelect = 'none';
        if (!isMobile) slider.style.cursor = 'grab';

        updateCardWidth();
        slideTo(0);
    }

    initSlider('.project-slider');
    initSlider('.achievement-slider');

    // Lightbox
    window.openLightbox = (src, caption) => {
        const lightbox = document.getElementById('lightbox');
        const lightboxImg = document.getElementById('lightbox-img');
        const lightboxCaption = document.getElementById('lightbox-caption');
        if (lightbox && lightboxImg && lightboxCaption) {
            lightboxImg.src = src;
            lightboxCaption.textContent = caption;
            lightbox.style.display = 'flex';
            if (typeof gsap !== 'undefined') {
                gsap.from(lightboxImg, { opacity: 0, scale: 0.8, duration: 0.5, ease: 'power2.out' });
                gsap.from(lightboxCaption, { opacity: 0, y: 20, duration: 0.5, ease: 'power2.out', delay: 0.2 });
            }
        }
    };

    window.closeLightbox = () => {
        const lightbox = document.getElementById('lightbox');
        if (lightbox && typeof gsap !== 'undefined') {
            gsap.to(lightbox, {
                opacity: 0,
                duration: 0.3,
                ease: 'power2.in',
                onComplete: () => {
                    lightbox.style.display = 'none';
                    document.getElementById('lightbox-img').src = '';
                    document.getElementById('lightbox-caption').textContent = '';
                }
            });
        } else if (lightbox) {
            lightbox.style.display = 'none';
        }
    };

    const lightbox = document.getElementById('lightbox');
    if (lightbox) {
        lightbox.addEventListener('click', (e) => {
            if (e.target.id === 'lightbox') closeLightbox();
        });
    }
});