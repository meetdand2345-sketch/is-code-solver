/* IS Code Solver — front-end logic */

let LANG = "en";
let PROBLEM_TYPES = [];
let CODES = [];

/* ---- UI strings -------------------------------------------------------- */
const UI = {
  en: {
    ask_label: "Type your engineering question",
    ask_btn: "Solve",
    ask_hint: "Mention the member and the values you know (e.g. b=300, fck=25, Mu=120 kNm).",
    tools_label: "Choose a design problem",
    tools_btn: "Compute",
    examples_label: "Try:",
    lib_intro: "The codes this app draws on. Each entry links to a public reference copy and to the official BIS source.",
    app_title: "IS Code Solver",
    app_subtitle: "Structural & RCC problems, solved with IS code references",
    tab_ask: "Ask a Question",
    tab_tools: "Design Tools",
    tab_library: "IS Code Library",
    footer_note: "Reference tool for study & preliminary design. Always verify against the current BIS code. Not a substitute for a licensed engineer.",
    inputs: "Inputs",
    steps: "Solution steps",
    references: "IS code references",
    need: "More information needed",
    fill_hint: "Fill these values (in the Design Tools tab) to get the full solution:",
    no_match: "No matching problem type.",
    solving: "Solving…",
    loading: "Loading…",
  },
  hi: {
    ask_label: "अपना अभियांत्रिकी प्रश्न लिखें",
    ask_btn: "हल करें",
    ask_hint: "सदस्य तथा ज्ञात मान लिखें (जैसे b=300, fck=25, Mu=120 kNm)।",
    tools_label: "अभिकल्प समस्या चुनें",
    tools_btn: "परिकलन करें",
    examples_label: "आज़माएँ:",
    lib_intro: "इस ऐप में प्रयुक्त संहिताएँ। प्रत्येक प्रविष्टि सार्वजनिक संदर्भ प्रति तथा आधिकारिक BIS स्रोत से जुड़ी है।",
    app_title: "IS कोड सॉल्वर",
    app_subtitle: "संरचनात्मक एवं RCC समस्याएँ, IS कोड संदर्भों के साथ हल",
    tab_ask: "प्रश्न पूछें",
    tab_tools: "अभिकल्प उपकरण",
    tab_library: "IS कोड पुस्तकालय",
    footer_note: "अध्ययन एवं प्रारंभिक अभिकल्प हेतु संदर्भ उपकरण। सदैव वर्तमान BIS संहिता से सत्यापित करें। यह लाइसेंस प्राप्त अभियंता का विकल्प नहीं है।",
    inputs: "निविष्टियाँ",
    steps: "हल के चरण",
    references: "IS कोड संदर्भ",
    need: "अधिक जानकारी आवश्यक",
    fill_hint: "पूर्ण हल हेतु ये मान भरें (अभिकल्प उपकरण टैब में):",
    no_match: "कोई मेल खाती समस्या नहीं मिली।",
    solving: "हल हो रहा है…",
    loading: "लोड हो रहा है…",
  },
};

function ui(key) { return (UI[LANG] && UI[LANG][key]) || UI.en[key] || key; }

/* pick a bilingual field */
function L(obj) {
  if (obj == null) return "";
  if (typeof obj === "string") return obj;
  return obj[LANG] || obj.en || "";
}

/* ---- language ---------------------------------------------------------- */
function setLang(lang) {
  LANG = lang;
  document.documentElement.lang = lang === "hi" ? "hi" : "en";
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = ui(el.getAttribute("data-i18n"));
  });
  document.getElementById("lang-en").classList.toggle("active", lang === "en");
  document.getElementById("lang-hi").classList.toggle("active", lang === "hi");
  // re-render dynamic sections in the new language
  renderForm();
  renderLibrary();
  const ar = document.getElementById("ask-result");
  const tr = document.getElementById("tool-result");
  if (ar.dataset.raw) ar.innerHTML = renderSolution(JSON.parse(ar.dataset.raw));
  if (tr.dataset.raw) tr.innerHTML = renderSolution(JSON.parse(tr.dataset.raw));
}

/* ---- tabs -------------------------------------------------------------- */
function showTab(name) {
  document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.tab === name));
  document.getElementById("panel-" + name).classList.add("active");
}

function fillExample(btn) {
  document.getElementById("question").value = btn.textContent.trim();
  showTab("ask");
  askQuestion();
}

/* ---- initial load ------------------------------------------------------ */
async function boot() {
  setLang("en");
  try {
    const [pt, cd] = await Promise.all([
      fetch("/api/problem-types").then((r) => r.json()),
      fetch("/api/codes").then((r) => r.json()),
    ]);
    PROBLEM_TYPES = pt.problem_types || [];
    CODES = cd.codes || [];
    const sel = document.getElementById("ptype");
    sel.innerHTML = PROBLEM_TYPES.map((p) => `<option value="${p.id}">${L(p.title)}</option>`).join("");
    renderForm();
    renderLibrary();
  } catch (e) {
    console.error(e);
  }
}

/* ---- design tools form ------------------------------------------------- */
function renderForm() {
  const sel = document.getElementById("ptype");
  const pt = PROBLEM_TYPES.find((p) => p.id === sel.value) || PROBLEM_TYPES[0];
  if (!pt) return;
  const area = document.getElementById("form-area");
  area.innerHTML = pt.fields.map((f) => {
    const label = `${L(f.label)}${f.unit ? ` <span class="unit">(${f.unit})</span>` : ""}`;
    const req = f.required ? "" : " (opt.)";
    if (f.type === "select") {
      const opts = (f.options || []).map((o) => `<option value="${o.value}">${L(o.label)}</option>`).join("");
      return `<div class="form-field"><label>${label}${req}</label><select id="in-${f.name}">${opts}</select></div>`;
    }
    return `<div class="form-field"><label>${label}${req}</label><input id="in-${f.name}" type="number" step="any" /></div>`;
  }).join("");
}

async function runTool() {
  const pt = document.getElementById("ptype").value;
  const pdef = PROBLEM_TYPES.find((p) => p.id === pt);
  const inputs = {};
  pdef.fields.forEach((f) => {
    const el = document.getElementById("in-" + f.name);
    if (el && el.value !== "") inputs[f.name] = el.value;
  });
  const out = document.getElementById("tool-result");
  out.innerHTML = `<div class="card">${ui("solving")}</div>`;
  try {
    const res = await fetch("/api/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: pt, inputs, lang: LANG }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error");
    out.dataset.raw = JSON.stringify(data);
    out.innerHTML = renderSolution(data);
  } catch (e) {
    out.innerHTML = `<div class="warnings"><b>${ui("no_match")}</b><br>${e.message}</div>`;
  }
}

/* ---- ask --------------------------------------------------------------- */
async function askQuestion() {
  const q = document.getElementById("question").value.trim();
  const out = document.getElementById("ask-result");
  if (!q) return;
  out.innerHTML = `<div class="card">${ui("solving")}</div>`;
  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q, lang: LANG }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error");
    out.dataset.raw = JSON.stringify(data);
    out.innerHTML = renderSolution(data);
  } catch (e) {
    out.innerHTML = `<div class="warnings"><b>${ui("no_match")}</b><br>${e.message}</div>`;
  }
}

/* ---- solution renderer ------------------------------------------------- */
function renderSolution(d) {
  // "no_match" / "need_inputs" responses
  if (d.status === "need_inputs") {
    const fields = (d.missing_fields || [])
      .map((f) => `<li>${L(f.label)}${f.unit ? ` (${f.unit})` : ""}</li>`)
      .join("");
    return `<div class="card">
      <div class="solution-head"><h2>${L(d.title)}</h2></div>
      <div class="summary">${L(d.message)}</div>
      <div class="warnings"><b>${ui("need")}</b>
        <p>${ui("fill_hint")}</p><ul>${fields}</ul></div>
      <button class="primary" onclick="showTab('tools')">${ui("tab_tools")}</button>
    </div>`;
  }
  if (d.status === "no_match") {
    return `<div class="card">
      <div class="warnings"><b>${ui("no_match")}</b><p>${L(d.message)}</p></div>
    </div>`;
  }

  // full solution
  const inputs = (d.inputs || []).map((i) =>
    `<div class="input-pill"><b>${L(i.label)}</b>${i.value} ${i.unit || ""}</div>`).join("");

  const warnings = (d.warnings && d.warnings.length)
    ? `<div class="warnings"><b>⚠</b><ul>${d.warnings.map((w) => `<li>${L(w)}</li>`).join("")}</ul></div>`
    : "";

  const mixTable = (d.mix_table && d.mix_table.length)
    ? `<div class="field-label">${LANG === 'hi' ? 'मात्राएँ (प्रति घन मीटर)' : 'Quantities (per m³)'}</div>
       <div class="inputs-grid">${d.mix_table.map((r) => `<div class="input-pill"><b>${escapeHtml(L(r.item))}</b>${r.value} ${r.unit || ''}</div>`).join('')}</div>`
    : "";

  const steps = (d.steps || []).map((s) => {
    const formula = s.formula ? `<div class="formula">${escapeHtml(s.formula)}</div>` : "";
    const subst = s.substitution ? `<div class="subst">${escapeHtml(L(s.substitution))}</div>` : "";
    const result = s.result ? `<div class="step-result">${escapeHtml(L(s.result))}</div>` : "";
    const refs = (s.references || []).map(refChip).join("");
    const refBlock = refs ? `<div class="refs">${refs}</div>` : "";
    return `<div class="step">
      <div class="step-head"><span class="step-num">${s.n}</span>${escapeHtml(L(s.title))}</div>
      ${formula}${subst}${result}${refBlock}
    </div>`;
  }).join("");

  return `<div class="card">
    <div class="solution-head"><h2>${escapeHtml(L(d.title))}</h2></div>
    <div class="summary">${escapeHtml(L(d.summary))}</div>
    ${warnings}
    <div class="field-label">${ui("inputs")}</div>
    <div class="inputs-grid">${inputs}</div>
    ${mixTable}
    <div class="field-label">${ui("steps")}</div>
    ${steps}
  </div>`;
}

function refChip(r) {
  const num = r.code_number || r.code || "";
  const cl = r.clause ? ` Cl. ${r.clause}` : "";
  const tbl = r.table ? ` (${r.table})` : "";
  const label = `${num}${cl}${tbl}`;
  const link = (r.links && r.links[0] && r.links[0].url) || "#";
  const note = r.note ? `<div class="ref-note">${escapeHtml(L(r.note))}</div>` : "";
  return `<a class="ref-chip" href="${link}" target="_blank" rel="noopener" title="${escapeHtml(label)}">📄 ${escapeHtml(label)}</a>${note}`;
}

/* ---- library ----------------------------------------------------------- */
function renderLibrary() {
  const box = document.getElementById("library");
  if (!box) return;
  box.innerHTML = CODES.map((c) => {
    const links = (c.links || []).map((l) =>
      `<a class="${l.kind}" href="${l.url}" target="_blank" rel="noopener">${L(l.label)}</a>`).join("");
    const clauses = (c.clauses || []).map((cl) =>
      `<div class="clause"><b>Cl. ${cl.number} — ${escapeHtml(L(cl.title))}</b><p>${escapeHtml(L(cl.summary))}</p></div>`).join("");
    return `<div class="code-card">
      <h3>${escapeHtml(c.number)}</h3>
      <div class="code-meta">${escapeHtml(L(c.title))} · ${escapeHtml(c.revision || "")} · ${escapeHtml(c.committee || "")}</div>
      <div class="code-scope">${escapeHtml(L(c.scope))}</div>
      <div class="code-links">${links}</div>
      <div class="clause-list">${clauses}</div>
    </div>`;
  }).join("");
}

function escapeHtml(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

boot();
