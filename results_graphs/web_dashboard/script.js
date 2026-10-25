
document.addEventListener("DOMContentLoaded", () => {
    const csvFile = document.getElementById("csvFile");
    const historyBody = document.getElementById("historyBody");
    const loadMessage = document.getElementById("loadMessage");

    const elements = {
        total: document.getElementById("totalRecords"),
        mostPredicted: document.getElementById("mostPredicted"),
        averageConfidence: document.getElementById("avgConfidence"),
        lowConfidence: document.getElementById("lowConfidence")
    };

    const charts = {};
    let autoRefreshEnabled = true;
    let lastSource = "server";

    function setText(element, value) {
        if (element) element.textContent = value;
    }

    function showMessage(message) {
        setText(loadMessage, message);
    }

    // Parse CSV while supporting quoted values and commas.
    function parseCSV(text) {
        const rows = [];
        let row = [];
        let value = "";
        let quoted = false;

        text = text.replace(/^\uFEFF/, "");

        for (let i = 0; i < text.length; i++) {
            const ch = text[i];

            if (ch === '"') {
                if (quoted && text[i + 1] === '"') {
                    value += '"';
                    i++;
                } else {
                    quoted = !quoted;
                }
            } else if (ch === "," && !quoted) {
                row.push(value.trim());
                value = "";
            } else if ((ch === "\n" || ch === "\r") && !quoted) {
                if (ch === "\r" && text[i + 1] === "\n") i++;

                row.push(value.trim());

                if (row.some(cell => cell !== "")) {
                    rows.push(row);
                }

                row = [];
                value = "";
            } else {
                value += ch;
            }
        }

        row.push(value.trim());

        if (row.some(cell => cell !== "")) {
            rows.push(row);
        }

        if (rows.length < 2) {
            throw new Error("The CSV contains no data rows.");
        }

        const headers = rows[0].map(header =>
            header.trim().toLowerCase().replace(/^\uFEFF/, "")
        );

        return rows.slice(1).map(cells => {
            const record = {};

            headers.forEach((header, index) => {
                record[header] = (cells[index] || "").trim();
            });

            return record;
        });
    }

    function getValue(record, names) {
        for (const name of names) {
            const value = record[name.toLowerCase()];

            if (value !== undefined && value !== "") {
                return value;
            }
        }

        return "";
    }

    function getNumber(record, names) {
        const value = getValue(record, names);
        if (value === "") return null;

        const number = Number(value);
        return Number.isFinite(number) ? number : null;
    }

    function getDevice(record) {
        return getValue(record, [
            "device",
            "predicted_device",
            "prediction",
            "label"
        ]) || "Unknown";
    }

    function getConfidence(record) {
        let value = getNumber(record, [
            "confidence",
            "confidence_score",
            "prediction_confidence"
        ]);

        if (value === null) return null;
        if (value >= 0 && value <= 1) value *= 100;

        return Math.max(0, Math.min(100, value));
    }

    function formatNumber(value, decimals = 1) {
        if (value === null || !Number.isFinite(value)) return "N/A";

        return value.toLocaleString("en-IN", {
            maximumFractionDigits: decimals
        });
    }

    function average(values) {
        const valid = values.filter(value =>
            value !== null && Number.isFinite(value)
        );

        if (!valid.length) return null;

        return valid.reduce((sum, value) => sum + value, 0) /
            valid.length;
    }

    // Summary cards.
    function updateStats(data) {
        setText(elements.total, data.length.toLocaleString("en-IN"));

        const counts = {};

        data.forEach(record => {
            const device = getDevice(record);
            counts[device] = (counts[device] || 0) + 1;
        });

        const ranked = Object.entries(counts)
            .sort((a, b) => b[1] - a[1]);

        setText(
            elements.mostPredicted,
            ranked.length ? `${ranked[0][0]} (${ranked[0][1]})` : "N/A"
        );

        const confidences = data.map(getConfidence).filter(
            value => value !== null
        );

        const avg = average(confidences);

        setText(
            elements.averageConfidence,
            avg === null ? "N/A" : `${formatNumber(avg)}%`
        );

        setText(
            elements.lowConfidence,
            confidences.filter(value => value < 70).length
                .toLocaleString("en-IN")
        );
    }

    // Analytics charts.
    function drawChart(canvasId, label, values, color, yLabel) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        if (typeof Chart === "undefined") {
            showMessage("Chart.js is unavailable. Check your internet connection.");
            return;
        }

        if (charts[canvasId]) charts[canvasId].destroy();

        charts[canvasId] = new Chart(canvas, {
            type: "line",
            data: {
                labels: values.map((_, index) => index + 1),
                datasets: [{
                    label,
                    data: values,
                    borderColor: color,
                    backgroundColor: color + "22",
                    borderWidth: 2,
                    pointRadius: values.length > 100 ? 0 : 3,
                    pointHoverRadius: 5,
                    fill: true,
                    tension: 0.25,
                    spanGaps: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: "index"
                },
                plugins: {
                    legend: {
                        labels: {
                            color: "#cbd5e1",
                            usePointStyle: true
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: "Record number",
                            color: "#8b9bb5"
                        },
                        ticks: {
                            color: "#8b9bb5",
                            maxTicksLimit: 8
                        },
                        grid: { color: "#26334c" }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: yLabel,
                            color: "#8b9bb5"
                        },
                        ticks: { color: "#8b9bb5" },
                        grid: { color: "#26334c" }
                    }
                }
            }
        });
    }

    function updateCharts(data) {
        drawChart(
            "packetChart",
            "Packet Size",
            data.map(record => getNumber(record, [
                "packet_size", "size", "avg_packet_size"
            ])),
            "#60a5fa",
            "Bytes"
        );

        drawChart(
            "iatChart",
            "Inter-Arrival Time",
            data.map(record => getNumber(record, [
                "iat_ms", "iat", "inter_arrival_time",
                "inter_arrival_time_ms"
            ])),
            "#a78bfa",
            "Milliseconds"
        );

        drawChart(
            "frequencyChart",
            "Frame Frequency",
            data.map(record => getNumber(record, [
                "frequency", "frames_per_sec",
                "frames_per_second", "frame_frequency"
            ])),
            "#34d399",
            "Frames per second"
        );

        drawChart(
            "confidenceChart",
            "Prediction Confidence",
            data.map(getConfidence),
            "#fbbf24",
            "Confidence (%)"
        );
    }

    // Safely build detection history.
    function addHistoryRow(record) {
        const row = document.createElement("tr");

        const timestamp = getValue(record, [
            "timestamp", "time", "datetime", "date"
        ]) || "N/A";

        const device = getDevice(record);

        const packetSize = getNumber(record, ["packet_size", "size"]);
        const iat = getNumber(record, [
            "iat_ms", "iat", "inter_arrival_time",
            "inter_arrival_time_ms"
        ]);
        const frequency = getNumber(record, [
            "frequency", "frames_per_sec",
            "frames_per_second", "frame_frequency"
        ]);
        const confidence = getConfidence(record);

        const status = getValue(record, ["status", "result"]) ||
            (confidence !== null && confidence < 70
                ? "LOW CONFIDENCE"
                : "RECORDED");

        const values = [
            timestamp,
            device,
            packetSize === null ? "N/A" : formatNumber(packetSize),
            iat === null ? "N/A" : formatNumber(iat),
            frequency === null ? "N/A" : formatNumber(frequency),
            confidence === null ? "N/A" : `${formatNumber(confidence)}%`
        ];

        values.forEach(value => {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });

        const statusCell = document.createElement("td");
        const pill = document.createElement("span");
        pill.className = "status-pill";

        if (confidence !== null && confidence < 70) {
            pill.classList.add("low");
        } else if (confidence !== null) {
            pill.classList.add("good");
        }

        pill.textContent = status;
        statusCell.appendChild(pill);
        row.appendChild(statusCell);

        historyBody.appendChild(row);
    }

    function updateHistory(data) {
        if (!historyBody) return;

        historyBody.replaceChildren();

        const groups = [
            {
                title: "LAPTOP RECORDS",
                records: data.filter(
                    r => getDevice(r).toLowerCase() === "laptop"
                ).slice(-15).reverse()
            },
            {
                title: "PHONE RECORDS",
                records: data.filter(
                    r => getDevice(r).toLowerCase() === "phone"
                ).slice(-15).reverse()
            },
            {
                title: "OTHER DEVICE RECORDS",
                records: data.filter(r => {
                    const d = getDevice(r).toLowerCase();
                    return d !== "laptop" && d !== "phone";
                }).slice(-15).reverse()
            }
        ];

        groups.forEach(group => {
            if (!group.records.length) return;

            const headingRow = document.createElement("tr");
            const headingCell = document.createElement("td");

            headingCell.colSpan = 7;
            headingCell.textContent =
                `${group.title} (${group.records.length} shown)`;
            headingCell.style.fontWeight = "700";
            headingCell.style.color = "#a78bfa";
            headingCell.style.background = "#18243a";

            headingRow.appendChild(headingCell);
            historyBody.appendChild(headingRow);

            group.records.forEach(addHistoryRow);
        });

        if (!groups.some(group => group.records.length)) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 7;
            cell.className = "empty-state";
            cell.textContent = "No device records found.";

            row.appendChild(cell);
            historyBody.appendChild(row);
        }
    }

    function renderData(data) {
        updateStats(data);
        updateCharts(data);
        updateHistory(data);
    }

    // Manual CSV upload remains available.
    if (csvFile) {
        csvFile.addEventListener("change", async event => {
            const file = event.target.files && event.target.files[0];
            if (!file) return;

            if (!file.name.toLowerCase().endsWith(".csv")) {
                showMessage("Please select a CSV file.");
                return;
            }

            try {
                autoRefreshEnabled = false;
                lastSource = "csv";

                const data = parseCSV(await file.text());
                renderData(data);

                showMessage(
                    `Loaded ${data.length} records from ${file.name}. ` +
                    "Automatic server refresh paused while using this CSV."
                );
            } catch (error) {
                showMessage(`Could not load CSV: ${error.message}`);
            }
        });
    }

    // Fetch latest saved records from Flask.
    async function refreshFromServer() {
        if (!autoRefreshEnabled || lastSource === "csv") return;

        try {
            const response = await fetch("/api/detections", {
                cache: "no-store"
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            if (!Array.isArray(data)) {
                throw new Error("Unexpected API response");
            }

            lastSource = "server";
            renderData(data);

            showMessage(
                `Auto-refresh active: ${data.length} saved records. ` +
                `Last update: ${new Date().toLocaleTimeString()}. ` +
                "Data comes from detections.csv; ESP32 live capture is not connected yet."
            );
        } catch (error) {
            console.error("Automatic refresh failed:", error);
            showMessage(`Server refresh failed: ${error.message}`);
        }
    }

    refreshFromServer();
    setInterval(refreshFromServer, 3000);

    console.log("DeviceGuard dashboard initialized.");
});
