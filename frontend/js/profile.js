const profileForm = document.getElementById("profileForm");
const message = document.getElementById("message");

const fullName = document.getElementById("fullName");
const gender = document.getElementById("gender");
const maritalStatus = document.getElementById("maritalStatus");
const birthDate = document.getElementById("birthDate");
const age = document.getElementById("age");
const heightCm = document.getElementById("heightCm");
const weightKg = document.getElementById("weightKg");
const bloodType = document.getElementById("bloodType");
const phone = document.getElementById("phone");
const address = document.getElementById("address");
const educationLevel = document.getElementById("educationLevel");
const medicalHistory = document.getElementById("medicalHistory");
const avatar = document.getElementById("avatar");
const avatarPreview = document.getElementById("avatarPreview");
const uploadAvatarButton = document.getElementById("uploadAvatarButton");
const avatarMessage = document.getElementById("avatarMessage");

avatar.addEventListener("change", function () {
    const file = avatar.files[0];

    if (!file) {
        return;
    }

    avatarPreview.src = URL.createObjectURL(file);
    avatarPreview.hidden = false;
});

uploadAvatarButton.addEventListener("click", async function () {
    const file = avatar.files[0];

    if (!file) {
        avatarMessage.textContent = "請先選擇圖片。";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/api/profile/avatar", {
            method: "POST",
            body: formData
        });

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            avatarMessage.textContent =
                data.detail || "大頭貼上傳失敗。";
            return;
        }

        avatarPreview.src = data.avatar_path;
        avatarPreview.hidden = false;

        avatarMessage.textContent = "大頭貼上傳成功。";
    } catch (error) {
        console.error(error);
        avatarMessage.textContent = "無法連線至伺服器。";
    }
});

let profileExists = false;

async function loadProfile() {
    try {
        const response = await fetch("/api/profile");

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (response.status === 404) {
            profileExists = false;
            message.textContent = "尚未建立基本資料。";
            return;
        }

        if (!response.ok) {
            message.textContent = "讀取基本資料失敗。";
            return;
        }

        const profile = await response.json();

        profileExists = true;
        
        if (profile.avatar_path) {
            avatarPreview.src = profile.avatar_path;
            avatarPreview.hidden = false;
        }

        fullName.value = profile.full_name ?? "";
        gender.value = profile.gender ?? "";
        maritalStatus.value = profile.marital_status ?? "";
        birthDate.value = profile.birth_date ?? "";
        age.textContent = profile.age ?? "—";
        heightCm.value = profile.height_cm ?? "";
        weightKg.value = profile.weight_kg ?? "";
        bloodType.value = profile.blood_type ?? "";
        phone.value = profile.phone ?? "";
        address.value = profile.address ?? "";
        educationLevel.value = profile.education_level ?? "";
        medicalHistory.value = profile.medical_history ?? "";

        message.textContent = "";
    } catch (error) {
        console.error(error);
        message.textContent = "無法連線至伺服器。";
    }
}
profileForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const profileData = {
        full_name: fullName.value.trim(),
        gender: gender.value || null,
        marital_status: maritalStatus.value || null,
        birth_date: birthDate.value || null,
        height_cm: heightCm.value ? Number(heightCm.value) : null,
        weight_kg: weightKg.value ? Number(weightKg.value) : null,
        blood_type: bloodType.value || null,
        phone: phone.value.trim() || null,
        address: address.value.trim() || null,
        education_level: educationLevel.value || null,
        medical_history: medicalHistory.value.trim() || null
    };

    try {
        const response = await fetch("/api/profile", {
            method: profileExists ? "PUT" : "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(profileData)
        });

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            message.textContent = data.detail || "儲存基本資料失敗。";
            return;
        }

        profileExists = true;

        age.textContent = data.age ?? "—";
        message.textContent = "基本資料儲存成功。";
    } catch (error) {
        console.error(error);
        message.textContent = "無法連線至伺服器。";
    }
});

function calculateAge(birthDateValue) {
    if (!birthDateValue) {
        return null;
    }

    const birth = new Date(`${birthDateValue}T00:00:00`);
    const today = new Date();

    let calculatedAge = today.getFullYear() - birth.getFullYear();

    const birthdayPassed =
        today.getMonth() > birth.getMonth() ||
        (
            today.getMonth() === birth.getMonth() &&
            today.getDate() >= birth.getDate()
        );

    if (!birthdayPassed) {
        calculatedAge--;
    }

    return calculatedAge;
}

birthDate.addEventListener("change", function () {
    const calculatedAge = calculateAge(birthDate.value);
    age.textContent = calculatedAge ?? "—";
});
loadProfile();