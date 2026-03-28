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
        <div class="fade-in flex flex-row items-center justify-center gap-3">
          <div class="nucleus-small"></div>
          <p class="text-text-secondary text-sm font-mono tracking-wide">
            noted. we'll be in touch.
          </p>
        </div>
      `;
    })
    .catch(() => {
      formContainer.innerHTML = `
        <div class="fade-in flex flex-row items-center justify-center gap-3">
          <div class="nucleus-small"></div>
          <p class="text-text-secondary text-sm font-mono tracking-wide">
            noted. we'll be in touch.
          </p>
        </div>
      `;
    });
});
