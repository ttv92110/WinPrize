// Load pending payments when admin page loads
document.addEventListener('DOMContentLoaded', function () {
    // Check if we're on admin page and user is admin
    const user = JSON.parse(localStorage.getItem("loggedUser"));
    if (user && window.location.pathname === '/admin') {
        loadPendingPayments();
    }
});

async function loadPendingPayments() {
    try {
        const user = JSON.parse(localStorage.getItem("loggedUser"));
        if (!user) return;

        const container = document.getElementById("pendingPaymentsContainer");
        if (!container) return;

        // Show loading
        container.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-warning" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Loading pending payments...</p></div>';

        // Fetch pending payments
        const res = await fetch(`/admin/pending-payments?email=${encodeURIComponent(user.email)}`);

        if (!res.ok) {
            if (res.status === 403) {
                container.innerHTML = '<div class="alert alert-danger">You don\'t have permission to view payments</div>';
                return;
            }
            throw new Error(`HTTP error! status: ${res.status}`);
        }

        const payments = await res.json();

        if (!payments || payments.length === 0) {
            container.innerHTML = '<div class="text-center py-4"><i class="fas fa-check-circle fa-3x text-success mb-3"></i><h5>No Pending Payments</h5><p class="text-muted">All payments are verified</p></div>';
            return;
        }

        container.innerHTML = '<h5 class="mb-3">Pending Payments (' + payments.length + ')</h5>';

        payments.forEach(payment => {
            const paymentCard = createPaymentCard(payment);
            container.innerHTML += paymentCard;
        });

    } catch (error) {
        console.error("Error loading pending payments:", error);
        const container = document.getElementById("pendingPaymentsContainer");
        if (container) {
            container.innerHTML = '<div class="alert alert-danger">Error loading payments. Please refresh.</div>';
        }
    }
}

function createPaymentCard(payment) {
    // Format date for display
    const createdDate = formatDate(payment.created_at);

    return `
        <div class="payment-card mb-3 p-3 border rounded" id="payment-${payment.id}">
            <div class="row">
                <div class="col-md-12">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="mb-0">
                            <i class="fas fa-user-circle me-2"></i>
                            ${payment.user_name}
                        </h6>
                        <span class="badge bg-warning text-dark">PENDING</span>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <small class="text-muted d-block">Email</small>
                            <strong>${payment.user_email}</strong>
                        </div>
                        <div class="col-md-2">
                            <small class="text-muted d-block">Amount</small>
                            <strong class="text-success">Rs. ${payment.amount}</strong>
                        </div>
                        <div class="col-md-3">
                            <small class="text-muted d-block">Draw</small>
                            <strong>${payment.lucky_draw_title}</strong>
                            <small class="d-block text-muted">ID: ${payment.lucky_draw_id}</small>
                        </div>
                        <div class="col-md-4">
                            <small class="text-muted d-block">Date</small>
                            <strong>${createdDate}</strong>
                        </div>
                    </div>
                    
                    <hr class="my-2">
                    
                    <div class="row">
                        <div class="col-md-4">
                            <small class="text-muted d-block">From Account</small>
                            <strong>${payment.account_bank_from}</strong>
                            <small class="d-block">${payment.account_number_from}</small>
                            <small>Holder: ${payment.holder_name}</small>
                        </div>
                        <div class="col-md-4">
                            <small class="text-muted d-block">To Account</small>
                            <strong>${payment.account_bank_to}</strong>
                            <small class="d-block">${payment.account_number_to}</small>
                            <small>Recipient: ${payment.recipient_name}</small>
                        </div>
                        <div class="col-md-4">
                            <small class="text-muted d-block">Transaction ID</small>
                            <strong>${payment.transaction_id}</strong>
                        </div>
                    </div>
                    
                    <div class="mt-3 d-flex justify-content-end gap-2">
                        <button class="btn btn-sm btn-success" onclick="approvePayment('${payment.id}')">
                            <i class="fas fa-check me-1"></i> Approve
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="rejectPayment('${payment.id}')">
                            <i class="fas fa-times me-1"></i> Reject
                        </button>
                        <button class="btn btn-sm btn-info" onclick="viewPaymentDetails('${payment.id}')">
                            <i class="fas fa-eye me-1"></i> Details
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    try {
        const parts = dateString.match(/(\d+)\/(\d+)\/(\d+)T(\d+)h:(\d+)m:(\d+)s/);
        if (parts) {
            const [_, day, month, year, hour, minute] = parts;
            return `${day}/${month}/${year} ${hour}:${minute}`;
        }
    } catch (e) {
        console.error("Error formatting date:", e);
    }
    return dateString;
}


async function approvePayment(paymentId) {
    if (!confirm("Are you sure you want to approve this payment? User will be enrolled in the draw.")) {
        return;
    }

    const user = JSON.parse(localStorage.getItem("loggedUser"));
    if (!user) {
        alert("Please login first");
        return;
    }

    // Disable button to prevent double submission
    const approveBtn = event.target;
    const originalText = approveBtn.innerHTML;
    approveBtn.disabled = true;
    approveBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Approving...';

    try {
        const res = await fetch(`/admin/approve-payment/${paymentId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_email: user.email
            })
        });

        const data = await res.json();

        if (data.success) {
            // Show success message
            showToast("Payment approved! User enrolled in draw.", "success");

            // Remove the payment card with animation
            const card = document.getElementById(`payment-${paymentId}`);
            if (card) {
                card.style.transition = 'all 0.3s';
                card.style.opacity = '0';
                card.style.transform = 'translateX(20px)';
                setTimeout(() => {
                    card.remove();
                    // Check if no more pending payments
                    checkEmptyPayments();
                }, 300);
            }
        } else {
            alert(data.message || "Failed to approve payment");
            approveBtn.disabled = false;
            approveBtn.innerHTML = originalText;
        }
    } catch (error) {
        console.error("Error approving payment:", error);
        alert("An error occurred while approving payment");
        approveBtn.disabled = false;
        approveBtn.innerHTML = originalText;
    }
}

async function rejectPayment(paymentId) {
    const reason = prompt("Enter reason for rejection (e.g., Fake transaction, Wrong amount, Invalid details):", "Fake/Invalid transaction");
    if (reason === null) return; // User cancelled

    const user = JSON.parse(localStorage.getItem("loggedUser"));
    if (!user) {
        alert("Please login first");
        return;
    }

    if (!confirm("⚠️ Warning: This will permanently remove the user from this draw. Continue?")) {
        return;
    }

    const rejectBtn = event.target;
    const originalText = rejectBtn.innerHTML;
    rejectBtn.disabled = true;
    rejectBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Rejecting...';

    try {
        const res = await fetch(`/admin/reject-payment/${paymentId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_email: user.email,
                reason: reason
            })
        });

        const data = await res.json();

        if (data.success) {
            showToast(`Payment rejected! Reason: ${reason}`, "warning");

            const card = document.getElementById(`payment-${paymentId}`);
            if (card) {
                card.style.transition = 'all 0.3s';
                card.style.opacity = '0';
                card.style.transform = 'translateX(-20px)';
                setTimeout(() => {
                    card.remove();
                    checkEmptyPayments();
                }, 300);
            }
        } else {
            alert(data.message || "Failed to reject payment");
            rejectBtn.disabled = false;
            rejectBtn.innerHTML = originalText;
        }
    } catch (error) {
        console.error("Error rejecting payment:", error);
        alert("An error occurred while rejecting payment");
        rejectBtn.disabled = false;
        rejectBtn.innerHTML = originalText;
    }
}

function checkEmptyPayments() {
    const container = document.getElementById("pendingPaymentsContainer");
    const cards = container.querySelectorAll('.payment-card');

    if (cards.length === 0) {
        // Reload to show empty state
        loadPendingPayments();
    }
}

// Toast function for better notifications
function showToast(message, type = 'success') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }

    // Create toast
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);

    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
    bsToast.show();

    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', function () {
        toast.remove();
    });
}

function viewPaymentDetails(paymentId) {
    // You can implement a modal to show full payment details
    alert("Payment details view - Implement modal here");
}

// Auto-refresh pending payments every 30 seconds
setInterval(() => {
    if (window.location.pathname === '/admin') {
        loadPendingPayments();
    }
}, 30000);
