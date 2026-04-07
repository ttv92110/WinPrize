async function runDraw(drawId) {

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
        showToast(`An error occurred : ${error}`, "danger");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

async function createNewDraw() {
    let userPay = prompt("Enter amount to pay (Rs):");
    if (!userPay) return;

    let timeInterval = prompt("Enter time interval (day/week/month):");
    if (!timeInterval) return;

    let winnerGet = prompt("Enter winner prize amount (Rs):");
    if (!winnerGet) return;

    try {
        let res = await fetch("/admin/create-draw", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_pay: parseInt(userPay),
                time_interval: timeInterval,
                winner_get: parseInt(winnerGet),
                visible: true
            })
        });

        let data = await res.json();
        // alert(data.message);
        location.reload();
    } catch (error) { 
        console(`Failed to create draw . ${error}`);
    }
}
