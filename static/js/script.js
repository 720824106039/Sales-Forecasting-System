/**
 * Sales Forecasting System - Client-Side JavaScript
 * Handles Chart.js visualizations, AJAX forecasting requests,
 * table search/filter, and CSV export.
 */

// Global chart references
let forecastChartInstance = null;
let dashboardChartInstance = null;
let analyticsCharts = {};

document.addEventListener("DOMContentLoaded", () => {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }

    // Auto-dismiss alerts after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
    }, 5000);

    // Initialize page-specific scripts
    initDashboardPage();
    initAnalyticsPage();
    initForecastPage();
    initSalesDataPage();
});

/* ==========================================================================
   1. DASHBOARD PAGE
   ========================================================================== */
function initDashboardPage() {
    const canvas = document.getElementById("dashboardTrendChart");
    if (!canvas) return;

    try {
        const rawData = JSON.parse(canvas.dataset.chartData || "{}");
        if (!rawData.labels || rawData.labels.length === 0) return;

        const ctx = canvas.getContext("2d");
        dashboardChartInstance = new Chart(ctx, {
            type: "line",
            data: {
                labels: rawData.labels,
                datasets: [{
                    label: "Daily Sales ($)",
                    data: rawData.values,
                    borderColor: "#1e40af",
                    backgroundColor: "rgba(30, 64, 175, 0.08)",
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 2,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => ` Sales: $${context.raw.toLocaleString(undefined, {minimumFractionDigits: 2})}`
                        }
                    }
                },
                scales: {
                    x: { grid: { display: false }, ticks: { maxTicksLimit: 10 } },
                    y: {
                        beginAtZero: true,
                        grid: { color: "#f1f5f9" },
                        ticks: { callback: (v) => "$" + v.toLocaleString() }
                    }
                }
            }
        });
    } catch (e) {
        console.error("Failed to load dashboard chart:", e);
    }
}

/* ==========================================================================
   2. ANALYTICS PAGE
   ========================================================================== */
function initAnalyticsPage() {
    const container = document.getElementById("analyticsDataContainer");
    if (!container) return;

    try {
        const data = JSON.parse(container.dataset.analytics || "{}");
        if (!data.daily) return;

        // 1. Sales Over Time (Line Chart)
        const ctxDaily = document.getElementById("chartSalesOverTime")?.getContext("2d");
        if (ctxDaily) {
            analyticsCharts.daily = new Chart(ctxDaily, {
                type: "line",
                data: {
                    labels: data.daily.labels,
                    datasets: [{
                        label: "Daily Sales ($)",
                        data: data.daily.values,
                        borderColor: "#0284c7",
                        backgroundColor: "rgba(2, 132, 199, 0.08)",
                        borderWidth: 2,
                        fill: true,
                        tension: 0.25,
                        pointRadius: 1.5,
                        pointHoverRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { ticks: { maxTicksLimit: 12 }, grid: { display: false } },
                        y: { beginAtZero: true, ticks: { callback: (v) => "$" + v.toLocaleString() } }
                    }
                }
            });
        }

        // 2. Monthly Sales (Bar Chart)
        const ctxMonthly = document.getElementById("chartMonthlySales")?.getContext("2d");
        if (ctxMonthly) {
            analyticsCharts.monthly = new Chart(ctxMonthly, {
                type: "bar",
                data: {
                    labels: data.monthly.labels,
                    datasets: [{
                        label: "Monthly Revenue ($)",
                        data: data.monthly.values,
                        backgroundColor: "#2563eb",
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true, ticks: { callback: (v) => "$" + v.toLocaleString() } }
                    }
                }
            });
        }

        // 3. Product Sales (Bar Chart)
        const ctxProducts = document.getElementById("chartProductSales")?.getContext("2d");
        if (ctxProducts) {
            analyticsCharts.products = new Chart(ctxProducts, {
                type: "bar",
                data: {
                    labels: data.products.labels,
                    datasets: [{
                        label: "Sales by Product ($)",
                        data: data.products.values,
                        backgroundColor: "#0d9488",
                        borderRadius: 6
                    }]
                },
                options: {
                    indexAxis: "y",
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { beginAtZero: true, ticks: { callback: (v) => "$" + v.toLocaleString() } }
                    }
                }
            });
        }

        // 4. Category Sales (Doughnut Chart)
        const ctxCategories = document.getElementById("chartCategorySales")?.getContext("2d");
        if (ctxCategories) {
            analyticsCharts.categories = new Chart(ctxCategories, {
                type: "doughnut",
                data: {
                    labels: data.categories.labels,
                    datasets: [{
                        data: data.categories.values,
                        backgroundColor: ["#2563eb", "#0284c7", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: "bottom" },
                        tooltip: {
                            callbacks: {
                                label: (context) => ` ${context.label}: $${context.raw.toLocaleString(undefined, {minimumFractionDigits: 2})}`
                            }
                        }
                    }
                }
            });
        }

    } catch (e) {
        console.error("Failed to parse analytics chart data:", e);
    }
}

/* ==========================================================================
   3. FORECAST PAGE
   ========================================================================== */
function initForecastPage() {
    const forecastForm = document.getElementById("forecastForm");
    if (!forecastForm) return;

    // Run initial forecast on page load
    fetchForecast(7);

    // Horizon button clicks
    const horizonButtons = document.querySelectorAll(".btn-forecast-horizon");
    horizonButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            horizonButtons.forEach(b => b.classList.remove("active", "btn-primary", "text-white"));
            horizonButtons.forEach(b => b.classList.add("btn-outline-primary"));
            btn.classList.remove("btn-outline-primary");
            btn.classList.add("active", "btn-primary", "text-white");

            const days = parseInt(btn.dataset.days || "7", 10);
            fetchForecast(days);
        });
    });

    // CSV Export button
    const exportBtn = document.getElementById("exportForecastBtn");
    if (exportBtn) {
        exportBtn.addEventListener("click", exportForecastToCSV);
    }
}

let currentForecastData = null;

async function fetchForecast(days) {
    const spinner = document.getElementById("forecastSpinner");
    if (spinner) spinner.style.display = "flex";

    try {
        const response = await fetch(`/api/forecast?days=${days}`);
        const data = await response.json();

        if (spinner) spinner.style.display = "none";

        if (data.error) {
            alert("Forecasting Error: " + data.error);
            return;
        }

        currentForecastData = data;
        updateForecastUI(data);
    } catch (err) {
        if (spinner) spinner.style.display = "none";
        console.error("Error generating forecast:", err);
        alert("Failed to connect to the forecasting service. Please try again.");
    }
}

function updateForecastUI(data) {
    // 1. Update Metrics
    document.getElementById("metricMAE").textContent = "$" + (data.metrics.mae || 0).toFixed(2);
    document.getElementById("metricRMSE").textContent = "$" + (data.metrics.rmse || 0).toFixed(2);
    document.getElementById("metricR2").textContent = (data.metrics.r2 !== undefined ? data.metrics.r2 : 0).toFixed(3);

    // 2. Update Forecast Summary
    document.getElementById("summaryTotalSales").textContent = "$" + data.total_forecasted_sales.toLocaleString(undefined, {minimumFractionDigits: 2});
    document.getElementById("summaryAvgSales").textContent = "$" + data.avg_forecasted_sales.toLocaleString(undefined, {minimumFractionDigits: 2});
    document.getElementById("summaryHorizon").textContent = `${data.forecast_days} Days`;

    // 3. Update Forecast Results Table
    const tbody = document.getElementById("forecastTableBody");
    if (tbody) {
        tbody.innerHTML = "";
        data.forecast_results.forEach((item, idx) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><span class="badge bg-light text-dark border">Day ${idx + 1}</span></td>
                <td><strong>${item.date}</strong></td>
                <td><span class="text-muted">${item.day_name}</span></td>
                <td class="fw-bold text-primary">$${item.predicted_sales.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                <td><span class="badge bg-success-subtle text-success border border-success-subtle">Model Estimate</span></td>
            `;
            tbody.appendChild(tr);
        });
    }

    // 4. Update Combined Line Chart (Historical + Forecast)
    renderForecastChart(data);
}

function renderForecastChart(data) {
    const canvas = document.getElementById("forecastCombinedChart");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    // Historical labels and values
    const histDates = data.historical_chart_data.map(d => d.date);
    const histValues = data.historical_chart_data.map(d => d.sales);

    // Future forecast labels and values
    const forecastDates = data.forecast_results.map(d => d.date);
    const forecastValues = data.forecast_results.map(d => d.predicted_sales);

    // Combined labels
    const allLabels = [...histDates, ...forecastDates];

    // Actual series: values for history, null for forecast
    const actualSeries = [...histValues, ...new Array(forecastDates.length).fill(null)];

    // Forecast series: bridge point from last historical point so lines connect cleanly
    const forecastSeries = new Array(histDates.length - 1).fill(null);
    if (histValues.length > 0) {
        forecastSeries.push(histValues[histValues.length - 1]); // Bridge point
    }
    forecastSeries.push(...forecastValues);

    if (forecastChartInstance) {
        forecastChartInstance.destroy();
    }

    forecastChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: allLabels,
            datasets: [
                {
                    label: "Historical Actual Sales ($)",
                    data: actualSeries,
                    borderColor: "#2563eb",
                    backgroundColor: "rgba(37, 99, 235, 0.05)",
                    borderWidth: 2.2,
                    pointRadius: 2,
                    tension: 0.2,
                    fill: false
                },
                {
                    label: "Forecasted Sales ($)",
                    data: forecastSeries,
                    borderColor: "#10b981",
                    backgroundColor: "rgba(16, 185, 129, 0.12)",
                    borderWidth: 2.5,
                    borderDash: [5, 5],
                    pointRadius: 4,
                    pointBackgroundColor: "#10b981",
                    tension: 0.25,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: {
                legend: { position: "top" },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            if (context.raw === null || context.raw === undefined) return null;
                            return ` ${context.dataset.label}: $${Number(context.raw).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: { maxTicksLimit: 14 },
                    grid: { display: false }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: "#f1f5f9" },
                    ticks: { callback: (v) => "$" + v.toLocaleString() }
                }
            }
        }
    });
}

function exportForecastToCSV() {
    if (!currentForecastData || !currentForecastData.forecast_results) {
        alert("No forecast data available to export.");
        return;
    }

    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Date,Day,Predicted_Sales\n";

    currentForecastData.forecast_results.forEach(row => {
        csvContent += `${row.date},${row.day_name},${row.predicted_sales}\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `sales_forecast_${currentForecastData.forecast_days}_days.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/* ==========================================================================
   4. SALES DATA PAGE
   ========================================================================== */
function initSalesDataPage() {
    const searchInput = document.getElementById("tableSearchInput");
    const tableBody = document.getElementById("salesDataTableBody");
    if (!searchInput || !tableBody) return;

    searchInput.addEventListener("input", () => {
        const term = searchInput.value.toLowerCase().trim();
        const rows = tableBody.querySelectorAll("tr");

        let visibleCount = 0;
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(term)) {
                row.style.display = "";
                visibleCount++;
            } else {
                row.style.display = "none";
            }
        });

        const counter = document.getElementById("visibleRecordCounter");
        if (counter) counter.textContent = visibleCount;
    });

    // Drag-and-drop file upload UX
    const dropzone = document.getElementById("csvDropzone");
    const fileInput = document.getElementById("csvFileInput");
    if (dropzone && fileInput) {
        dropzone.addEventListener("click", () => fileInput.click());

        fileInput.addEventListener("change", () => {
            if (fileInput.files.length > 0) {
                const fileName = fileInput.files[0].name;
                const label = document.getElementById("dropzoneText");
                if (label) {
                    label.innerHTML = `<strong>Selected file:</strong> ${fileName}`;
                }
            }
        });

        ["dragenter", "dragover"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.add("border-primary", "bg-light");
            });
        });

        ["dragleave", "drop"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.remove("border-primary", "bg-light");
            });
        });

        dropzone.addEventListener("drop", (e) => {
            if (e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                const fileName = e.dataTransfer.files[0].name;
                const label = document.getElementById("dropzoneText");
                if (label) {
                    label.innerHTML = `<strong>Selected file:</strong> ${fileName}`;
                }
            }
        });
    }
}
