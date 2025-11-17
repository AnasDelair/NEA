const loginMessage = document.getElementById("login-message")

document.getElementById("login-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    console.log(this)

    const password = this.password.value;

    const response = await fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ password: password })
    });

    const data = await response.json();

    loginMessage.style.color = "#8e4e4eff"
    if (data.success) {
        loginMessage.style.color = "#6b8e4e"
        setTimeout(() => { 
            window.location.href = "/";
        }, 1000);
    }

    loginMessage.innerText = data.message;

    setTimeout(() => {
        loginMessage.innerText = ""
    }, 2000)
});