"""Design of a singly reinforced rectangular beam (limit state, IS 456:2000)."""

import math

from .common import (
    BAR_DIAMETERS,
    bar_area,
    collect_references,
    inp,
    num,
    ref,
    select_bars,
    step,
    t,
    xu_max_ratio,
)

TYPE = "beam_flexure"

TITLE = t("Singly Reinforced Rectangular Beam — Flexural Design",
          "एकल-प्रबलित आयताकार बीम — बंकन अभिकल्प")


def solve(p):
    """p keys: b, D, d, fck, fy, Mu (kNm) OR (w kN/m, L m). Optional cover, support."""
    b = float(p["b"])            # mm
    D = float(p["D"])            # mm
    d = float(p.get("d") or (D - float(p.get("cover", 40.0)) - 6 - 10))
    fck = float(p["fck"])
    fy = float(p["fy"])
    support = p.get("support", "simply_supported")

    steps = []
    warnings = []

    # Mu ------------------------------------------------------------------
    if p.get("Mu") not in (None, ""):
        Mu = float(p["Mu"])                      # kNm
        mu_source = t("given", "दिया गया")
    elif p.get("w") not in (None, "") and p.get("L") not in (None, ""):
        w = float(p["w"])                        # kN/m
        L = float(p["L"])                        # m
        Mu = w * L * L / 8.0
        mu_source = t(f"computed from w={num(w)} kN/m and L={num(L)} m (wL²/8)",
                      f"w={num(w)} kN/m एवं L={num(L)} m से परिकलित (wL²/8)")
    else:
        raise ValueError("beam_flexure requires either Mu (kNm) or both w (kN/m) and L (m)")

    Mu_Nmm = Mu * 1e6
    inputs = [
        inp(t("Width b", "चौड़ाई b"), num(b), "mm"),
        inp(t("Overall depth D", "कुल गहराई D"), num(D), "mm"),
        inp(t("Effective depth d", "प्रभावी गहराई d"), num(d), "mm"),
        inp(t("Concrete grade fck", "कंक्रीट ग्रेड fck"), num(fck), "N/mm²"),
        inp(t("Steel grade fy", "स्टील ग्रेड fy"), num(fy), "N/mm²"),
        inp(t("Factored moment Mu", "गुणित आघूर्ण Mu"), num(Mu), "kN·m"),
    ]

    steps.append(step(
        1,
        t("Factored design moment", "गुणित अभिकल्प आघूर्ण"),
        formula="Mu = " + ("wL²/8" if mu_source["en"].startswith("computed") else "given"),
        substitution=mu_source,
        result=t(f"Mu = {num(Mu)} kN·m = {num(Mu_Nmm,0)} N·mm",
                 f"Mu = {num(Mu)} kN·m = {num(Mu_Nmm,0)} N·mm"),
        references=[ref("IS456", "36.4.1", note=t("Design load / moment uses γf from Table 18.", "अभिकल्प भार/आघूर्ण में तालिका 18 का γf प्रयुक्त।"))],
    ))

    # Limiting moment ------------------------------------------------------
    k = xu_max_ratio(fy)
    Mu_lim = 0.36 * k * (1 - 0.42 * k) * fck * b * d * d   # Nmm
    Mu_lim_kNm = Mu_lim / 1e6
    steps.append(step(
        2,
        t("Limiting depth of neutral axis and limiting moment",
          "उदासीन अक्ष की सीमांत गहराई एवं सीमांत आघूर्ण"),
        formula="xu,max/d = f(fy) ;  Mu,lim = 0.36·(xu,max/d)·(1 − 0.42·xu,max/d)·fck·b·d²",
        substitution=f"xu,max/d = {num(k,3)} (fy = {num(fy)} N/mm²);  "
                     f"Mu,lim = 0.36×{num(k,3)}×(1−0.42×{num(k,3)})×{num(fck)}×{num(b)}×{num(d)}²",
        result=t(f"Mu,lim = {num(Mu_lim_kNm)} kN·m", f"Mu,lim = {num(Mu_lim_kNm)} kN·m"),
        references=[
            ref("IS456", "38.1", note=t("Limiting xu,max/d: Fe250 0.53, Fe415 0.48, Fe500 0.46.", "सीमांत xu,max/d: Fe250 0.53, Fe415 0.48, Fe500 0.46।")),
            ref("IS456", "Annex G-1.1", note=t("Moment of resistance of rectangular sections.", "आयताकार परिच्छेद के प्रतिरोध आघूर्ण।")),
        ],
    ))

    if Mu > Mu_lim_kNm + 1e-6:
        warnings.append(t(
            f"Mu ({num(Mu)} kN·m) exceeds the singly reinforced limiting moment ({num(Mu_lim_kNm)} kN·m). "
            "The section needs compression reinforcement (doubly reinforced) or a larger depth/grade.",
            f"Mu ({num(Mu)} kN·m) एकल-प्रबलित सीमांत आघूर्ण ({num(Mu_lim_kNm)} kN·m) से अधिक है। "
            "परिच्छेद को संपीडन प्रबलन (द्वि-प्रबलित) या अधिक गहराई/ग्रेड की आवश्यकता है।"))
        steps.append(step(
            3, t("Section adequacy — action required", "परिच्छेद पर्याप्तता — कार्रवाई आवश्यक"),
            result=t("Mu > Mu,lim → redesign as doubly reinforced / increase section.",
                     "Mu > Mu,lim → द्वि-प्रबलित रूप में पुनरभिकल्प / परिच्छेद बढ़ाएँ।"),
            references=[ref("IS456", "Annex G-1.2", note=t("Sections with compression reinforcement.", "संपीडन प्रबलन वाले परिच्छेद।"))],
        ))
    else:
        # Area of steel ----------------------------------------------------
        term = 4.6 * Mu_Nmm / (fck * b * d * d)
        if term >= 1:
            warnings.append(t("Mu is at/over the singly reinforced limit; result not reliable.",
                              "Mu एकल-प्रबलित सीमा पर/उससे अधिक; परिणाम विश्वसनीय नहीं।"))
            term = min(term, 0.999999)
        Ast = 0.5 * fck / fy * (1 - math.sqrt(1 - term)) * b * d
        steps.append(step(
            4, t("Area of tension steel required", "आवश्यक तनन स्टील क्षेत्रफल"),
            formula="Ast = (0.5·fck/fy)·[1 − √(1 − 4.6·Mu/(fck·b·d²))]·b·d",
            substitution=f"= (0.5×{num(fck)}/{num(fy)})×[1 − √(1 − 4.6×{num(Mu_Nmm,0)}/({num(fck)}×{num(b)}×{num(d)}²))]×{num(b)}×{num(d)}",
            result=t(f"Ast = {num(Ast)} mm²", f"Ast = {num(Ast)} mm²"),
            references=[
                ref("IS456", "38.1", note=t("Flexural assumptions (stress block).", "बंकन अवधारणाएँ (प्रतिबल खंड)।")),
                ref("IS456", "Annex G-1.1", note=t("Mu = 0.87 fy Ast d (1 − Ast fy/(b d fck)).", "Mu = 0.87 fy Ast d (1 − Ast fy/(b d fck))।")),
            ],
        ))

        # Min / max steel --------------------------------------------------
        As_min = 0.85 * b * d / fy
        As_max = 0.04 * b * D
        steps.append(step(
            5, t("Minimum and maximum steel limits", "न्यूनतम एवं अधिकतम स्टील सीमाएँ"),
            formula="As,min = 0.85·b·d/fy ;  As,max = 0.04·b·D",
            substitution=f"= 0.85×{num(b)}×{num(d)}/{num(fy)} = {num(As_min)} mm² ;  0.04×{num(b)}×{num(D)} = {num(As_max)} mm²",
            result=t(f"As,min = {num(As_min)} mm², As,max = {num(As_max)} mm²",
                     f"As,min = {num(As_min)} mm², As,max = {num(As_max)} mm²"),
            references=[ref("IS456", "26.5.1.1", note=t("Tension reinforcement limits for beams.", "बीम हेतु तनन प्रबलन सीमाएँ।"))],
        ))

        Ast_prov_req = max(Ast, As_min)
        if Ast > As_max:
            warnings.append(t("Required steel exceeds As,max = 0.04 bD — increase section.",
                              "आवश्यक स्टील As,max = 0.04 bD से अधिक — परिच्छेद बढ़ाएँ।"))
        if Ast < As_min:
            steps.append(step(
                5.1, t("Minimum steel governs", "न्यूनतम स्टील नियंत्रक"),
                result=t(f"Ast < As,min, so provide Ast = {num(As_min)} mm².",
                         f"Ast < As,min, अतः Ast = {num(As_min)} mm² प्रदान करें।"),
                references=[ref("IS456", "26.5.1.1")],
            ))

        # Bar selection ----------------------------------------------------
        bars = select_bars(Ast_prov_req, breadth=b)
        if bars:
            steps.append(step(
                6, t("Bar arrangement (trial)", "सरिया विन्यास (परीक्षण)"),
                substitution=t(
                    f"Provide {bars['count']} nos. of {bars['dia']} mm dia bars",
                    f"{bars['dia']} मिमी व्यास की {bars['count']} सरियाँ प्रदान करें"),
                result=t(f"Provided area = {num(bars['area'])} mm² ≥ {num(Ast_prov_req)} mm²",
                         f"प्रदत्त क्षेत्रफल = {num(bars['area'])} mm² ≥ {num(Ast_prov_req)} mm²"),
                references=[ref("IS1786", "1.1", note=t("Deformed bar grades and nominal sizes.", "विकृत सरिया ग्रेड एवं नाममात्र आकार।")),
                            ref("IS456", "26.3.3", note=t("Spacing / clear distance between bars.", "सरियों के बीच अंतराल / स्पष्ट दूरी।"))],
            ))

        # Deflection (span/depth) -----------------------------------------
        if p.get("L") not in (None, ""):
            L_mm = float(p["L"]) * 1000.0
            ratio = L_mm / d
            base = {"cantilever": 7, "simply_supported": 20, "continuous": 26}.get(support, 20)
            ok = ratio <= base
            steps.append(step(
                7, t("Deflection check (span/depth)", "विक्षेप जाँच (विस्तृति/गहराई)"),
                formula="span/effective depth ≤ basic ratio (cantilever 7, SS 20, continuous 26)",
                substitution=f"span/d = {num(L_mm)}/{num(d)} = {num(ratio)} vs basic {base}",
                result=t(("OK — within basic span/depth ratio." if ok else
                          "Exceeds basic ratio — apply modification factor (Fig. 4) or increase depth."),
                         ("ठीक — मूल विस्तृति/गहराई अनुपात के भीतर।" if ok else
                          "मूल अनुपात से अधिक — संशोधन गुणक (चित्र 4) लागू करें या गहराई बढ़ाएँ।")),
                references=[ref("IS456", "23.2.1", note=t("Basic span/effective-depth ratios.", "मूल विस्तृति/प्रभावी-गहराई अनुपात।"))],
            ))
            if not ok:
                warnings.append(t("Deflection check not satisfied by basic ratio alone.",
                                  "केवल मूल अनुपात से विक्षेप जाँच संतुष्ट नहीं।"))

    summary = {
        "en": (f"Section {num(b)}×{num(D)} mm, d = {num(d)} mm, M{num(fck)} / Fe{num(fy)}. "
               f"Mu = {num(Mu)} kN·m vs Mu,lim = {num(Mu_lim_kNm)} kN·m."
               + ("" if Mu <= Mu_lim_kNm else " Section inadequate as singly reinforced.")),
        "hi": (f"परिच्छेद {num(b)}×{num(D)} मिमी, d = {num(d)} मिमी, M{num(fck)} / Fe{num(fy)}। "
               f"Mu = {num(Mu)} kN·m बनाम Mu,lim = {num(Mu_lim_kNm)} kN·m।"
               + ("" if Mu <= Mu_lim_kNm else " एकल-प्रबलित रूप में परिच्छेद अपर्याप्त।")),
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
