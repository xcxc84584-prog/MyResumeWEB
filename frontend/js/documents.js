const documentForm = document.getElementById("documentForm");
const documentFile = document.getElementById("documentFile");
const uploadButton = document.getElementById("uploadButton");
const documentList = document.getElementById("documentList");
const message = document.getElementById("message");

const MAX_FILE_SIZE = 10 * 1024 * 1024;

const ALLOWED_EXTENSIONS = [
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".zip"
];

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function getExtension(filename) {
    const index = filename.lastIndexOf(".");

    if (index === -1) {
        return "";
    }

    return filename
        .slice(index)
        .toLowerCase();
}

function getFileType(document) {
    const extension = getExtension(
        document.original_filename
    );

    if (extension === ".pdf") {
        return "PDF";
    }

    if (
        extension === ".jpg" ||
        extension === ".jpeg"
    ) {
        return "JPG";
    }

    if (extension === ".png") {
        return "PNG";
    }

    if (extension === ".webp") {
        return "WebP";
    }

    if (extension === ".zip") {
        return "ZIP";
    }

    return document.content_type;
}

function formatFileSize(bytes) {
    if (bytes < 1024) {
        return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(
        bytes /
        (1024 * 1024)
    ).toFixed(2)} MB`;
}

function formatDateTime(value) {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString(
        "zh-TW"
    );
}

async function loadDocuments() {
    try {
        const response = await fetch(
            "/api/documents"
        );

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!response.ok) {
            documentList.innerHTML = `
                <tr>
                    <td colspan="6">
                        文件資料讀取失敗
                    </td>
                </tr>
            `;
            return;
        }

        const documents = await response.json();

        renderDocuments(documents);

    } catch (error) {
        console.error(error);

        documentList.innerHTML = `
            <tr>
                <td colspan="6">
                    無法連線至伺服器
                </td>
            </tr>
        `;
    }
}

function renderDocuments(documents) {
    if (documents.length === 0) {
        documentList.innerHTML = `
            <tr>
                <td colspan="6">
                    尚未上傳任何文件
                </td>
            </tr>
        `;
        return;
    }

    documentList.innerHTML = documents
        .map(function (document) {
            return `
                <tr>
                    <td>${document.id}</td>
                    <td>
                        ${escapeHtml(
                            document.original_filename
                        )}
                    </td>
                    <td>
                        ${escapeHtml(
                            getFileType(document)
                        )}
                    </td>
                    <td>
                        ${formatFileSize(
                            document.file_size
                        )}
                    </td>
                    <td>
                        ${escapeHtml(
                            formatDateTime(
                                document.created_at
                            )
                        )}
                    </td>
                    <td>
                        <button
                            type="button"
                            onclick="openDocument(${document.id})"
                        >
                            查看
                        </button>
                        <button
                            type="button"
                            onclick="deleteDocument(
                                ${document.id},
                                '${encodeURIComponent(
                                    document.original_filename
                                )}'
                            )"
                        >
                            刪除
                        </button>
                    </td>
                </tr>
            `;
        })
        .join("");
}

async function uploadDocument(event) {
    event.preventDefault();

    message.textContent = "";

    const file = documentFile.files[0];

    if (!file) {
        message.textContent = "請選擇文件。";
        return;
    }

    const extension = getExtension(
        file.name
    );

    if (
        !ALLOWED_EXTENSIONS.includes(
            extension
        )
    ) {
        message.textContent =
            "不支援此文件格式。";
        return;
    }

    if (file.size === 0) {
        message.textContent =
            "不能上傳空白文件。";
        return;
    }

    if (file.size > MAX_FILE_SIZE) {
        message.textContent =
            "文件大小不能超過 10 MB。";
        return;
    }

    const formData = new FormData();

    formData.append(
        "file",
        file
    );

    uploadButton.disabled = true;
    uploadButton.textContent = "上傳中...";

    try {
        const response = await fetch(
            "/api/documents",
            {
                method: "POST",
                body: formData
            }
        );

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            if (
                typeof data.detail === "string"
            ) {
                message.textContent =
                    data.detail;
            } else {
                message.textContent =
                    `文件上傳失敗（HTTP ${response.status}）`;
            }

            return;
        }

        message.textContent =
            "文件上傳成功。";

        documentForm.reset();

        await loadDocuments();

    } catch (error) {
        console.error(error);

        message.textContent =
            "無法連線至伺服器。";

    } finally {
        uploadButton.disabled = false;
        uploadButton.textContent = "上傳文件";
    }
}

function openDocument(documentId) {
    window.open(
        `/api/documents/${documentId}/file`,
        "_blank"
    );
}

async function deleteDocument(
    documentId,
    encodedFilename
) {
    const filename = decodeURIComponent(
        encodedFilename
    );

    const confirmed = window.confirm(
        `確定要刪除「${filename}」嗎？`
    );

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(
            `/api/documents/${documentId}`,
            {
                method: "DELETE"
            }
        );

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            message.textContent =
                data.detail ||
                "文件刪除失敗。";
            return;
        }

        message.textContent =
            "文件刪除成功。";

        await loadDocuments();

    } catch (error) {
        console.error(error);

        message.textContent =
            "無法連線至伺服器。";
    }
}

documentForm.addEventListener(
    "submit",
    uploadDocument
);

loadDocuments();