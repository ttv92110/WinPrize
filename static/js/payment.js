let selectedDraw = null;
let currentUser = null;

document.addEventListener('DOMContentLoaded', function () {
    // Check login
    currentUser = JSON.parse(localStorage.getItem("loggedUser"));
    if (!currentUser) {
        window.location.href = "/";
        return;
    }

    // Get selected draw
    selectedDraw = JSON.parse(localStorage.getItem("selected_draw"));
    if (!selectedDraw) {
        showError("No draw selected. Please go back and select a draw.");
        return;
    }

    loadDrawDetails();
    setupEventListeners();
});

async function loadDrawDetails() {
    showLoading(true);

    try {
        // Fetch draw details
        const drawRes = await fetch(`/draws/${selectedDraw.id}`);
        const draw = await drawRes.json();

        if (!draw || draw.status !== 'open') {
            showError("This draw is no longer available.");
            return;
        }

        // Display draw info
        document.getElementById('displayAmount').textContent = `Rs. ${draw.user_pay}`;
        document.getElementById('displayDrawTitle').textContent = draw.title || `${draw.time_interval}ly Draw`;
        document.getElementById('displayDrawId').textContent = `Draw ID: ${draw.id}`;
        document.getElementById('drawId').value = draw.id;
        document.getElementById('userEmail').value = currentUser.email;
        document.getElementById('amount').value = draw.user_pay;
        document.getElementById('confirmAmount').textContent = `Rs. ${draw.user_pay}`;

        // Check if user already has pending payment
        const checkRes = await fetch(`/payments/check/${currentUser.email}/${draw.id}`);
        const checkData = await checkRes.json();

        if (checkData.has_payment && checkData.status === 'pending') {
            showSuccess("You already have a pending payment for this draw.");
            return;
        }

        // Show form
        showLoading(false);
        document.getElementById('paymentForm').style.display = 'block';

    } catch (error) {
        console.error("Error loading draw details:", error);
        showError("Failed to load draw details. Please try again.");
    }
}

function setupEventListeners() {
    // Bank selection change
    document.getElementById('bankTo').addEventListener('change', async function (e) {
        const bankName = e.target.value;
        if (bankName) {
            await loadBankDetails(bankName);
        } else {
            document.getElementById('recipientDetails').style.display = 'none';
        }
    });

    // Form submission
    document.getElementById('paymentDetailsForm').addEventListener('submit', async function (e) {
        e.preventDefault();
        await submitPayment();
    });
}

async function loadBankDetails(bankName) {
    try {
        const res = await fetch(`/payments/bank-account/${bankName}`);
        const bankData = await res.json();

        // Update bank details display
        document.getElementById('bankName').textContent = bankName;
        document.getElementById('accountTitle').textContent = bankData.holder_name;
        document.getElementById('accountNumber').textContent = bankData.account_number;
        document.getElementById('bankInstructions').innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            ${bankData.instructions}
        `;

        // Show recipient details in form
        document.getElementById('recipientAccount').textContent = bankData.account_number;
        document.getElementById('recipientName').textContent = bankData.holder_name;
        document.getElementById('recipientDetails').style.display = 'block';

    } catch (error) {
        console.error("Error loading bank details:", error);
    }
}

async function submitPayment() {
    // Validate form
    const holderName = document.getElementById('holderName').value.trim();
    const bankFrom = document.getElementById('bankFrom').value;
    const accountFrom = document.getElementById('accountFrom').value.trim();
    const bankTo = document.getElementById('bankTo').value;
    const transactionId = document.getElementById('transactionId').value.trim();
    const termsCheck = document.getElementById('termsCheck').checked;

    if (!holderName || !bankFrom || !accountFrom || !bankTo || !transactionId) {
        alert("Please fill all required fields");
        return;
    }

    if (!termsCheck) {
        alert("Please confirm that you have made the payment");
        return;
    }

    // Get draw title
    const drawTitle = document.getElementById('displayDrawTitle').textContent;

    // Show loading
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting...';

    try {
        const paymentData = {
            user_email: currentUser.email,
            user_name: currentUser.name,
            lucky_draw_id: selectedDraw.id,
            lucky_draw_title: drawTitle,
            amount: parseInt(document.getElementById('amount').value),
            holder_name: holderName,
            account_bank_from: bankFrom,
            account_number_from: accountFrom,
            account_bank_to: bankTo,
            transaction_id: transactionId
        };

        const res = await fetch("/payments/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(paymentData)
        });

        const data = await res.json();

        if (data.success) {
            // Clear selected draw
            localStorage.removeItem("selected_draw");

            // Show success state
            document.getElementById('paymentForm').style.display = 'none';
            document.getElementById('successState').style.display = 'block';

            // Store payment info for status checking
            localStorage.setItem("last_payment", JSON.stringify({
                draw_id: selectedDraw.id,
                payment_id: data.payment_id,
                bank_details: data.bank_details
            }));

        } else {
            alert(data.detail || "Failed to submit payment");
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-check-circle me-2"></i>Submit Payment Details';
        }
    } catch (error) {
        console.error("Error submitting payment:", error);
        alert("An error occurred. Please try again.");
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-check-circle me-2"></i>Submit Payment Details';
    }
}

function viewPaymentStatus() {
    window.location.href = "/payment-status";
}

function showLoading(show) {
    document.getElementById('loadingState').style.display = show ? 'block' : 'none';
    document.getElementById('paymentForm').style.display = show ? 'none' : 'block';
    document.getElementById('errorState').style.display = 'none';
    document.getElementById('successState').style.display = 'none';
}

function showError(message) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('paymentForm').style.display = 'none';
    document.getElementById('successState').style.display = 'none';
    document.getElementById('errorState').style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
}

function showSuccess(message) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('paymentForm').style.display = 'none';
    document.getElementById('errorState').style.display = 'none';
    document.getElementById('successState').style.display = 'block';

    // Show message in success state
    const successDiv = document.getElementById('successState');
    const alertDiv = successDiv.querySelector('.alert');
    if (alertDiv) {
        alertDiv.innerHTML = `<i class="fas fa-clock me-2"></i>${message}`;
    }
}