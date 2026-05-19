async function loadDashboard() {

    try {

        // --------------------------------------------------
        // LIVE DASHBOARD DATA
        // --------------------------------------------------

        const dashboardRes = await fetch("/api/dashboard");
        const data = await dashboardRes.json();

        console.log("Dashboard:", data);

        if (!data) return;

        // Safe UI updates (undgår null crash)
        document.getElementById("recovery-score").innerText =
            data.recovery?.score ?? "--";

        document.getElementById("recovery-status").innerText =
            data.recovery?.status ?? "NO DATA";

        document.getElementById("fatigue-score").innerText =
            data.fatigue?.score ?? "--";

        document.getElementById("fatigue-status").innerText =
            data.fatigue?.status ?? "NO DATA";

        document.getElementById("sleep-hours").innerText =
            data.sleep_hours != null ? data.sleep_hours + " h" : "--";

        document.getElementById("hrv").innerText =
            data.hrv ?? "--";

        document.getElementById("body-battery").innerText =
            data.body_battery ?? "--";

        document.getElementById("resting-hr").innerText =
            data.resting_hr ?? "--";


        // --------------------------------------------------
        // HISTORY DATA (STEP 3A)
        // --------------------------------------------------

        const historyRes = await fetch("/api/history");
        const history = await historyRes.json();

        console.log("History:", history);

        if (!Array.isArray(history) || history.length === 0) {
            console.warn("No history data");
            return;
        }

        // --------------------------------------------------
        // CHART DATA PREPARATION
        // --------------------------------------------------

        const labels = history.map(item =>
            new Date(item.created_at).toLocaleDateString()
        );

        const recoveryData = history.map(item =>
            item.recovery_score ?? null
        );

        const fatigueData = history.map(item =>
            item.fatigue_score ?? null
        );

        const hrvData = history.map(item =>
            item.hrv ?? null
        );


        // --------------------------------------------------
        // CHART RENDER
        // --------------------------------------------------

        const ctx = document.getElementById("recoveryChart");

        if (!ctx) return;

        new Chart(ctx, {

            type: "line",

            data: {

                labels: labels,

                datasets: [

                    {
                        label: "Recovery Score",
                        data: recoveryData,
                        borderColor: "#4ade80",
                        tension: 0.3
                    },

                    {
                        label: "Fatigue Score",
                        data: fatigueData,
                        borderColor: "#f87171",
                        tension: 0.3
                    },

                    {
                        label: "HRV",
                        data: hrvData,
                        borderColor: "#60a5fa",
                        tension: 0.3
                    }
                ]
            },

            options: {

                responsive: true,

                plugins: {
                    legend: {
                        labels: {
                            color: "white"
                        }
                    }
                },

                scales: {
                    x: {
                        ticks: {
                            color: "white"
                        }
                    },
                    y: {
                        ticks: {
                            color: "white"
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error("Dashboard load error:", error);
    }
}


// Auto refresh every 60 sec (optional but powerful)
loadDashboard();
setInterval(loadDashboard, 60000);
