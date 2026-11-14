/* Point & Clickle · title autocomplete. Small, dependency-free, accessible (ARIA 1.2 combobox) replacement for
   typeahead.js. Asks GET <url>?q=<text> (a JSON array of titles) 150 ms after typing stops, cancels the
   request it no longer needs, highlights the words typed and works with mouse, touch and keyboard
   (↑ ↓ to move, Enter or Tab to pick, Esc to close).

   const ac = Autocomplete(input, { url, max: 20 });
   ac.clear();                                   // empty the box and close the list
   input events: "ac:results" (detail.count), "ac:select" (detail.value) */
"use strict";
function Autocomplete(input, opts) {
  opts = Object.assign({ max: 20, delay: 150, minLength: 1 }, opts || {});
  const list = document.createElement("ul");
  const id = (input.id || "ac") + "-list";
  list.id = id;
  list.className = "ac-list";
  list.setAttribute("role", "listbox");
  list.hidden = true;
  input.setAttribute("role", "combobox");
  input.setAttribute("aria-autocomplete", "list");
  input.setAttribute("aria-controls", id);
  input.setAttribute("aria-expanded", "false");
  input.insertAdjacentElement("afterend", list);
  input.parentElement.classList.add("ac-wrap");

  let timer = null, ctrl = null, items = [], active = -1, last = "";

  const esc = s => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  function highlight(text, query) {
    const words = query.trim().split(/\s+/).filter(Boolean).map(w => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
    if (!words.length) return esc(text);
    const re = new RegExp("(" + words.join("|") + ")", "ig");
    return text.split(re).map((part, i) => (i % 2 ? "<mark>" + esc(part) + "</mark>" : esc(part))).join("");
  }
  function close() {
    list.hidden = true;
    input.setAttribute("aria-expanded", "false");
    input.removeAttribute("aria-activedescendant");
    active = -1;
  }
  function setActive(i) {
    const opts_ = list.children;
    if (active >= 0 && opts_[active]) opts_[active].removeAttribute("aria-selected");
    active = i;
    if (i >= 0 && opts_[i]) {
      opts_[i].setAttribute("aria-selected", "true");
      input.setAttribute("aria-activedescendant", opts_[i].id);
      opts_[i].scrollIntoView({ block: "nearest" });
    } else input.removeAttribute("aria-activedescendant");
  }
  function render(titles, query) {
    items = titles.slice(0, opts.max);
    list.innerHTML = items.map((t, i) => '<li role="option" id="' + id + "-" + i + '" class="ac-option">' + highlight(t, query) + "</li>").join("");
    input.dispatchEvent(new CustomEvent("ac:results", { detail: { count: items.length } }));
    if (!items.length) return close();
    list.hidden = false;
    input.setAttribute("aria-expanded", "true");
    active = -1;
  }
  function pick(i) {
    if (i < 0 || i >= items.length) return false;
    input.value = items[i];
    last = input.value;
    close();
    input.dispatchEvent(new CustomEvent("ac:select", { detail: { value: items[i] } }));
    return true;
  }
  async function query(q) {
    if (ctrl) ctrl.abort();
    ctrl = "AbortController" in window ? new AbortController() : null;
    try {
      const r = await fetch(opts.url + "?q=" + encodeURIComponent(q), ctrl ? { signal: ctrl.signal } : {});
      if (!r.ok) return;
      const data = await r.json();
      if (input.value.trim() === q) render(Array.isArray(data) ? data : [], q);
    } catch (e) { /* aborted or offline: keep what is shown */ }
  }

  input.addEventListener("input", () => {
    clearTimeout(timer);
    const q = input.value.trim();
    if (q === last) return;
    last = q;
    if (q.length < opts.minLength) { if (ctrl) ctrl.abort(); return close(); }
    timer = setTimeout(() => query(q), opts.delay);
  });
  /* registered before the game's own key handler: Enter on a highlighted option picks it and stops there */
  input.addEventListener("keydown", e => {
    const open = !list.hidden && items.length;
    if (e.key === "ArrowDown" && open) { e.preventDefault(); setActive((active + 1) % items.length); }
    else if (e.key === "ArrowUp" && open) { e.preventDefault(); setActive(active <= 0 ? items.length - 1 : active - 1); }
    else if ((e.key === "Enter" || e.key === "Tab") && open && active >= 0) {
      e.preventDefault(); e.stopImmediatePropagation(); pick(active);
    } else if (e.key === "Escape" && open) { e.preventDefault(); close(); }
  });
  /* pointerdown, not click: picks before the input loses focus, also on touch screens */
  list.addEventListener("pointerdown", e => {
    const li = e.target.closest(".ac-option");
    if (!li) return;
    e.preventDefault();
    pick([].indexOf.call(list.children, li));
  });
  list.addEventListener("pointermove", e => {
    const li = e.target.closest(".ac-option");
    if (li) setActive([].indexOf.call(list.children, li));
  });
  input.addEventListener("blur", () => setTimeout(close, 120));
  input.addEventListener("focus", () => { if (items.length && input.value.trim() === last && last) { list.hidden = false; input.setAttribute("aria-expanded", "true"); } });

  return {
    clear() { clearTimeout(timer); if (ctrl) ctrl.abort(); input.value = ""; last = ""; items = []; list.innerHTML = ""; close(); },
    close: close,
  };
}
