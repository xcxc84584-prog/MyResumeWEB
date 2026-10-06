const loginForm =
    document.getElementById("loginForm");

const message =
    document.getElementById("message");

loginForm.addEventListener(
    "submit",
    async function (event) {
        event.preventDefault();

        const username =
            document.getElementById("username")
                .value
                .trim();

        const password =
            document.getElementById("password")
                .value;

        if (!username) {
            message.textContent =
                "請輸入帳號。";
            return;
        }

        message.textContent =
            "登入中...";

        try {
            const response = await fetch(
                "/api/auth/login",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json"
                    },
                    credentials: "include",
                    body: JSON.stringify({
                        username: username,
                        password: password
                    })
                }
            );

            const data =
                await response.json();

            if (response.ok) {
                window.location.href =
                    data.redirect
                    || "/dashboard";

                return;
            }

            if (response.status === 401) {
                message.textContent =
                    "帳號或密碼錯誤，或此帳戶尚未開啟查閱模式。";

                return;
            }

            message.textContent =
                data.detail
                || "登入失敗";
        } catch (error) {
            console.error(error);

            message.textContent =
                "無法連線至伺服器";
        }
    }
);