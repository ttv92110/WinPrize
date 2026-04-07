document.addEventListener('DOMContentLoaded', function () {
    // Display draw info
    let draw = JSON.parse(localStorage.getItem("selected_draw"));
    let payAmountElement = document.getElementById("payAmount");

    if (draw) {
        payAmountElement.textContent = `Pay Amount: ${draw.pay} Rs`;
    } else {
        payAmountElement.textContent = "No draw selected";
        document.getElementById("confirmBtn").disabled = true;
    }

    // Pre-fill email if user is logged in
    let user = JSON.parse(localStorage.getItem("loggedUser"));
    if (user && user.email) {
        document.getElementById("email").value = user.email;
    }
});

async function confirmEnroll() {
    let user = JSON.parse(localStorage.getItem("loggedUser"));
    if (!user) {
        showToast("Please login first", "alert");
        window.location.href = "/login";
        return;
    }

    let draw = JSON.parse(localStorage.getItem("selected_draw"));
    if (!draw) {
        showToast("No draw selected", "info");
        window.location.href = "/";
        return;
    }

    let email = document.getElementById("email").value;
    if (!email) {
        showToast("Please enter your email", "alert");
        return;
    }

    try {
        let res = await fetch("/draws/join", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_email: email,
                user_pay: draw.pay,
                lucky_draw_id: draw.id
            })
        });

        let data = await res.json();

        if (data.success) {
            showToast("Successfully enrolled in the draw!", "success");
            localStorage.removeItem("selected_draw"); // Clear selected draw
            window.location.href = "/";
        } else {
            showToast(data.message || "Failed to enroll.Maybe participant completed.");
        }
    } catch (error) {
        console.error("Error:", error);
        showToast("An error occurred. Please try again.", "error");
    }
}

document.getElementById("confirmBtn")?.addEventListener("click", confirmEnroll);
