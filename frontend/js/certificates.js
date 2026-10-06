const certificateForm = document.getElementById("certificateForm");
const certificateName = document.getElementById("certificateName");
const certificateIssuer = document.getElementById("certificateIssuer");
const certificateIssueDate = document.getElementById("certificateIssueDate");
const certificateExpirationDate = document.getElementById(
    "certificateExpirationDate"
);
const certificateNumber = document.getElementById("certificateNumber");
const certificateList = document.getElementById("certificateList");
const certificateMessage = document.getElementById("certificateMessage");
const certificateFormTitle = document.getElementById(
    "certificateFormTitle"
);
const certificateSaveButton = document.getElementById(
    "certificateSaveButton"
);
const certificateCancelEditButton = document.getElementById(
    "certificateCancelEditButton"
);

let editingCertificateId = null;
let linkingCertificateId = null;

async function loadCertificates() {
    try {
        const response = await fetch("/api/certificates");

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!response.ok) {
            showCertificateTableMessage(
                "讀取證照資料失敗。"
            );
            return;
        }

        const certificates = await response.json();

        renderCertificates(certificates);
    } catch (error) {
        console.error(error);

        showCertificateTableMessage(
            "無法連線至伺服器。"
        );
    }
}

function showCertificateTableMessage(text) {
    certificateList.innerHTML = "";

    const row = document.createElement("tr");
    const cell = document.createElement("td");

    cell.colSpan = 7;
    cell.textContent = text;

    row.appendChild(cell);
    certificateList.appendChild(row);
}

function renderCertificates(certificates) {
    certificateList.innerHTML = "";

    if (certificates.length === 0) {
        showCertificateTableMessage(
            "尚未建立證照。"
        );
        return;
    }

    for (const certificate of certificates) {
        const row = document.createElement("tr");

        const nameCell = document.createElement("td");
        nameCell.textContent =
            certificate.certificate_name;

        const issuerCell = document.createElement("td");
        issuerCell.textContent =
            certificate.issuer || "—";

        const issueDateCell = document.createElement("td");
        issueDateCell.textContent =
            certificate.issue_date || "—";

        const expirationDateCell =
            document.createElement("td");

        expirationDateCell.textContent =
            certificate.expiration_date || "—";

        const numberCell = document.createElement("td");
        numberCell.textContent =
            certificate.certificate_number || "—";

        const documentCell =
            document.createElement("td");

        renderCertificateDocuments(
            documentCell,
            certificate
        );

        const actionCell =
            document.createElement("td");

        const editButton =
            document.createElement("button");

        editButton.type = "button";
        editButton.textContent = "編輯";

        editButton.addEventListener(
            "click",
            function () {
                startEditCertificate(
                    certificate
                );
            }
        );

        const deleteButton =
            document.createElement("button");

        deleteButton.type = "button";
        deleteButton.textContent = "刪除";

        deleteButton.addEventListener(
            "click",
            function () {
                deleteCertificate(
                    certificate.id,
                    certificate.certificate_name
                );
            }
        );

        actionCell.appendChild(editButton);
        actionCell.appendChild(deleteButton);

        row.appendChild(nameCell);
        row.appendChild(issuerCell);
        row.appendChild(issueDateCell);
        row.appendChild(expirationDateCell);
        row.appendChild(numberCell);
        row.appendChild(documentCell);
        row.appendChild(actionCell);

        certificateList.appendChild(row);
    }
}

function renderCertificateDocuments(
    documentCell,
    certificate
) {
    documentCell.innerHTML = "";

    const documents =
        certificate.documents || [];

    if (documents.length === 0) {
        const empty =
            document.createElement("div");

        empty.className =
            "proof-document-empty";

        empty.textContent = "—";

        documentCell.appendChild(empty);
    } else {
        for (const file of documents) {
            const container =
                document.createElement("div");

            container.className =
                "proof-document";

            const fileName =
                document.createElement("span");

            fileName.textContent =
                file.original_filename;

            const openButton =
                document.createElement("button");

            openButton.type = "button";
            openButton.textContent = "查看";

            openButton.addEventListener(
                "click",
                function () {
                    openCertificateDocument(
                        file.id
                    );
                }
            );

            const unlinkButton =
                document.createElement("button");

            unlinkButton.type = "button";
            unlinkButton.textContent = "解除";

            unlinkButton.addEventListener(
                "click",
                function () {
                    unlinkCertificateDocument(
                        certificate.id,
                        file.id
                    );
                }
            );

            container.appendChild(fileName);
            container.appendChild(openButton);
            container.appendChild(unlinkButton);

            documentCell.appendChild(container);
        }
    }

    const linkButton =
        document.createElement("button");

    linkButton.type = "button";
    linkButton.className =
        "link-document-button";

    linkButton.textContent =
        "串接文件";

    linkButton.addEventListener(
        "click",
        function () {
            showCertificateDocumentSelector(
                certificate.id
            );
        }
    );

    documentCell.appendChild(linkButton);

    const selector =
        document.createElement("div");

    selector.id =
        `certificate-document-selector-${certificate.id}`;

    selector.className =
        "certificate-document-selector";

    selector.hidden = true;

    documentCell.appendChild(selector);
}

async function showCertificateDocumentSelector(
    certificateId
) {
    certificateMessage.textContent = "";

    const selector =
        document.getElementById(
            `certificate-document-selector-${certificateId}`
        );

    if (!selector) {
        certificateMessage.textContent =
            "找不到文件選擇區域。";
        return;
    }

    if (
        linkingCertificateId === certificateId &&
        !selector.hidden
    ) {
        selector.hidden = true;
        selector.innerHTML = "";
        linkingCertificateId = null;
        return;
    }

    linkingCertificateId =
        certificateId;

    selector.hidden = false;

    selector.innerHTML = "";

    const loading =
        document.createElement("div");

    loading.className =
        "document-selector-loading";

    loading.textContent =
        "正在讀取文件庫...";

    selector.appendChild(loading);

    try {
        const response = await fetch(
            "/api/documents"
        );

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!response.ok) {
            selector.innerHTML = "";

            const error =
                document.createElement("div");

            error.textContent =
                "文件資料讀取失敗。";

            selector.appendChild(error);
            return;
        }

        const documents =
            await response.json();

        selector.innerHTML = "";

        if (
            !documents ||
            documents.length === 0
        ) {
            const empty =
                document.createElement("div");

            empty.className =
                "document-selector-empty";

            empty.textContent =
                "文件庫目前沒有文件。";

            selector.appendChild(empty);
            return;
        }

        const box =
            document.createElement("div");

        box.className =
            "document-selector-box";

        const select =
            document.createElement("select");

        select.id =
            `certificate-document-select-${certificateId}`;

        select.className =
            "document-selector-select";

        const defaultOption =
            document.createElement("option");

        defaultOption.value = "";
        defaultOption.textContent =
            "請選擇文件";

        select.appendChild(
            defaultOption
        );

        for (const file of documents) {
            const option =
                document.createElement("option");

            option.value =
                String(file.id);

            option.textContent =
                file.original_filename;

            select.appendChild(option);
        }

        const confirmButton =
            document.createElement("button");

        confirmButton.type = "button";
        confirmButton.textContent =
            "確認串接";

        confirmButton.addEventListener(
            "click",
            function () {
                confirmCertificateDocumentLink(
                    certificateId
                );
            }
        );

        const cancelButton =
            document.createElement("button");

        cancelButton.type = "button";
        cancelButton.textContent =
            "取消";

        cancelButton.addEventListener(
            "click",
            function () {
                cancelCertificateDocumentLink(
                    certificateId
                );
            }
        );

        box.appendChild(select);
        box.appendChild(confirmButton);
        box.appendChild(cancelButton);

        selector.appendChild(box);

    } catch (error) {
        console.error(error);

        selector.innerHTML = "";

        const errorMessage =
            document.createElement("div");

        errorMessage.textContent =
            "無法連線至伺服器。";

        selector.appendChild(
            errorMessage
        );
    }
}

async function confirmCertificateDocumentLink(
    certificateId
) {
    certificateMessage.textContent = "";

    const select =
        document.getElementById(
            `certificate-document-select-${certificateId}`
        );

    if (!select) {
        certificateMessage.textContent =
            "找不到文件選擇器。";
        return;
    }

    const documentId =
        Number(select.value);

    if (
        !Number.isInteger(documentId) ||
        documentId <= 0
    ) {
        certificateMessage.textContent =
            "請先選擇要串接的文件。";
        return;
    }

    await linkCertificateDocument(
        certificateId,
        documentId
    );
}

function cancelCertificateDocumentLink(
    certificateId
) {
    const selector =
        document.getElementById(
            `certificate-document-selector-${certificateId}`
        );

    if (selector) {
        selector.hidden = true;
        selector.innerHTML = "";
    }

    if (
        linkingCertificateId ===
        certificateId
    ) {
        linkingCertificateId = null;
    }
}

async function linkCertificateDocument(
    certificateId,
    documentId
) {
    try {
        const response = await fetch(
            `/api/certificates/${certificateId}/documents/${documentId}`,
            {
                method: "POST"
            }
        );

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        const data =
            await response.json();

        if (response.status === 409) {
            certificateMessage.textContent =
                "這份文件已經串接此證照。";
            return;
        }

        if (!response.ok) {
            certificateMessage.textContent =
                data.detail ||
                "文件串接失敗。";
            return;
        }

        linkingCertificateId = null;

        certificateMessage.textContent =
            "證明文件串接成功。";

        await loadCertificates();

    } catch (error) {
        console.error(error);

        certificateMessage.textContent =
            "無法連線至伺服器。";
    }
}

function openCertificateDocument(
    documentId
) {
    window.open(
        `/api/documents/${documentId}/file`,
        "_blank"
    );
}

async function unlinkCertificateDocument(
    certificateId,
    documentId
) {
    const confirmed = window.confirm(
        "確定要解除這份證明文件嗎？"
    );

    if (!confirmed) {
        return;
    }

    certificateMessage.textContent = "";

    try {
        const response = await fetch(
            `/api/certificates/${certificateId}/documents/${documentId}`,
            {
                method: "DELETE"
            }
        );

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        const data =
            await response.json();

        if (!response.ok) {
            certificateMessage.textContent =
                data.detail ||
                "解除證明文件失敗。";
            return;
        }

        certificateMessage.textContent =
            "證明文件已解除。";

        await loadCertificates();

    } catch (error) {
        console.error(error);

        certificateMessage.textContent =
            "無法連線至伺服器。";
    }
}

function startEditCertificate(certificate) {
    editingCertificateId =
        certificate.id;

    certificateName.value =
        certificate.certificate_name;

    certificateIssuer.value =
        certificate.issuer || "";

    certificateIssueDate.value =
        certificate.issue_date || "";

    certificateExpirationDate.value =
        certificate.expiration_date || "";

    certificateNumber.value =
        certificate.certificate_number || "";

    certificateFormTitle.textContent =
        "編輯證照";

    certificateSaveButton.textContent =
        "儲存修改";

    certificateCancelEditButton.hidden =
        false;

    certificateMessage.textContent =
        `正在編輯：${certificate.certificate_name}`;

    certificateFormTitle.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

function cancelEditCertificate() {
    editingCertificateId = null;

    certificateForm.reset();

    certificateFormTitle.textContent =
        "新增證照";

    certificateSaveButton.textContent =
        "新增證照";

    certificateCancelEditButton.hidden =
        true;

    certificateMessage.textContent = "";
}

certificateCancelEditButton.addEventListener(
    "click",
    function () {
        cancelEditCertificate();
    }
);

certificateForm.addEventListener(
    "submit",
    async function (event) {
        event.preventDefault();

        certificateMessage.textContent = "";

        const certificateData = {
            certificate_name:
                certificateName.value.trim(),

            issuer:
                certificateIssuer.value.trim() ||
                null,

            issue_date:
                certificateIssueDate.value ||
                null,

            expiration_date:
                certificateExpirationDate.value ||
                null,

            certificate_number:
                certificateNumber.value.trim() ||
                null
        };

        let url =
            "/api/certificates";

        let method =
            "POST";

        if (
            editingCertificateId !== null
        ) {
            url =
                `/api/certificates/${editingCertificateId}`;

            method =
                "PUT";
        }

        try {
            const response =
                await fetch(
                    url,
                    {
                        method: method,
                        headers: {
                            "Content-Type":
                                "application/json"
                        },
                        body:
                            JSON.stringify(
                                certificateData
                            )
                    }
                );

            if (
                response.status === 401
            ) {
                window.location.href =
                    "/login";

                return;
            }

            const data =
                await response.json();

            if (!response.ok) {
                console.error(
                    "Certificate API error:",
                    data
                );

                if (
                    typeof data.detail ===
                    "string"
                ) {
                    certificateMessage.textContent =
                        data.detail;

                } else if (
                    Array.isArray(
                        data.detail
                    )
                ) {
                    certificateMessage.textContent =
                        data.detail
                            .map(
                                function (
                                    error
                                ) {
                                    const field =
                                        error.loc
                                            ? error.loc.join(
                                                  "."
                                              )
                                            : "unknown";

                                    return `${field}: ${error.msg}`;
                                }
                            )
                            .join("；");

                } else {
                    certificateMessage.textContent =
                        `證照資料儲存失敗（HTTP ${response.status}）`;
                }

                return;
            }

            if (
                editingCertificateId !==
                null
            ) {
                cancelEditCertificate();

                certificateMessage.textContent =
                    "證照修改成功。";

            } else {
                certificateForm.reset();

                certificateMessage.textContent =
                    "證照新增成功。";
            }

            await loadCertificates();

        } catch (error) {
            console.error(error);

            certificateMessage.textContent =
                "無法連線至伺服器。";
        }
    }
);

async function deleteCertificate(
    certificateId,
    certificateNameText
) {
    const confirmed =
        window.confirm(
            `確定要刪除證照「${certificateNameText}」嗎？`
        );

    if (!confirmed) {
        return;
    }

    try {
        const response =
            await fetch(
                `/api/certificates/${certificateId}`,
                {
                    method: "DELETE"
                }
            );

        if (
            response.status === 401
        ) {
            window.location.href =
                "/login";

            return;
        }

        const data =
            await response.json();

        if (!response.ok) {
            certificateMessage.textContent =
                data.detail ||
                "刪除證照失敗。";

            return;
        }

        if (
            editingCertificateId ===
            certificateId
        ) {
            cancelEditCertificate();
        }

        certificateMessage.textContent =
            "證照刪除成功。";

        await loadCertificates();

    } catch (error) {
        console.error(error);

        certificateMessage.textContent =
            "無法連線至伺服器。";
    }
}

loadCertificates();