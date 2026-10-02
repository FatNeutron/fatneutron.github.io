const restackButton = document.querySelector(".restack");

restackButton.addEventListener("click", () => {
  const counter = document.querySelector(".days");
  const trace = document.querySelector(".trace object");
  const svg = trace.contentDocument && trace.contentDocument.documentElement;

  counter.style.animation = "none";
  counter.offsetWidth;
  counter.style.animation = "";

  if (svg) svg.setCurrentTime(0);
});
