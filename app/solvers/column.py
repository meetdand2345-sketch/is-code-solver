"""Short axially loaded RC column (IS 456 Cl. 39.3)."""

from .common import collect_references, inp, num, ref, step, t

TYPE = "column_axial"

TITLE = t("Short Axially Loaded RC Column", "लघु अक्षीय भारित प्रबलित कंक्रीट स्तंभ")


def solve(p):
    """p keys: b, D, fck, fy, Pu (kN). Optional Asc (mm2) to check capacity."""
    b = float(p["b"])
    D = float(p["D"])
    fck = float(p["fck"])
    fy = float(p["fy"])
    Pu = float(p["Pu"])                      # kN
    Asc_in = p.get("Asc")

    Ag = b * D
    inputs = [
        inp(t("Width b", "चौड़ाई b"), num(b), "mm"),
        inp(t("Depth D", "गहराई D"), num(D), "mm"),
        inp(t("Concrete grade fck", "कंक्रीट ग्रेड fck"), num(fck), "N/mm²"),
        inp(t("Steel grade fy", "स्टील ग्रेड fy"), num(fy), "N/mm²"),
        inp(t("Factored axial load Pu", "गुणित अक्षीय भार Pu"), num(Pu), "kN"),
    ]
    if Asc_in not in (None, ""):
        inputs.append(inp(t("Provided steel Asc", "प्रदत्त स्टील Asc"), num(float(Asc_in)), "mm²"))

    steps = []
    warnings = []

    steps.append(step(
        1, t("Gross area and steel limits", "सकल क्षेत्रफल एवं स्टील सीमाएँ"),
        formula="Ag = b·D ;  0.8%·Ag ≤ Asc ≤ 6%·Ag",
        substitution=f"Ag = {num(b)}×{num(D)} = {num(Ag,0)} mm² ; limits = {num(0.008*Ag,0)} to {num(0.06*Ag,0)} mm²",
        result=t(f"Ag = {num(Ag,0)} mm², Asc limits {num(0.008*Ag,0)}–{num(0.06*Ag,0)} mm²",
                 f"Ag = {num(Ag,0)} mm², Asc सीमाएँ {num(0.008*Ag,0)}–{num(0.06*Ag,0)} mm²"),
        references=[ref("IS456", "26.5.3.1", note=t("Longitudinal steel in columns: 0.8% to 6% of gross area.",
                                                    "स्तंभ में अनुदैर्ध्य स्टील: सकल क्षेत्रफल का 0.8% से 6%।"))],
    ))

    Pu_N = Pu * 1000.0
    if Asc_in not in (None, ""):
        Asc = float(Asc_in)
        Ac = Ag - Asc
        Pu_cap = 0.4 * fck * Ac + 0.67 * fy * Asc
        steps.append(step(
            2, t("Axial load capacity of the section", "परिच्छेद की अक्षीय भार क्षमता"),
            formula="Pu = 0.4·fck·Ac + 0.67·fy·Asc ,  Ac = Ag − Asc",
            substitution=f"= 0.4×{num(fck)}×{num(Ac,0)} + 0.67×{num(fy)}×{num(Asc)} = {num(Pu_cap,0)} N",
            result=t(f"Capacity = {num(Pu_cap/1000.0)} kN vs demand {num(Pu)} kN → "
                     + ("SAFE" if Pu_cap >= Pu_N else "UNSAFE"),
                     f"क्षमता = {num(Pu_cap/1000.0)} kN बनाम माँग {num(Pu)} kN → "
                     + ("सुरक्षित" if Pu_cap >= Pu_N else "असुरक्षित")),
            references=[ref("IS456", "39.3", note=t("Short axially loaded members in compression.",
                                                    "संपीडन में लघु अक्षीय भारित सदस्य।"))],
        ))
        if Pu_cap < Pu_N:
            warnings.append(t("Section capacity is less than the applied load — increase size or steel.",
                              "परिच्छेद की क्षमता लागू भार से कम है — आकार या स्टील बढ़ाएँ।"))
    else:
        # solve for Asc
        denom = 0.67 * fy - 0.4 * fck
        Asc = (Pu_N - 0.4 * fck * Ag) / denom
        Asc_min = 0.008 * Ag
        Asc_max = 0.06 * Ag
        Asc_req = max(Asc, Asc_min)
        if Asc_req > Asc_max:
            warnings.append(t("Required steel exceeds 6% of gross area — increase the column size.",
                              "आवश्यक स्टील सकल क्षेत्रफल के 6% से अधिक — स्तंभ का आकार बढ़ाएँ।"))
        steps.append(step(
            2, t("Required longitudinal steel", "आवश्यक अनुदैर्ध्य स्टील"),
            formula="Asc = (Pu − 0.4·fck·Ag) / (0.67·fy − 0.4·fck) ;  ≥ 0.8%·Ag",
            substitution=f"= ({num(Pu_N,0)} − 0.4×{num(fck)}×{num(Ag,0)})/(0.67×{num(fy)} − 0.4×{num(fck)}) = {num(Asc,0)} mm²",
            result=t(f"Required Asc = {num(Asc_req,0)} mm² ({num(100*Asc_req/Ag,2)}% of Ag)",
                     f"आवश्यक Asc = {num(Asc_req,0)} mm² (Ag का {num(100*Asc_req/Ag,2)}%)"),
            references=[ref("IS456", "39.3"), ref("IS456", "26.5.3.1")],
        ))

    summary = {
        "en": f"Column {num(b)}×{num(D)} mm, M{num(fck)}/Fe{num(fy)}, Pu = {num(Pu)} kN.",
        "hi": f"स्तंभ {num(b)}×{num(D)} मिमी, M{num(fck)}/Fe{num(fy)}, Pu = {num(Pu)} kN।",
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
