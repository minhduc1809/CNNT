// Hàm vẽ dùng chung cho các sơ đồ SV1 (SVG thuần, xuất PNG bằng trình duyệt headless)
const NS = "http://www.w3.org/2000/svg";
const C = {
  ink: "#1f2937", sub: "#4b5563", mute: "#9ca3af", line: "#9ca3af", panel: "#f8fafc", border: "#d1d5db",
  flow: "#2563eb", flowBg: "#eff6ff", backup: "#ea580c",
  v30: "#059669", v20: "#d97706", v10: "#2563eb", net: "#7c3aed", db: "#0f766e",
};
const FONT = "'Segoe UI', Arial, sans-serif";
let svg;

function el(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  (parent || svg).appendChild(e);
  return e;
}

function init(w, h) {
  svg = el("svg", { width: w, height: h, viewBox: `0 0 ${w} ${h}`, "font-family": FONT }, document.body);
  const defs = el("defs", {});
  for (const [id, col] of [["aFlow", C.flow], ["aGrey", C.line], ["aBackup", C.backup], ["aInk", C.ink]]) {
    const m = el("marker", { id, viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse" }, defs);
    el("path", { d: "M0,0 L10,5 L0,10 z", fill: col }, m);
  }
  rect(0, 0, w, h, { fill: "#ffffff", stroke: "none" });
}

function rect(x, y, w, h, o = {}) {
  return el("rect", { x, y, width: w, height: h, rx: o.rx ?? 10, fill: o.fill ?? "#fff", stroke: o.stroke ?? C.border,
    "stroke-width": o.sw ?? 1.5, "stroke-dasharray": o.dash ?? "" });
}

function text(x, y, s, o = {}) {
  const t = el("text", { x, y, "font-size": o.size ?? 15, "font-weight": o.weight ?? 400, fill: o.fill ?? C.ink,
    "text-anchor": o.anchor ?? "start", "font-style": o.italic ? "italic" : "normal" });
  t.textContent = s;
  return t;
}

// Thẻ thiết bị: nền trắng, vạch màu bên trái, tiêu đề đậm, các dòng mô tả
function card(x, y, w, h, title, lines, accent, o = {}) {
  rect(x, y, w, h, { fill: o.fill ?? "#fff", stroke: o.stroke ?? C.border, rx: 10 });
  el("rect", { x, y, width: 7, height: h, rx: 3, fill: accent });
  text(x + 20, y + 28, title, { size: o.titleSize ?? 17, weight: 700 });
  lines.forEach((s, i) => text(x + 20, y + 52 + i * (o.lh ?? 21), s, { size: o.size ?? 14, fill: C.sub }));
}

function line(pts, o = {}) {
  const d = pts.map((p, i) => (i ? "L" : "M") + p[0] + "," + p[1]).join(" ");
  return el("path", { d, fill: "none", stroke: o.stroke ?? C.line, "stroke-width": o.sw ?? 2,
    "stroke-dasharray": o.dash ?? "", "marker-end": o.arrow ? `url(#${o.arrow})` : "",
    "marker-start": o.arrowStart ? `url(#${o.arrowStart})` : "", "stroke-linejoin": "round" });
}

// Nhãn có nền trắng đặt trên đường nối
function tag(x, y, s, o = {}) {
  const size = o.size ?? 13;
  const w = s.length * size * 0.55 + 14;
  const ax = o.anchor === "start" ? x : o.anchor === "end" ? x - w : x - w / 2;
  rect(ax, y - size - 3, w, size + 10, { fill: o.bg ?? "#fff", stroke: o.border ?? "none", rx: 5, sw: 1 });
  text(ax + w / 2, y + 1, s, { size, fill: o.fill ?? C.sub, anchor: "middle", weight: o.weight ?? 400 });
}

function badge(x, y, n, col = C.flow) {
  el("circle", { cx: x, cy: y, r: 14, fill: col });
  text(x, y + 5, String(n), { size: 15, weight: 700, fill: "#fff", anchor: "middle" });
}

// Nhãn trạng thái: real = true -> "CHẠY THẬT" (xanh lá), false -> "SƠ ĐỒ + PT" (xám); căn phải tại xr
function pill(xr, y, real, s) {
  s = s ?? (real ? "CHẠY THẬT" : "SƠ ĐỒ + PT");
  const w = s.length * 7.6 + 18;
  rect(xr - w, y, w, 22, { fill: real ? "#16a34a" : "#e5e7eb", stroke: "none", rx: 11 });
  text(xr - w / 2, y + 15.5, s, { size: 11.5, weight: 700, fill: real ? "#fff" : "#4b5563", anchor: "middle" });
}

function heading(x, y, w, s, col) {
  rect(x, y, w, 38, { fill: col, stroke: "none", rx: 8 });
  text(x + w / 2, y + 25, s, { size: 16, weight: 700, fill: "#fff", anchor: "middle" });
}
