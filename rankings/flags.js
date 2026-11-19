/* State flags, drawn as simplified SVG in a 300x200 box. Geometric flags are drawn
   faithfully; flags built around a detailed state seal show the field color with a
   simplified seal. Each entry: field (main flag color), accent (UI color), draw(). */
const FLAGS = (() => {
  const R = (x, y, w, h, f) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${f}"/>`;
  const C = (cx, cy, r, f, extra = "") => `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${f}" ${extra}/>`;
  const P = (pts, f) => `<polygon points="${pts}" fill="${f}"/>`;
  const star = (cx, cy, r, f, n = 5, inner = 0.382, rot = -90) => {
    const p = [];
    for (let i = 0; i < n * 2; i++) {
      const rr = i % 2 ? r * inner : r, a = (rot + i * 180 / n) * Math.PI / 180;
      p.push(`${(cx + rr * Math.cos(a)).toFixed(1)},${(cy + rr * Math.sin(a)).toFixed(1)}`);
    }
    return P(p.join(" "), f);
  };
  const ring = (cx, cy, rad, n, r, f) => Array.from({ length: n }, (_, i) => {
    const a = (i / n) * 2 * Math.PI - Math.PI / 2;
    return star(cx + rad * Math.cos(a), cy + rad * Math.sin(a), r, f);
  }).join("");
  const seal = (cx, cy, r, ring_, field) =>
    C(cx, cy, r, ring_) + C(cx, cy, r * 0.82, field) +
    `<circle cx="${cx}" cy="${cy}" r="${r * 0.66}" fill="none" stroke="${ring_}" stroke-width="2"/>` +
    star(cx, cy - r * 0.08, r * 0.3, ring_);
  const sealFlag = (field, ringC, accent, opts = {}) => ({
    field, accent,
    draw: () => R(0, 0, 300, 200, field) + (opts.under || "") + seal(opts.x ?? 150, opts.y ?? 100, opts.r ?? 52, ringC, opts.inner ?? field),
  });
  const unionJack = (x, y, w, h) =>
    `<svg x="${x}" y="${y}" width="${w}" height="${h}" viewBox="0 0 60 30" preserveAspectRatio="none">` +
    `<rect width="60" height="30" fill="#012169"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/>` +
    `<path d="M0,0 L60,30 M60,0 L0,30" stroke="#C8102E" stroke-width="2"/><path d="M30,0 v30 M0,15 h60" stroke="#fff" stroke-width="10"/>` +
    `<path d="M30,0 v30 M0,15 h60" stroke="#C8102E" stroke-width="6"/></svg>`;

  const BLUE = "#002868", RED = "#BF0A30", WHITE = "#FFFFFF", GOLD = "#FFC72C", NAVY = "#0B2A5B";

  return {
    AL: { field: "#9E1B32", accent: "#9E1B32", draw: () => R(0, 0, 300, 200, WHITE) +
      `<path d="M0,0 L300,200 M300,0 L0,200" stroke="#9E1B32" stroke-width="38"/>` },
    AK: { field: "#0F204B", accent: "#B8860B", draw: () => R(0, 0, 300, 200, "#0F204B") +
      [[48, 160], [82, 150], [104, 128], [132, 118], [178, 132], [202, 104], [160, 92]].map(([x, y]) => star(x, y, 10, GOLD)).join("") +
      star(256, 42, 17, GOLD) },
    AZ: { field: BLUE, accent: "#CE5C17", draw: () => {
      let s = R(0, 0, 300, 200, BLUE);
      for (let i = 0; i < 13; i++) {
        const a1 = Math.PI + (i / 13) * Math.PI, a2 = Math.PI + ((i + 1) / 13) * Math.PI;
        s += P(`150,100 ${150 + 400 * Math.cos(a1)},${100 + 400 * Math.sin(a1)} ${150 + 400 * Math.cos(a2)},${100 + 400 * Math.sin(a2)}`, i % 2 ? GOLD : RED);
      }
      return s + R(0, 100, 300, 100, BLUE) + star(150, 100, 34, "#CE5C17");
    } },
    AR: { field: RED, accent: RED, draw: () => R(0, 0, 300, 200, RED) +
      P("150,22 262,100 150,178 38,100", BLUE) + P("150,34 245,100 150,166 55,100", WHITE) +
      [[150, 70], [120, 116], [180, 116]].map(([x, y]) => star(x, y, 13, BLUE)).join("") + star(150, 94, 11, BLUE) },
    CA: { field: "#B22234", accent: "#B22234", draw: () => R(0, 0, 300, 200, WHITE) + R(0, 172, 300, 28, "#B22234") +
      star(42, 36, 18, "#B22234") + R(60, 150, 180, 6, "#3E7B3A") +
      `<g fill="#6B4423"><ellipse cx="150" cy="118" rx="62" ry="26"/><ellipse cx="206" cy="98" rx="20" ry="15"/>` +
      `<rect x="102" y="128" width="14" height="24" rx="5"/><rect x="128" y="132" width="14" height="20" rx="5"/>` +
      `<rect x="164" y="132" width="14" height="20" rx="5"/><rect x="188" y="124" width="14" height="28" rx="5"/></g>` },
    CO: { field: BLUE, accent: RED, draw: () => R(0, 0, 300, 200, BLUE) + R(0, 66.7, 300, 66.7, WHITE) +
      `<path d="M158,62 A48,48 0 1,0 158,138" fill="none" stroke="#BF0A30" stroke-width="30"/>` + C(130, 100, 26, GOLD) },
    CT: sealFlag("#0F2D6B", WHITE, "#0F2D6B"),
    DE: { field: "#46699B", accent: "#46699B", draw: () => R(0, 0, 300, 200, "#46699B") +
      P("150,42 222,100 150,158 78,100", "#E6D3A8") + C(150, 100, 22, "#46699B") },
    FL: { field: "#C8102E", accent: "#C8102E", draw: () => R(0, 0, 300, 200, WHITE) +
      `<path d="M0,0 L300,200 M300,0 L0,200" stroke="#C8102E" stroke-width="30"/>` + seal(150, 100, 34, "#B8860B", "#7FB3D5") },
    GA: { field: "#B22234", accent: "#B22234", draw: () => R(0, 0, 300, 200, "#B22234") + R(0, 66.7, 300, 66.7, WHITE) +
      R(0, 0, 112, 133.3, BLUE) + ring(56, 66.7, 42, 13, 6, WHITE) + C(56, 66.7, 26, "#C9A227") },
    HI: { field: "#012169", accent: "#C8102E", draw: () =>
      Array.from({ length: 8 }, (_, i) => R(0, i * 25, 300, 25, [WHITE, "#C8102E", "#012169"][i % 3])).join("") + unionJack(0, 0, 150, 100) },
    ID: sealFlag(BLUE, GOLD, "#B8860B"),
    IL: sealFlag(WHITE, "#1F3B73", "#1F3B73", { inner: "#E9EEF6" }),
    IN: { field: BLUE, accent: "#B8860B", draw: () => R(0, 0, 300, 200, BLUE) + ring(150, 104, 62, 13, 7, GOLD) +
      ring(150, 104, 36, 5, 6, GOLD) + star(150, 30, 11, GOLD) + R(144, 92, 12, 54, GOLD) +
      `<path d="M150,62 C140,76 142,88 150,92 C158,88 160,76 150,62Z" fill="${GOLD}"/>` },
    IA: { field: BLUE, accent: "#C8102E", draw: () => R(0, 0, 100, 200, BLUE) + R(100, 0, 100, 200, WHITE) + R(200, 0, 100, 200, "#C8102E") +
      `<path d="M112,96 Q150,62 188,96 Q160,86 150,104 Q140,86 112,96Z" fill="#3B2A1A"/>` + R(118, 112, 64, 12, "#C8102E") },
    KS: sealFlag("#003F87", GOLD, "#B8860B"),
    KY: sealFlag(NAVY, GOLD, "#B8860B"),
    LA: { field: "#002A86", accent: "#B8860B", draw: () => R(0, 0, 300, 200, "#002A86") +
      `<g fill="${WHITE}"><ellipse cx="150" cy="104" rx="46" ry="22"/><path d="M120,96 Q102,60 126,52 Q142,50 140,66 Q128,62 128,84Z"/>` +
      `<path d="M126,52 L104,60 L126,58Z"/><rect x="104" y="138" width="92" height="20" rx="3"/></g>` + C(150, 132, 12, WHITE) },
    ME: sealFlag(NAVY, "#C9A227", "#B8860B"),
    MD: { field: "#000000", accent: "#C8102E", draw: () => {
      const calvert = (x, y) => Array.from({ length: 6 }, (_, i) => R(x + i * 25, y, 25, 100, i % 2 ? "#000" : "#EAAA00")).join("") +
        `<clipPath id="b${x}${y}"><polygon points="${x},${y + 20} ${x + 150},${y + 60} ${x + 150},${y + 82} ${x},${y + 42}"/></clipPath>` +
        `<g clip-path="url(#b${x}${y})">${Array.from({ length: 6 }, (_, i) => R(x + i * 25, y, 25, 100, i % 2 ? "#EAAA00" : "#000")).join("")}</g>`;
      const crossland = (x, y) => R(x, y, 75, 50, WHITE) + R(x + 75, y, 75, 50, "#C8102E") + R(x, y + 50, 75, 50, "#C8102E") + R(x + 75, y + 50, 75, 50, WHITE) +
        `<clipPath id="c${x}${y}"><rect x="${x + 63}" y="${y + 12}" width="24" height="76"/><rect x="${x + 33}" y="${y + 38}" width="84" height="24"/></clipPath>` +
        `<g clip-path="url(#c${x}${y})">${R(x, y, 75, 50, "#C8102E")}${R(x + 75, y, 75, 50, WHITE)}${R(x, y + 50, 75, 50, WHITE)}${R(x + 75, y + 50, 75, 50, "#C8102E")}</g>`;
      return calvert(0, 0) + crossland(150, 0) + crossland(0, 100) + calvert(150, 100);
    } },
    MA: sealFlag(WHITE, "#14306B", "#14306B", { inner: "#2A55A3" }),
    MI: sealFlag(NAVY, "#C9A227", "#B8860B"),
    MN: { field: "#002D5D", accent: "#0077B6", draw: () => R(0, 0, 300, 200, "#52C9E8") +
      P("0,0 96,0 120,100 96,200 0,200", "#002D5D") + star(56, 100, 30, WHITE, 8, 0.45) },
    MS: { field: "#002A86", accent: "#BF0A30", draw: () => R(0, 0, 300, 200, RED) + R(46, 0, 208, 200, GOLD) + R(52, 0, 196, 200, "#002A86") +
      ring(150, 100, 52, 20, 6, WHITE) + star(150, 36, 9, GOLD) + C(150, 100, 32, WHITE) +
      `<g fill="#3A7D2C"><ellipse cx="128" cy="116" rx="14" ry="6" transform="rotate(-30 128 116)"/><ellipse cx="172" cy="116" rx="14" ry="6" transform="rotate(30 172 116)"/></g>` + C(150, 98, 10, "#F5E7C4") },
    MO: { field: "#0A3161", accent: "#B31942", draw: () => R(0, 0, 300, 66.7, "#B31942") + R(0, 66.7, 300, 66.7, WHITE) +
      R(0, 133.3, 300, 66.7, "#0A3161") + seal(150, 100, 36, "#0A3161", WHITE) },
    MT: sealFlag(NAVY, GOLD, "#B8860B"),
    NE: sealFlag("#003F87", "#C9A227", "#B8860B"),
    NV: { field: "#003DA5", accent: "#003DA5", draw: () => R(0, 0, 300, 200, "#003DA5") + star(56, 50, 20, WHITE) +
      `<path d="M26,58 Q30,92 56,96 Q82,92 86,58" fill="none" stroke="#C9A227" stroke-width="6"/>` + R(24, 18, 64, 10, "#C9A227") },
    NH: sealFlag(NAVY, GOLD, "#B8860B"),
    NJ: sealFlag("#E3C9A2", "#003A8C", "#003A8C"),
    NM: { field: "#FFD700", accent: "#BF0A30", draw: () => {
      let s = R(0, 0, 300, 200, "#FFD700") + C(150, 100, 20, "#BF0A30");
      for (let k = -1.5; k <= 1.5; k++) {
        const len = Math.abs(k) > 1 ? 38 : 50, off = 150 + k * 9 - 2.5, offY = 100 + k * 9 - 2.5;
        s += R(176, offY, len, 5, "#BF0A30") + R(124 - len, offY, len, 5, "#BF0A30") +
             R(off, 126, 5, len, "#BF0A30") + R(off, 74 - len, 5, len, "#BF0A30");
      }
      return s;
    } },
    NY: sealFlag(NAVY, GOLD, "#B8860B"),
    NC: { field: BLUE, accent: RED, draw: () => R(0, 0, 300, 100, RED) + R(0, 100, 300, 100, WHITE) + R(0, 0, 100, 200, BLUE) + star(50, 100, 22, WHITE) },
    ND: sealFlag("#003F87", "#C9A227", "#B8860B"),
    OH: { field: RED, accent: RED, draw: () => `<clipPath id="oh"><polygon points="0,0 300,30 240,100 300,170 0,200"/></clipPath><g clip-path="url(#oh)">` +
      Array.from({ length: 5 }, (_, i) => R(0, i * 40, 300, 40, i % 2 ? WHITE : RED)).join("") +
      P("0,0 160,100 0,200", BLUE) + C(58, 100, 24, WHITE) + C(58, 100, 16, RED) + ring(58, 100, 36, 13, 4.5, WHITE) + `</g>` },
    OK: sealFlag("#3A72C4", "#C8A97E", "#2E5EA8", { inner: "#3A72C4" }),
    OR: sealFlag(NAVY, "#C9A227", "#B8860B"),
    PA: sealFlag(NAVY, GOLD, "#B8860B"),
    RI: { field: WHITE, accent: "#B8860B", draw: () => R(0, 0, 300, 200, WHITE) + ring(150, 92, 58, 13, 7, "#C9A227") +
      `<g fill="none" stroke="#C9A227" stroke-width="8" stroke-linecap="round"><path d="M150,58 V124"/><path d="M126,108 Q150,136 174,108"/><path d="M136,70 H164"/></g>` +
      C(150, 52, 7, "none", 'stroke="#C9A227" stroke-width="5"') + R(110, 162, 80, 16, "#1F3B73") },
    SC: { field: "#003366", accent: "#003366", draw: () => R(0, 0, 300, 200, "#003366") +
      `<path d="M36,34 a24,24 0 1,0 30,-14 a18,18 0 1,1 -30,14z" fill="${WHITE}"/>` +
      `<g fill="${WHITE}"><rect x="144" y="70" width="12" height="100" rx="4"/>` +
      Array.from({ length: 7 }, (_, i) => `<ellipse cx="150" cy="70" rx="40" ry="8" transform="rotate(${-150 + i * 20} 150 70) translate(30 0)"/>`).join("") + `</g>` },
    SD: sealFlag("#2A5DAA", GOLD, "#B8860B", { under: Array.from({ length: 24 }, (_, i) => {
      const a = i / 24 * 2 * Math.PI; return `<path d="M150,100 L${150 + 76 * Math.cos(a)},${100 + 76 * Math.sin(a)}" stroke="${GOLD}" stroke-width="4"/>`; }).join("") }),
    TN: { field: RED, accent: RED, draw: () => R(0, 0, 300, 200, RED) + R(276, 0, 6, 200, WHITE) + R(282, 0, 18, 200, BLUE) +
      C(138, 100, 56, WHITE) + C(138, 100, 50, BLUE) + star(138, 70, 15, WHITE) + star(112, 116, 15, WHITE) + star(164, 116, 15, WHITE) },
    TX: { field: BLUE, accent: RED, draw: () => R(0, 0, 300, 100, WHITE) + R(0, 100, 300, 100, RED) + R(0, 0, 100, 200, BLUE) + star(50, 100, 34, WHITE) },
    UT: { field: "#0B2B4A", accent: "#C8442B", draw: () => R(0, 0, 300, 200, WHITE) + R(0, 0, 300, 62, "#0B2B4A") +
      P("0,62 60,62 100,40 140,62 300,62 300,40 240,62 200,30 160,62", "#0B2B4A") + R(0, 150, 300, 50, "#C8442B") +
      P("150,74 182,92 182,128 150,146 118,128 118,92", "#0B2B4A") + C(150, 112, 14, "#E0A526") },
    VT: sealFlag(NAVY, "#3A7D2C", "#2F6B2A", { inner: "#E9E3C7" }),
    VA: sealFlag(NAVY, WHITE, "#0B2A5B"),
    WA: sealFlag("#00573F", "#C9A227", "#00573F"),
    WV: { field: "#002855", accent: "#002855", draw: () => R(0, 0, 300, 200, "#002855") + R(10, 10, 280, 180, WHITE) +
      seal(150, 100, 46, "#002855", WHITE) + `<path d="M98,130 Q150,176 202,130" fill="none" stroke="#2E7D32" stroke-width="7"/>` },
    WI: sealFlag(NAVY, GOLD, "#B8860B"),
    WY: { field: "#002A86", accent: "#BF0A30", draw: () => R(0, 0, 300, 200, RED) + R(10, 10, 280, 180, WHITE) + R(18, 18, 264, 164, "#002A86") +
      `<g fill="${WHITE}"><ellipse cx="150" cy="104" rx="66" ry="36"/><ellipse cx="96" cy="96" rx="26" ry="30"/>` +
      `<rect x="104" y="124" width="14" height="30" rx="4"/><rect x="186" y="124" width="14" height="30" rx="4"/></g>` + C(150, 104, 18, "#002A86") },
  };
})();
