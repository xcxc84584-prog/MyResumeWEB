const reviewerLoginForm = document.getElementById("reviewerLoginForm");
const message = document.getElementById("message");

reviewerLoginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const companyName = document.getElementById("companyName").value.trim();
    const description = document.getElementById("description").value.trim();
    const password = document.getElementById("password").value;

    message.textContent = "登入中...";

    try {
        const response = await fetch("/api/reviewer/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            body: JSON.stringify({
                company_name: companyName,
                description: description,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            window.location.href =
                data.redirect || "/reviewer/dashboard";
            return;
        }

        if (response.status === 401) {
            message.textContent = "公司名稱、描述或密碼錯誤。";
            return;
        }

        message.textContent = data.detail || "登入失敗";
    } catch (error) {
        console.error(error);
        message.textContent = "無法連線至伺服器";
    }
});