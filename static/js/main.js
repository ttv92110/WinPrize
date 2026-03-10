
// Initialize AOS
AOS.init({
    duration: 1000,
    once: true
});
// Navbar scroll effect
window.addEventListener('scroll', function () {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('navbar-scrolled');
    } else {
        navbar.classList.remove('navbar-scrolled');
    }
});
// Toggle password visibility
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(`toggle${inputId.charAt(0).toUpperCase() + inputId.slice(1)}`);

    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}
// Password strength checker
document.getElementById('registerPassword')?.addEventListener('input', function (e) {
    const password = e.target.value;
    const strengthBar = document.getElementById('passwordStrength');
    const strengthText = document.getElementById('passwordStrengthText');

    let strength = 0;
    if (password.length >= 8) strength += 25;
    if (password.match(/[a-z]+/)) strength += 25;
    if (password.match(/[A-Z]+/)) strength += 25;
    if (password.match(/[0-9]+/)) strength += 25;

    strengthBar.style.width = strength + '%';

    if (strength <= 25) {
        strengthBar.className = 'progress-bar bg-danger';
        strengthText.textContent = 'Weak password';
    } else if (strength <= 50) {
        strengthBar.className = 'progress-bar bg-warning';
        strengthText.textContent = 'Fair password';
    } else if (strength <= 75) {
        strengthBar.className = 'progress-bar bg-info';
        strengthText.textContent = 'Good password';
    } else {
        strengthBar.className = 'progress-bar bg-success';
        strengthText.textContent = 'Strong password';
    }
});
// Confirm password match
document.getElementById('confirmPassword')?.addEventListener('input', function (e) {
    const password = document.getElementById('registerPassword').value;
    const confirm = e.target.value;
    const mismatch = document.getElementById('passwordMismatch');

    if (password !== confirm) {
        mismatch.classList.remove('d-none');
    } else {
        mismatch.classList.add('d-none');
    }
});
// Show toast function
function showToast(message, type = 'success') {
    const toast = document.getElementById('successToast');
    const toastMessage = document.getElementById('toastMessage');
    toastMessage.textContent = message;

    toast.className = `toast align-items-center text-white bg-${type} border-0`;

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}
// Handle modal switching
document.querySelectorAll('[data-bs-toggle="modal"]').forEach(button => {
    button.addEventListener('click', function (e) {
        e.preventDefault();
        const target = this.getAttribute('data-bs-target');
        if (target) {
            const modal = new bootstrap.Modal(document.querySelector(target));
            modal.show();
        }
    });
});
