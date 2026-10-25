"""Development length and lap length of reinforcement (IS 456 Cl. 26.2)."""

from .common import collect_references, design_bond_stress, inp, num, ref, step, t

TYPE = "development"

TITLE = t("Development Length and Lap Length",
          "विकास लंबाई एवं लैप लंबाई")


def solve(p):
    """p keys: phi (mm), fck, fy, optional bar_type ('deformed'|'plain'),
    condition ('tension'|'compression')."""
    phi = float(p["phi"])
    fck = float(p["fck"])
    fy = float(p["fy"])
    bar_type = p.get("bar_type", "deformed")
    condition = p.get("condition", "tension")

    inputs = [
        inp(t("Bar diameter φ", "सरिया व्यास φ"), num(phi), "mm"),
        inp(t("Concrete grade fck", "कंक्रीट ग्रेड fck"), num(fck), "N/mm²"),
        inp(t("Steel grade fy", "स्टील ग्रेड fy"), num(fy), "N/mm²"),
        inp(t("Bar type", "सरिया प्रकार"),
            t("deformed" if bar_type == "deformed" else "plain",
              "विकृत" if bar_type == "deformed" else "सादा"), ""),
        inp(t("Condition", "स्थिति"),
            t("tension" if condition == "tension" else "compression",
              "तनाव" if condition == "tension" else "संपीडन"), ""),
    ]

    steps = []

    # 1. bond stress
    tbd0 = design_bond_stress(fck)
    factor = 1.0
    notes = []
    if bar_type == "deformed":
        factor *= 1.6
        notes.append(t("×1.6 for deformed bars (IS 1786)", "विकृत सरियों हेतु ×1.6 (IS 1786)"))
    if condition == "compression":
        factor *= 1.25
        notes.append(t("×1.25 for bars in compression", "संपीडन में सरियों हेतु ×1.25"))
    tbd = tbd0 * factor

    steps.append(step(
        1, t("Design bond stress τbd", "अभिकल्प बंध प्रतिबल τbd"),
        formula="τbd = τbd(basic) × 1.6 (deformed) × 1.25 (compression)",
        substitution=f"basic τbd (M{num(fck)}) = {num(tbd0)} N/mm² ; "
                     + " ; ".join(n["en"] for n in notes) + f" ; τbd = {num(tbd)} N/mm²",
        result=t(f"τbd = {num(tbd)} N/mm²", f"τbd = {num(tbd)} N/mm²"),
        references=[ref("IS456", "26.2.1.1",
                        note=t("Basic values: M20 1.2, M25 1.4, M30 1.5, M35 1.7, M40+ 1.9 N/mm².",
                               "मूल मान: M20 1.2, M25 1.4, M30 1.5, M35 1.7, M40+ 1.9 N/mm²।"))],
    ))

    # 2. development length
    sigma_s = 0.87 * fy
    Ld = phi * sigma_s / (4.0 * tbd)
    steps.append(step(
        2, t("Development length Ld", "विकास लंबाई Ld"),
        formula="Ld = φ·σs / (4·τbd)   with σs = 0.87·fy (limit state)",
        substitution=f"Ld = {num(phi)}×{num(sigma_s)}/(4×{num(tbd)}) = {num(Ld)} mm",
        result=t(f"Ld = {num(Ld)} mm ≈ {num(Ld/phi,1)}·φ", f"Ld = {num(Ld)} मिमी ≈ {num(Ld/phi,1)}·φ"),
        references=[ref("IS456", "26.2.1", note=t("Development length of bars.", "सरियों की विकास लंबाई।"))],
    ))

    # 3. lap length
    if condition == "tension":
        lap = max(Ld, 30.0 * phi)
        lap_note = t("Lap (tension) = max(Ld, 30φ)", "लैप (तनाव) = max(Ld, 30φ)")
    else:
        lap = max(Ld, 24.0 * phi)
        lap_note = t("Lap (compression) = max(Ld, 24φ)", "लैप (संपीडन) = max(Ld, 24φ)")

    steps.append(step(
        3, t("Lap length", "लैप लंबाई"),
        formula="tension: max(Ld, 30φ) ;  compression: max(Ld, 24φ)",
        substitution=f"max({num(Ld)}, {num(30*phi if condition=='tension' else 24*phi)}) = {num(lap)} mm",
        result=t(f"Lap length = {num(lap)} mm", f"लैप लंबाई = {num(lap)} मिमी"),
        references=[ref("IS456", "26.2.5.1",
                        note=t("Lap splices: tension ≥ Ld or 30φ; compression ≥ Ld or 24φ.",
                               "लैप जोड़: तनाव ≥ Ld या 30φ; संपीडन ≥ Ld या 24φ।"))],
    ))

    summary = {
        "en": f"φ{num(phi)} ({bar_type}, {condition}): τbd = {num(tbd)} N/mm², Ld = {num(Ld)} mm, lap = {num(lap)} mm.",
        "hi": f"φ{num(phi)} ({'विकृत' if bar_type=='deformed' else 'सादा'}, {'तनाव' if condition=='tension' else 'संपीडन'}): τbd = {num(tbd)} N/mm², Ld = {num(Ld)} मिमी, लैप = {num(lap)} मिमी।",
    }

    return {
        "type": TYPE,
        "title": TITLE,
        "inputs": inputs,
        "steps": steps,
        "summary": summary,
        "references": collect_references(steps),
        "warnings": [],
    }
