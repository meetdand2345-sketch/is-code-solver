"""Shared helpers for the rule-based IS-code solvers.

Every solver returns the same JSON shape so the front-end can render any
problem uniformly:

    {
      "type": "<problem_type>",
      "title": {"en": ..., "hi": ...},
      "inputs": [{"label": {en,hi}, "value": "...", "unit": "..."}],
      "steps": [
          {"n": 1,
           "title": {"en": ..., "hi": ...},
           "formula": "..." | null,
           "substitution": "..." | null,
           "result": {"en": ..., "hi": ...} | "..." | null,
           "references": [{"code": "IS456", "clause": "38.1", "table": null,
                           "note": {en,hi} | null}]
          }, ...
      ],
      "summary": {"en": ..., "hi": ...},
      "references": [{"code":..., "clause":..., "table":...}],  # de-duplicated
      "warnings": [{"en":...,"hi":...}]
    }
"""

import math


def t(en, hi):
    """Bilingual text object."""
    return {"en": en, "hi": hi}


def ref(code, clause, table=None, note=None):
    return {"code": code, "clause": clause, "table": table, "note": note}


def step(n, title, formula=None, substitution=None, result=None, references=None):
    return {
        "n": n,
        "title": title,
        "formula": formula,
        "substitution": substitution,
        "result": result,
        "references": references or [],
    }


def inp(label, value, unit=""):
    return {"label": label, "value": value, "unit": unit}


def collect_references(steps):
    seen = []
    out = []
    for s in steps:
        for r in s.get("references", []):
            key = (r["code"], r.get("clause"), r.get("table"))
            if key not in seen:
                seen.append(key)
                out.append({"code": r["code"], "clause": r.get("clause"), "table": r.get("table")})
    return out


def num(x, places=2):
    """Format a number cleanly for display."""
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if abs(x - round(x)) < 1e-9 and abs(x) >= 1:
        return str(int(round(x)))
    return f"{x:.{places}f}"


# ---------------------------------------------------------------------------
# Standard bar diameters (mm) — nominal sizes in common use (IS 1786 Cl. 6.1)
# ---------------------------------------------------------------------------
BAR_DIAMETERS = [8, 10, 12, 16, 20, 25, 32]


def bar_area(dia):
    return math.pi * dia * dia / 4.0


def select_bars(required_area, breadth=None, min_count=2, max_count=8, cover=25.0, stirrup_dia=8.0):
    """Pick a bar arrangement whose provided area >= required_area.

    Prefers the smallest provided area (least over-design); ties broken by
    fewer, smaller bars. Returns dict or None.
    """
    best = None
    for dia in BAR_DIAMETERS:
        a1 = bar_area(dia)
        n = max(min_count, math.ceil(required_area / a1))
        if n > max_count:
            continue
        provided = n * a1
        # crude single-layer fit check against breadth
        if breadth is not None:
            clear = breadth - 2 * cover - 2 * stirrup_dia
            needed = n * dia + (n - 1) * max(dia, 25.0)
            if needed > clear and n > 1:
                continue
        cand = {"dia": dia, "count": n, "area": provided}
        if best is None or provided < best["area"] - 1e-6:
            best = cand
        elif abs(provided - best["area"]) < 1e-6 and dia < best["dia"]:
            best = cand
    if best is None:
        # fall back to the largest single arrangement
        dia = BAR_DIAMETERS[-1]
        n = max(min_count, math.ceil(required_area / bar_area(dia)))
        best = {"dia": dia, "count": n, "area": n * bar_area(dia)}
    return best


# ---------------------------------------------------------------------------
# IS 456:2000 Table 19 — design shear strength of concrete tau_c (N/mm^2)
# rows: 100*As/(b*d)  ; cols: M15, M20, M25, M30, M35, M40+
# ---------------------------------------------------------------------------
_T19_PT = [0.15, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00, 2.25, 2.50, 2.75, 3.00]
_T19_GRADES = [15, 20, 25, 30, 35, 40]
_T19 = {
    0.15: [0.28, 0.28, 0.29, 0.29, 0.29, 0.30],
    0.25: [0.35, 0.36, 0.36, 0.37, 0.37, 0.38],
    0.50: [0.46, 0.48, 0.49, 0.50, 0.50, 0.51],
    0.75: [0.54, 0.56, 0.57, 0.59, 0.59, 0.60],
    1.00: [0.60, 0.62, 0.64, 0.66, 0.67, 0.68],
    1.25: [0.64, 0.67, 0.70, 0.71, 0.73, 0.74],
    1.50: [0.68, 0.72, 0.74, 0.76, 0.78, 0.79],
    1.75: [0.71, 0.75, 0.78, 0.80, 0.82, 0.84],
    2.00: [0.71, 0.79, 0.82, 0.84, 0.86, 0.88],
    2.25: [0.71, 0.81, 0.85, 0.88, 0.90, 0.92],
    2.50: [0.71, 0.82, 0.88, 0.91, 0.93, 0.95],
    2.75: [0.71, 0.82, 0.90, 0.94, 0.96, 0.98],
    3.00: [0.71, 0.82, 0.92, 0.96, 0.99, 1.01],
}


def _interp(x, xs, ys):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(1, len(xs)):
        if x <= xs[i]:
            x0, x1 = xs[i - 1], xs[i]
            y0, y1 = ys[i - 1], ys[i]
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return ys[-1]


def tau_c(pt, fck):
    """Design shear strength of concrete (IS 456 Table 19), interpolated."""
    pt = max(0.15, min(3.0, pt))
    # interpolate pt within table rows
    for i in range(1, len(_T19_PT)):
        if pt <= _T19_PT[i]:
            x0, x1 = _T19_PT[i - 1], _T19_PT[i]
            v0 = _T19[x0]
            v1 = _T19[x1]
            frac = (pt - x0) / (x1 - x0)
            col = [v0[j] + (v1[j] - v0[j]) * frac for j in range(len(_T19_GRADES))]
            break
    else:
        col = _T19[_T19_PT[-1]]
    # interpolate grade
    g = min(40, fck)
    return round(_interp(g, _T19_GRADES, col), 3)


# IS 456 Table 20 — maximum shear stress tau_c,max (N/mm^2)
_T20 = {15: 2.5, 20: 2.8, 25: 3.1, 30: 3.5, 35: 3.7, 40: 4.0}


def tau_c_max(fck):
    g = max(15, min(40, fck))
    xs = sorted(_T20)
    return round(_interp(g, xs, [_T20[k] for k in xs]), 2)


# IS 456 Cl. 26.2.1.1 — design bond stress (plain bars, tension), N/mm^2
_BOND = {20: 1.2, 25: 1.4, 30: 1.5, 35: 1.7, 40: 1.9}


def design_bond_stress(fck):
    g = max(20, min(40, fck))
    xs = sorted(_BOND)
    return round(_interp(g, xs, [_BOND[k] for k in xs]), 2)


# Limiting neutral-axis depth xu,max/d by steel grade (IS 456 Cl. 38.1)
XU_MAX = {250: 0.53, 415: 0.48, 500: 0.46}


def xu_max_ratio(fy):
    grades = sorted(XU_MAX)
    if fy <= grades[0]:
        return XU_MAX[grades[0]]
    if fy >= grades[-1]:
        return XU_MAX[grades[-1]]
    return round(_interp(fy, grades, [XU_MAX[g] for g in grades]), 3)
