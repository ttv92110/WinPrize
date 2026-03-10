let currentAdmin = null;
let editModal = null;
let accessDeniedModal = null;

document.addEventListener('DOMContentLoaded', function () {
    // Initialize modals
    editModal = new bootstrap.Modal(document.getElementById('editDrawModal'));
    accessDeniedModal = new bootstrap.Modal(document.getElementById('accessDeniedModal'));

    // Check admin status immediately
    checkAdminStatus();
});

async function checkAdminStatus() {
    const loadingState = document.getElementById('loadingState');
    const adminContent = document.getElementById('adminContent');

    try {
        const user = JSON.parse(localStorage.getItem("loggedUser"));

        if (!user) {
            // No user logged in
            showAccessDenied("Please login first");
            return;
        }

        // Verify admin status with backend
        const response = await fetch(`/admin/verify-admin?email=${encodeURIComponent(user.email)}`);
        const data = await response.json();

        if (data.isAdmin) {
            // User is admin, show admin content
            currentAdmin = { email: user.email, name: user.name };
            document.getElementById("adminEmail").value = user.email;

            // Hide loading, show content
            loadingState.style.display = 'none';
            adminContent.style.display = 'block';

            // Load admin draws
            loadAdminDraws();
        } else {
            // User is not admin
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

    // Hide loading and content
    loadingState.style.display = 'none';
    adminContent.style.display = 'none';

    // Update modal message if needed
    const modalBody = document.querySelector('#accessDeniedModal .modal-body p:first-of-type');
    if (modalBody && message) {
        modalBody.textContent = message;
    }

    // Show access denied modal
    accessDeniedModal.show();

    // Redirect to home after 3 seconds
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
                setTimeout(() => {
                    logout();
                }, 2000);
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
                            ${draw.status === 'awaiting' ?
                    '<br><small class="text-warning">Needs attention!</small>' : ''}
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
                    `<button class="btn btn-sm btn-success" onclick="runDraw('${draw.id}')">
                                        <i class="fas fa-play"></i> Run
                                    </button>` : ''}
                                ${draw.status === 'awaiting' ?
                    `<button class="btn btn-sm btn-warning" onclick="runDraw('${draw.id}')">
                                        <i class="fas fa-trophy"></i> Announce
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
        case 'open':
            return '<span class="badge bg-success">OPEN</span>';
        case 'awaiting':
            return '<span class="badge bg-warning text-dark">AWAITING ⚠️</span>';
        case 'completed':
            return '<span class="badge bg-primary">COMPLETED</span>';
        case 'finished':
            return '<span class="badge bg-secondary">FINISHED</span>';
        default:
            return '<span class="badge bg-secondary">UNKNOWN</span>';
    }
}

async function editDraw(drawId) {
    if (!currentAdmin) return;

    try {
        const res = await fetch(`/draws/${drawId}`);
        const draw = await res.json();

        // Populate modal
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

        // Parse and set datetime
        if (draw.closed_at) {
            try {
                const parts = draw.closed_at.match(/(\d+)\/(\d+)\/(\d+)T(\d+)h:(\d+)m:(\d+)s/);
                if (parts) {
                    const [_, day, month, year, hour, minute, second] = parts;
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
        alert("Failed to load draw details");
    }
}

async function saveDrawChanges() {
    if (!currentAdmin) return;

    const drawId = document.getElementById('editDrawId').value;
    const closedAt = document.getElementById('editClosedAt').value;

    // Format closed_at back to required format
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
            alert("Draw updated successfully!");
            editModal.hide();
            loadAdminDraws();
        } else {
            alert(data.message || "Failed to update draw");
        }
    } catch (error) {
        console.error("Error updating draw:", error);
        alert("Failed to update draw");
    }
}

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
            alert("Draw reopened successfully!");
            loadAdminDraws();
        } else {
            alert(data.message || "Failed to reopen draw");
        }
    } catch (error) {
        console.error("Error reopening draw:", error);
        alert("Failed to reopen draw");
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
            alert("Draw deleted successfully!");
            loadAdminDraws();
        } else {
            alert(data.message || "Failed to delete draw");
        }
    } catch (error) {
        console.error("Error deleting draw:", error);
        alert("Failed to delete draw");
    }
}


async function runDraw(drawId) {
    if (!currentAdmin) return;

    const action = confirm("Do you want to manually select a winner? Click OK to enter email, Cancel for random selection.");

    if (action) {
        const winnerEmail = prompt("Enter winner email:");
        if (winnerEmail && winnerEmail.trim() !== "") {
            try {
                const res = await fetch(`/admin/update-result/${drawId}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        user_email: currentAdmin.email,
                        winner_email: winnerEmail.trim()
                    })
                });

                const data = await res.json();
                if (data.success) {
                    alert(`Winner: ${data.winner.name} (${winnerEmail})`);
                    loadAdminDraws();
                } else {
                    alert(data.message || "Failed to update result");
                }
            } catch (error) {
                console.error("Error updating result:", error);
                alert("An error occurred");
            }
        }
    } else {
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
                    alert(`Winner: ${data.winner.user_name || 'Winner'} (${data.winner.user_email})`);
                } else {
                    alert(data.message || "No participants for this draw");
                }
                loadAdminDraws();
            } else {
                alert(data.message || "Failed to run draw");
            }
        } catch (error) {
            console.error("Error running draw:", error);
            alert("An error occurred");
        }
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
        alert("Please fill all required fields");
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

    try {
        const res = await fetch("/admin/create-draw", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(drawData)
        });

        const data = await res.json();

        if (data.success) {
            alert(data.message);

            // Clear form
            document.getElementById("newTitle").value = "";
            document.getElementById("newUserPay").value = "";
            document.getElementById("newWinnerGet").value = "";
            document.getElementById("newMaxParticipants").value = "";
            document.getElementById("newDescription").value = "";

            loadAdminDraws();
        } else {
            alert(data.message || "Failed to create draw");
        }
    } catch (error) {
        console.error("Error creating draw:", error);
        alert("Failed to create draw");
    }
}

function logout() {
    localStorage.removeItem("loggedUser");
    window.location.href = "/";
}