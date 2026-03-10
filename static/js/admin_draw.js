async function runDraw(drawId) {
    if (!confirm(`Are you sure you want to run this draw?`)) {
        return;
    }

    try {
        let res = await fetch(`/admin/run-draw/${drawId}`, {
            method: "POST"
        });
        let data = await res.json();

        if (data.success) {
            if (data.winner) {
                alert(`Winner: ${data.winner.user_email}`);
            } else {
                alert("No participants for this draw");
            }
        } else {
            alert(data.message || "Failed to run draw");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred while running the draw");
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
        alert(data.message);
        location.reload();
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to create draw");
    }
}
