const reviewerRegisterForm = document.getElementById("reviewerRegisterForm");
const message = document.getElementById("message");

reviewerRegisterForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const companyName = document.getElementById("companyName").value.trim();
    const description = document.getElementById("description").value.trim();
    const password = document.getElementById("password").value;

    message.textContent = "註冊中...";

    try {
        const response = await fetch("/api/reviewer/register", {
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
            message.textContent = "批閱帳號建立成功，即將前往登入頁面。";

            setTimeout(function () {
                window.location.href = "/reviewer/login";
            }, 800);

            return;
        }

        if (response.status === 409) {
            message.textContent = "此公司名稱與描述的組合已存在。";
            return;
        }

        message.textContent = data.detail || "註冊失敗";
    } catch (error) {
        console.error(error);
        message.textContent = "無法連線至伺服器";
    }
});