// Login function
// Update user menu based on login status
function updateUserMenu() {
    const user = JSON.parse(localStorage.getItem("loggedUser"));
    const userMenu = document.getElementById("userMenu");

    if (user) {
        // Check if user is admin (staff)
        const isAdmin = user.user_status === "staff";

        // Build dropdown menu items
        let dropdownItems = `
            <li><a class="dropdown-item" href="#"><i class="fas fa-user me-2"></i>Profile</a></li>
            <li><a class="dropdown-item" href="/my-draws"><i class="fas fa-ticket-alt me-2"></i>My Draws</a></li>
            <li><a class="dropdown-item" href="/winner"><i class="fas fa-trophy me-2"></i>Winners</a></li>
        `;

        // Add Admin link if user is staff
        if (isAdmin) {
            dropdownItems += `
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item text-primary" href="/admin">
                    <i class="fas fa-shield-alt me-2"></i>Admin Panel
                </a></li>
            `;
        }

        // Add logout
        dropdownItems += `
            <li><hr class="dropdown-divider"></li>
            <li><a class="dropdown-item text-danger" href="#" onclick="logout()">
                <i class="fas fa-sign-out-alt me-2"></i>Logout
            </a></li>
        `;

        userMenu.innerHTML = `
            <div class="dropdown">
                <button class="btn btn-outline-light dropdown-toggle rounded-pill" type="button" data-bs-toggle="dropdown">
                    <i class="fas fa-user-circle me-2"></i>${user.name || 'User'}
                    ${isAdmin ? '<span class="badge bg-warning text-dark ms-2">Admin</span>' : ''}
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                    ${dropdownItems}
                </ul>
            </div>
        `;
    } else {
        userMenu.innerHTML = `
            <button class="btn btn-outline-light rounded-pill px-4 me-2" data-bs-toggle="modal" data-bs-target="#loginModal">
                <i class="fas fa-sign-in-alt me-2"></i>Login
            </button>
            <button class="btn btn-warning rounded-pill px-4" data-bs-toggle="modal" data-bs-target="#registerModal">
                <i class="fas fa-user-plus me-2"></i>Register
            </button>
        `;
    }
}

// Modify login function to store user_status
async function login() {
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;
    const submitBtn = document.getElementById("loginSubmitBtn");
    const spinner = document.getElementById("loginSpinner");
    const btnText = document.getElementById("loginBtnText");

    if (!email || !password) {
        showToast("Please fill all fields", "warning");
        return;
    }

    // Show loading state
    submitBtn.disabled = true;
    spinner.classList.remove("d-none");
    btnText.textContent = "Logging in...";

    try {
        const res = await fetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (data.success) {
            // Make sure user_status is stored
            const userData = {
                ...data.user,
                user_status: data.user.user_status || 'user'
            };
            localStorage.setItem("loggedUser", JSON.stringify(userData));

            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
            modal.hide();

            // Show success message
            showToast("Login successful! Welcome back!", "success");

            // Update UI
            updateUserMenu();

            // Clear form
            document.getElementById("loginForm").reset();

            // If user is admin, show a special message
            if (userData.user_status === 'staff') {
                setTimeout(() => {
                    showToast("You have admin privileges", "info");
                }, 500);
            }
        } else {
            showToast(data.message || "Invalid email or password", "danger");
        }
    } catch (error) {
        console.error("Error:", error);
        showToast("An error occurred during login", "danger");
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        spinner.classList.add("d-none");
        btnText.textContent = "Login";
    }
}

// Forgot password function (CORRECT ONE - keeps this one, removes the duplicate)
async function forgotPassword() {
    const email = document.getElementById("forgotEmail").value;

    if (!email) {
        showToast("Please enter your email", "warning");
        return;
    }

    const submitBtn = document.querySelector('#forgotPasswordForm button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Sending...';

    try {
        const res = await fetch("/password/forgot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email })
        });

        const data = await res.json();

        if (data.success) {
            // Close forgot password modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('forgotPasswordModal'));
            modal.hide();

            // Show success message
            showToast(data.message, "success");

            // Clear form
            document.getElementById("forgotEmail").value = "";

            // Show login modal after delay
            setTimeout(() => {
                const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
                loginModal.show();
            }, 2000);
        } else {
            showToast(data.detail || "Failed to send reset email", "danger");
        }
    } catch (error) {
        console.error("Error:", error);
        showToast("An error occurred. Please try again.", "danger");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

// Signup function with email verification
async function signup() {
    const name = document.getElementById("registerName").value;
    const email = document.getElementById("registerEmail").value;
    const password = document.getElementById("registerPassword").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const termsCheck = document.getElementById("termsCheck").checked;

    const submitBtn = document.getElementById("registerSubmitBtn");
    const spinner = document.getElementById("registerSpinner");
    const btnText = document.getElementById("registerBtnText");

    // Validation
    if (!name || !email || !password || !confirmPassword) {
        showToast("Please fill all fields", "warning");
        return;
    }

    if (password !== confirmPassword) {
        showToast("Passwords do not match", "danger");
        return;
    }

    if (password.length < 6) {
        showToast("Password must be at least 6 characters", "warning");
        return;
    }

    if (!termsCheck) {
        showToast("Please agree to Terms & Conditions", "warning");
        return;
    }

    // Show loading state
    submitBtn.disabled = true;
    spinner.classList.remove("d-none");
    btnText.textContent = "Sending verification...";

    try {
        // Send PIN to email
        const res = await fetch("/verify/send-pin", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name,
                email,
                password,
                user_status: "user"
            })
        });

        const data = await res.json();

        if (data.success) {
            // Close register modal
            const registerModal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
            registerModal.hide();

            // Store email for verification page
            localStorage.setItem("verification_email", email);

            // Show success message
            showToast("Verification PIN sent to your email!", "success");

            // Clear form
            document.getElementById("registerForm").reset();

            // Redirect to verification page
            setTimeout(() => {
                window.location.href = "/verify";
            }, 1500);
        } else {
            showToast(data.detail || "Failed to send verification", "danger");
            submitBtn.disabled = false;
            spinner.classList.add("d-none");
            btnText.textContent = "Create Account";
        }
    } catch (error) {
        console.error("Error:", error);
        showToast("An error occurred during registration", "danger");
        submitBtn.disabled = false;
        spinner.classList.add("d-none");
        btnText.textContent = "Create Account";
    }
}

// Show/hide admin nav link based on user status
function updateAdminNavLink() {
    const user = JSON.parse(localStorage.getItem("loggedUser"));
    const adminNavLink = document.getElementById("adminNavLink");

    if (adminNavLink) {
        if (user && user.user_status === 'staff') {
            adminNavLink.style.display = 'block';
        } else {
            adminNavLink.style.display = 'none';
        }
    }
}

// Update the DOMContentLoaded event
document.addEventListener('DOMContentLoaded', function () {
    updateUserMenu();
    updateAdminNavLink();

    // Handle join draw button clicks from draws.js
    window.joinDraw = function (drawId, payAmount) {
        const user = JSON.parse(localStorage.getItem("loggedUser"));

        if (!user) {
            // Show login modal
            const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
            loginModal.show();

            // Store draw info for after login
            localStorage.setItem("pendingDraw", JSON.stringify({
                id: drawId,
                pay: payAmount
            }));

            showToast("Please login to join the draw", "info");
            return;
        }

        // Proceed with joining draw
        localStorage.setItem("selected_draw", JSON.stringify({
            id: drawId,
            pay: payAmount
        }));

        window.location.href = "/confirm";
    };
});

// Logout function
function logout() {
    localStorage.removeItem("loggedUser");
    updateUserMenu();
    updateAdminNavLink();
    showToast("Logged out successfully", "info");
}

// Show toast function
function showToast(message, type = 'success') {
    const toast = document.getElementById('successToast');
    const toastMessage = document.getElementById('toastMessage');
    toastMessage.textContent = message;

    toast.className = `toast align-items-center text-white bg-${type} border-0`;

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}