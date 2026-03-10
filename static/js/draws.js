async function loadDraws() {
    try {
        let res = await fetch("/draws/");
        let draws = await res.json();
        let container = document.getElementById("drawContainer");
        let user = JSON.parse(localStorage.getItem("loggedUser"));

        if (!container) return;

        container.innerHTML = "";

        if (draws.length === 0) {
            container.innerHTML = '<div class="col-12 text-center"><h3>No active draws available</h3></div>';
            return;
        }

        // Get participant counts for all draws
        const participantCounts = {};
        for (const draw of draws) {
            if (draw.visible) {
                try {
                    const countRes = await fetch(`/draws/participants/count/${draw.id}`);
                    const countData = await countRes.json();
                    participantCounts[draw.id] = countData.participants;
                } catch (error) {
                    participantCounts[draw.id] = Math.floor(Math.random() * 50) + 10;
                }
            }
        }

        // Check which draws user has joined
        const joinedDraws = {};
        if (user) {
            try {
                const userDrawsRes = await fetch(`/draws/user/${user.email}`);
                const userDraws = await userDrawsRes.json();
                userDraws.forEach(item => {
                    joinedDraws[item.draw.id] = item.participation;
                });
            } catch (error) {
                console.error("Error fetching user draws:", error);
            }
        }

        for (let i = 0; i < draws.length; i++) {
            const draw = draws[i];
            if (draw.visible) {
                let timeIcon = draw.time_interval === 'day' ? 'fa-sun' :
                    draw.time_interval === 'week' ? 'fa-calendar-week' : 'fa-calendar-alt';

                // Get accurate time left
                let timeLeft = "Loading...";
                let timeStatus = "";

                try {
                    const timeRes = await fetch(`/draws/time-left/${draw.id}`);
                    const timeData = await timeRes.json();
                    timeLeft = timeData.time_left;
                    timeStatus = timeData.status || draw.status;
                } catch (error) {
                    console.error("Error fetching time left:", error);
                    timeLeft = "Unknown";
                }

                // Determine badge color and text
                let badgeClass = 'bg-success';
                let badgeIcon = 'fa-bolt';
                let badgeText = 'LIVE';

                if (draw.status === 'completed') {
                    badgeClass = 'bg-primary';
                    badgeIcon = 'fa-check-circle';
                    badgeText = 'COMPLETED';
                } else if (draw.status === 'awaiting') {
                    badgeClass = 'bg-warning text-dark';
                    badgeIcon = 'fa-clock';
                    badgeText = 'AWAITING';
                } else if (draw.status === 'finished') {
                    badgeClass = 'bg-secondary';
                    badgeIcon = 'fa-flag';
                    badgeText = 'FINISHED';
                }

                const participantsCount = participantCounts[draw.id] || 0;

                // Check if user has joined this specific draw - FIXED: Define userJoined here
                const userJoined = joinedDraws[draw.id];

                let card = `<div class="col-lg-4 col-md-6 mb-4" data-aos="fade-up" data-aos-delay="${i * 100}">
                    <div class="draw-card ${draw.status !== 'open' ? 'completed-draw' : ''}">
                        <div class="card-badge ${badgeClass}">
                            <i class="fas ${badgeIcon} me-1"></i>
                            ${badgeText}
                        </div>
                        <div class="card-body">
                            <div class="text-center mb-3">
                                <span class="time-badge">
                                    <i class="fas ${timeIcon} me-2"></i>
                                    ${draw.time_interval.charAt(0).toUpperCase() + draw.time_interval.slice(1)}ly Draw
                                </span>
                            </div>
                            
                            <h5 class="text-center mb-2">${draw.title || ''}</h5>
                            
                            <div class="price-tag text-center">
                                <small class="text-muted">Entry Fee</small>
                                <div>
                                    <span class="display-6 fw-bold">Rs. ${draw.user_pay}</span>
                                </div>
                            </div>
                            
                            <div class="prize-section text-center my-4">
                                <small class="text-muted">Prize Pool</small>
                                <div class="prize-amount">
                                    <span class="display-5 fw-bold text-success">Rs. ${draw.winner_get}</span>
                                </div>
                            </div>
                            
                            <div class="draw-stats d-flex justify-content-around mb-4">
                                <div class="text-center">
                                    <small class="text-muted d-block">Entries</small>
                                    <span class="fw-bold">${participantsCount}</span>
                                </div>
                                <div class="text-center">
                                    <small class="text-muted d-block">Time Left</small>
                                    <span class="fw-bold ${timeLeft === 'Ended' ? 'text-danger' : 'text-primary'}">
                                        <i class="fas fa-clock me-1"></i>
                                        ${timeLeft}
                                    </span>
                                </div>
                            </div>`;

                if (draw.status === 'completed') {
                    card += `<button onclick="viewResult('${draw.id}')" 
                                    class="btn-result">
                                <i class="fas fa-trophy me-2"></i>
                                View Result
                            </button>`;
                } else if (draw.status === 'awaiting') {
                    card += `<div class="awaiting-status text-center">
                                <span class="badge bg-warning text-dark p-3 w-100">
                                    <i class="fas fa-hourglass-half me-2"></i>
                                    Awaiting Result Announcement
                                </span>
                            </div>`;
                } else if (userJoined) {
                    // User has joined this draw
                    const status = userJoined.status === "win" ? "You won! 🎉" :
                        userJoined.status === "loss" ? "You lost 😢" :
                            "You've joined";
                    card += `<div class="joined-status text-center">
                                <span class="badge bg-info p-3 w-100">
                                    <i class="fas fa-check-circle me-2"></i>
                                    ${status}
                                </span>
                            </div>`;
                } else if (draw.status === 'open') {
                    // Draw is open and user hasn't joined
                    card += `<button onclick="joinDraw('${draw.id}', ${draw.user_pay})" 
                                    class="btn-join ${!isLoggedIn() ? 'disabled' : ''}"
                                    ${!isLoggedIn() ? 'disabled' : ''}>
                                <i class="fas ${isLoggedIn() ? 'fa-hand-pointer' : 'fa-lock'} me-2"></i>
                                ${isLoggedIn() ? 'Join Draw Now' : 'Login to Join'}
                            </button>`;
                }

                card += `   <div class="mt-3 text-center">
                                <small class="text-muted">
                                    <i class="fas fa-users me-1"></i>
                                    ${participantsCount} people joined
                                </small>
                            </div>
                        </div>
                    </div>
                </div>`;

                container.innerHTML += card;
            }
        }
    } catch (error) {
        console.error("Error loading draws:", error);
        // Show error message to user
        const container = document.getElementById("drawContainer");
        if (container) {
            container.innerHTML = '<div class="col-12 text-center"><div class="alert alert-danger">Error loading draws. Please refresh the page.</div></div>';
        }
    }
}

function viewResult(drawId) {
    localStorage.setItem("view_result_draw", drawId);
    window.location.href = "/winner";
}

async function checkUserJoined(drawId) {
    const user = JSON.parse(localStorage.getItem("loggedUser"));
    if (!user) return false;

    try {
        const res = await fetch(`/draws/check/joined/${user.email}/${drawId}`);
        const data = await res.json();
        return data.joined;
    } catch (error) {
        console.error("Error checking join status:", error);
        return false;
    }
}

function isLoggedIn() {
    return localStorage.getItem("loggedUser") !== null;
}

async function joinDraw(drawId, payAmount) {
    if (!isLoggedIn()) {
        showLoginPrompt();
        return;
    }

    const joined = await checkUserJoined(drawId);
    if (joined) {
        showToast("You have already joined this draw!", "info");
        return;
    }

    localStorage.setItem("selected_draw", JSON.stringify({
        id: drawId,
        pay: payAmount
    }));

    window.location.href = "/confirm";
}

function showLoginPrompt() {
    // Check if modal already exists
    let modal = document.getElementById('loginPromptModal');
    if (modal) {
        modal.remove();
    }

    modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'loginPromptModal';
    modal.setAttribute('tabindex', '-1');
    modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header border-0">
                    <h5 class="modal-title">
                        <i class="fas fa-lock text-warning me-2"></i>
                        Login Required
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body text-center py-4">
                    <i class="fas fa-user-circle fa-4x text-primary mb-3"></i>
                    <h5>Please login to join this draw</h5>
                    <p class="text-muted">Create an account or login to participate in lucky draws and win amazing prizes!</p>
                </div>
                <div class="modal-footer border-0 justify-content-center">
                    <button class="btn btn-primary px-4" onclick="showLoginModal()">
                        <i class="fas fa-sign-in-alt me-2"></i>Login
                    </button>
                    <button class="btn btn-warning px-4" onclick="showRegisterModal()">
                        <i class="fas fa-user-plus me-2"></i>Register
                    </button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();

    modal.addEventListener('hidden.bs.modal', function () {
        modal.remove();
    });
}

function showLoginModal() {
    // Hide login prompt if open
    const promptModal = document.getElementById('loginPromptModal');
    if (promptModal) {
        const modal = bootstrap.Modal.getInstance(promptModal);
        if (modal) modal.hide();
    }

    // Show login modal
    const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    loginModal.show();
}

function showRegisterModal() {
    // Hide login prompt if open
    const promptModal = document.getElementById('loginPromptModal');
    if (promptModal) {
        const modal = bootstrap.Modal.getInstance(promptModal);
        if (modal) modal.hide();
    }

    // Show register modal
    const registerModal = new bootstrap.Modal(document.getElementById('registerModal'));
    registerModal.show();
}

function showToast(message, type = 'success') {
    // Check if toast element exists
    let toast = document.getElementById('dynamicToast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'dynamicToast';
        toast.className = 'toast align-items-center text-white border-0 position-fixed bottom-0 end-0 m-3';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.style.zIndex = '9999';

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body" id="dynamicToastMessage"></div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        document.body.appendChild(toast);
    }

    toast.className = `toast align-items-center text-white bg-${type} border-0 position-fixed bottom-0 end-0 m-3`;
    document.getElementById('dynamicToastMessage').textContent = message;

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// Load draws when page loads
document.addEventListener('DOMContentLoaded', loadDraws);
// Refresh time every minute
setInterval(loadDraws, 60000);