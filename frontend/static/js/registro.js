/* Validación de formulario de registro de clientes en cliente */
document.addEventListener('DOMContentLoaded', function () {
    const registerForm = document.querySelector("#register-form");

    if (registerForm) {
        const passwordInput = registerForm.querySelector("#register-password");
        const confirmationInput = registerForm.querySelector("#register-password-confirm");
        const mismatchMessage = registerForm.querySelector("#password-mismatch");

        const validatePasswords = () => {
            const passwordsDoNotMatch = confirmationInput.value !== passwordInput.value;
            if (mismatchMessage) mismatchMessage.hidden = !passwordsDoNotMatch;
            confirmationInput.setAttribute("aria-invalid", String(passwordsDoNotMatch));
            return !passwordsDoNotMatch;
        };

        registerForm.addEventListener("submit", (event) => {
            if (!validatePasswords()) {
                event.preventDefault();
                confirmationInput.focus();
            }
        });

        confirmationInput.addEventListener("input", () => {
            if (mismatchMessage && !mismatchMessage.hidden) {
                validatePasswords();
            }
        });

        passwordInput.addEventListener("input", () => {
            if (mismatchMessage && !mismatchMessage.hidden) {
                validatePasswords();
            }
        });
    }
});

