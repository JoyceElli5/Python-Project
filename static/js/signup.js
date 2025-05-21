document.addEventListener("DOMContentLoaded", function () {
  // Initialize AOS
  AOS.init({
    once: true, // whether animation should happen only once - while scrolling down
    mirror: false, // whether elements should animate out while scrolling past them
    disable: "mobile", // accepts: 'phone', 'tablet', 'mobile', boolean, expression or function
  });

  // Form validation
  const form = document.querySelector(".form");
  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirm_password");

  if (form) {
    form.addEventListener("submit", function (event) {
      // Check if passwords match
      if (password.value !== confirmPassword.value) {
        event.preventDefault();

        // Create error message if it doesn't exist
        let errorMessage = document.querySelector(".password-error");
        if (!errorMessage) {
          errorMessage = document.createElement("div");
          errorMessage.className = "password-error";
          errorMessage.style.color = "#e53e3e";
          errorMessage.style.fontSize = "14px";
          errorMessage.style.marginTop = "-15px";
          errorMessage.style.marginBottom = "15px";
          confirmPassword.parentNode.insertAdjacentElement(
            "afterend",
            errorMessage
          );
        }

        errorMessage.textContent = "Passwords do not match";

        // Add error styling
        confirmPassword.parentNode.style.boxShadow =
          "0 0 0 2px rgba(229, 62, 62, 0.3)";

        // Remove error styling after 3 seconds
        setTimeout(() => {
          confirmPassword.parentNode.style.boxShadow = "";
          errorMessage.textContent = "";
        }, 3000);
      }
    });
  }

  // Add hover effect to buttons
  const buttons = document.querySelectorAll(".btn");

  buttons.forEach((button) => {
    button.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-2px)";
    });

    button.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0)";
    });
  });

  // Real-time password validation
  if (password && confirmPassword) {
    confirmPassword.addEventListener("input", function () {
      if (password.value && this.value) {
        if (password.value !== this.value) {
          this.setCustomValidity("Passwords do not match");
        } else {
          this.setCustomValidity("");
        }
      }
    });
  }
});
