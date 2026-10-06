console.log("submit-resume.js loaded.");

const companyNameInput =
    document.getElementById("companyNameInput");

const descriptionInput =
    document.getElementById("descriptionInput");

const searchCompanyButton =
    document.getElementById("searchCompanyButton");

const companyTableBody =
    document.getElementById("companyTableBody");

const submissionTableBody =
    document.getElementById("submissionTableBody");

const message =
    document.getElementById("message");

let mySubmissions = [];

if (searchCompanyButton) {
    searchCompanyButton.onclick = function () {
        searchCompanies();
    };
}

async function searchCompanies() {
    const companyName =
        companyNameInput.value.trim();

    const description =
        descriptionInput.value.trim();

    const params =
        new URLSearchParams();

    if (companyName) {
        params.append(
            "company_name",
            companyName
        );
    }

    if (description) {
        params.append(
            "description",
            description
        );
    }

    message.textContent =
        "搜尋中...";

    try {
        const response = await fetch(
            `/api/reviewer/search?${params.toString()}`,
            {
                method: "GET",
                credentials: "include"
            }
        );

        const data =
            await response.json();

        if (!response.ok) {
            message.textContent =
                data.detail || "搜尋失敗";

            return;
        }

        renderCompanies(data);

        message.textContent =
            `找到 ${data.length} 筆結果`;
    } catch (error) {
        console.error(
            "Search companies error:",
            error
        );

        message.textContent =
            "無法連線至伺服器";
    }
}

function renderCompanies(companies) {
    companyTableBody.innerHTML = "";

    const visibleCompanies =
        companies.slice(0, 3);

    if (visibleCompanies.length === 0) {
        companyTableBody.innerHTML = `
            <tr>
                <td colspan="3">
                    找不到符合條件的公司
                </td>
            </tr>
        `;

        return;
    }

    visibleCompanies.forEach(function (company) {
        const row =
            document.createElement("tr");

        const companyNameCell =
            document.createElement("td");

        const descriptionCell =
            document.createElement("td");

        const actionCell =
            document.createElement("td");

        companyNameCell.textContent =
            company.company_name;

        descriptionCell.textContent =
            company.description;

        const existingSubmission =
            mySubmissions.find(
                function (submission) {
                    return (
                        submission.reviewer_account_id
                        === company.id
                    );
                }
            );

        if (existingSubmission) {
            const statusText =
                document.createElement("span");

            statusText.textContent =
                existingSubmission.status_text;

            actionCell.appendChild(
                statusText
            );
        } else {
            const submitButton =
                document.createElement("button");

            submitButton.type =
                "button";

            submitButton.textContent =
                "提交履歷";

            submitButton.onclick =
                function () {
                    console.log(
                        "Submit resume clicked:",
                        company.id,
                        company.company_name
                    );

                    submitResume(company);
                };

            actionCell.appendChild(
                submitButton
            );
        }

        row.appendChild(
            companyNameCell
        );

        row.appendChild(
            descriptionCell
        );

        row.appendChild(
            actionCell
        );

        companyTableBody.appendChild(
            row
        );
    });
}

async function submitResume(company) {
    console.log(
        "submitResume called:",
        company
    );

    const confirmed =
        window.confirm(
            `確定要提交履歷給「${company.company_name}｜${company.description}」嗎？`
        );

    if (!confirmed) {
        return;
    }

    message.textContent =
        "提交履歷中...";

    try {
        const response = await fetch(
            "/api/submissions",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                credentials: "include",
                body: JSON.stringify({
                    reviewer_account_id:
                        company.id
                })
            }
        );

        const data =
            await response.json();

        console.log(
            "Submit response:",
            response.status,
            data
        );

        if (!response.ok) {
            if (response.status === 409) {
                message.textContent =
                    "你已經提交履歷給這個批閱帳號。";

                await loadMySubmissions();

                return;
            }

            if (response.status === 401) {
                window.location.href =
                    "/login";

                return;
            }

            if (response.status === 403) {
                window.location.href =
                    "/resume";

                return;
            }

            message.textContent =
                data.detail || "提交失敗";

            return;
        }

        message.textContent =
            "履歷提交成功";

        await loadMySubmissions();

        await searchCompanies();
    } catch (error) {
        console.error(
            "Submit resume error:",
            error
        );

        message.textContent =
            "無法連線至伺服器";
    }
}

async function loadMySubmissions() {
    console.log(
        "loadMySubmissions called"
    );

    try {
        console.log(
            "Requesting /api/submissions/mine"
        );

        const response = await fetch(
            "/api/submissions/mine",
            {
                method: "GET",
                credentials: "include"
            }
        );

        console.log(
            "Mine response status:",
            response.status
        );

        if (response.status === 401) {
            window.location.href =
                "/login";

            return;
        }

        if (response.status === 403) {
            window.location.href =
                "/resume";

            return;
        }

        const data =
            await response.json();

        console.log(
            "My submissions:",
            data
        );

        if (!response.ok) {
            message.textContent =
                data.detail ||
                "無法取得已提交履歷";

            return;
        }

        if (!Array.isArray(data)) {
            console.error(
                "Invalid submissions response:",
                data
            );

            message.textContent =
                "已提交履歷資料格式錯誤";

            return;
        }

        mySubmissions =
            data;

        renderMySubmissions();
    } catch (error) {
        console.error(
            "loadMySubmissions error:",
            error
        );

        message.textContent =
            "無法取得已提交履歷";
    }
}

function renderMySubmissions() {
    console.log(
        "Rendering submissions:",
        mySubmissions
    );

    submissionTableBody.innerHTML =
        "";

    if (mySubmissions.length === 0) {
        submissionTableBody.innerHTML = `
            <tr>
                <td colspan="4">
                    尚無已提交履歷
                </td>
            </tr>
        `;

        return;
    }

    mySubmissions.forEach(
        function (submission) {
            const row =
                document.createElement("tr");

            const companyCell =
                document.createElement("td");

            const descriptionCell =
                document.createElement("td");

            const statusCell =
                document.createElement("td");

            const actionCell =
                document.createElement("td");

            const withdrawButton =
                document.createElement("button");

            companyCell.textContent =
                submission.company_name;

            descriptionCell.textContent =
                submission.description;

            statusCell.textContent =
                submission.status_text;

            withdrawButton.type =
                "button";

            withdrawButton.textContent =
                "收回履歷";

            withdrawButton.onclick =
                function () {
                    withdrawSubmission(
                        submission
                    );
                };

            actionCell.appendChild(
                withdrawButton
            );

            row.appendChild(
                companyCell
            );

            row.appendChild(
                descriptionCell
            );

            row.appendChild(
                statusCell
            );

            row.appendChild(
                actionCell
            );

            submissionTableBody.appendChild(
                row
            );
        }
    );
}

async function withdrawSubmission(
    submission
) {
    const confirmed =
        window.confirm(
            `確定要收回提交給「${submission.company_name}｜${submission.description}」的履歷嗎？`
        );

    if (!confirmed) {
        return;
    }

    message.textContent =
        "正在收回履歷...";

    try {
        const response = await fetch(
            `/api/submissions/${submission.id}`,
            {
                method: "DELETE",
                credentials: "include"
            }
        );

        const data =
            await response.json();

        console.log(
            "Withdraw response:",
            response.status,
            data
        );

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href =
                    "/login";

                return;
            }

            if (response.status === 403) {
                window.location.href =
                    "/resume";

                return;
            }

            message.textContent =
                data.detail ||
                "收回履歷失敗";

            return;
        }

        message.textContent =
            "履歷已收回";

        await loadMySubmissions();

        await searchCompanies();
    } catch (error) {
        console.error(
            "Withdraw submission error:",
            error
        );

        message.textContent =
            "無法連線至伺服器";
    }
}

loadMySubmissions();