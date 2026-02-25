document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.ask-form');
    const btn = document.getElementById('askBtn');

    form.addEventListener('submit', () => {
        btn.innerHTML = '<span class="spinner"></span> Processing...';
        btn.style.opacity = '0.8';
        btn.disabled = true;
    });
});