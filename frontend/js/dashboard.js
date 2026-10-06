const welcomeMessage =
    document.getElementById("welcomeMessage");

const userEmail =
    document.getElementById("userEmail");

const logoutButton =
    document.getElementById("logoutButton");

const reviewModeStatus =
    document.getElementById("reviewModeStatus");

const reviewModeDescription =
    document.getElementById("reviewModeDescription");

const enterReviewButton =
    document.getElementById("enterReviewButton");

const viewResumeButton =
    document.getElementById("viewResumeButton");

const exitReviewButton =
    document.getElementById("exitReviewButton");

const reviewPasswordPanel =
    document.getElementById("reviewPasswordPanel");

const reviewPasswordTitle =
    document.getElementById("reviewPasswordTitle");

const reviewPasswordInput =
    document.getElementById("reviewPasswordInput");

const confirmReviewButton =
    document.getElementById("confirmReviewButton");

const cancelReviewButton =
    document.getElementById("cancelReviewButton");

const reviewMessage =
    document.getElementById("reviewMessage");

let reviewAction = null;

async function loadCurrentUser() {
    try {
        const response = await fetch(
            "/api/auth/me",
            {
                method: "GET",
                credentials: "include"
            }
        );

        if (response.status === 401) {
            window.location.href = "/login";
            return false;
        }

        if (!response.ok) {
            throw new Error(
                "無法取得使用者資料"
            );
        }

        const user = await response.json();

        welcomeMessage.textContent =
            `歡迎，${user.username}`;

        userEmail.textContent =
            `Email：${user.email}`;

        return true;
    } catch (error) {
        console.error(
            "loadCurrentUser:",
            error
        );

        welcomeMessage.textContent =
            "使用者資料載入失敗";

        return false;
    }
}

async function loadReviewStatus() {
    try {
        const response = await fetch(
            "/api/review/status",
            {
                method: "GET",
                credentials: "include"
            }
        );

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (response.status === 403) {
            window.location.href = "/resume";
            return;
        }

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data = await response.json();

        if (data.access_mode === "review") {
            window.location.href = "/resume";
            return;
        }

        renderReviewStatus(
            data.account_mode
        );
    } catch (error) {
        console.error(
            "loadReviewStatus:",
            error
        );

        reviewModeStatus.textContent =
            "取得失敗";

        reviewModeDescription.textContent =
            "無法取得目前的查閱模式狀態。";
    }
}

function renderReviewStatus(accountMode) {
    hidePasswordPanel();

    if (accountMode === "review") {
        reviewModeStatus.textContent =
            "已開啟";

        reviewModeDescription.textContent =
            "面試官目前可以使用帳號名稱搭配空白密碼登入查閱履歷。";

        enterReviewButton.hidden = true;
        viewResumeButton.hidden = false;
        exitReviewButton.hidden = false;

        return;
    }

    reviewModeStatus.textContent =
        "未開啟";

    reviewModeDescription.textContent =
        "目前只有帳戶擁有者可以登入。開啟後，面試官可以使用帳號名稱搭配空白密碼進入唯讀履歷。";

    enterReviewButton.hidden = false;
    viewResumeButton.hidden = false;
    exitReviewButton.hidden = true;
}

function showPasswordPanel(action) {
    reviewAction = action;

    reviewPasswordInput.value = "";
    reviewMessage.textContent = "";

    if (action === "enter") {
        reviewPasswordTitle.textContent =
            "請輸入帳戶密碼以開啟查閱模式";
    } else {
        reviewPasswordTitle.textContent =
            "請輸入帳戶密碼以退出查閱模式";
    }

    reviewPasswordPanel.hidden = false;

    reviewPasswordInput.focus();
}

function hidePasswordPanel() {
    reviewAction = null;

    reviewPasswordInput.value = "";
    reviewMessage.textContent = "";

    reviewPasswordPanel.hidden = true;
}

async function submitReviewAction() {
    if (
        reviewAction !== "enter"
        && reviewAction !== "exit"
    ) {
        return;
    }

    const password =
        reviewPasswordInput.value;

    if (!password) {
        reviewMessage.textContent =
            "請輸入帳戶密碼。";
        return;
    }

    const currentAction =
        reviewAction;

    confirmReviewButton.disabled = true;
    cancelReviewButton.disabled = true;

    reviewMessage.textContent =
        "處理中...";

    try {
        const response = await fetch(
            `/api/review/${currentAction}`,
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                credentials: "include",
                body: JSON.stringify({
                    password: password
                })
            }
        );

        if (response.status === 401) {
            reviewMessage.textContent =
                "密碼錯誤。";
            return;
        }

        if (response.status === 403) {
            reviewMessage.textContent =
                "目前沒有權限執行此操作。";
            return;
        }

        if (!response.ok) {
            let detail =
                "操作失敗";

            try {
                const errorData =
                    await response.json();

                if (errorData.detail) {
                    detail =
                        errorData.detail;
                }
            } catch (error) {
                console.error(error);
            }

            throw new Error(
                detail
            );
        }

        const data =
            await response.json();

        hidePasswordPanel();

        if (currentAction === "enter") {
            window.location.href =
                data.redirect
                || "/resume";
            return;
        }

        window.location.href =
            data.redirect
            || "/dashboard";
    } catch (error) {
        console.error(
            "submitReviewAction:",
            error
        );

        reviewMessage.textContent =
            error.message;
    } finally {
        confirmReviewButton.disabled = false;
        cancelReviewButton.disabled = false;
    }
}

enterReviewButton.addEventListener(
    "click",
    function () {
        showPasswordPanel(
            "enter"
        );
    }
);

exitReviewButton.addEventListener(
    "click",
    function () {
        showPasswordPanel(
            "exit"
        );
    }
);

viewResumeButton.addEventListener(
    "click",
    function () {
        window.location.href =
            "/resume";
    }
);

confirmReviewButton.addEventListener(
    "click",
    submitReviewAction
);

cancelReviewButton.addEventListener(
    "click",
    hidePasswordPanel
);

reviewPasswordInput.addEventListener(
    "keydown",
    function (event) {
        if (event.key === "Enter") {
            submitReviewAction();
        }

        if (event.key === "Escape") {
            hidePasswordPanel();
        }
    }
);

logoutButton.addEventListener(
    "click",
    async function () {
        try {
            const response = await fetch(
                "/api/auth/logout",
                {
                    method: "POST",
                    credentials: "include"
                }
            );

            if (response.ok) {
                window.location.href =
                    "/login";
            }
        } catch (error) {
            console.error(
                "logout:",
                error
            );
        }
    }
);

async function initializeDashboard() {
    await loadCurrentUser();
    await loadReviewStatus();
}

initializeDashboard();