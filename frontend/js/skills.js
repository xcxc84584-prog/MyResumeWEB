const skillForm = document.getElementById("skillForm");
const skillName = document.getElementById("skillName");
const learningDuration = document.getElementById("learningDuration");
const proficiencyLevel = document.getElementById("proficiencyLevel");
const saveButton = document.getElementById("saveButton");
const cancelEditButton = document.getElementById("cancelEditButton");
const formTitle = document.getElementById("formTitle");
const skillList = document.getElementById("skillList");
const message = document.getElementById("message");

let editingSkillId = null;
let linkingSkillId = null;

const learningDurationText = {
    less_than_30_days: "小於 30 天",
    one_month: "一個月",
    three_months: "三個月",
    six_months: "半年",
    over_one_year: "一年以上"
};

const proficiencyLevelText = {
    beginner: "初階",
    intermediate: "中階",
    advanced: "高階"
};

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function getLearningDurationText(value) {
    return learningDurationText[value] || value;
}

function getProficiencyLevelText(value) {
    return proficiencyLevelText[value] || value;
}

function renderSkillDocuments(skillId, documents) {
    let html = "";

    if (!documents || documents.length === 0) {
        html += `
            <div class="proof-document-empty">
                —
            </div>
        `;
    } else {
        html += documents
            .map(function (document) {
                return `
                    <div class="proof-document">
                        <span>
                            ${escapeHtml(document.original_filename)}
                        </span>
                        <button
                            type="button"
                            onclick="openSkillDocument(${document.id})"
                        >
                            查看
                        </button>
                        <button
                            type="button"
                            onclick="unlinkSkillDocument(${skillId}, ${document.id})"
                        >
                            解除
                        </button>
                    </div>
                `;
            })
            .join("");
    }

    html += `
        <button
            type="button"
            class="link-document-button"
            onclick="showSkillDocumentSelector(${skillId})"
        >
            串接文件
        </button>

        <div
            id="skill-document-selector-${skillId}"
            class="skill-document-selector"
            hidden
        >
        </div>
    `;

    return html;
}

async function loadSkills() {
    try {
        const response = await fetch("/api/skills");

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!response.ok) {
            skillList.innerHTML = `
                <tr>
                    <td colspan="5">
                        技能資料讀取失敗
                    </td>
                </tr>
            `;
            return;
        }

        const skills = await response.json();

        renderSkills(skills);

    } catch (error) {
        console.error(error);

        skillList.innerHTML = `
            <tr>
                <td colspan="5">
                    無法連線至伺服器
                </td>
            </tr>
        `;
    }
}

function renderSkills(skills) {
    if (!skills || skills.length === 0) {
        skillList.innerHTML = `
            <tr>
                <td colspan="5">
                    尚未建立任何技能
                </td>
            </tr>
        `;
        return;
    }

    skillList.innerHTML = skills
        .map(function (skill) {
            return `
                <tr>
                    <td>
                        ${escapeHtml(skill.skill_name)}
                    </td>

                    <td>
                        ${escapeHtml(
                            getLearningDurationText(
                                skill.learning_duration
                            )
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            getProficiencyLevelText(
                                skill.proficiency_level
                            )
                        )}
                    </td>

                    <td>
                        ${renderSkillDocuments(
                            skill.id,
                            skill.documents
                        )}
                    </td>

                    <td>
                        <button
                            type="button"
                            onclick="editSkill(${skill.id})"
                        >
                            編輯
                        </button>

                        <button
                            type="button"
                            onclick="deleteSkill(${skill.id})"
                        >
                            刪除
                        </button>
                    </td>
                </tr>
            `;
        })
        .join("");
}

async function saveSkill(event) {
    event.preventDefault();

    message.textContent = "";

    const name = skillName.value.trim();
    const duration = learningDuration.value;
    const level = proficiencyLevel.value;

    if (!name) {
        message.textContent = "請輸入技能名稱。";
        return;
    }

    if (!duration) {
        message.textContent = "請選擇學習時長。";
        return;
    }

    if (!level) {
        message.textContent = "請選擇學習程度。";
        return;
    }

    const skillData = {
        skill_name: name,
        learning_duration: duration,
        proficiency_level: level
    };

    let url = "/api/skills";
    let method = "POST";

    if (editingSkillId !== null) {
        url = `/api/skills/${editingSkillId}`;
        method = "PUT";
    }

    saveButton.disabled = true;

    if (editingSkillId === null) {
        saveButton.textContent = "新增中...";
    } else {
        saveButton.textContent = "儲存中...";
    }

    try {
        const response = await fetch(
            url,
            {
                method: method,
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(skillData)
            }
        );

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            if (typeof data.detail === "string") {
                message.textContent = data.detail;
            } else {
                message.textContent =
                    `技能資料儲存失敗（HTTP ${response.status}）`;
            }

            return;
        }

        if (editingSkillId === null) {
            message.textContent = "技能建立成功。";
        } else {
            message.textContent = "技能更新成功。";
        }

        resetSkillForm();

        await loadSkills();

    } catch (error) {
        console.error(error);

        message.textContent =
            "無法連線至伺服器。";

    } finally {
        saveButton.disabled = false;

        if (editingSkillId === null) {
            saveButton.textContent =
                "新增技能";
        } else {
            saveButton.textContent =
                "儲存修改";
        }
    }
}

async function editSkill(skillId) {
    message.textContent = "";

    try {
        const response = await fetch(
            `/api/skills/${skillId}`
        );

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (response.status === 404) {
            message.textContent =
                "找不到此技能。";

            await loadSkills();
            return;
        }

        if (!response.ok) {
            message.textContent =
                "技能資料讀取失敗。";
            return;
        }

        const skill = await response.json();

        editingSkillId = skill.id;

        skillName.value =
            skill.skill_name;

        learningDuration.value =
            skill.learning_duration;

        proficiencyLevel.value =
            skill.proficiency_level;

        formTitle.textContent =
            "編輯技能";

        saveButton.textContent =
            "儲存修改";

        cancelEditButton.hidden = false;

        skillName.focus();

    } catch (error) {
        console.error(error);

        message.textContent =
            "無法連線至伺服器。";
    }
}

function cancelEdit() {
    resetSkillForm();

    message.textContent =
        "已取消編輯。";
}

function resetSkillForm() {
    editingSkillId = null;

    skillForm.reset();

    formTitle.textContent =
        "新增技能";

    saveButton.textContent =
        "新增技能";

    saveButton.disabled = false;

    cancelEditButton.hidden = true;
}

async function deleteSkill(skillId) {
    const confirmed = window.confirm(
        "確定要刪除這項技能嗎？"
    );

    if (!confirmed) {
        return;
    }

    message.textContent = "";

    try {
        const response = await fetch(
            `/api/skills/${skillId}`,
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
                "技能刪除失敗。";
            return;
        }

        if (editingSkillId === skillId) {
            resetSkillForm();
        }

        message.textContent =
            "技能刪除成功。";

        await loadSkills();

    } catch (error) {
        console.error(error);

        message.textContent =
            "無法連線至伺服器。";
    }
}

async function showSkillDocumentSelector(skillId) {
    message.textContent = "";

    const selector = document.getElementById(
        `skill-document-selector-${skillId}`
    );

    if (!selector) {
        message.textContent =
            "找不到文件選擇區域。";
        return;
    }

    if (
        linkingSkillId === skillId &&
        !selector.hidden
    ) {
        selector.hidden = true;
        linkingSkillId = null;
        return;
    }

    linkingSkillId = skillId;

    selector.hidden = false;

    selector.innerHTML = `
        <div class="document-selector-loading">
            正在讀取文件庫...
        </div>
    `;

    try {
        const response = await fetch(
            "/api/documents"
        );

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!response.ok) {
            selector.innerHTML = `
                <div>
                    文件資料讀取失敗。
                </div>
            `;
            return;
        }

        const documents =
            await response.json();

        if (
            !documents ||
            documents.length === 0
        ) {
            selector.innerHTML = `
                <div class="document-selector-empty">
                    文件庫目前沒有文件。
                </div>
            `;
            return;
        }

        const options = documents
            .map(function (document) {
                return `
                    <option value="${document.id}">
                        ${escapeHtml(
                            document.original_filename
                        )}
                    </option>
                `;
            })
            .join("");

        selector.innerHTML = `
            <div class="document-selector-box">
                <select
                    id="skill-document-select-${skillId}"
                    class="document-selector-select"
                >
                    <option value="">
                        請選擇文件
                    </option>

                    ${options}
                </select>

                <button
                    type="button"
                    onclick="confirmSkillDocumentLink(${skillId})"
                >
                    確認串接
                </button>

                <button
                    type="button"
                    onclick="cancelSkillDocumentLink(${skillId})"
                >
                    取消
                </button>
            </div>
        `;

    } catch (error) {
        console.error(error);

        selector.innerHTML = `
            <div>
                無法連線至伺服器。
            </div>
        `;
    }
}

async function confirmSkillDocumentLink(skillId) {
    message.textContent = "";

    const select =
        document.getElementById(
            `skill-document-select-${skillId}`
        );

    if (!select) {
        message.textContent =
            "找不到文件選擇器。";
        return;
    }

    const documentId =
        Number(select.value);

    if (
        !Number.isInteger(documentId) ||
        documentId <= 0
    ) {
        message.textContent =
            "請先選擇要串接的文件。";
        return;
    }

    await linkSkillDocument(
        skillId,
        documentId
    );
}

function cancelSkillDocumentLink(skillId) {
    const selector =
        document.getElementById(
            `skill-document-selector-${skillId}`
        );

    if (selector) {
        selector.hidden = true;
        selector.innerHTML = "";
    }

    if (linkingSkillId === skillId) {
        linkingSkillId = null;
    }
}

async function linkSkillDocument(
    skillId,
    documentId
) {
    try {
        const response = await fetch(
            `/api/skills/${skillId}/documents/${documentId}`,
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
            message.textContent =
                "這份文件已經串接此技能。";
            return;
        }

        if (!response.ok) {
            message.textContent =
                data.detail ||
                "文件串接失敗。";
            return;
        }

        linkingSkillId = null;

        message.textContent =
            "證明文件串接成功。";

        await loadSkills();

    } catch (error) {
        console.error(error);

        message.textContent =
            "無法連線至伺服器。";
    }
}

function openSkillDocument(documentId) {
    window.open(
        `/api/documents/${documentId}/file`,
        "_blank"
    );
}

async function unlinkSkillDocument(
    skillId,
    documentId
) {
    const confirmed = window.confirm(
        "確定要解除這份證明文件嗎？"
    );

    if (!confirmed) {
        return;
    }

    message.textContent = "";

    try {
        const response = await fetch(
            `/api/skills/${skillId}/documents/${documentId}`,
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
            message.textContent =
                data.detail ||
                "解除證明文件失敗。";
            return;
        }

        message.textContent =
            "證明文件已解除。";

        await loadSkills();

    } catch (error) {
        console.error(error);

        message.textContent =
            "無法連線至伺服器。";
    }
}

skillForm.addEventListener(
    "submit",
    saveSkill
);

cancelEditButton.addEventListener(
    "click",
    cancelEdit
);

loadSkills();