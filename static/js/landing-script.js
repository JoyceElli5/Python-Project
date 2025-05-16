document.addEventListener("DOMContentLoaded", function () {
  AOS.init({
    once: false, // whether animation should happen only once - while scrolling down
    mirror: false, // whether elements should animate out while scrolling past them
    // disable: "mobile", // accepts: 'phone', 'tablet', 'mobile', boolean, expression or function
  });

  // Make the chart bars interactive
  const months = document.querySelectorAll(".month");
  const tooltip = document.getElementById("tooltip");

  months.forEach((month) => {
    month.addEventListener("mouseenter", function () {
      // Remove active class from all months
      months.forEach((m) => m.classList.remove("active"));

      // Add active class to current month
      this.classList.add("active");

      // If this is August, show the tooltip
      if (this.querySelector("span").textContent === "Aug") {
        tooltip.style.display = "block";
      } else {
        tooltip.style.display = "none";
      }
    });
  });

  // Make the category pills interactive
  const pills = document.querySelectorAll(".pill");

  pills.forEach((pill) => {
    pill.addEventListener("click", function () {
      // Toggle active class
      this.classList.toggle("active");
    });
  });

  // Make the period selector interactive
  const periodSelector = document.getElementById("period");

  periodSelector.addEventListener("change", function () {
    // In a real app, this would update the chart data
    console.log("Period changed to:", this.value);
  });

  // Add hover effect to buttons
  const buttons = document.querySelectorAll(".btn");

  buttons.forEach((button) => {
    button.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-2px)";
    });

    button.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0)";
    });
  });

  // Initialize with August as active month
  const augustMonth = Array.from(months).find(
    (month) => month.querySelector("span").textContent === "Aug"
  );

  if (augustMonth) {
    augustMonth.classList.add("active");
    tooltip.style.display = "block";
  }
});
