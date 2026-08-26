class BannerSlider {
    constructor(el) {
        this.el = el;
        this.track = el.querySelector('.banner-track');
        this.slides = el.querySelectorAll('.banner-slide');
        this.cur = 0;
        this.total = this.slides.length;
        this.autoplay = null;
        this.init();
    }

    init() {
        this.buildDots();
        this.bindNav();
        this.startAutoplay();
        // pause روی hover
        this.el.addEventListener('mouseenter', () => clearInterval(this.autoplay));
        this.el.addEventListener('mouseleave', () => this.startAutoplay());
    }

    go(n) {
        this.cur = (n + this.total) % this.total;
        this.track.style.transform = `translateX(-${this.cur * 100}%)`;
        this.el.querySelectorAll('.dot').forEach((d, i) =>
            d.classList.toggle('active', i === this.cur)
        );
    }

    buildDots() {
        const wrap = this.el.querySelector('.dots');
        this.slides.forEach((_, i) => {
            const d = document.createElement('button');
            d.className = 'dot' + (i === 0 ? ' active' : '');
            d.setAttribute('aria-label', `بنر ${i + 1}`);
            d.onclick = () => this.go(i);
            wrap.appendChild(d);
        });
    }

    bindNav() {
        this.el.querySelector('.prev')?.addEventListener('click', () => this.go(this.cur - 1));
        this.el.querySelector('.next')?.addEventListener('click', () => this.go(this.cur + 1));
    }

    startAutoplay() {
        this.autoplay = setInterval(() => this.go(this.cur + 1), 4000);
    }
}

document.querySelectorAll('.banner-slider').forEach(el => new BannerSlider(el));