const registerForm = document.getElementById("registerForm");
const message = document.getElementById("message");

registerForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            email: email,
            password: password
        })
    });

    const data = await response.json();

    if (response.ok) {
        message.textContent = `帳號 ${data.username} 建立成功！`;
        registerForm.reset();
    } else {
        message.textContent = data.detail || "建立帳號失敗";
    }
});