const palette = ["#a68456", "#3e4a45", "#8c5a4a", "#c4b49a", "#5e6b73", "#6e5a3c", "#b7a48a", "#2f3432"];
const liveCharts = [];

function inr(value) {
  if (value === null || value === undefined || value === "") return "–";
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(Number(value) || 0);
}
function shown(value, suffix) {
  if (value === null || value === undefined) return "–";
  return suffix ? `${value}${suffix}` : value;
}
function card(title, body) {
  return `<section class="panel"><h2>${title}</h2>${body}</section>`;
}
function makeChart(canvas, config) {
  liveCharts.push(new Chart(canvas, config));
}
function heatColor(value, max) {
  if (!max) return "#f6f3ee";
  const mix = Math.round(255 - (value / max) * 140);
  return `rgb(${mix}, ${Math.round(mix * 0.9)}, ${Math.round(mix * 0.7)})`;
}

function render(data) {
  liveCharts.splice(0).forEach((chart) => chart.destroy());
  const root = document.getElementById("analytics-root");
  const revenue = data.revenue;
  const customers = data.customers;
  const enquiries = data.enquiries;
  const services = data.services;
  const seasonal = data.seasonal;
  const locations = data.locations;
  const maxHeat = Math.max(0, ...seasonal.heatmap.values.flat());
  root.innerHTML = [
    card("Business insights", (data.insights || []).map((line) => `<div class="insight">${line}</div>`).join("") || "<p>Not enough data.</p>"),
    card("Revenue", `
      <div class="kpis">
        <article class="kpi"><span>Collected</span><strong style="font-size:1.5rem">${inr(revenue.total_revenue)}</strong></article>
        <article class="kpi"><span>Refunds</span><strong style="font-size:1.5rem">${inr(revenue.refunds)}</strong></article>
        <article class="kpi"><span>Pending, excluded</span><strong style="font-size:1.5rem">${inr(revenue.pending_not_counted)}</strong></article>
        <article class="kpi"><span>Average booking value</span><strong style="font-size:1.5rem">${inr(revenue.average_booking_value)}</strong><small>Mean contract of non-cancelled bookings. Not cash.</small></article>
      </div>
      <p class="note">Monthly collected cash uses the payment date. Refunds are already subtracted. Pending payments are not in the line.</p>
      <div class="charts"><div><canvas id="c-revenue"></canvas></div><div><canvas id="c-service-revenue"></canvas></div></div>
      <p class="note">Change versus the previous month: ${revenue.growth ? revenue.growth.percent + "% (" + revenue.growth.previous_label + " to " + revenue.growth.current_label + ")" : "not enough months"}.</p>
      <canvas id="c-yoy"></canvas>`),
    card("Customers", `
      <div class="kpis">
        <article class="kpi"><span>Customers by period end</span><strong>${customers.total_customers}</strong></article>
        <article class="kpi"><span>New in range</span><strong>${customers.new_customers}</strong></article>
        <article class="kpi"><span>Returning in this range</span><strong>${customers.returning_customers}</strong><small>Booked during these dates, and already have two or more bookings.</small></article>
        <article class="kpi"><span>Average spend in range</span><strong style="font-size:1.4rem">${inr(customers.average_spending)}</strong></article>
      </div>
      <p class="note">${customers.segment_note || ""}</p>
      <table class="data"><thead><tr><th>Segment</th><th>Rule</th><th>Count</th></tr></thead><tbody>
        ${(customers.segments || []).map((item) => `<tr><td>${item.name}</td><td>${item.rule}</td><td>${item.count}</td></tr>`).join("")}
      </tbody></table>
      <h2>High-value customers</h2>
      ${customers.high_value_threshold ? `<p class="note">Threshold ${inr(customers.high_value_threshold)} lifetime collected spend.</p>` : "<p class='note'>Need at least four paying customers before a 75th-percentile threshold is shown.</p>"}
      <table class="data"><thead><tr><th>Name</th><th>City</th><th>Spend</th><th>Bookings</th></tr></thead><tbody>
        ${(customers.high_value || []).map((item) => `<tr><td><a href="/admin/customers/${item.id}">${item.name}</a></td><td>${item.city}</td><td>${inr(item.spending)}</td><td>${item.bookings}</td></tr>`).join("") || "<tr><td colspan='4'>None in this view.</td></tr>"}
      </tbody></table>
      <canvas id="c-growth"></canvas>
      <canvas id="c-cities"></canvas>`),
    card("Enquiry conversion", `
      <p>${enquiries.definition}</p>
      <div class="kpis">
        <article class="kpi"><span>Total</span><strong>${enquiries.total}</strong></article>
        <article class="kpi"><span>Eligible</span><strong>${enquiries.eligible}</strong></article>
        <article class="kpi"><span>Converted</span><strong>${enquiries.converted}</strong></article>
        <article class="kpi"><span>Rate</span><strong>${shown(enquiries.conversion_rate, "%")}</strong><small>New excluded: ${enquiries.new_excluded}. Average days to convert: ${shown(enquiries.average_conversion_days)}</small></article>
      </div>
      <canvas id="c-status"></canvas>
      <canvas id="c-rate"></canvas>
      <table class="data"><thead><tr><th>Service</th><th>Enquiries</th><th>Eligible</th><th>Converted</th><th>Rate</th></tr></thead><tbody>
        ${(enquiries.by_service || []).map((row) => `<tr><td>${row.service}</td><td>${row.total}</td><td>${row.eligible}</td><td>${row.converted}</td><td>${shown(row.conversion_rate, "%")}</td></tr>`).join("")}
      </tbody></table>`),
    card("Service performance", `
      <p>Most enquiries: ${services.most_popular || "–"}. Fewest enquiries: ${services.least_popular || "–"}. Highest revenue: ${services.highest_revenue || "–"}. Most booked: ${services.most_booked || "–"}.</p>
      <table class="data"><thead><tr><th>Service</th><th>Enquiries</th><th>Bookings</th><th>Collected</th><th>Avg contract</th></tr></thead><tbody>
        ${(services.rows || []).map((row) => `<tr><td>${row.service}</td><td>${row.enquiries}</td><td>${row.bookings}</td><td>${inr(row.revenue)}</td><td>${inr(row.average_booking_value)}</td></tr>`).join("")}
      </tbody></table>
      <p class="note">The lines count bookings created in this range, by month created. Cancelled bookings are excluded, matching the Bookings column.</p>
      <canvas id="c-demand"></canvas>`),
    card("Seasonal demand", `
      <p>Counted by event date. Weekend share ${shown(seasonal.weekend_share, "%")} · weekday share ${shown(seasonal.weekday_share, "%")}.</p>
      <table class="data"><thead><tr><th>Season rule</th><th>Months</th><th>Bookings</th></tr></thead><tbody>
        ${(seasonal.seasons || []).map((row) => `<tr><td>${row.name}</td><td>${row.months.join(", ")}</td><td>${row.bookings}</td></tr>`).join("")}
      </tbody></table>
      <p>Higher demand: ${(seasonal.high_demand || []).join(", ") || "not distinct"}. Quieter: ${(seasonal.low_demand || []).join(", ") || "not distinct"}.</p>
      <table class="heat"><thead><tr><th></th>${seasonal.heatmap.months.map((month) => `<th>${month.slice(0,3)}</th>`).join("")}</tr></thead><tbody>
        ${seasonal.heatmap.years.map((year, index) => `<tr><th>${year}</th>${seasonal.heatmap.values[index].map((value) => `<td style="background:${heatColor(value, maxHeat)}">${value}</td>`).join("")}</tr>`).join("")}
      </tbody></table>
      <canvas id="c-weekday"></canvas>`),
    card("Locations", `
      <p>${locations.top_city ? locations.top_city + " has " + locations.top_city_share + "% of bookings recorded in this range." : "No location split yet."}</p>
      <p class="note">Enquiries and bookings use the day they were recorded. Revenue uses the payment date.</p>
      <table class="data"><thead><tr><th>City</th><th>Enquiries</th><th>Bookings</th><th>Revenue</th><th>Conversion</th></tr></thead><tbody>
        ${(locations.rows || []).map((row) => `<tr><td>${row.city}</td><td>${row.enquiries}</td><td>${row.bookings}</td><td>${inr(row.revenue)}</td><td>${shown(row.conversion_rate, "%")}</td></tr>`).join("")}
      </tbody></table>`),
    card("Predicted, not actual", `
      <p>${data.forecast.disclaimer}</p>
      ${forecastBlock(data.forecast.bookings)}
      ${forecastBlock(data.forecast.revenue)}
      <canvas id="c-forecast"></canvas>`),
  ].join("");

  const axis = { responsive: true, plugins: { legend: { position: "bottom" } }, scales: { y: { beginAtZero: true } } };
  makeChart(document.getElementById("c-revenue"), { type: "line", data: { labels: revenue.monthly.labels, datasets: [{ label: "Collected revenue", data: revenue.monthly.values, borderColor: "#a68456", tension: 0.25 }] }, options: axis });
  makeChart(document.getElementById("c-service-revenue"), { type: "bar", data: { labels: revenue.by_service.labels, datasets: [{ label: "By service", data: revenue.by_service.values, backgroundColor: "#a68456" }] }, options: axis });
  makeChart(document.getElementById("c-yoy"), { type: "bar", data: { labels: revenue.yearly.labels, datasets: [{ label: "Yearly collected revenue", data: revenue.yearly.values, backgroundColor: "#3e4a45" }] }, options: axis });
  makeChart(document.getElementById("c-growth"), { type: "line", data: { labels: customers.growth.labels, datasets: [{ label: "New customers", data: customers.growth.values, borderColor: "#8c5a4a" }] }, options: axis });
  makeChart(document.getElementById("c-cities"), { type: "bar", data: { labels: customers.location.labels, datasets: [{ label: "New customers by city", data: customers.location.values, backgroundColor: palette }] }, options: axis });
  makeChart(document.getElementById("c-status"), { type: "pie", data: { labels: enquiries.by_status.labels, datasets: [{ data: enquiries.by_status.values, backgroundColor: palette }] }, options: { responsive: true, plugins: { legend: { position: "bottom" } } } });
  makeChart(document.getElementById("c-rate"), { type: "line", data: { labels: enquiries.monthly_rate.labels, datasets: [{ label: "Conversion %", data: enquiries.monthly_rate.values, borderColor: "#6e5a3c" }] }, options: axis });
  const demand = services.demand_trend || { labels: [], datasets: [] };
  makeChart(document.getElementById("c-demand"), { type: "line", data: { labels: demand.labels, datasets: demand.datasets.map((set, index) => ({ label: set.label, data: set.values, borderColor: palette[index % palette.length] })) }, options: axis });
  makeChart(document.getElementById("c-weekday"), { type: "bar", data: { labels: seasonal.by_weekday.labels, datasets: [{ label: "Events", data: seasonal.by_weekday.values, backgroundColor: "#a68456" }] }, options: axis });
  if (data.forecast.revenue.available) {
    makeChart(document.getElementById("c-forecast"), {
      type: "line",
      data: {
        labels: data.forecast.revenue.history_labels.concat(data.forecast.revenue.future_labels),
        datasets: [
          { label: "Actual collected revenue", data: data.forecast.revenue.history_values.concat(data.forecast.revenue.future_labels.map(() => null)), borderColor: "#3e4a45" },
          { label: "Predicted revenue", data: data.forecast.revenue.history_values.map(() => null).concat(data.forecast.revenue.future_values), borderColor: "#a68456", borderDash: [5, 4] },
        ],
      },
      options: axis,
    });
  }
}

function forecastBlock(item) {
  if (!item.available) return `<p>${item.message}</p>`;
  const rows = item.future_labels.map((label, index) => `<li>${label}: ${item.name.includes("revenue") ? inr(item.future_values[index]) : item.future_values[index]} predicted</li>`).join("");
  return `<p>${item.message}</p><ul>${rows}</ul>`;
}

async function loadAnalytics() {
  const preset = document.getElementById("preset").value;
  const start = document.getElementById("start");
  const end = document.getElementById("end");
  start.hidden = preset !== "custom";
  end.hidden = preset !== "custom";
  if (preset === "custom" && (!start.value || !end.value)) return;
  const params = new URLSearchParams({ preset });
  if (preset === "custom") { params.set("start", start.value); params.set("end", end.value); }
  try {
    const data = await api(`/api/analytics?${params.toString()}`);
    document.getElementById("range-label").textContent = `${data.range.label}: ${data.range.start} to ${data.range.end}`;
    render(data);
  } catch (error) {
    document.getElementById("analytics-root").innerHTML = `<div class="panel">${error.message}</div>`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (!document.getElementById("analytics-root")) return;
  Chart.defaults.font.family = "Outfit, sans-serif";
  Chart.defaults.color = "#746d64";
  ["preset", "start", "end"].forEach((id) => document.getElementById(id).addEventListener("change", loadAnalytics));
  loadAnalytics();
});
