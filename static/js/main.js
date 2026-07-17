/*
 * Minimal JavaScript for the Smart Network Firewall project.
 * Currently used for small UI helpers only.
 */

document.addEventListener("DOMContentLoaded", function () {
    // Auto-hide flash alerts after a few seconds
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach(function (alertBox) {
        setTimeout(function () {
            // Bootstrap's Alert API removes the element cleanly
            const instance = bootstrap.Alert.getOrCreateInstance(alertBox);
            instance.close();
        }, 5000);
    });
});
