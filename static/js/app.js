// Check login status and update UI
document.addEventListener('DOMContentLoaded', function () {
    let user = JSON.parse(localStorage.getItem("loggedUser"));

    // Update navigation based on login status
    let loginBtn = document.getElementById("loginBtn");
    let registerBtn = document.getElementById("registerBtn");
    let userMenu = document.getElementById("userMenu");

    if (user) {
        if (loginBtn) loginBtn.style.display = "none";
        if (registerBtn) registerBtn.style.display = "none";

        if (userMenu) {
            userMenu.innerHTML = `
                <div class="dropdown">
                    <button class="btn btn-outline-light dropdown-toggle rounded-pill" type="button" data-bs-toggle="dropdown">
                        <i class="fas fa-user-circle me-2"></i>${user.name || 'User'}
                        ${user.user_status === 'staff' ? '<span class="badge bg-warning text-dark ms-2">Admin</span>' : ''}
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <!-- <li><a class="dropdown-item" href="#"><i class="fas fa-user me-2"></i>Profile</a></li> -->
                        <li><a class="dropdown-item" href="/#draws"><i class="fas fa-ticket-alt me-2"></i>My Draws</a></li>
                        <li><a class="dropdown-item" href="/notifications"><i class="fas fa-bell me-2"></i>Notifications</a></li>
                        <li><a class="dropdown-item" href="/winner"><i class="fas fa-trophy me-2"></i>Winners</a></li>
                        <li><a class="dropdown-item" href="/payment-status"><i class="fas fa-money me-2"></i>Payment Status</a></li>
                        ${user.user_status === 'staff' ? `
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-primary" href="/admin">
                                <i class="fas fa-shield-alt me-2"></i>Admin Panel
                            </a></li>
                        ` : ''}
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item text-danger" href="#" onclick="logout()">
                            <i class="fas fa-sign-out-alt me-2"></i>Logout
                        </a></li>
                    </ul>
                </div>
            `;
        }

        // Show notification bell
        const notificationBell = document.getElementById('notificationBell');
        if (notificationBell) notificationBell.style.display = 'inline-block';

        // Update notification badge immediately
        updateNotificationBadge();

        // Check for new notifications every 30 seconds
        setInterval(updateNotificationBadge, 30000);

    } else {
        if (loginBtn) loginBtn.style.display = "inline-block";
        if (registerBtn) registerBtn.style.display = "inline-block";

        // Hide notification bell
        const notificationBell = document.getElementById('notificationBell');
        if (notificationBell) notificationBell.style.display = 'none';
    }
});

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

// Logout function
function logout() {
    localStorage.removeItem("loggedUser");
    window.location.href = "/";
}

// Show toast function
function showToast(message, type = 'success') {
    const toast = document.getElementById('successToast');
    const toastMessage = document.getElementById('toastMessage');
    if (toast) {
        toastMessage.textContent = message;
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    } else {
        alert(message);
    }
}

// ========== Notification Bell Functions ==========
async function updateNotificationBadge() {
    const user = JSON.parse(localStorage.getItem("loggedUser"));
    const notificationBell = document.getElementById('notificationBell');
    const badge = document.getElementById('notificationBadge');

    if (!user) {
        if (notificationBell) notificationBell.style.display = 'none';
        return;
    }

    try {
        const res = await fetch(`/notifications/count/${user.email}`);
        const data = await res.json();

        if (notificationBell) notificationBell.style.display = 'inline-block';

        if (data.unread_count > 0) {
            badge.textContent = data.unread_count;
            badge.style.display = 'inline';
            badge.style.animation = 'pulse 1s infinite';
        } else {
            badge.style.display = 'none';
            badge.style.animation = 'none';
        }
    } catch (error) {
        console.error("Error updating notification badge:", error);
    }
}

// Call updateNotificationBadge when page loads and after login
window.updateNotificationBadge = updateNotificationBadge;
 
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
    updateAdminNavLink(); // Add this line

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

// Also update the logout function
function logout() {
    localStorage.removeItem("loggedUser");
    updateUserMenu();
    updateAdminNavLink(); // Add this line
    showToast("Logged out successfully", "info");
}

// Logout function
window.logout = function () {
    localStorage.removeItem("loggedUser");
    window.location.href = "/";
};