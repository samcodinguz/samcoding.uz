document.addEventListener("DOMContentLoaded", function () {
  const monthsContainer = document.querySelector(".months");
  if (!monthsContainer) return;

  const yearElement = document.getElementById("contrib-year");
  if (!yearElement) return;

  const year = parseInt(yearElement.dataset.year);

  const monthNames = [
    "Yan",
    "Fev",
    "Mar",
    "Apr",
    "May",
    "Iyn",
    "Iyl",
    "Avg",
    "Sen",
    "Okt",
    "Noy",
    "Dek",
  ];

  function renderMonths() {
    monthsContainer.innerHTML = "";

    const startDate = new Date(year, 0, 1);
    const firstWeekday = startDate.getDay() === 0 ? 6 : startDate.getDay() - 1;

    const firstGridDate = new Date(startDate);
    firstGridDate.setDate(startDate.getDate() - firstWeekday);

    const cellSize = parseInt(
      getComputedStyle(document.documentElement).getPropertyValue(
        "--cell-size",
      ),
    );

    const cellGap = parseInt(
      getComputedStyle(document.documentElement).getPropertyValue("--cell-gap"),
    );

    const weekdaysWidth = document.querySelector(".weekdays").offsetWidth;

    for (let month = 0; month < 12; month++) {
      const date = new Date(year, month, 1);
      const diffDays = Math.floor((date - firstGridDate) / 86400000);
      const weekIndex = Math.floor(diffDays / 7);

      const label = document.createElement("div");
      label.classList.add("month-label");
      label.textContent = monthNames[month];

      label.style.left =
        weekdaysWidth + weekIndex * (cellSize + cellGap) + "px";

      monthsContainer.appendChild(label);
    }
  }

  renderMonths();
  window.addEventListener("resize", renderMonths);
});
