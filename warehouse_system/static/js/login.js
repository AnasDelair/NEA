const loginMessage = document.getElementById("login-message")
const originalMessage = loginMessage.innerText

const colours = {
    error : "#8e4e4eff",
    success : "#6b8e4e",
    normal : "#2d2d2d"
}

const setColour = (colour) => loginMessage.style.color = colour;
const setText = (msg) => loginMessage.innerText = msg;

document.getElementById("login-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const password = this.password.value;

    const response = await fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ password: password })
    });

    const data = await response.json();

    setColour(colours.error)
    if (data.success) {
        setColour(colours.success)
        setTimeout(() => { 
            window.location.href = "/";
        }, 1000);
    }

    setText(data.message)

    setTimeout(() => {
        setColour(colours.normal)
        setText(originalMessage)
    }, 2000)
});