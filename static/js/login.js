async function login() {
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;

    let res = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    let data = await res.json();
    if (data.success) {
        localStorage.setItem("loggedUser", JSON.stringify(data.user));
        window.location.href = "/";
    } else {
        alert(data.message);
    }
} async function login() {
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;

    let res = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    let data = await res.json();
    if (data.success) {
        localStorage.setItem("loggedUser", JSON.stringify(data.user));
        window.location.href = "/";
    } else {
        alert(data.message);
    }
}
