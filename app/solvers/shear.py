"""Shear design of a reinforced concrete beam (IS 456 Cl. 40, 26.5.1.5/6)."""

from .common import (
    bar_area,
    collect_references,
    inp,
    num,
    ref,
    step,
    t,
    tau_c,
    tau_c_max,
)

TYPE = "shear"

TITLE = t("Shear Design of a Beam — Stirrups", "बीम का अपरूपण अभिकल्प — रकाब")


def solve(p):
    """p keys: b, d, Vu (kN), Ast (mm2), fck, fy, optional stirrup_dia, legs."""
    b = float(p["b"])
    d = float(p["d"])
    Vu = float(p["Vu"])                 # kN
    Ast = float(p["Ast"])               # mm2 (tension steel continuing)
    fck = float(p["fck"])
    fy = float(p["fy"])
    stirrup_dia = float(p.get("stirrup_dia") or 8)
    legs = int(float(p.get("legs") or 2))

    inputs = [
        inp(t("Width b", "चौड़ाई b"), num(b), "mm"),
        inp(t("Effective depth d", "प्रभावी गहराई d"), num(d), "mm"),
        inp(t("Factored shear Vu", "गुणित अपरूपण Vu"), num(Vu), "kN"),
        inp(t("Tension steel Ast", "तनन स्टील Ast"), num(Ast), "mm²"),
        inp(t("Concrete grade fck", "कंक्रीट ग्रेड fck"), num(fck), "N/mm²"),
        inp(t("Stirrup steel fy", "रकाब स्टील fy"), num(fy), "N/mm²"),
        inp(t("Stirrup dia / legs", "रकाब व्यास / भुजाएँ"), f"{num(stirrup_dia)} / {legs}", "mm / nos."),
    ]

    steps = []
    warnings = []

    # 1. nominal shear stress
    tv = Vu * 1000.0 / (b * d)
    steps.append(step(
        1, t("Nominal shear stress τv", "नाममात्र अपरूपण प्रतिबल τv"),
        formula="τv = Vu / (b·d)",
        substitution=f"= {num(Vu*1000.0,0)} / ({num(b)}×{num(d)})",
        result=t(f"τv = {num(tv,3)} N/mm²", f"τv = {num(tv,3)} N/mm²"),
        references=[ref("IS456", "40.1", note=t("Nominal shear stress.", "नाममात्र अपरूपण प्रतिबल।"))],
    ))

    # 2. tau_c
    pt = 100.0 * Ast / (b * d)
    tc = tau_c(pt, fck)
    steps.append(step(
        2, t("Design shear strength of concrete τc", "कंक्रीट की अभिकल्प अपरूपण सामर्थ्य τc"),
        formula="100·As/(b·d) → τc from Table 19",
        substitution=f"100·As/(b·d) = 100×{num(Ast)}/({num(b)}×{num(d)}) = {num(pt,3)} ;  fck = {num(fck)} N/mm²",
        result=t(f"τc = {num(tc,3)} N/mm²", f"τc = {num(tc,3)} N/mm²"),
        references=[ref("IS456", "40.2.1", table="Table 19",
                        note=t("τc vs 100As/bd and concrete grade.", "τc बनाम 100As/bd एवं कंक्रीट ग्रेड।"))],
    ))

    # 3. tau_c,max
    tcmax = tau_c_max(fck)
    steps.append(step(
        3, t("Maximum shear stress τc,max", "अधिकतम अपरूपण प्रतिबल τc,max"),
        formula="τc,max from Table 20 (function of fck)",
        result=t(f"τc,max = {num(tcmax,2)} N/mm²", f"τc,max = {num(tcmax,2)} N/mm²"),
        references=[ref("IS456", "40.2.3", table="Table 20",
                        note=t("Nominal shear stress shall not exceed τc,max.", "नाममात्र अपरूपण प्रतिबल τc,max से अधिक नहीं।"))],
    ))

    # 4. compare & design
    Asv = legs * bar_area(stirrup_dia)
    min_asv_sv = 0.4 * b / (0.87 * fy)          # mm²/mm

    if tv > tcmax:
        warnings.append(t(
            f"τv ({num(tv,3)}) > τc,max ({num(tcmax,2)}) — section inadequate in shear even with reinforcement. "
            "Increase depth, breadth or concrete grade.",
            f"τv ({num(tv,3)}) > τc,max ({num(tcmax,2)}) — प्रबलन के साथ भी परिच्छेद अपरूपण में अपर्याप्त। "
            "गहराई, चौड़ाई या कंक्रीट ग्रेड बढ़ाएँ।"))
        steps.append(step(
            4, t("Section inadequate", "परिच्छेद अपर्याप्त"),
            result=t("τv > τc,max → redesign the section.", "τv > τc,max → परिच्छेद पुनरभिकल्पित करें।"),
            references=[ref("IS456", "40.2.3", table="Table 20")],
        ))
        sv = None
        asv_sv_req = None
        mode = "inadequate"
    elif tv <= tc / 2.0:
        mode = "minimum"
        asv_sv_req = min_asv_sv
        sv = Asv / asv_sv_req
        steps.append(step(
            4, t("Minimum shear reinforcement", "न्यूनतम अपरूपण प्रबलन"),
            formula="Asv/(b·sv) ≥ 0.4/(0.87·fy)",
            substitution=f"Asv/sv ≥ 0.4×{num(b)}/(0.87×{num(fy)}) = {num(min_asv_sv,4)} mm²/mm",
            result=t(f"τv ≤ τc/2 → provide minimum stirrups; Asv/sv = {num(min_asv_sv,4)} mm²/mm",
                     f"τv ≤ τc/2 → न्यूनतम रकाब; Asv/sv = {num(min_asv_sv,4)} mm²/mm"),
            references=[ref("IS456", "26.5.1.6", note=t("Minimum shear reinforcement.", "न्यूनतम अपरूपण प्रबलन।"))],
        ))
    elif tv <= tc:
        mode = "minimum"
        asv_sv_req = min_asv_sv
        sv = Asv / asv_sv_req
        steps.append(step(
            4, t("Minimum shear reinforcement governs", "न्यूनतम अपरूपण प्रबलन नियंत्रक"),
            formula="Asv/(b·sv) ≥ 0.4/(0.87·fy)",
            substitution=f"Asv/sv ≥ 0.4×{num(b)}/(0.87×{num(fy)}) = {num(min_asv_sv,4)} mm²/mm",
            result=t(f"τc/2 < τv ≤ τc → minimum stirrups; Asv/sv = {num(min_asv_sv,4)} mm²/mm",
                     f"τc/2 < τv ≤ τc → न्यूनतम रकाब; Asv/sv = {num(min_asv_sv,4)} mm²/mm"),
            references=[ref("IS456", "40.3"), ref("IS456", "26.5.1.6")],
        ))
    else:
        mode = "design"
        vus = (tv - tc) * b * d               # N
        asv_sv_req = max(vus / (0.87 * fy * d), min_asv_sv)
        sv = Asv / asv_sv_req
        steps.append(step(
            4, t("Design shear reinforcement for excess shear", "अतिरिक्त अपरूपण हेतु प्रबलन अभिकल्प"),
            formula="Vus = (τv − τc)·b·d ;  Asv/sv = Vus/(0.87·fy·d) ; not less than 0.4b/(0.87fy)",
            substitution=f"Vus = ({num(tv,3)}−{num(tc,3)})×{num(b)}×{num(d)} = {num(vus,0)} N ; "
                         f"Asv/sv = {num(vus,0)}/(0.87×{num(fy)}×{num(d)}) = {num(asv_sv_req,4)} mm²/mm",
            result=t(f"τc < τv ≤ τc,max → Asv/sv = {num(asv_sv_req,4)} mm²/mm",
                     f"τc < τv ≤ τc,max → Asv/sv = {num(asv_sv_req,4)} mm²/mm"),
            references=[ref("IS456", "40.4", note=t("Vertical stirrups: Vus = 0.87 fy Asv d/sv.", "ऊर्ध्वाधर रकाब: Vus = 0.87 fy Asv d/sv।"))],
        ))

    # 5. spacing
    if sv is not None:
        sv_max = min(0.75 * d, 300.0)
        sv_prov = min(sv, sv_max)
        # round down to nearest 5 mm for practicality
        sv_prov = max(25.0, (sv_prov // 5) * 5.0)
        steps.append(step(
            5, t("Stirrup spacing", "रकाब अंतराल"),
            formula="sv = Asv/(Asv/sv)  ;  sv ≤ 0.75·d and ≤ 300 mm",
            substitution=f"Asv = {legs}×{num(stirrup_dia)}mm legs = {num(Asv)} mm² ; "
                         f"sv ≤ min(0.75×{num(d)}, 300) = {num(sv_max)} mm",
            result=t(f"Provide {legs}-legged {num(stirrup_dia)} mm dia stirrups @ {num(sv_prov)} mm c/c",
                     f"{legs}-भुजा, {num(stirrup_dia)} मिमी व्यास रकाब @ {num(sv_prov)} मिमी केंद्र-से-केंद्र प्रदान करें"),
            references=[ref("IS456", "26.5.1.5", note=t("Max spacing of shear reinforcement.", "अपरूपण प्रबलन का अधिकतम अंतराल।")),
                        ref("IS456", "40.4")],
        ))
    else:
        sv_prov = None

    summary = {
        "en": (f"τv = {num(tv,3)}, τc = {num(tc,3)}, τc,max = {num(tcmax,2)} N/mm². "
               + (f"Provide {legs}-legged {num(stirrup_dia)} mm stirrups @ {num(sv_prov)} mm c/c."
                  if sv_prov else "Section inadequate — redesign.")),
        "hi": (f"τv = {num(tv,3)}, τc = {num(tc,3)}, τc,max = {num(tcmax,2)} N/mm²। "
               + (f"{legs}-भुजा, {num(stirrup_dia)} मिमी रकाब @ {num(sv_prov)} मिमी केंद्र-से-केंद्र प्रदान करें।"
                  if sv_prov else "परिच्छेद अपर्याप्त — पुनरभिकल्प करें।")),
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
