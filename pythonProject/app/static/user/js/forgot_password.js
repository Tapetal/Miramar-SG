// Select necessary elements
const container = document.querySelector(".container"),
      pwShowHide = document.querySelectorAll(".showHidePw"),
      resetPassword = document.querySelector(".reset-password-link"),
      forgotPassword = document.querySelector(".forgot-password-link")

// Toggle password visibility
pwShowHide.forEach(eyeIcon => {
    eyeIcon.addEventListener("click", () => {
        const passwordFields = eyeIcon.closest('.input-field').querySelectorAll('input[type="password"], input[type="text"]');
        passwordFields.forEach(pwField => {
            if (pwField.type === "password") {
                pwField.type = "text";
                eyeIcon.classList.replace("uil-eye-slash", "uil-eye");
            } else {
                pwField.type = "password";
                eyeIcon.classList.replace("uil-eye", "uil-eye-slash");
            }
        });
    });
});


// Switch between login and signup forms
resetPassword.addEventListener("click", () => {
    container.classList.add("active");
});
forgotPassword.addEventListener("click", () => {
    container.classList.remove("active");
});


// Password validation function (should be more than 8 characters)
function isValidPassword(password) {
    return password.length > 8;
}

// Validate reset password form
if (resetForm) {
    resetForm.addEventListener('submit', (event) => {
        const newPassword = resetForm.querySelector('input[name="new_password"]').value;
        const confirmPassword = resetForm.querySelector('input[name="confirm_password"]').value;

        if (!isValidPassword(newPassword)) {
            alert('Password must be more than 8 characters.');
            event.preventDefault();
        } else if (newPassword !== confirmPassword) {
            alert('Passwords do not match.');
            event.preventDefault();
        }
    });
}

// Handle message display and fade out
window.addEventListener('DOMContentLoaded', (event) => {
    const msg = document.getElementById('msg');
    if (msg && msg.innerText.trim() !== '') {
        setTimeout(() => {
            msg.style.opacity = '0';  // Fade out the message
            setTimeout(() => {
                msg.innerText = '';  // Clear the text after fading out
            }, 1500); // Wait for the fade out transition to complete
        }, 1000);  // Wait for 1 second before starting the fade out
    }
});
