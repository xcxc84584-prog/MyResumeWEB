(() => {
    const section = document.querySelector(".account-deletion");
    const form = document.getElementById("deleteAccountForm");
    if (!form) return;
    const button = document.getElementById("deleteAccountButton");
    const message = document.getElementById("deleteAccountMessage");
    form.addEventListener("submit", async event => {
        event.preventDefault();
        if (button.disabled || !form.reportValidity()) return;
        if (!window.confirm("確定永久註銷此帳號及上述資料？此操作無法復原。")) return;
        button.disabled = true;
        message.textContent = "正在註銷...";
        try {
            const response = await fetch(section.dataset.accountKind === "reviewer"
                ? "/api/reviewer/account" : "/api/auth/account", {
                method: "DELETE", credentials: "include",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    password: document.getElementById("deleteAccountPassword").value,
                    confirmation: document.getElementById("deleteAccountConfirmation").value
                })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(typeof data.detail === "string"
                ? data.detail : "請確認密碼與確認文字後再試");
            window.alert(data.file_cleanup_pending
                ? "帳號已註銷，部分附件清理失敗，請聯絡管理者。" : data.message);
            window.location.replace(data.redirect || "/");
        } catch (error) {
            message.textContent = error.message || "註銷失敗，請稍後再試";
            button.disabled = false;
        } finally {
            document.getElementById("deleteAccountPassword").value = "";
        }
    });
})();
