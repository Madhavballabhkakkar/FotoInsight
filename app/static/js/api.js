function csrfToken() {
  const tag = document.querySelector('meta[name="csrf-token"]');
  return tag ? tag.content : "";
}

async function api(url, { method = "GET", body = null } = {}) {
  const headers = { "X-CSRF-Token": csrfToken(), "X-Requested-With": "fetch" };
  const options = { method, headers };
  if (body !== null) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }
  const response = await fetch(url, options);
  const text = await response.text();
  let data = {};
  if (text) {
    try { data = JSON.parse(text); } catch (error) { data = { error: "Unexpected server response." }; }
  }
  if (!response.ok) {
    const err = new Error(data.error || "Request failed.");
    err.status = response.status;
    throw err;
  }
  return data;
}

function formToObject(form) {
  const body = {};
  new FormData(form).forEach((value, key) => {
    if (Object.prototype.hasOwnProperty.call(body, key)) {
      if (!Array.isArray(body[key])) body[key] = [body[key]];
      body[key].push(value);
    } else {
      body[key] = value;
    }
  });
  return body;
}

const formCollectors = {};
function registerCollector(formId, collector) {
  formCollectors[formId] = collector;
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form[data-api]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const alertBox = form.querySelector(".form-alert");
      const button = form.querySelector("[type=submit]");
      if (button) button.disabled = true;
      try {
        let body = formToObject(form);
        if (formCollectors[form.id]) body = formCollectors[form.id](body, form);
        const data = await api(form.dataset.api, { method: form.dataset.method || "POST", body });
        if (data.csrf_token) {
          const tag = document.querySelector('meta[name="csrf-token"]');
          if (tag) tag.content = data.csrf_token;
        }
        if (form.dataset.redirect) {
          window.location.href = form.dataset.redirect.replace(":id", data.id || "");
          return;
        }
        if (form.dataset.reload === "1") {
          window.location.reload();
          return;
        }
        if (alertBox) {
          alertBox.textContent = data.message || "Saved.";
          alertBox.classList.remove("d-none", "alert-danger");
          alertBox.classList.add("alert-success");
        }
      } catch (error) {
        if (alertBox) {
          alertBox.textContent = error.message;
          alertBox.classList.remove("d-none", "alert-success");
          alertBox.classList.add("alert-danger");
        } else {
          window.alert(error.message);
        }
      } finally {
        if (button) button.disabled = false;
      }
    });
  });

  document.querySelectorAll("[data-delete]").forEach((button) => {
    button.addEventListener("click", async () => {
      if (!window.confirm(button.dataset.confirm || "Delete this record? This cannot be undone.")) return;
      button.disabled = true;
      try {
        await api(button.dataset.delete, { method: "DELETE" });
        window.location.href = button.dataset.after || window.location.pathname;
      } catch (error) {
        window.alert(error.message);
        button.disabled = false;
      }
    });
  });

  document.querySelectorAll("[data-post]").forEach((button) => {
    button.addEventListener("click", async () => {
      if (button.dataset.confirm && !window.confirm(button.dataset.confirm)) return;
      button.disabled = true;
      try {
        const body = button.dataset.body ? JSON.parse(button.dataset.body) : {};
        await api(button.dataset.post, { method: button.dataset.method || "POST", body });
        window.location.reload();
      } catch (error) {
        window.alert(error.message);
        button.disabled = false;
      }
    });
  });

  const toggle = document.querySelector("[data-sidebar]");
  const sidebar = document.querySelector(".sidebar");
  if (toggle && sidebar) toggle.addEventListener("click", () => sidebar.classList.toggle("open"));

  document.querySelectorAll("[data-pop]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      const menu = document.querySelector(button.dataset.pop);
      document.querySelectorAll(".menu-pop.open").forEach((open) => { if (open !== menu) open.classList.remove("open"); });
      menu.classList.toggle("open");
    });
  });
  document.addEventListener("click", () => document.querySelectorAll(".menu-pop.open").forEach((menu) => menu.classList.remove("open")));
});
