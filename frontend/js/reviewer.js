console.log("Reviewer page loaded.");

const reviewerLoginButton =
    document.getElementById("reviewerLoginButton");

const reviewerRegisterButton =
    document.getElementById("reviewerRegisterButton");

if (reviewerLoginButton) {
    reviewerLoginButton.addEventListener("click", function () {
        console.log("Reviewer login button clicked.");
        window.location.href = "/reviewer/login";
    });
}

if (reviewerRegisterButton) {
    reviewerRegisterButton.addEventListener("click", function () {
        console.log("Reviewer register button clicked.");
        window.location.href = "/reviewer/register";
    });
}