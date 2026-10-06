function renderResume(resume) {
    renderHeader(
        resume.username,
        resume.profile
    );

    renderProfile(
        resume.profile
    );

    renderSkills(
        resume.skills || []
    );

    renderCertificates(
        resume.certificates || []
    );
}

function renderHeader(username, profile) {
    const name = document.getElementById("resumeName");
    const usernameElement = document.getElementById("resumeUsername");
    const education = document.getElementById("resumeEducation");
    const avatar = document.getElementById("resumeAvatar");
    const placeholder = document.getElementById("resumeAvatarPlaceholder");

    name.textContent =
        profile?.full_name
        || username
        || "未設定姓名";

    usernameElement.textContent =
        username
        ? `@${username}`
        : "";

    education.textContent =
        profile?.education_level
        || "";

    if (profile?.avatar_path) {
        avatar.src = profile.avatar_path;
        avatar.hidden = false;
        placeholder.hidden = true;
    } else {
        avatar.hidden = true;
        placeholder.hidden = false;
    }
}

function renderProfile(profile) {
    const container = document.getElementById("profileGrid");

    container.innerHTML = "";

    if (!profile) {
        container.innerHTML =
            '<p class="resume-empty">尚未建立基本資料。</p>';
        return;
    }

    const fields = [
        ["性別", profile.gender],
        ["出生日期", formatDate(profile.birth_date)],
        ["年齡", profile.age !== null && profile.age !== undefined
            ? `${profile.age} 歲`
            : null
        ],
        ["電話", profile.phone],
        ["教育程度", profile.education_level]
    ];

    fields.forEach(([label, value]) => {
        if (
            value === null
            || value === undefined
            || value === ""
        ) {
            return;
        }

        const item = document.createElement("div");
        item.className = "resume-info-item";

        const labelElement = document.createElement("span");
        labelElement.className = "resume-info-label";
        labelElement.textContent = label;

        const valueElement = document.createElement("span");
        valueElement.className = "resume-info-value";
        valueElement.textContent = value;

        item.appendChild(labelElement);
        item.appendChild(valueElement);

        container.appendChild(item);
    });

    if (!container.children.length) {
        container.innerHTML =
            '<p class="resume-empty">尚無可顯示的基本資料。</p>';
    }
}

function renderSkills(skills) {
    const container = document.getElementById("skillList");

    container.innerHTML = "";

    if (!skills.length) {
        container.innerHTML =
            '<p class="resume-empty">尚無技能資料。</p>';
        return;
    }

    skills.forEach(skill => {
        const card = document.createElement("div");
        card.className = "resume-card";

        const title = document.createElement("h3");
        title.textContent = skill.skill_name;

        card.appendChild(title);

        appendDetail(
            card,
            "學習時長",
            formatLearningDuration(
                skill.learning_duration
            )
        );

        appendDetail(
            card,
            "熟練程度",
            formatProficiency(
                skill.proficiency_level
            )
        );

        appendDocuments(
            card,
            skill.documents || []
        );

        container.appendChild(card);
    });
}

function renderCertificates(certificates) {
    const container = document.getElementById("certificateList");

    container.innerHTML = "";

    if (!certificates.length) {
        container.innerHTML =
            '<p class="resume-empty">尚無證照資料。</p>';
        return;
    }

    certificates.forEach(certificate => {
        const card = document.createElement("div");
        card.className = "resume-card";

        const title = document.createElement("h3");
        title.textContent =
            certificate.certificate_name;

        card.appendChild(title);

        appendDetail(
            card,
            "發證單位",
            certificate.issuer
        );

        appendDetail(
            card,
            "取得日期",
            formatDate(
                certificate.issue_date
            )
        );

        appendDetail(
            card,
            "有效期限",
            formatDate(
                certificate.expiration_date
            )
        );

        appendDetail(
            card,
            "證照編號",
            certificate.certificate_number
        );

        appendDocuments(
            card,
            certificate.documents || []
        );

        container.appendChild(card);
    });
}

function appendDetail(container, label, value) {
    if (
        value === null
        || value === undefined
        || value === ""
    ) {
        return;
    }

    const row = document.createElement("p");
    row.className = "resume-detail";

    const labelElement = document.createElement("strong");
    labelElement.textContent = `${label}：`;

    row.appendChild(labelElement);
    row.appendChild(
        document.createTextNode(value)
    );

    container.appendChild(row);
}

function appendDocuments(container, documents) {
    if (!documents.length) {
        return;
    }

    const wrapper = document.createElement("div");
    wrapper.className = "resume-documents";

    const label = document.createElement("strong");
    label.textContent = "證明文件";

    wrapper.appendChild(label);

    const links = document.createElement("div");
    links.className = "resume-document-links";

    documents.forEach(documentData => {
        const link = document.createElement("a");

        link.className = "resume-document-link";

        link.href =
            documentData.file_url || `/api/resume/documents/${documentData.id}/file`;

        link.target = "_blank";
        link.rel = "noopener noreferrer";

        link.textContent =
            documentData.original_filename;

        links.appendChild(link);
    });

    wrapper.appendChild(links);
    container.appendChild(wrapper);
}

function formatDate(value) {
    if (!value) {
        return null;
    }

    return value;
}

function formatLearningDuration(value) {
    const labels = {
        less_than_30_days: "30 天以下",
        one_month: "1 個月",
        three_months: "3 個月",
        six_months: "6 個月",
        over_one_year: "1 年以上"
    };

    return labels[value] || value;
}

function formatProficiency(value) {
    const labels = {
        beginner: "初階",
        intermediate: "中階",
        advanced: "高階"
    };

    return labels[value] || value;
}