async function loadDashboard() {

    const response = await fetch("/api/dashboard");

    const data = await response.json();

    console.log(data);

    // Recovery
    document.getElementById("recovery-score").innerText =
        data.recovery.score;

    document.getElementById("recovery-status").innerText =
        data.recovery.status;

    // Fatigue
    document.getElementById("fatigue-score").innerText =
        data.fatigue.score;

    document.getElementById("fatigue-status").innerText =
        data.fatigue.status;

    // Metrics
    document.getElementById("sleep-hours").innerText =
        data.sleep_hours + " h";

    document.getElementById("hrv").innerText =
        data.hrv;

    document.getElementById("body-battery").innerText =
        data.body_battery;

    document.getElementById("resting-hr").innerText =
        data.resting_hr;

    // Chart

    const ctx = document.getElementById("recoveryChart");

    new Chart(ctx, {

        type: "line",

        data: {

            labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],

            datasets: [{
                label: "Recovery",

                data: [62, 58, 70, 64, 55, 68, data.recovery.score]
            }]
        }
    });
}

loadDashboard();
