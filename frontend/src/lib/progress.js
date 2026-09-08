/** Renders a simple progress bar + step list into `container`. */
export function renderProgress(container, { progress, steps, currentStepId }) {
  const pct = progress.total === 0 ? 0 : Math.round((progress.completed / progress.total) * 100);

  container.innerHTML = "";

  const barTrack = document.createElement("div");
  barTrack.className = "h-2 w-full overflow-hidden rounded-full bg-slate-200";
  const barFill = document.createElement("div");
  barFill.className = "h-full rounded-full bg-slate-900 transition-all";
  barFill.style.width = `${pct}%`;
  barTrack.append(barFill);

  const caption = document.createElement("p");
  caption.className = "mt-2 text-xs text-slate-500";
  caption.textContent = `${progress.completed} of ${progress.total} steps complete`;

  const list = document.createElement("ol");
  list.className = "mt-4 flex flex-col gap-1 text-sm";
  for (const step of steps) {
    const item = document.createElement("li");
    const isCurrent = step.id === currentStepId;
    const marker = step.status === "completed" ? "✓" : isCurrent ? "→" : "○";
    item.className = `flex items-center gap-2 ${
      step.status === "completed"
        ? "text-slate-400 line-through"
        : isCurrent
          ? "font-medium text-slate-900"
          : "text-slate-500"
    }`;
    item.textContent = `${marker} ${step.title}`;
    list.append(item);
  }

  container.append(barTrack, caption, list);
}
