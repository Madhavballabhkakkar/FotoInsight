document.addEventListener("DOMContentLoaded", () => {
  const filters = document.querySelectorAll("[data-filter]");
  const cards = document.querySelectorAll("[data-category]");
  filters.forEach((button) => {
    button.addEventListener("click", () => {
      filters.forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      const chosen = button.dataset.filter;
      cards.forEach((card) => {
        card.style.display = chosen === "all" || card.dataset.category === chosen ? "" : "none";
      });
    });
  });

  const box = document.querySelector(".lightbox");
  if (box) {
    const image = box.querySelector("img");
    const caption = box.querySelector("p");
    document.querySelectorAll("[data-preview]").forEach((link) => {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        image.src = link.dataset.preview;
        image.alt = link.dataset.title || "";
        caption.textContent = link.dataset.title || "";
        box.classList.add("open");
      });
    });
    box.querySelector("button").addEventListener("click", () => box.classList.remove("open"));
    box.addEventListener("click", (event) => { if (event.target === box) box.classList.remove("open"); });
  }

  const form = document.querySelector("form[data-public]");
  if (!form) return;
  const tokenField = form.querySelector("[name=submission_token]");
  const makeToken = () => (window.crypto && crypto.randomUUID ? crypto.randomUUID().replace(/-/g, "") : `t${Date.now()}${Math.random().toString(36).slice(2, 10)}`);
  if (tokenField && !tokenField.value) tokenField.value = makeToken();
  const eventType = form.querySelector("[name=event_type]");
  const packageSelect = form.querySelector("[name=package_id]");
  const packageData = document.getElementById("package-data");
  if (eventType && packageSelect && packageData) {
    const packages = JSON.parse(packageData.textContent || "[]");
    const filterPackages = () => {
      const selected = eventType.value;
      const current = packageSelect.value;
      packageSelect.innerHTML = '<option value="">No package preference</option>';
      packages.filter((item) => item.service_name === selected).forEach((item) => {
        const option = document.createElement("option");
        option.value = item.id;
        option.textContent = `${item.name} · INR ${Number(item.price).toLocaleString("en-IN")}`;
        if (String(item.id) === current) option.selected = true;
        packageSelect.appendChild(option);
      });
    };
    eventType.addEventListener("change", filterPackages);
    filterPackages();
  }
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = form.querySelector("[type=submit]");
    const alertBox = form.querySelector(".form-alert");
    button.disabled = true;
    const body = {};
    new FormData(form).forEach((value, key) => { body[key] = value; });
    try {
      const response = await fetch(form.dataset.public, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": document.querySelector('meta[name="csrf-token"]').content,
          "X-Requested-With": "fetch",
        },
        body: JSON.stringify(body),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || "Could not submit the form.");
      form.hidden = true;
      const done = document.querySelector(".success-box");
      done.hidden = false;
      done.querySelector("[data-code]").textContent = data.enquiry_code;
      done.querySelector("[data-message]").textContent = data.message;
    } catch (error) {
      alertBox.textContent = error.message;
      alertBox.classList.remove("d-none");
      if (tokenField) tokenField.value = makeToken();
      button.disabled = false;
    }
  });
});
