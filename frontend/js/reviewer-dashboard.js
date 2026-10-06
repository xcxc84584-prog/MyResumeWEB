console.log("reviewer-dashboard.js loaded.");

const companyName =
    document.getElementById("companyName");

const companyDescription =
    document.getElementById("companyDescription");

const submissionTableBody =
    document.getElementById("submissionTableBody");

const logoutButton =
    document.getElementById("logoutButton");

const message =
    document.getElementById("message");

async function loadReviewer() {
    console.log("loadReviewer called.");

    try {
        const response = await fetch(
            "/api/reviewer/me",
            {
                method: "GET",
                credentials: "include"
            }
        );

        if (response.status === 401) {
            window.location.href =
                "/reviewer/login";
            return;
        }

        const data =
            await response.json();

        if (!response.ok) {
            message.textContent =
                data.detail ||
                "無法取得批閱帳號資料";
            return;
        }

        companyName.textContent =
            data.company_name;

        companyDescription.textContent =
            data.description;
    } catch (error) {
        console.error(
            "loadReviewer error:",
            error
        );

        message.textContent =
            "無法連線至伺服器";
    }
}

async function loadSubmissions() {
    console.log(
        "loadSubmissions called."
    );

    try {
        const response = await fetch(
            "/api/reviewer/submissions",
            {
                method: "GET",
                credentials: "include"
            }
        );

        console.log(
            "Submissions response:",
            response.status
        );

        if (response.status === 401) {
            window.location.href =
                "/reviewer/login";
            return;
        }

        const data =
            await response.json();

        console.log(
            "Submissions data:",
            data
        );

        if (!response.ok) {
            message.textContent =
                data.detail ||
                "無法取得收到的履歷";
            return;
        }

        if (!Array.isArray(data)) {
            message.textContent =
                "履歷資料格式錯誤";
            return;
        }

        renderSubmissions(data);
    } catch (error) {
        console.error(
            "loadSubmissions error:",
            error
        );

        message.textContent =
            "無法取得收到的履歷";
    }
}

function renderSubmissions(
    submissions
) {
    console.log(
        "renderSubmissions:",
        submissions
    );

    if (!submissionTableBody) {
        console.error(
            "submissionTableBody not found."
        );
        return;
    }

    submissionTableBody.innerHTML =
        "";

    if (submissions.length === 0) {
        submissionTableBody.innerHTML = `
            <tr>
                <td colspan="3">
                    尚無履歷
                </td>
            </tr>
        `;
        return;
    }

    submissions.forEach(
        function (submission) {
            const row =
                document.createElement("tr");

            const sequenceCell =
                document.createElement("td");

            const resumeCell =
                document.createElement("td");

            const statusCell =
                document.createElement("td");

            const usernameSpan =
                document.createElement("span");

            const viewButton =
                document.createElement("button");

            sequenceCell.textContent =
                submission.sequence;

            usernameSpan.textContent =
                submission.username + " ";

            viewButton.type =
                "button";

            viewButton.textContent =
                "查看履歷";

            viewButton.onclick =
                function () {
                    window.location.href =
                        `/reviewer/submission/${submission.id}`;
                };

            resumeCell.appendChild(
                usernameSpan
            );

            resumeCell.appendChild(
                viewButton
            );

            const statusSelect =
                document.createElement("select");

            const statusOptions = [
                {
                    value: "unread",
                    text: "未讀"
                },
                {
                    value: "backup",
                    text: "備選"
                },
                {
                    value: "accepted",
                    text: "正取"
                },
                {
                    value: "rejected",
                    text: "落選"
                }
            ];

            statusOptions.forEach(
                function (optionData) {
                    const option =
                        document.createElement("option");

                    option.value =
                        optionData.value;

                    option.textContent =
                        optionData.text;

                    if (
                        optionData.value
                        === submission.status
                    ) {
                        option.selected = true;
                    }

                    statusSelect.appendChild(
                        option
                    );
                }
            );

            statusSelect.onchange =
                function () {
                    updateSubmissionStatus(
                        submission.id,
                        statusSelect.value,
                        statusSelect
                    );
                };

            statusCell.appendChild(
                statusSelect
            );

            row.appendChild(
                sequenceCell
            );

            row.appendChild(
                resumeCell
            );

            row.appendChild(
                statusCell
            );

            submissionTableBody.appendChild(
                row
            );
        }
    );
}
async function updateSubmissionStatus(
    submissionId,
    newStatus,
    selectElement
) {
    console.log(
        "updateSubmissionStatus:",
        submissionId,
        newStatus
    );

    selectElement.disabled = true;

    message.textContent =
        "正在更新狀態...";

    try {
        const response = await fetch(
            `/api/reviewer/submissions/${submissionId}/status`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                credentials: "include",
                body: JSON.stringify({
                    status: newStatus
                })
            }
        );

        let data = null;

        try {
            data =
                await response.json();
        } catch (error) {
            data = null;
        }

        console.log(
            "Update status response:",
            response.status,
            data
        );

        if (response.status === 401) {
            window.location.href =
                "/reviewer/login";

            return;
        }

        if (response.status === 404) {
            message.textContent =
                "找不到此履歷，或沒有修改權限。";

            await loadSubmissions();

            return;
        }

        if (!response.ok) {
            message.textContent =
                data?.detail ||
                "狀態更新失敗";

            await loadSubmissions();

            return;
        }

        message.textContent =
            `狀態已更新為：${data.status_text}`;

        await loadSubmissions();
    } catch (error) {
        console.error(
            "updateSubmissionStatus error:",
            error
        );

        message.textContent =
            "無法連線至伺服器";

        await loadSubmissions();
    }
}
async function logoutReviewer() {
    try {
        const response = await fetch(
            "/api/reviewer/logout",
            {
                method: "POST",
                credentials: "include"
            }
        );

        if (response.ok) {
            window.location.href =
                "/";
            return;
        }

        message.textContent =
            "登出失敗";
    } catch (error) {
        console.error(
            "logoutReviewer error:",
            error
        );

        message.textContent =
            "無法連線至伺服器";
    }
}

if (logoutButton) {
    logoutButton.onclick =
        logoutReviewer;
}

loadReviewer();
loadSubmissions();