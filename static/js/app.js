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
                <span class="text-light me-3">Welcome, ${user.name}</span>
                <button class="btn btn-outline-light" onclick="logout()">Logout</button>
            `;
        }
    } else {
        if (loginBtn) loginBtn.style.display = "inline-block";
        if (registerBtn) registerBtn.style.display = "inline-block";
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