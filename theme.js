const root = document.documentElement;

try {
  const saved = localStorage.getItem("theme");
  if (saved) root.dataset.theme = saved;
} catch (error) {}

function currentTheme() {
  if (root.dataset.theme) return root.dataset.theme;
  return matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

function paintTrace() {
  const trace = document.querySelector(".trace object");
  const svg = trace && trace.contentDocument && trace.contentDocument.documentElement;
  if (svg) svg.setAttribute("data-theme", currentTheme());
}

function paintButton(button) {
  const other = currentTheme() === "dark" ? "light" : "dark";
  button.textContent = other;
  button.setAttribute("aria-label", "Switch to " + other + " mode");
}

document.addEventListener("DOMContentLoaded", () => {
  const button = document.querySelector(".theme-toggle");
  const trace = document.querySelector(".trace object");

  paintButton(button);
  paintTrace();
  if (trace) trace.addEventListener("load", paintTrace);

  matchMedia("(prefers-color-scheme: light)").addEventListener("change", () => {
    paintButton(button);
    paintTrace();
  });

  button.addEventListener("click", () => {
    const next = currentTheme() === "dark" ? "light" : "dark";
    root.dataset.theme = next;
    try {
      localStorage.setItem("theme", next);
    } catch (error) {}
    paintButton(button);
    paintTrace();
  });
});
