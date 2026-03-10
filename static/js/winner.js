document.addEventListener('DOMContentLoaded', function () {
    loadWinners();
    loadUserDrawResult();
});

function maskEmail(email) {
    if (!email) return '';

    const parts = email.split('@');
    if (parts.length !== 2) return email;

    const username = parts[0];
    const domain = parts[1];

    if (username.length <= 3) {
        // For short usernames like "ak9" -> show last character only
        const lastChar = username.slice(-1);
        return '*'.repeat(username.length - 1) + lastChar + '@' + domain;
    } else {
        // For longer usernames, show last 3 characters
        const lastThree = username.slice(-3);
        return '*'.repeat(username.length - 3) + lastThree + '@' + domain;
    }
}

function getWinnerName(winner) {
    // Try different possible name fields
    return winner.user_name ||
        winner.winner_name ||
        winner.name ||
        (winner.user ? winner.user.name : null) ||
        'Winner';
}

async function loadWinners() {
    try {
        const res = await fetch("/draws/winners/list");

        if (!res.ok) {
            console.error("Failed to load winners:", res.status);
            showWinnersFallback();
            return;
        }

        const winners = await res.json();
        const winnerList = document.getElementById("winnerList");

        if (!winnerList) return;

        if (!winners || winners.length === 0) {
            winnerList.innerHTML = '<div class="text-center py-5"><i class="fas fa-trophy fa-4x text-muted mb-3"></i><h3>No winners yet</h3><p class="text-muted">Be the first to win!</p></div>';
            return;
        }

        winnerList.innerHTML = '';
        winners.forEach(item => {
            const winner = item.winner;
            const winnerName = getWinnerName(winner);
            const maskedEmail = maskEmail(winner.user_email);

            const winnerCard = `
                <div class="winner-card mb-3">
                    <div class="d-flex align-items-center">
                        <div class="winner-avatar me-3">
                            <i class="fas fa-crown text-warning"></i>
                        </div>
                        <div class="flex-grow-1">
                            <h5 class="mb-1">${winnerName}</h5>
                            <p class="mb-0 text-muted">
                                <i class="fas fa-envelope me-1"></i> ${maskedEmail}
                            </p>
                            <p class="mb-0 text-muted">
                                Won Rs. ${item.draw.winner_get} in ${item.draw.time_interval}ly draw
                            </p>
                            <small class="text-success">
                                <i class="fas fa-check-circle me-1"></i>
                                ${new Date().toLocaleDateString()}
                            </small>
                        </div>
                        <div class="prize-badge">
                            <span class="badge bg-warning text-dark p-3">
                                <i class="fas fa-trophy me-1"></i>
                                WINNER
                            </span>
                        </div>
                    </div>
                </div>
            `;
            winnerList.innerHTML += winnerCard;
        });
    } catch (error) {
        console.error("Error loading winners:", error);
        showWinnersFallback();
    }
}

function showWinnersFallback() {
    const winnerList = document.getElementById("winnerList");
    if (winnerList) {
        winnerList.innerHTML = '<div class="text-center py-5"><i class="fas fa-trophy fa-4x text-muted mb-3"></i><h3>Unable to load winners</h3><p class="text-muted">Please try again later</p></div>';
    }
}

async function loadUserDrawResult() {
    const user = JSON.parse(localStorage.getItem("loggedUser"));
    const viewDrawId = localStorage.getItem("view_result_draw");

    if (!user && !viewDrawId) return;

    try {
        let drawsToShow = [];

        if (viewDrawId) {
            // Show specific draw result
            const drawRes = await fetch(`/draws/${viewDrawId}`);
            const draw = await drawRes.json();

            // Get winner for this draw
            const winnersRes = await fetch("/draws/winners/list");
            const winners = await winnersRes.json();
            const drawWinner = winners.find(w => w.draw.id === viewDrawId);

            if (drawWinner) {
                drawsToShow.push({
                    draw: draw,
                    winner: drawWinner.winner
                });
            }

            // Clear stored draw ID
            localStorage.removeItem("view_result_draw");
        } else if (user) {
            // Show all draws user participated in
            const userDrawsRes = await fetch(`/draws/user/${user.email}`);
            const userDraws = await userDrawsRes.json();

            // Filter for completed draws
            const completedDraws = userDraws.filter(item =>
                item.draw.status === "completed" || item.draw.status === "finished"
            );

            // Get winners info
            const winnersRes = await fetch("/draws/winners/list");
            const winners = await winnersRes.json();

            completedDraws.forEach(item => {
                const winner = winners.find(w => w.draw.id === item.draw.id);
                if (winner) {
                    drawsToShow.push({
                        draw: item.draw,
                        winner: winner.winner,
                        userStatus: item.participation.status
                    });
                }
            });
        }

        // Display user results
        const userResultsContainer = document.getElementById("userResults");
        if (!userResultsContainer) return;

        if (drawsToShow.length === 0) {
            userResultsContainer.innerHTML = '<div class="text-center py-4"><p class="text-muted">No results available yet</p></div>';
            return;
        }

        userResultsContainer.innerHTML = '<h4 class="mb-3">Your Results</h4>';
        drawsToShow.forEach(item => {
            const isUserWinner = user && item.winner.user_email === user.email;
            const winnerName = getWinnerName(item.winner);
            const maskedWinnerEmail = maskEmail(item.winner.user_email);

            const resultCard = `
                <div class="result-card mb-3 ${isUserWinner ? 'winner-bg' : ''}">
                    <div class="d-flex align-items-center">
                        <div class="result-icon me-3">
                            <i class="fas ${isUserWinner ? 'fa-trophy text-warning' : 'fa-times-circle text-danger'} fa-2x"></i>
                        </div>
                        <div class="flex-grow-1">
                            <h5 class="mb-1">${item.draw.time_interval.charAt(0).toUpperCase() + item.draw.time_interval.slice(1)}ly Draw</h5>
                            <p class="mb-0">
                                Winner: <strong>${winnerName}</strong> 
                                ${isUserWinner ? '<span class="badge bg-success ms-2">You Won! 🎉</span>' : ''}
                            </p>
                            <p class="mb-0 text-muted small">
                                <i class="fas fa-envelope me-1"></i> ${maskedWinnerEmail}
                            </p>
                            <small class="text-muted">
                                Prize: Rs. ${item.draw.winner_get} | Entry: Rs. ${item.draw.user_pay}
                            </small>
                        </div>
                        <div class="result-date">
                            <small class="text-muted">
                                ${new Date().toLocaleDateString()}
                            </small>
                        </div>
                    </div>
                </div>
            `;
            userResultsContainer.innerHTML += resultCard;
        });
    } catch (error) {
        console.error("Error loading user results:", error);
    }
}