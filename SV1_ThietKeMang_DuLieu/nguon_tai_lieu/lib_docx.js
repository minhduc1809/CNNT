// Hàm dựng docx dùng chung (A4, Times New Roman 13, lề 3-2-2-2 cm)
const fs = require("fs");
const d = require("docx");
const { Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType, HeadingLevel,
  ImageRun, BorderStyle, LevelFormat, Footer, PageNumber, PageBreak, TableOfContents } = d;

const FONT = "Times New Roman";
const W = 9070; // bề rộng vùng chữ (DXA)

function runs(s, base = {}) {
  // **đậm**, `mã`
  const out = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(s))) {
    if (m.index > last) out.push(new TextRun({ text: s.slice(last, m.index), ...base }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, ...base }));
    else out.push(new TextRun({ text: t.slice(1, -1), font: "Consolas", size: (base.size ?? 26) - 4, ...base, bold: base.bold }));
    last = re.lastIndex;
  }
  if (last < s.length) out.push(new TextRun({ text: s.slice(last), ...base }));
  return out;
}

const P = (s, o = {}) => new Paragraph({ children: runs(s, o.run), alignment: o.align ?? AlignmentType.JUSTIFIED,
  spacing: { after: o.after ?? 120, line: 300 }, indent: o.indent, keepNext: o.keepNext });
const H1 = (s) => new Paragraph({ text: s, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 160 }, keepNext: true });
const H2 = (s) => new Paragraph({ text: s, heading: HeadingLevel.HEADING_2, spacing: { before: 220, after: 120 }, keepNext: true });
const B = (s, lvl = 0) => new Paragraph({ children: runs(s), numbering: { reference: "dot", level: lvl }, spacing: { after: 80, line: 300 }, alignment: AlignmentType.JUSTIFIED });
const N = (s, ref = "num") => new Paragraph({ children: runs(s), numbering: { reference: ref, level: 0 }, spacing: { after: 80, line: 300 }, alignment: AlignmentType.JUSTIFIED });
const CODE = (lines) => lines.map((l, i) => new Paragraph({
  children: [new TextRun({ text: l || " ", font: "Consolas", size: 19 })],
  shading: { type: ShadingType.CLEAR, fill: "F3F4F6", color: "auto" }, spacing: { after: i === lines.length - 1 ? 160 : 0, line: 250 },
  indent: { left: 200 } }));
const BREAK = () => new Paragraph({ children: [new PageBreak()] });
const CAP = (s) => new Paragraph({ children: [new TextRun({ text: s, italics: true, size: 22 })], alignment: AlignmentType.CENTER, spacing: { after: 200 } });

function IMG(path, wpx) {
  const buf = fs.readFileSync(path);
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, keepNext: true,
    children: [new ImageRun({ type: "png", data: buf, transformation: { width: wpx, height: Math.round(wpx * h / w) } })] });
}

const border = { style: BorderStyle.SINGLE, size: 4, color: "9CA3AF" };
const borders = { top: border, bottom: border, left: border, right: border };

// headers: mảng tiêu đề; rows: mảng mảng chuỗi; ratio: tỉ lệ cột
function T(headers, rows, ratio, o = {}) {
  const sum = ratio.reduce((a, b) => a + b, 0);
  const widths = ratio.map((r) => Math.floor((W * r) / sum));
  widths[widths.length - 1] += W - widths.reduce((a, b) => a + b, 0);
  const size = o.size ?? 21;
  const cell = (s, i, head, fill) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA }, borders,
    shading: fill ? { type: ShadingType.CLEAR, fill, color: "auto" } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: String(s).split("\n").map((line) => new Paragraph({ children: runs(line, { size, bold: head || undefined }),
      alignment: o.center && o.center.includes(i) ? AlignmentType.CENTER : AlignmentType.LEFT, spacing: { after: 0, line: 260 } })),
  });
  const trs = [new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, i, true, "DCE6F2")) })];
  rows.forEach((r, k) => trs.push(new TableRow({ cantSplit: true, children: r.map((s, i) => cell(s, i, false, o.zebra !== false && k % 2 ? "F8FAFC" : undefined)) })));
  return [new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: widths, rows: trs }), new Paragraph({ spacing: { after: 120 }, children: [] })];
}

function readCsv(path) {
  const txt = fs.readFileSync(path, "utf8").replace(/^﻿/, "");
  const rows = [];
  for (const line of txt.split(/\r?\n/).filter(Boolean)) {
    const cells = []; let cur = "", q = false;
    for (const ch of line) {
      if (ch === '"') q = !q; else if (ch === "," && !q) { cells.push(cur); cur = ""; } else cur += ch;
    }
    cells.push(cur); rows.push(cells);
  }
  const head = rows.shift();
  return rows.map((r) => Object.fromEntries(head.map((h, i) => [h, r[i] ?? ""])));
}

function makeDoc(children, o = {}) {
  return new d.Document({
    creator: o.creator ?? "SV1", title: o.title,
    styles: {
      default: { document: { run: { font: FONT, size: 26 } } },
      paragraphStyles: [
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 30, bold: true, font: FONT, color: "1F3864" }, paragraph: { outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 27, bold: true, font: FONT, color: "2E5597" }, paragraph: { outlineLevel: 1 } },
      ],
    },
    numbering: { config: [
      { reference: "dot", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 500, hanging: 280 } } } },
                                   { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1000, hanging: 280 } } } }] },
      ...["num", "num2", "num3", "num4", "num5"].map((reference) => ({ reference, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 500, hanging: 320 } } } }] })),
    ] },
    sections: [{
      properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1701, right: 1134 } } },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: o.footer ?? "", size: 20, color: "6B7280" }), new TextRun({ children: [PageNumber.CURRENT], size: 20 })] })] }) },
      children,
    }],
    features: { updateFields: !!o.toc },
  });
}

async function save(doc, path) {
  fs.writeFileSync(path, await d.Packer.toBuffer(doc));
}

module.exports = { d, P, H1, H2, B, N, CODE, BREAK, CAP, IMG, T, readCsv, makeDoc, save, runs, W, TableOfContents };
