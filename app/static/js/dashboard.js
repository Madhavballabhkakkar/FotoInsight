const palette = ["#a68456", "#3e4a45", "#8c5a4a", "#c4b49a", "#5e6b73", "#6e5a3c", "#b7a48a", "#2f3432"];
const charts = {};

function money(value) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(Number(value) || 0);
}

function destroyChart(id) {
  if (charts[id]) charts[id].destroy();
}

function lineOrBar(id, type, labels, values, label) {
  const canvas = document.getElementById(id);
  if (!canvas) return;
  destroyChart(id);
  charts[id] = new Chart(canvas, {
    type,
    data: { labels, datasets: [{ label, data: values, borderColor: "#a68456", backgroundColor: type === "line" ? "rgba(166,132,86,0.18)" : palette, fill: type === "line", tension: 0.25 }] },
    options: { responsive: true, plugins: { legend: { display: type !== "line" && type !== "bar" } }, scales: { y: { beginAtZero: true } } },
  });
}

function doughnut(id, labels, values) {
  const canvas = document.getElementById(id);
  if (!canvas) return;
  destroyChart(id);
  charts[id] = new Chart(canvas, {
    type: id.includes("status") || id.includes("service") ? (id.includes("status") ? "pie" : "doughnut") : "doughnut",
    data: { labels, datasets: [{ data: values, backgroundColor: palette }] },
    options: { responsive: true, plugins: { legend: { position: "bottom" } } },
  });
}

function chartCard(title, canvasId) {
  return `<section class="panel"><h2>${title}</h2><canvas id="${canvasId}" height="140"></canvas></section>`;
}

async function loadDashboard() {
  const preset = document.getElementById("preset").value;
  const start = document.getElementById("start");
  const end = document.getElementById("end");
  start.hidden = preset !== "custom";
  end.hidden = preset !== "custom";
  if (preset === "custom" && (!start.value || !end.value)) return;
  const params = new URLSearchParams({ preset });
  if (preset === "custom") { params.set("start", start.value); params.set("end", end.value); }
  const grid = document.getElementById("kpi-grid");
  try {
    const data = await api(`/api/dashboard?${params.toString()}`);
    document.getElementById("range-label").textContent = `${data.range.label}: ${data.range.start} to ${data.range.end}`;
    grid.innerHTML = data.kpis.map((item) => {
      let shown = item.value;
      if (shown === null || shown === undefined) shown = "–";
      else if (item.money) shown = money(item.value);
      else if (item.percent) shown = `${item.value}%`;
      return `<article class="kpi"><span>${item.label}</span><strong>${shown}</strong><small>${item.hint}</small></article>`;
    }).join("");
    document.getElementById("highlights").innerHTML = `<section class="panel">${(data.highlights || []).map((line) => `<div class="insight">${line}</div>`).join("")}</section>`;
    const chartsHost = document.getElementById("chart-grid");
    if (data.scope === "employee") {
      chartsHost.innerHTML = chartCard("Your events by month", "chart-bookings") + chartCard("Your project statuses", "chart-projects");
      lineOrBar("chart-bookings", "bar", data.charts.monthly_bookings.labels, data.charts.monthly_bookings.values, "Events");
      doughnut("chart-projects", data.charts.project_status.labels, data.charts.project_status.values);
      document.getElementById("chart-note").textContent = "Employee view hides studio revenue.";
      return;
    }
    chartsHost.innerHTML = [
      chartCard("Monthly revenue", "chart-revenue"),
      chartCard("Monthly bookings", "chart-bookings"),
      chartCard("Service distribution", "chart-services"),
      chartCard("Enquiry status", "chart-status"),
      chartCard("Revenue by service", "chart-service-revenue"),
      chartCard("Customer growth", "chart-growth"),
    ].join("");
    lineOrBar("chart-revenue", "line", data.charts.monthly_revenue.labels, data.charts.monthly_revenue.values, "Collected revenue");
    lineOrBar("chart-bookings", "bar", data.charts.monthly_bookings.labels, data.charts.monthly_bookings.values, "Bookings");
    doughnut("chart-services", data.charts.service_distribution.labels, data.charts.service_distribution.values);
    const statusChart = charts["chart-status"];
    void statusChart;
    destroyChart("chart-status");
    charts["chart-status"] = new Chart(document.getElementById("chart-status"), {
      type: "pie",
      data: { labels: data.charts.enquiry_status.labels, datasets: [{ data: data.charts.enquiry_status.values, backgroundColor: palette }] },
      options: { responsive: true, plugins: { legend: { position: "bottom" } } },
    });
    lineOrBar("chart-service-revenue", "bar", data.charts.revenue_by_service.labels, data.charts.revenue_by_service.values, "Revenue");
    lineOrBar("chart-growth", "line", data.charts.customer_growth.labels, data.charts.customer_growth.values, "New customers");
    document.getElementById("chart-note").textContent = "Revenue uses payments that were collected. Pending payments and unpaid booking totals are not included.";
  } catch (error) {
    grid.innerHTML = `<div class="panel">${error.message}</div>`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (!document.getElementById("preset")) return;
  Chart.defaults.font.family = "Outfit, sans-serif";
  Chart.defaults.color = "#746d64";
  document.getElementById("preset").addEventListener("change", loadDashboard);
  document.getElementById("start").addEventListener("change", loadDashboard);
  document.getElementById("end").addEventListener("change", loadDashboard);
  loadDashboard();
});
