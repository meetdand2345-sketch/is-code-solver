"""Factored load / load-combination solver (IS 456 Table 18 + IS 875)."""

from .common import collect_references, inp, num, ref, step, t

TYPE = "loads"

TITLE = t("Factored Load and Load Combinations",
          "गुणित भार एवं भार संयोजन")


def solve(p):
    """p keys: dl, ll, optional wl (all same units, kN/m or kN/m²)."""
    dl = float(p["dl"])
    ll = float(p["ll"])
    wl = float(p["wl"]) if p.get("wl") not in (None, "") else None

    inputs = [
        inp(t("Dead load DL", "स्थायी भार DL"), num(dl), "kN/m (or kN/m²)"),
        inp(t("Imposed / live load LL", "आरोपित / चल भार LL"), num(ll), "kN/m (or kN/m²)"),
    ]
    if wl is not None:
        inputs.append(inp(t("Wind / seismic load WL/EL", "पवन / भूकंप भार WL/EL"), num(wl), "kN/m (or kN/m²)"))

    steps = []

    steps.append(step(
        1, t("Characteristic loads", "अभिलाक्षणिक भार"),
        result=t(
            f"DL = {num(dl)}, LL = {num(ll)}" + (f", WL/EL = {num(wl)}" if wl is not None else "") + " (characteristic values)",
            f"DL = {num(dl)}, LL = {num(ll)}" + (f", WL/EL = {num(wl)}" if wl is not None else "") + " (अभिलाक्षणिक मान)"),
        references=[
            ref("IS875P1", "Cl. 2 / Table 1", note=t("Unit weights for dead load.", "स्थायी भार हेतु एकक भार।")),
            ref("IS875P2", "Table 1", note=t("Imposed (live) loads by occupancy.", "उपभोग अनुसार आरोपित (चल) भार।")),
        ],
    ))

    steps.append(step(
        2, t("Partial safety factors for loads (γf)", "भार हेतु आंशिक सुरक्षा गुणक (γf)"),
        formula="DL+LL: 1.5(DL+LL) | DL+WL/EL: 1.2(DL+WL/EL) or 0.9DL+1.5(WL/EL) | DL+LL+WL: 1.2(DL+LL+WL)",
        result=t("γf taken from IS 456 Table 18 for the limit state of collapse.",
                 "γf संक्षिप्त अवस्था हेतु IS 456 तालिका 18 से लिया गया।"),
        references=[ref("IS456", "36.4.1", table="Table 18",
                        note=t("Partial safety factors for loads.", "भार हेतु आंशिक सुरक्षा गुणक।"))],
    ))

    combos = []
    c1 = 1.5 * (dl + ll)
    combos.append((t("1.5(DL + LL)", "1.5(DL + LL)"), c1))
    if wl is not None:
        c2a = 1.2 * (dl + wl)
        c2b = 0.9 * dl + 1.5 * wl
        c3 = 1.2 * (dl + ll + wl)
        combos.append((t("1.2(DL + WL/EL)", "1.2(DL + WL/EL)"), c2a))
        combos.append((t("0.9 DL + 1.5(WL/EL)  (DL stabilising)", "0.9 DL + 1.5(WL/EL)  (DL स्थिरकारी)"), c2b))
        combos.append((t("1.2(DL + LL + WL/EL)", "1.2(DL + LL + WL/EL)"), c3))

    rows = [{"combination": lbl, "value": num(v)} for lbl, v in combos]
    governing = max(combos, key=lambda x: x[1])

    steps.append(step(
        3, t("Factored (design) loads for each combination", "प्रत्येक संयोजन हेतु गुणित (अभिकल्प) भार"),
        formula="Design load Fd = γf × characteristic load",
        result={"en": " | ".join(f"{lbl['en']} = {num(v)}" for lbl, v in combos),
                "hi": " | ".join(f"{lbl['hi']} = {num(v)}" for lbl, v in combos)},
        references=[ref("IS456", "36.4.1", table="Table 18"),
                    ref("IS875P5", "Cl. 3", note=t("Combination of loads.", "भारों का संयोजन।"))],
    ))

    steps.append(step(
        4, t("Governing combination", "नियंत्रक संयोजन"),
        result=t(f"Governing: {governing[0]['en']} = {num(governing[1])} (maximum)",
                 f"नियंत्रक: {governing[0]['hi']} = {num(governing[1])} (अधिकतम)"),
        references=[ref("IS456", "36.4.1", table="Table 18")],
    ))

    summary = {
        "en": f"Factored design load = {num(governing[1])} (from {governing[0]['en']}).",
        "hi": f"गुणित अभिकल्प भार = {num(governing[1])} ({governing[0]['hi']} से)।",
    }

    return {
        "type": TYPE,
        "title": TITLE,
        "inputs": inputs,
        "steps": steps,
        "combinations": rows,
        "summary": summary,
        "references": collect_references(steps),
        "warnings": [],
    }
