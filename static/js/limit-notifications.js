// Check limit status periodically
function setupLimitNotifications() {
  // Check immediately on page load
  checkLimitStatus();

  // Then check every hour
  setInterval(checkLimitStatus, 60 * 60 * 1000);
}

function checkLimitStatus() {
  fetch("/check_limit_status")
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        if (data.status === "danger") {
          showLimitNotification(
            "Warning!",
            `You've used ${Math.round(
              data.percentage
            )}% of your monthly budget.`,
            "danger"
          );
        } else if (data.status === "warning") {
          showLimitNotification(
            "Heads up!",
            `You've used ${Math.round(
              data.percentage
            )}% of your monthly budget.`,
            "warning"
          );
        }
      }
    })
    .catch((error) => {
      console.error("Error checking limit status:", error);
    });
}

function showLimitNotification(title, message, type) {
  // Check if the notification system exists
  if (typeof showNotification === "function") {
    showNotification(title, message, type);
  } else {
    // Create a simple notification if the app doesn't have one
    const notification = document.createElement("div");
    notification.className = `alert alert-${type} notification`;
    notification.innerHTML = `
            <strong>${title}</strong> ${message}
            <button type="button" class="close" onclick="this.parentElement.remove()">
                <span>&times;</span>
            </button>
        `;

    // Style the notification
    notification.style.position = "fixed";
    notification.style.top = "20px";
    notification.style.right = "20px";
    notification.style.zIndex = "9999";
    notification.style.minWidth = "300px";
    notification.style.padding = "15px";
    notification.style.borderRadius = "8px";
    notification.style.boxShadow = "0 4px 12px rgba(0,0,0,0.15)";

    // Add to the document
    document.body.appendChild(notification);

    // Remove after 5 seconds
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 5000);
  }
}

// Initialize when the document is ready
document.addEventListener("DOMContentLoaded", setupLimitNotifications);
