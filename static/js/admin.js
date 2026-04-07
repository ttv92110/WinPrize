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