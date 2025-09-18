const container = document.querySelector(".container"),
      pwShowHide = document.querySelectorAll(".showHidePw"),
      pwFields = document.querySelectorAll(".password"),
      signUp = document.querySelector(".signup-link"),
      login = document.querySelector(".login-link");


// Check if the message element exists and if it has content
window.addEventListener('DOMContentLoaded', (event) => {
    const msg = document.getElementById('msg');
    if (msg && msg.innerText.trim() !== '') {
        setTimeout(() => {
            msg.style.opacity = '0';  // Fade out the message
            setTimeout(() => {
                msg.innerText = '';  // Clear the text after fading out
            }, 1500); // Wait for the fade out transition to complete
        }, );  // Wait for 5 seconds before starting the fade out
    }
});


// Toggle password visibility
pwShowHide.forEach(eyeIcon => {
    eyeIcon.addEventListener("click", () => {
        pwFields.forEach(pwField => {
            if (pwField.type === "password") {
                pwField.type = "text";
                pwShowHide.forEach(icon => {
                    icon.classList.replace("uil-eye-slash", "uil-eye");
                });
            } else {
                pwField.type = "password";
                pwShowHide.forEach(icon => {
                    icon.classList.replace("uil-eye", "uil-eye-slash");
                });
            }
        });
    });
});

// Switch between login and signup forms
signUp.addEventListener("click", () => {
    container.classList.add("active");
});
login.addEventListener("click", () => {
    container.classList.remove("active");
});



document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.querySelector('.login form');
    const signupForm = document.querySelector('.signup form');

    // Email validation function
    function isValidEmail(email) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailPattern.test(email);
    }

    // Username validation function (should not contain digits only)
    function isValidUsername(username) {
        const usernamePattern = /^[a-zA-Z]+$/;
        return usernamePattern.test(username);
    }

    // Password validation function (should be more than 8 characters)
    function isValidPassword(password) {
        return password.length > 8;
    }

    // Validate login form
    loginForm.addEventListener('submit', (event) => {
        const email = loginForm.querySelector('input[name="email"]').value;
        const password = loginForm.querySelector('input[name="password"]').value;

        if (!isValidEmail(email)) {
            alert('Please enter a valid email address.');
            event.preventDefault();
            return;
        }

        if (!isValidPassword(password)) {
            alert('Password must be more than 8 characters.');
            event.preventDefault();
            return;
        }
    });

    // Validate signup form
    signupForm.addEventListener('submit', (event) => {
        const name = signupForm.querySelector('input[name="name"]').value;
        const email = signupForm.querySelector('input[name="email"]').value;
        const password = signupForm.querySelector('input[name="password"]').value;
        const confirmPassword = signupForm.querySelector('input[name="confirm_password"]').value;

        if (!isValidUsername(name)) {
            alert('Username should not contain digits.');
            event.preventDefault();
            return;
        }

        if (!isValidEmail(email)) {
            alert('Please enter a valid email address.');
            event.preventDefault();
            return;
        }

        if (!isValidPassword(password)) {
            alert('Password must be more than 8 characters.');
            event.preventDefault();
            return;
        }

        if (password !== confirmPassword) {
            alert('Passwords do not match.');
            event.preventDefault();
            return;
        }
    });
});