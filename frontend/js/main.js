console.log("ResumeSystem frontend loaded.");

const registerButton = document.getElementById("registerButton");
const loginButton = document.getElementById("loginButton");
const reviewerButton = document.getElementById("reviewerButton");
const deleteAccountButton = document.getElementById("deleteAccountButton");

if (registerButton) {
    registerButton.addEventListener("click", function () {
        window.location.href = "/register";
    });
}

if (loginButton) {
    loginButton.addEventListener("click", function () {
        window.location.href = "/login";
    });
}

if (reviewerButton) {
    reviewerButton.addEventListener("click", function () {
        window.location.href = "/reviewer";
    });
}

if (deleteAccountButton) {
    deleteAccountButton.addEventListener("click", function () {
        window.location.href = "/delete-account";
    });
}