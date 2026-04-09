let currentAdmin = null;
let editModal = null;
let accessDeniedModal = null;
let winnerModal = null;
let currentDrawId = null;
let currentDrawParticipants = [];

document.addEventListener('DOMContentLoaded', function () {
    editModal = new bootstrap.Modal(document.getElementById('editDrawModal'));
    accessDeniedModal = new bootstrap.Modal(document.getElementById('accessDeniedModal'));
    winnerModal = new bootstrap.Modal(document.getElementById('winnerModal'));
    checkAdminStatus();
});

async function checkAdminStatus() {
    const loadingState = document.getElementById('loadingState');
    const adminContent = document.getElementById('adminContent');

    try {
        const user = JSON.parse(localStorage.getItem("loggedUser"));

        if (!user) {
            showAccessDenied("Please login first");
            return;
        }

        const response = await fetch(`/admin/verify-admin?email=${encodeURIComponent(user.email)}`);
        const data = await response.json();

        if (data.isAdmin) {
            currentAdmin = { email: user.email, name: user.name };
            document.getElementById("adminEmail").value = user.email;
            loadingState.style.display = 'none';
            adminContent.style.display = 'block';
            loadAdminDraws();
            loadStats();           // new
            loadUsers();           // new
            loadVerifications();   // new
            loadUserDraws();       // new
        } else {
            showAccessDenied("You don't have admin privileges");
        }
    } catch (error) {
        console.error("Error verifying admin:", error);
        showAccessDenied("Error verifying admin status");
    }
}

function showAccessDenied(message) {
    const loadingState = document.getElementById('loadingState');
    const adminContent = document.getElementById('adminContent');
    loadingState.style.display = 'none';
    adminContent.style.display = 'none';
    const modalBody = document.querySelector('#accessDeniedModal .modal-body p:first-of-type');
    if (modalBody && message) {
        modalBody.textContent = message;
    }
    accessDeniedModal.show();
    setTimeout(() => {
        window.location.href = "/";
    }, 3000);
}

async function loadAdminDraws() {
    if (!currentAdmin) return;

    try {
        const container = document.getElementById("adminDrawsContainer");
        if (!container) return;

        container.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';

        const res = await fetch(`/admin/draws?email=${encodeURIComponent(currentAdmin.email)}`);

        if (!res.ok) {
            if (res.status === 403) {
                container.innerHTML = '<div class="alert alert-danger">Session expired. Please refresh and login again.</div>';
                setTimeout(() => { logout(); }, 2000);
                return;
            }
            throw new Error(`HTTP error! status: ${res.status}`);
        }

        const draws = await res.json();

        if (!draws || draws.length === 0) {
            container.innerHTML = '<div class="text-center py-4">No draws found. Create your first draw!</div>';
            return;
        }

        container.innerHTML = '';
        draws.forEach(draw => {
            const statusBadge = getStatusBadge(draw.status);

            const drawCard = `
                <div class="admin-draw-card mb-3 p-3 border rounded" id="draw-${draw.id}">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <h5 class="mb-1">${draw.title || draw.time_interval + 'ly Draw'}</h5>
                            <small class="text-muted">ID: ${draw.id}</small>
                        </div>
                        <div class="col-md-2">
                            <div>Entry: Rs. ${draw.user_pay}</div>
                            <div>Prize: Rs. ${draw.winner_get}</div>
                        </div>
                        <div class="col-md-2">
                            ${statusBadge}
                            ${draw.status === 'awaiting' ? '<br><small class="text-warning">Needs attention!</small>' : ''}
                        </div>
                        <div class="col-md-3">
                            <small>Created: ${draw.created_at || 'N/A'}</small><br>
                            <small>Closes: ${draw.closed_at || 'N/A'}</small>
                            <br><small>Participants: ${draw.participants_count || 0}</small>
                        </div>
                        <div class="col-md-2">
                            <div class="btn-group-vertical w-100">
                                <button class="btn btn-sm btn-primary" onclick="editDraw('${draw.id}')">
                                    <i class="fas fa-edit"></i> Edit
                                </button>
                                ${draw.status === 'open' ?
                `<button class="btn btn-sm btn-success" onclick="runDrawRandom('${draw.id}')">
                                        <i class="fas fa-random"></i> Random Winner
                                    </button>
                                    <button class="btn btn-sm btn-warning" onclick="openWinnerModal('${draw.id}')">
                                        <i class="fas fa-hand-pointer"></i> Manual Winner
                                    </button>` : ''}
                                ${draw.status === 'awaiting' ?
                `<button class="btn btn-sm btn-warning" onclick="openWinnerModal('${draw.id}')">
                                        <i class="fas fa-trophy"></i> Announce Winner
                                    </button>` : ''}
                                ${draw.status !== 'open' ?
                    `<button class="btn btn-sm btn-info" onclick="reopenDraw('${draw.id}')">
                                        <i class="fas fa-redo"></i> Reopen
                                    </button>` : ''}
                                <button class="btn btn-sm btn-danger" onclick="deleteDraw('${draw.id}')">
                                    <i class="fas fa-trash"></i> Delete
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            container.innerHTML += drawCard;
        });
    } catch (error) {
        console.error("Error loading admin draws:", error);
        const container = document.getElementById("adminDrawsContainer");
        if (container) {
            container.innerHTML = '<div class="alert alert-danger">Error loading draws. Please try again.</div>';
        }
    }
}

function getStatusBadge(status) {
    switch (status) {
        case 'open': return '<span class="badge bg-success">OPEN</span>';
        case 'awaiting': return '<span class="badge bg-warning text-dark">AWAITING ⚠️</span>';
        case 'completed': return '<span class="badge bg-primary">COMPLETED</span>';
        case 'finished': return '<span class="badge bg-secondary">FINISHED</span>';
        default: return '<span class="badge bg-secondary">UNKNOWN</span>';
    }
}

// ========== Edit Draw Functions ==========
async function editDraw(drawId) {
    if (!currentAdmin) return;

    try {
        const res = await fetch(`/draws/${drawId}`);
        const draw = await res.json();

        document.getElementById('editDrawId').value = draw.id;
        document.getElementById('editTitle').value = draw.title || '';
        document.getElementById('editDescription').value = draw.description || '';
        document.getElementById('editUserPay').value = draw.user_pay;
        document.getElementById('editWinnerGet').value = draw.winner_get;
        document.getElementById('editTimeInterval').value = draw.time_interval;
        document.getElementById('editStatus').value = draw.status;
        document.getElementById('editMaxParticipants').value = draw.max_participants || '';
        document.getElementById('editVisible').value = draw.visible ? 'true' : 'false';
        document.getElementById('editAutoComplete').value = draw.auto_complete ? 'true' : 'false';

        if (draw.closed_at) {
            try {
                const parts = draw.closed_at.match(/(\d+)\/(\d+)\/(\d+)T(\d+)h:(\d+)m:(\d+)s/);
                if (parts) {
                    const [_, day, month, year, hour, minute] = parts;
                    const isoString = `${year}-${month}-${day}T${hour.padStart(2, '0')}:${minute.padStart(2, '0')}`;
                    document.getElementById('editClosedAt').value = isoString;
                }
            } catch (e) {
                console.error("Error parsing date:", e);
            }
        }

        editModal.show();
    } catch (error) {
        console.error("Error loading draw for edit:", error);
        showToast("Failed to load draw details", "danger");
    }
}

async function saveDrawChanges() {
    if (!currentAdmin) return;

    const drawId = document.getElementById('editDrawId').value;
    const closedAt = document.getElementById('editClosedAt').value;

    let formattedClosedAt = null;
    if (closedAt) {
        const date = new Date(closedAt);
        formattedClosedAt = `${date.getDate().toString().padStart(2, '0')}/${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getFullYear()}T${date.getHours().toString().padStart(2, '0')}h:${date.getMinutes().toString().padStart(2, '0')}m:00s`;
    }

    const updateData = {
        user_email: currentAdmin.email,
        title: document.getElementById('editTitle').value,
        description: document.getElementById('editDescription').value,
        user_pay: parseInt(document.getElementById('editUserPay').value),
        winner_get: parseInt(document.getElementById('editWinnerGet').value),
        time_interval: document.getElementById('editTimeInterval').value,
        status: document.getElementById('editStatus').value,
        max_participants: document.getElementById('editMaxParticipants').value ? parseInt(document.getElementById('editMaxParticipants').value) : null,
        visible: document.getElementById('editVisible').value === 'true',
        auto_complete: document.getElementById('editAutoComplete').value === 'true'
    };

    if (formattedClosedAt) {
        updateData.closed_at = formattedClosedAt;
    }

    try {
        const res = await fetch(`/admin/update-draw/${drawId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updateData)
        });

        const data = await res.json();

        if (data.success) {
            showToast("Draw updated successfully!", "success");
            editModal.hide();
            loadAdminDraws();
        } else {
            showToast(data.message || "Failed to update draw", "danger");
        }
    } catch (error) {
        console.error("Error updating draw:", error);
        showToast("Failed to update draw", "danger");
    }
}

// ========== Winner Announcement Functions ==========
async function openWinnerModal(drawId) {
    if (!currentAdmin) return;

    currentDrawId = drawId;

    document.getElementById('winnerSelect').innerHTML = '<option value="">-- Select a participant --</option>';
    document.getElementById('winnerNotes').value = '';
    document.getElementById('winnerModalContent').style.display = 'none';
    document.getElementById('winnerModalLoading').style.display = 'block';

    winnerModal.show();

    try {
        const res = await fetch(`/draws/participants/list/${drawId}?email=${encodeURIComponent(currentAdmin.email)}`);

        if (!res.ok) {
            throw new Error('Failed to load participants');
        }

        const data = await res.json();
        currentDrawParticipants = data.participants;

        document.getElementById('winnerModalLoading').style.display = 'none';
        document.getElementById('winnerModalContent').style.display = 'block';

        const select = document.getElementById('winnerSelect');

        if (!data.participants || data.participants.length === 0) {
            select.innerHTML = '<option value="">No participants found</option>';
            document.getElementById('confirmWinnerBtn').disabled = true;
            return;
        }

        data.participants.forEach(participant => {
            const option = document.createElement('option');
            option.value = participant.email;
            option.textContent = `${participant.name} (${participant.email})`;
            select.appendChild(option);
        });

        document.getElementById('confirmWinnerBtn').disabled = false;

    } catch (error) {
        console.error("Error loading participants:", error);
        document.getElementById('winnerModalLoading').style.display = 'none';
        document.getElementById('winnerModalContent').style.display = 'block';
        document.getElementById('winnerSelect').innerHTML = '<option value="">Error loading participants</option>';
        document.getElementById('confirmWinnerBtn').disabled = true;
        showToast("Failed to load participants", "danger");
    }
}

async function confirmWinner() {
    const winnerSelect = document.getElementById('winnerSelect');
    const winnerEmail = winnerSelect.value;
    const notes = document.getElementById('winnerNotes').value;

    if (!winnerEmail) {
        showToast("Please select a winner", "warning");
        return;
    }

    const confirmBtn = document.getElementById('confirmWinnerBtn');
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Announcing...';

    try {
        const res = await fetch(`/admin/update-result/${currentDrawId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_email: currentAdmin.email,
                winner_email: winnerEmail,
                notes: notes
            })
        });

        const data = await res.json();

        if (data.success) {
            showToast(`Winner announced: ${data.winner.name}`, "success");
            winnerModal.hide();
            loadAdminDraws();
        } else {
            showToast(data.message || "Failed to announce winner", "danger");
        }
    } catch (error) {
        console.error("Error announcing winner:", error);
        showToast("An error occurred", "danger");
    } finally {
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = '<i class="fas fa-trophy me-2"></i>Announce Winner';
    }
}

async function runDrawRandom(drawId) {
    if (!currentAdmin) return;

    if (!confirm("Run random draw? A winner will be selected automatically.")) {
        return;
    }

    const btn = event.target;
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Running...';

    try {
        const res = await fetch(`/admin/run-draw/${drawId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_email: currentAdmin.email
            })
        });

        const data = await res.json();

        if (data.success) {
            if (data.winner) {
                showToast(`Winner: ${data.winner.user_name || 'Winner'} (${data.winner.user_email})`, "success");
            } else {
                showToast(data.message || "No participants for this draw", "info");
            }
            loadAdminDraws();
        } else {
            showToast(data.message || "Failed to run draw", "danger");
        }
    } catch (error) {
        console.error("Error running draw:", error);
        showToast("An error occurred", "danger");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// ========== Draw Management Functions ==========
async function reopenDraw(drawId) {
    if (!currentAdmin) return;

    if (!confirm("Are you sure you want to reopen this draw?")) return;

    try {
        const res = await fetch(`/admin/reopen-draw/${drawId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_email: currentAdmin.email
            })
        });

        const data = await res.json();

        if (data.success) {
            showToast("Draw reopened successfully!", "success");
            loadAdminDraws();
        } else {
            showToast(data.message || "Failed to reopen draw", "danger");
        }
    } catch (error) {
        console.error("Error reopening draw:", error);
        showToast("Failed to reopen draw", "danger");
    }
}

async function deleteDraw(drawId) {
    if (!currentAdmin) return;

    if (!confirm("Are you sure you want to delete this draw? This action cannot be undone!")) return;

    try {
        const res = await fetch(`/admin/delete-draw/${drawId}`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_email: currentAdmin.email
            })
        });

        const data = await res.json();

        if (data.success) {
            showToast("Draw deleted successfully!", "success");
            loadAdminDraws();
        } else {
            showToast(data.message || "Failed to delete draw", "danger");
        }
    } catch (error) {
        console.error("Error deleting draw:", error);
        showToast("Failed to delete draw", "danger");
    }
}

async function createNewDraw() {
    if (!currentAdmin) return;

    const title = document.getElementById("newTitle").value;
    const userPay = document.getElementById("newUserPay").value;
    const timeInterval = document.getElementById("newTimeInterval").value;
    const winnerGet = document.getElementById("newWinnerGet").value;
    const maxParticipants = document.getElementById("newMaxParticipants").value;
    const description = document.getElementById("newDescription").value;
    const autoComplete = document.getElementById("newAutoComplete").value === 'true';

    if (!userPay || !timeInterval || !winnerGet) {
        showToast("Please fill all required fields", "warning");
        return;
    }

    const drawData = {
        user_pay: parseInt(userPay),
        time_interval: timeInterval,
        winner_get: parseInt(winnerGet),
        visible: true,
        auto_complete: autoComplete,
        user_email: currentAdmin.email
    };

    if (title) drawData.title = title;
    if (description) drawData.description = description;
    if (maxParticipants) drawData.max_participants = parseInt(maxParticipants);

    const btn = event.target;
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Creating...';

    try {
        const res = await fetch("/admin/create-draw", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(drawData)
        });

        const data = await res.json();

        if (data.success) {
            showToast(data.message, "success");

            document.getElementById("newTitle").value = "";
            document.getElementById("newUserPay").value = "";
            document.getElementById("newWinnerGet").value = "";
            document.getElementById("newMaxParticipants").value = "";
            document.getElementById("newDescription").value = "";

            loadAdminDraws();
        } else {
            showToast(data.message || "Failed to create draw", "danger");
        }
    } catch (error) {
        console.error("Error creating draw:", error);
        showToast("Failed to create draw", "danger");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

function logout() {
    localStorage.removeItem("loggedUser");
    window.location.href = "/";
}

function showToast(message, type = 'success') {
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }

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
    const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', function () {
        toast.remove();
    });
}

// ========== Load Statistics ==========
async function loadStats() {
    try {
        const res = await fetch(`/admin/payment-stats?email=${encodeURIComponent(currentAdmin.email)}`);
        if (!res.ok) throw new Error('Failed to load stats');
        const stats = await res.json();
        document.getElementById('statPaid').innerText = stats.total_paid;
        document.getElementById('statPending').innerText = stats.total_pending;
        document.getElementById('statCancelled').innerText = stats.total_cancelled;
        document.getElementById('statAmount').innerText = `Rs. ${stats.total_amount.toLocaleString()}`;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// ========== Load Users ==========
async function loadUsers() {
    try {
        const res = await fetch(`/admin/users?email=${encodeURIComponent(currentAdmin.email)}`);
        if (!res.ok) throw new Error('Failed to load users');
        const users = await res.json();
        const tbody = document.getElementById('usersTableBody');
        if (!users.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No users found</td></tr>';
            return;
        }
        tbody.innerHTML = '';
        for (const user of users) {
            // Get verification status from verifications table
            let verified = 'N/A';
            try {
                const verRes = await fetch(`/admin/verifications?email=${encodeURIComponent(currentAdmin.email)}`);
                const vers = await verRes.json();
                const userVer = vers.find(v => v.email === user.email);
                verified = userVer ? (userVer.verified ? 'Yes' : 'No') : 'No';
            } catch (e) { console.error(e); }
            const row = `
                <tr>
                    <td>${user.id.substring(0, 8)}...</td>
                    <td>${user.name}</td>
                    <td>${user.email}</td>
                    <td>
                        <select class="form-select form-select-sm user-status-select" data-id="${user.id}" data-email="${user.email}" style="width:auto; display:inline-block;">
                            <option value="user" ${user.user_status === 'user' ? 'selected' : ''}>User</option>
                            <option value="staff" ${user.user_status === 'staff' ? 'selected' : ''}>Staff</option>
                        </select>
                    </td>
                    <td>${verified}</td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="deleteUser('${user.id}')">Delete</button>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        }
        // Attach change event to status selects
        document.querySelectorAll('.user-status-select').forEach(select => {
            select.addEventListener('change', async (e) => {
                const userId = select.dataset.id;
                const newStatus = select.value;
                await updateUserStatus(userId, newStatus);
            });
        });
    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('usersTableBody').innerHTML = '<tr><td colspan="6" class="text-center text-danger">Failed to load users</td></tr>';
    }
}

async function updateUserStatus(userId, newStatus) {
    try {
        const res = await fetch(`/admin/user/${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                admin_email: currentAdmin.email,
                user_status: newStatus
            })
        });
        const data = await res.json();
        if (data.success) {
            showToast(`User status updated to ${newStatus}`, 'success');
        } else {
            showToast('Failed to update status', 'danger');
            loadUsers(); // reload to revert
        }
    } catch (error) {
        console.error(error);
        showToast('Error updating status', 'danger');
        loadUsers();
    }
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user and all their data? This action is irreversible!')) return;
    try {
        const res = await fetch(`/admin/user/${userId}?admin_email=${encodeURIComponent(currentAdmin.email)}`, {
            method: 'DELETE'
        });
        const data = await res.json();
        if (data.success) {
            showToast('User deleted successfully', 'success');
            loadUsers();           // refresh users table
            loadVerifications();   // refresh verifications table
            loadUserDraws();       // refresh user draws table
            loadStats();           // refresh statistics
        } else {
            showToast(data.message || 'Failed to delete user', 'danger');
        }
    } catch (error) {
        console.error(error);
        showToast('Error deleting user', 'danger');
    }
}

// ========== Load Verifications ==========
async function loadVerifications() {
    try {
        const res = await fetch(`/admin/verifications?email=${encodeURIComponent(currentAdmin.email)}`);
        if (!res.ok) throw new Error('Failed to load verifications');
        const vers = await res.json();
        const tbody = document.getElementById('verificationsTableBody');
        if (!vers.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No verifications found</td></tr>';
            return;
        }
        tbody.innerHTML = '';
        vers.forEach(v => {
            const row = `
                <tr>
                    <td>${v.email}</td>
                    <td>${v.name}</td>
                    <td>${v.pin}</td>
                    <td>${v.created_at || 'N/A'}</td>
                    <td>${v.expires_at || 'N/A'}</td>
                    <td>${v.verified ? 'Yes' : 'No'}</td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    } catch (error) {
        console.error('Error loading verifications:', error);
        document.getElementById('verificationsTableBody').innerHTML = '<tr><td colspan="6" class="text-center text-danger">Failed to load</td></tr>';
    }
}

// ========== Load User Draws ==========
async function loadUserDraws() {
    try {
        const res = await fetch(`/admin/user-draws?email=${encodeURIComponent(currentAdmin.email)}`);
        if (!res.ok) throw new Error('Failed to load user draws');
        const draws = await res.json();
        const tbody = document.getElementById('userDrawsTableBody');
        if (!draws.length) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">No enrollments found</td></tr>';
            return;
        }
        tbody.innerHTML = '';
        draws.forEach(d => {
            const row = `
                <tr>
                    <td>${d.user_email}</td>
                    <td>${d.lucky_draw_id}</td>
                    <td>Rs. ${d.user_pay}</td>
                    <td>${d.status}</td>
                    <td>${d.joined_at || 'N/A'}</td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    } catch (error) {
        console.error('Error loading user draws:', error);
        document.getElementById('userDrawsTableBody').innerHTML = '<tr><td colspan="5" class="text-center text-danger">Failed to load</td></tr>';
    }
}


// ========== Verification Management ==========
async function updateVerification(verificationId, field, value) {
    try {
        const payload = { admin_email: currentAdmin.email };
        payload[field] = value;
        const res = await fetch(`/admin/verification/${verificationId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            showToast(`Verification ${field} updated`, 'success');
            loadVerifications(); // refresh table
        } else {
            showToast('Update failed', 'danger');
        }
    } catch (error) {
        console.error(error);
        showToast('Error updating verification', 'danger');
    }
}

async function deleteVerification(verificationId) {
    if (!confirm('Delete this verification record?')) return;
    try {
        const res = await fetch(`/admin/verification/${verificationId}?admin_email=${encodeURIComponent(currentAdmin.email)}`, {
            method: 'DELETE'
        });
        const data = await res.json();
        if (data.success) {
            showToast('Verification deleted', 'success');
            loadVerifications(); // refresh table
        } else {
            showToast(data.detail || 'Delete failed', 'danger');
        }
    } catch (error) {
        console.error(error);
        showToast('Error deleting verification', 'danger');
    }
}

// Modify loadVerifications to include edit/delete buttons
async function loadVerifications() {
    try {
        const res = await fetch(`/admin/verifications?email=${encodeURIComponent(currentAdmin.email)}`);
        if (!res.ok) throw new Error('Failed to load verifications');
        const vers = await res.json();
        const tbody = document.getElementById('verificationsTableBody');
        if (!vers.length) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No verifications found</td></tr>';
            return;
        }
        tbody.innerHTML = '';
        vers.forEach(v => {
            const row = `
                <tr>
                    <td>${v.email}</td>
                    <td>${v.name}</td>
                    <td>
                        <input type="text" class="form-control form-control-sm pin-input" value="${v.pin}" 
                               data-id="${v.id}" style="width:100px; display:inline-block;">
                        <button class="btn btn-sm btn-primary update-pin" data-id="${v.id}">Update</button>
                    </td>
                    <td>${v.created_at || 'N/A'}</td>
                    <td>${v.expires_at || 'N/A'}</td>
                    <td>
                        <select class="form-select form-select-sm verified-select" data-id="${v.id}">
                            <option value="true" ${v.verified ? 'selected' : ''}>Yes</option>
                            <option value="false" ${!v.verified ? 'selected' : ''}>No</option>
                        </select>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-danger delete-verification" data-id="${v.id}">Delete</button>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
        // Attach event handlers
        document.querySelectorAll('.update-pin').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = btn.dataset.id;
                const input = btn.parentElement.querySelector('.pin-input');
                const newPin = input.value;
                updateVerification(id, 'pin', newPin);
            });
        });
        document.querySelectorAll('.verified-select').forEach(select => {
            select.addEventListener('change', (e) => {
                const id = select.dataset.id;
                const newValue = select.value === 'true';
                updateVerification(id, 'verified', newValue);
            });
        });
        document.querySelectorAll('.delete-verification').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = btn.dataset.id;
                deleteVerification(id);
            });
        });
    } catch (error) {
        console.error('Error loading verifications:', error);
        document.getElementById('verificationsTableBody').innerHTML = '<tr><td colspan="7" class="text-center text-danger">Failed to load</td></tr>';
    }
}

// ========== User Draw Management ==========
let allDrawsList = [];

async function loadDrawsList() {
    try {
        const res = await fetch(`/admin/draws-list?admin_email=${encodeURIComponent(currentAdmin.email)}`);
        if (!res.ok) throw new Error('Failed to load draws list');
        allDrawsList = await res.json();
    } catch (error) {
        console.error('Error loading draws list:', error);
    }
}

async function updateUserDraw(enrollmentId, field, value) {
    try {
        const payload = { admin_email: currentAdmin.email };
        payload[field] = value;
        const res = await fetch(`/admin/user-draw/${enrollmentId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            showToast('Enrollment updated', 'success');
            loadUserDraws();
        } else {
            showToast('Update failed', 'danger');
        }
    } catch (error) {
        console.error(error);
        showToast('Error updating enrollment', 'danger');
    }
}

async function deleteUserDraw(enrollmentId) {
    if (!confirm('Delete this enrollment?')) return;
    try {
        const res = await fetch(`/admin/user-draw/${enrollmentId}?admin_email=${encodeURIComponent(currentAdmin.email)}`, {
            method: 'DELETE'
        });
        const data = await res.json();
        if (data.success) {
            showToast('Enrollment deleted', 'success');
            loadUserDraws();
        } else {
            showToast('Delete failed', 'danger');
        }
    } catch (error) {
        console.error(error);
        showToast('Error deleting enrollment', 'danger');
    }
}

// Modify loadUserDraws to include edit/delete and draw dropdown
async function loadUserDraws() {
    try {
        await loadDrawsList(); // ensure dropdown options are ready
        const res = await fetch(`/admin/user-draws?email=${encodeURIComponent(currentAdmin.email)}`);
        if (!res.ok) throw new Error('Failed to load user draws');
        const draws = await res.json();
        const tbody = document.getElementById('userDrawsTableBody');
        if (!draws.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No enrollments found</td></tr>';
            return;
        }
        tbody.innerHTML = '';
        draws.forEach(d => {
            const statusOptions = ['open', 'pending', 'win', 'loss'];
            const statusSelect = `<select class="form-select form-select-sm status-select" data-id="${d.id}">
                ${statusOptions.map(opt => `<option value="${opt}" ${d.status === opt ? 'selected' : ''}>${opt}</option>`).join('')}
            </select>`;
            const drawOptions = allDrawsList.map(draw => `<option value="${draw.id}" ${d.lucky_draw_id === draw.id ? 'selected' : ''}>${draw.title} (${draw.id})</option>`).join('');
            const drawSelect = `<select class="form-select form-select-sm draw-select" data-id="${d.id}">
                ${drawOptions}
            </select>`;
            const row = `
                <tr>
                    <td>${d.user_email}</td>
                    <td>${drawSelect}</td>
                    <td>Rs. ${d.user_pay}</td>
                    <td>${statusSelect}</td>
                    <td>${d.joined_at || 'N/A'}</td>
                    <td><button class="btn btn-sm btn-danger delete-enrollment" data-id="${d.id}">Delete</button></td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
        // Attach event handlers
        document.querySelectorAll('.status-select').forEach(select => {
            select.addEventListener('change', (e) => {
                const id = select.dataset.id;
                updateUserDraw(id, 'status', select.value);
            });
        });
        document.querySelectorAll('.draw-select').forEach(select => {
            select.addEventListener('change', (e) => {
                const id = select.dataset.id;
                updateUserDraw(id, 'lucky_draw_id', select.value);
            });
        });
        document.querySelectorAll('.delete-enrollment').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = btn.dataset.id;
                deleteUserDraw(id);
            });
        });
    } catch (error) {
        console.error('Error loading user draws:', error);
        document.getElementById('userDrawsTableBody').innerHTML = '<tr><td colspan="6" class="text-center text-danger">Failed to load</td></tr>';
    }
}

// Also extend loadUsers to allow name editing (inline)
async function loadUsers() {
    try {
        const res = await fetch(`/admin/users?email=${encodeURIComponent(currentAdmin.email)}`);
        if (!res.ok) throw new Error('Failed to load users');
        const users = await res.json();
        const tbody = document.getElementById('usersTableBody');
        if (!users.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No users found</td></tr>';
            return;
        }
        tbody.innerHTML = '';
        for (const user of users) {
            // Get verification status
            let verified = 'N/A';
            try {
                const verRes = await fetch(`/admin/verifications?email=${encodeURIComponent(currentAdmin.email)}`);
                const vers = await verRes.json();
                const userVer = vers.find(v => v.email === user.email);
                verified = userVer ? (userVer.verified ? 'Yes' : 'No') : 'No';
            } catch (e) { console.error(e); }
            const row = `
                <tr>
                    <td>${user.id.substring(0, 8)}...</td>
                    <td>
                        <input type="text" class="form-control form-control-sm user-name-input" value="${user.name}" data-id="${user.id}" style="width:150px;">
                        <button class="btn btn-sm btn-primary update-name" data-id="${user.id}">Save</button>
                    </td>
                    <td>${user.email}</td>
                    <td>
                        <select class="form-select form-select-sm user-status-select" data-id="${user.id}">
                            <option value="user" ${user.user_status === 'user' ? 'selected' : ''}>User</option>
                            <option value="staff" ${user.user_status === 'staff' ? 'selected' : ''}>Staff</option>
                        </select>
                    </td>
                    <td>${verified}</td>
                    <td><button class="btn btn-sm btn-danger delete-user" data-id="${user.id}">Delete</button></td>
                </tr>
            `;
            tbody.innerHTML += row;
        }
        // Name update
        document.querySelectorAll('.update-name').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const userId = btn.dataset.id;
                const newName = btn.parentElement.querySelector('.user-name-input').value;
                await updateUserField(userId, 'name', newName);
            });
        });
        // Status update
        document.querySelectorAll('.user-status-select').forEach(select => {
            select.addEventListener('change', async (e) => {
                const userId = select.dataset.id;
                const newStatus = select.value;
                await updateUserField(userId, 'user_status', newStatus);
            });
        });
        // Delete user
        document.querySelectorAll('.delete-user').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const userId = btn.dataset.id;
                await deleteUser(userId);
            });
        });
    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('usersTableBody').innerHTML = '<tr><td colspan="6" class="text-center text-danger">Failed to load users</td></tr>';
    }
}

async function updateUserField(userId, field, value) {
    try {
        const payload = { admin_email: currentAdmin.email };
        payload[field] = value;
        const res = await fetch(`/admin/user/${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            showToast(`User ${field} updated`, 'success');
            loadUsers(); // refresh to show changes
        } else {
            showToast('Update failed', 'danger');
        }
    } catch (error) {
        console.error(error);
        showToast('Error updating user', 'danger');
    }
}