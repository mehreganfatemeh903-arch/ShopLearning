document.addEventListener('DOMContentLoaded', function () {

    // ============ MOBILE FILTER TOGGLE ============
    const toggleBtn = document.getElementById('mobile-filter-products');
    const closeBtn = document.getElementById('close-filter');
    const filterSection = document.getElementById('filter-section');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function () {
            filterSection.classList.add('active');
            toggleBtn.classList.add('d-none');
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            filterSection.classList.remove('active');
            toggleBtn.classList.remove('d-none');
        });
    }

    // ============ PRICE RANGE SLIDER ============
    const minRange = document.getElementById('minRange');
    const maxRange = document.getElementById('maxRange');
    const minLabel = document.getElementById('minLabel');
    const maxLabel = document.getElementById('maxLabel');
    const priceFill = document.getElementById('priceFill');

    function updateRange() {
        let min = parseInt(minRange.value);
        let max = parseInt(maxRange.value);
        const total = parseInt(minRange.max);

        if (min >= max) minRange.value = max - 1;

        const minPct = (parseInt(minRange.value) / total) * 100;
        const maxPct = (parseInt(maxRange.value) / total) * 100;

        priceFill.style.left = minPct + '%';
        priceFill.style.width = (maxPct - minPct) + '%';

        minLabel.textContent = '$' + Number(minRange.value).toLocaleString();
        maxLabel.textContent = '$' + Number(maxRange.value).toLocaleString();
    }

    if (minRange && maxRange) {
        minRange.addEventListener('input', updateRange);
        maxRange.addEventListener('input', updateRange);
        updateRange();
    }

    // ============ CATEGORY ACCORDION ============
    const catList = document.getElementById('categoryList');
    const catArrow = document.getElementById('catArrow');
    const catHeader = document.querySelector('.cat-accordion-header');

    if (catHeader) {
        catHeader.addEventListener('click', function () {
            catList.classList.toggle('open');
            catArrow.classList.toggle('open');
        });
    }

});
