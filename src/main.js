import "./style.css";

const form = document.getElementById("notify-form");
const emailInput = document.getElementById("email-input");
const submitBtn = document.getElementById("submit-btn");
const formContainer = document.getElementById("form-container");

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const email = emailInput.value.trim();
  if (!email) return;

  submitBtn.disabled = true;
  submitBtn.textContent = "...";

  fetch("/api/notify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  })
    .then(() => {
      formContainer.innerHTML = `
        <p class="fade-in text-text-secondary text-sm font-mono tracking-wide">
          noted. we'll be in touch.
        </p>
      `;
    })
    .catch(() => {
      formContainer.innerHTML = `
        <p class="fade-in text-text-secondary text-sm font-mono tracking-wide">
          noted. we'll be in touch.
        </p>
      `;
    });
});
