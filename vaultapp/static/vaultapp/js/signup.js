// Wait for the DOM to load
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const nameInput = document.getElementById("name");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
  
    // Helper function to display error messages
    function showError(input, message) {
      const parent = input.parentElement;
      let error = parent.querySelector(".error-message");
  
      // Create an error element if not present
      if (!error) {
        error = document.createElement("div");
        error.className = "error-message";
        parent.appendChild(error);
      }
  
      error.textContent = message;
      input.classList.add("error");
    }
  
    // Helper function to clear errors
    function clearError(input) {
      const parent = input.parentElement;
      const error = parent.querySelector(".error-message");
      if (error) {
        error.textContent = "";
      }
      input.classList.remove("error");
    }
  
    // Validate form inputs
    form.addEventListener("submit", function (e) {
      let valid = true;
  
      // Validate name
      if (nameInput.value.trim() === "") {
        showError(nameInput, "Name is required.");
        valid = false;
      } else {
        clearError(nameInput);
      }
  
      // Validate email
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(emailInput.value.trim())) {
        showError(emailInput, "Enter a valid email address.");
        valid = false;
      } else {
        clearError(emailInput);
      }
  
      // Validate password
      if (passwordInput.value.trim().length < 6) {
        showError(passwordInput, "Password must be at least 6 characters.");
        valid = false;
      } else {
        clearError(passwordInput);
      }
  
      // Prevent form submission if invalid
      if (!valid) {
        e.preventDefault();
      }
    });
  });
  