document.addEventListener("DOMContentLoaded", () => {
    loadResume();
    loadResumeOwnerControls();
});

async function loadResumeOwnerControls() {
    const controls = document.getElementById("ownerResumeControls");
    const backButton = document.getElementById("backToDashboardButton");

    try {
        const response = await fetch(
            "/api/review/status",
            {
                method: "GET",
                credentials: "include"
            }
        );

        if (!response.ok) {
            return;
        }

        const data = await response.json();

        if (data.access_mode === "owner") {
            controls.hidden = false;
        }

        backButton.addEventListener("click", function () {
            window.location.href = "/dashboard";
        });
    } catch (error) {
        console.error(
            "Unable to load resume access mode:",
            error
        );
    }
}

async function loadResume() {
    const loading = document.getElementById("resumeLoading");
    const error = document.getElementById("resumeError");
    const content = document.getElementById("resumeContent");

    try {
        const response = await fetch(
            "/api/resume",
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
            throw new Error("沒有權限查看此履歷");
        }

        if (!response.ok) {
            throw new Error("無法取得履歷資料");
        }

        const resume = await response.json();

        renderResume(resume);

        loading.hidden = true;
        error.hidden = true;
        content.hidden = false;
    } catch (err) {
        loading.hidden = true;
        content.hidden = true;
        error.textContent = err.message;
        error.hidden = false;
    }
}

