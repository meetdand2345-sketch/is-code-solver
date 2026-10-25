"""Design of a one-way reinforced concrete slab (IS 456:2000)."""

import math

from .common import (
    collect_references,
    inp,
    num,
    ref,
    select_bars,
    step,
    t,
)

TYPE = "slab_oneway"

TITLE = t("One-Way Reinforced Concrete Slab — Design",
          "एक-दिशीय प्रबलित कंक्रीट स्लैब — अभिकल्प")


def solve(p):
    """p keys: L (effective span, m), LL (kN/m2), fck, fy, optional ff (floor finish),
    support ('simply_supported'|'continuous'), cover."""
    L = float(p["L"])                         # m (effective span)
    LL = float(p["LL"])                       # kN/m2
    fck = float(p["fck"])
    fy = float(p["fy"])
    ff = float(p.get("ff") or 1.0)            # floor finish + services, kN/m2
    support = p.get("support", "simply_supported")
    cover = float(p.get("cover") or 20.0)

    inputs = [
        inp(t("Effective span L", "प्रभावी विस्तृति L"), num(L), "m"),
        inp(t("Imposed (live) load LL", "आरोपित (चल) भार LL"), num(LL), "kN/m²"),
        inp(t("Floor finish + services", "फर्श परिसज्जा + सेवाएँ"), num(ff), "kN/m²"),
        inp(t("Concrete grade fck", "कंक्रीट ग्रेड fck"), num(fck), "N/mm²"),
        inp(t("Steel grade fy", "स्टील ग्रेड fy"), num(fy), "N/mm²"),
        inp(t("Support condition", "आलंबन स्थिति"),
            t("simply supported" if support == "simply_supported" else "continuous",
              "शुद्धालंबित" if support == "simply_supported" else "सतत"), ""),
    ]

    steps = []
    warnings = []
    b = 1000.0  # per metre width, mm

    # 1. effective span note
    steps.append(step(
        1, t("Effective span", "प्रभावी विस्तृति"),
        formula="Effective span = clear span + d (≤ centre-to-centre), whichever is less",
        result=t(f"Design effective span L = {num(L)} m",
                 f"अभिकल्प प्रभावी विस्तृति L = {num(L)} मी"),
        references=[ref("IS456", "22.2", note=t("Effective span of a simply supported member.", "शुद्धालंबित सदस्य की प्रभावी विस्तृति।"))],
    ))

    # 2. trial depth from span/depth
    base = 26 if support == "continuous" else 20
    d_req = L * 1000.0 / base
    D = math.ceil((d_req + cover + 5) / 10.0) * 10.0   # round to 10 mm
    d = D - cover - 5.0                                 # assume 10 mm bars, half dia 5
    steps.append(step(
        2, t("Trial depth from span/effective-depth ratio", "विस्तृति/प्रभावी-गहराई अनुपात से परीक्षण गहराई"),
        formula="d ≈ span / basic ratio (SS 20, continuous 26)  [modified by Fig. 4 factor]",
        substitution=f"d ≈ {num(L*1000.0,0)}/{base} = {num(d_req)} mm → adopt D = {num(D)} mm, d = {num(d)} mm",
        result=t(f"Adopt overall depth D = {num(D)} mm (d = {num(d)} mm)",
                 f"कुल गहराई D = {num(D)} मिमी अपनाएँ (d = {num(d)} मिमी)"),
        references=[ref("IS456", "23.2.1", note=t("Basic span/depth ratios: SS 20, continuous 26.", "मूल विस्तृति/गहराई अनुपात: SS 20, सतत 26।")),
                    ref("IS456", "24.1", note=t("Beam provisions apply to slabs.", "बीम के प्रावधान स्लैब पर लागू।"))],
    ))

    # 3. loads
    self_wt = D / 1000.0 * 25.0
    DL = self_wt + ff
    w = DL + LL
    wu = 1.5 * w
    steps.append(step(
        3, t("Loads and factored load", "भार एवं गुणित भार"),
        formula="self wt = D/1000 × 25 kN/m³ ;  w = (self wt + ff) + LL ;  wu = 1.5·w",
        substitution=f"self wt = {num(D)}/1000×25 = {num(self_wt)} kN/m² ; "
                     f"DL = {num(self_wt)}+{num(ff)} = {num(DL)} kN/m² ; w = {num(DL)}+{num(LL)} = {num(w)} kN/m² ; "
                     f"wu = 1.5×{num(w)} = {num(wu)} kN/m²",
        result=t(f"wu = {num(wu)} kN/m²", f"wu = {num(wu)} kN/m²"),
        references=[ref("IS875P1", "Cl. 2 / Table 1", note=t("RCC unit weight 25 kN/m³.", "RCC एकक भार 25 kN/m³।")),
                    ref("IS875P2", "Table 1", note=t("Imposed loads.", "आरोपित भार।")),
                    ref("IS456", "36.4.1", table="Table 18", note=t("γf = 1.5 for DL+LL.", "DL+LL हेतु γf = 1.5।"))],
    ))

    # 4. design moment
    Mu = wu * L * L / 8.0                      # kNm per m (SS); use coefficient for continuous
    if support == "continuous":
        Mu = wu * L * L / 10.0
    steps.append(step(
        4, t("Design bending moment", "अभिकल्प बंकन आघूर्ण"),
        formula=("Mu = wu·L²/8 (simply supported)" if support == "simply_supported"
                 else "Mu = wu·L²/10 (continuous, near support)"),
        substitution=f"Mu = {num(wu)}×{num(L)}²/{8 if support=='simply_supported' else 10}",
        result=t(f"Mu = {num(Mu)} kN·m per metre width", f"Mu = {num(Mu)} kN·m प्रति मीटर चौड़ाई"),
        references=[ref("IS456", "22.5", note=t("Moment coefficients for continuous beams/slabs.", "सतत बीम/स्लैब हेतु आघूर्ण गुणक।"))],
    ))

    # 5. steel
    Mu_Nmm = Mu * 1e6
    term = 4.6 * Mu_Nmm / (fck * b * d * d)
    if term >= 1:
        warnings.append(t("Depth insufficient for the applied moment — increase depth.",
                          "लागू आघूर्ण हेतु गहराई अपर्याप्त — गहराई बढ़ाएँ।"))
        term = 0.999999
    Ast = 0.5 * fck / fy * (1 - math.sqrt(1 - term)) * b * d
    steps.append(step(
        5, t("Main (tension) reinforcement", "मुख्य (तनन) प्रबलन"),
        formula="Ast = (0.5·fck/fy)·[1 − √(1 − 4.6·Mu/(fck·b·d²))]·b·d  (b = 1000 mm)",
        substitution=f"= (0.5×{num(fck)}/{num(fy)})×[1 − √(1 − 4.6×{num(Mu_Nmm,0)}/({num(fck)}×1000×{num(d)}²))]×1000×{num(d)}",
        result=t(f"Ast = {num(Ast)} mm²/m", f"Ast = {num(Ast)} mm²/मी"),
        references=[ref("IS456", "38.1"), ref("IS456", "Annex G-1.1")],
    ))

    # 6. min steel (slabs)
    As_min = 0.0012 * b * D if fy >= 415 else 0.0015 * b * D
    Ast_req = max(Ast, As_min)
    steps.append(step(
        6, t("Minimum reinforcement in slabs", "स्लैब में न्यूनतम प्रबलन"),
        formula="As,min = 0.12%·b·D (deformed bars) or 0.15%·b·D (mild steel)",
        substitution=f"= {'0.12' if fy>=415 else '0.15'}%×1000×{num(D)} = {num(As_min)} mm²/m",
        result=t(f"As,min = {num(As_min)} mm²/m → design Ast = {num(Ast_req)} mm²/m",
                 f"As,min = {num(As_min)} mm²/मी → अभिकल्प Ast = {num(Ast_req)} mm²/मी"),
        references=[ref("IS456", "26.5.2.1", note=t("Min steel in slabs.", "स्लैब में न्यूनतम स्टील।"))],
    ))

    # 7. spacing of main bars
    bars = select_bars(Ast_req, breadth=1000.0)
    if bars:
        sv = 1000.0 * bars["area"] / Ast_req * (1.0 / bars["count"]) if bars["count"] else 0
        # spacing = area_of_one_bar / required_area_per_mm * 1000
        a1 = math.pi * bars["dia"] ** 2 / 4.0
        spacing = a1 / Ast_req * 1000.0
        spacing_max = min(3.0 * d, 300.0)
        spacing_prov = max(75.0, (min(spacing, spacing_max) // 10) * 10.0)
        steps.append(step(
            7, t("Spacing of main bars", "मुख्य सरियों का अंतराल"),
            formula="spacing = (area of one bar / Ast) × 1000  ;  ≤ min(3d, 300 mm)",
            substitution=f"Provide {num(bars['dia'])} mm dia @ spacing = {num(a1)}/{num(Ast_req)}×1000 = {num(spacing)} mm ; "
                         f"max = min(3×{num(d)}, 300) = {num(spacing_max)} mm",
            result=t(f"Provide {num(bars['dia'])} mm dia main bars @ {num(spacing_prov)} mm c/c",
                     f"{num(bars['dia'])} मिमी व्यास मुख्य सरियाँ @ {num(spacing_prov)} मिमी केंद्र-से-केंद्र प्रदान करें"),
            references=[ref("IS456", "26.3.3", note=t("Max spacing: 3d or 300 mm (main).", "अधिकतम अंतराल: 3d या 300 मिमी (मुख्य)।")),
                        ref("IS1786", "1.1")],
        ))
    else:
        spacing_prov = None

    # 8. distribution steel
    As_dist = As_min
    dist_dia = 8.0
    a1d = math.pi * dist_dia ** 2 / 4.0
    spacing_d = a1d / As_dist * 1000.0
    spacing_d_max = min(5.0 * d, 450.0)
    spacing_d_prov = max(75.0, (min(spacing_d, spacing_d_max) // 10) * 10.0)
    steps.append(step(
        8, t("Distribution steel", "वितरण प्रबलन"),
        formula="As,dist = 0.12%·b·D  ;  spacing ≤ min(5d, 450 mm)",
        substitution=f"= {num(As_dist)} mm²/m ; provide {num(dist_dia)} mm dia @ {num(spacing_d_prov)} mm c/c",
        result=t(f"Provide {num(dist_dia)} mm dia distribution bars @ {num(spacing_d_prov)} mm c/c",
                 f"{num(dist_dia)} मिमी व्यास वितरण सरियाँ @ {num(spacing_d_prov)} मिमी केंद्र-से-केंद्र प्रदान करें"),
        references=[ref("IS456", "26.5.2.1"), ref("IS456", "26.3.3",
                    note=t("Max spacing: 5d or 450 mm (distribution).", "अधिकतम अंतराल: 5d या 450 मिमी (वितरण)।"))],
    ))

    summary = {
        "en": (f"Slab {num(L)} m span, D = {num(D)} mm, M{num(fck)}/Fe{num(fy)}. "
               f"wu = {num(wu)} kN/m², Mu = {num(Mu)} kN·m/m, Ast = {num(Ast_req)} mm²/m."
               + (f" Main: {num(bars['dia'])} mm @ {num(spacing_prov)} mm c/c." if bars else "")),
        "hi": (f"स्लैब {num(L)} मी विस्तृति, D = {num(D)} मिमी, M{num(fck)}/Fe{num(fy)}। "
               f"wu = {num(wu)} kN/m², Mu = {num(Mu)} kN·m/मी, Ast = {num(Ast_req)} mm²/मी।"
               + (f" मुख्य: {num(bars['dia'])} मिमी @ {num(spacing_prov)} मिमी केंद्र-से-केंद्र।" if bars else "")),
    }

    return {
        "type": TYPE,
        "title": TITLE,
        "inputs": inputs,
        "steps": steps,
        "summary": summary,
        "references": collect_references(steps),
        "warnings": warnings,
    }
