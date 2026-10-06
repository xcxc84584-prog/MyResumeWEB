document.addEventListener("DOMContentLoaded", async () => {
    const id = window.location.pathname.split("/").pop();
    const loading = document.getElementById("resumeLoading");
    const error = document.getElementById("resumeError");
    try {
        const response = await fetch(`/api/reviewer/submissions/${encodeURIComponent(id)}`, {credentials: "include"});
        if (response.status === 401) { window.location.replace("/reviewer/login"); return; }
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "無法取得履歷");
        renderResume(data.resume);
        document.getElementById("submittedAt").textContent = new Date(data.submitted_at).toLocaleString("zh-TW");
        document.getElementById("submissionStatus").textContent = data.status_text;
        if (data.legacy_snapshot) document.getElementById("snapshotNotice").textContent =
            "此為舊版投遞紀錄，未保存證明文件連結；申請者撤回並重新投遞後即可補齊。";
        document.getElementById("resumeContent").hidden = false;
    } catch (err) {
        error.textContent = err.message || "無法載入履歷";
        error.hidden = false;
    } finally { loading.hidden = true; }
});
