"""Concrete mix proportioning per IS 10262:2019 (ordinary / standard grades)."""

from .common import collect_references, inp, num, ref, step, t

TYPE = "mix_design"

TITLE = t("Concrete Mix Proportioning (IS 10262:2019)",
          "कंक्रीट मिश्रण अनुपातन (IS 10262:2019)")

# --- IS 10262:2019 Table 2 — assumed standard deviation S (N/mm^2) ---------
def _std_dev(fck):
    if fck <= 15:
        return 3.5
    if fck <= 25:
        return 4.0
    if fck <= 60:
        return 5.0
    return 6.0


# --- IS 10262:2019 Table 1 — factor X (N/mm^2) ------------------------------
def _factor_x(fck):
    if fck <= 15:
        return 5.0
    if fck <= 25:
        return 5.5
    if fck <= 60:
        return 6.5
    return 8.0


# --- IS 10262:2019 Table 3 — entrapped air (fraction of volume) ------------
_AIR = {10: 0.015, 20: 0.010, 40: 0.008}

# --- IS 10262:2019 Table 4 — water content (kg/m^3), angular, 50 mm slump --
_WATER = {10: 208.0, 20: 186.0, 40: 165.0}

# --- IS 10262:2019 Table 5 — volume of CA per unit volume of total agg @ w/c 0.5
_CA_VOL = {
    10: {"IV": 0.54, "III": 0.52, "II": 0.50, "I": 0.48},
    20: {"IV": 0.66, "III": 0.64, "II": 0.62, "I": 0.60},
    40: {"IV": 0.73, "III": 0.72, "II": 0.71, "I": 0.69},
}

# --- IS 456:2000 Table 5 — durability limits for reinforced concrete -------
_DURABILITY = {
    "mild":        {"min_cement": 300, "max_wc": 0.55, "min_grade": "M20"},
    "moderate":    {"min_cement": 300, "max_wc": 0.50, "min_grade": "M25"},
    "severe":      {"min_cement": 320, "max_wc": 0.45, "min_grade": "M30"},
    "very_severe": {"min_cement": 340, "max_wc": 0.45, "min_grade": "M35"},
    "extreme":     {"min_cement": 360, "max_wc": 0.40, "min_grade": "M40"},
}

_SHAPE_DROP = {"angular": 0.0, "sub_angular": 10.0, "gravel": 15.0, "rounded": 20.0}


def _parse_grade(g):
    """Accept 'M25', '25' or 25 -> 25."""
    if isinstance(g, str):
        g = g.strip().upper().lstrip("M")
    return int(float(g))


def solve(p):
    fck = _parse_grade(p["grade"])
    msa = int(float(p.get("msa") or 20))
    if msa not in _WATER:
        msa = min(_WATER, key=lambda k: abs(k - msa))
    slump = float(p.get("slump") or 50)
    zone = (p.get("zone") or "II").upper().replace("ZONE", "").strip()
    if zone not in ("I", "II", "III", "IV"):
        zone = "II"
    exposure = (p.get("exposure") or "moderate").lower()
    if exposure not in _DURABILITY:
        exposure = "moderate"
    shape = (p.get("agg_shape") or "angular").lower()
    admix = float(p.get("admix") or 0)          # % water reduction from admixture
    sg_cement = float(p.get("sg_cement") or 3.15)
    sg_ca = float(p.get("sg_ca") or 2.74)
    sg_fa = float(p.get("sg_fa") or 2.65)
    wc_in = p.get("wc")

    dur = _DURABILITY[exposure]
    steps = []
    warnings = []

    inputs = [
        inp(t("Grade of concrete", "कंक्रीट ग्रेड"), f"M{fck}", ""),
        inp(t("Nominal max. size of aggregate", "गिट्टी का नाममात्र अधिकतम आकार"), num(msa), "mm"),
        inp(t("Slump (workability)", "स्लंप (कार्यशीलता)"), num(slump), "mm"),
        inp(t("Fine aggregate grading zone", "बारीक गिट्टी ग्रेडिंग ज़ोन"), zone, ""),
        inp(t("Exposure condition", "अनावरण स्थिति"), exposure.replace("_", " "), ""),
        inp(t("Coarse aggregate shape", "मोटी गिट्टी आकार"), shape.replace("_", "-"), ""),
    ]
    if admix:
        inputs.append(inp(t("Admixture water reduction", "मिश्रण जल कमी"), num(admix), "%"))

    # 1. target mean strength ------------------------------------------------
    S = _std_dev(fck)
    X = _factor_x(fck)
    f_target = max(fck + 1.65 * S, fck + X)
    steps.append(step(
        1, t("Target mean strength", "लक्ष्य माध्य सामर्थ्य"),
        formula="f'ck = fck + 1.65·S   or   fck + X   (whichever is higher)",
        substitution=f"fck = {num(fck)} N/mm²;  S (Table 2) = {num(S)};  X (Table 1) = {num(X)};  "
                     f"fck+1.65S = {num(fck + 1.65*S)};  fck+X = {num(fck + X)}",
        result=t(f"Target mean strength f'ck = {num(f_target)} N/mm²",
                 f"लक्ष्य माध्य सामर्थ्य f'ck = {num(f_target)} N/mm²"),
        references=[ref("IS10262", "4.2", table="Tables 1 & 2",
                        note=t("Target strength, factor X and assumed standard deviation.",
                               "लक्ष्य सामर्थ्य, गुणक X एवं अनुमानित मानक विचलन।"))],
    ))

    # 2. air content ---------------------------------------------------------
    air = _AIR[msa]
    steps.append(step(
        2, t("Entrapped air content", "फँसी वायु अंश"),
        formula="Entrapped air (Table 3) for non-air-entrained concrete",
        substitution=f"{msa} mm aggregate → {num(air*100)}% of concrete volume",
        result=t(f"Air = {num(air*100)}%", f"वायु = {num(air*100)}%"),
        references=[ref("IS10262", "5.2", table="Table 3")],
    ))

    # 3. water-cement ratio --------------------------------------------------
    if wc_in not in (None, ""):
        wc_prelim = float(wc_in)
        wc_source = t(f"given as {num(wc_prelim,3)}", f"दिया गया {num(wc_prelim,3)}")
    else:
        wc_prelim = dur["max_wc"]
        wc_source = t(f"taken as the durability limit {num(dur['max_wc'],2)} (confirm from Fig. 1)",
                      f"टिकाऊपन सीमा {num(dur['max_wc'],2)} के रूप में लिया गया (चित्र 1 से पुष्टि करें)")
        warnings.append(t(
            "Preliminary w/c not supplied — the durability maximum was used as a starting value. "
            "Read the strength-based w/c from IS 10262 Fig. 1 for the actual cement and finalise by trials.",
            "प्रारंभिक w/c नहीं दिया गया — टिकाऊपन अधिकतम को प्रारंभिक मान लिया गया। "
            "वास्तविक सीमेंट हेतु IS 10262 चित्र 1 से सामर्थ्य-आधारित w/c पढ़ें तथा परीक्षणों से अंतिम रूप दें।"))
    wc = min(wc_prelim, dur["max_wc"])
    steps.append(step(
        3, t("Water-cement ratio", "जल-सीमेंट अनुपात"),
        formula="Adopt the lower of: preliminary free w/c  and  durability maximum w/c (IS 456 Table 5)",
        substitution=f"preliminary = {num(wc_prelim,3)} ({wc_source['en']});  "
                     f"durability max ({exposure.replace('_',' ')}) = {num(dur['max_wc'],2)}",
        result=t(f"Adopted w/c = {num(wc,3)}", f"अपनाया गया w/c = {num(wc,3)}"),
        references=[ref("IS10262", "5.1", note=t("Water-cement ratio selection and durability check.", "जल-सीमेंट अनुपात चयन एवं टिकाऊपन जाँच।")),
                    ref("IS456", "Table 5", note=t("Max free w/c and min cement by exposure.", "अनावरण अनुसार अधिकतम मुक्त w/c एवं न्यूनतम सीमेंट।"))],
    ))

    # 4. water content -------------------------------------------------------
    base = _WATER[msa]
    slump_factor = 1 + 0.03 * ((slump - 50.0) / 25.0)
    shape_drop = _SHAPE_DROP.get(shape, 0.0)
    water = base * slump_factor - shape_drop
    water_after_admix = water * (1 - admix / 100.0)
    steps.append(step(
        4, t("Water content", "जल मात्रा"),
        formula="water = Table 4 base ± 3% per 25 mm slump − shape correction − admixture reduction",
        substitution=f"base ({msa} mm) = {num(base)} kg/m³;  slump {num(slump)} mm → ×{num(slump_factor,3)};  "
                     f"shape ({shape.replace('_','-')}) −{num(shape_drop)} kg"
                     + (f";  admixture −{num(admix)}%" if admix else ""),
        result=t(f"Water content = {num(water_after_admix)} kg/m³",
                 f"जल मात्रा = {num(water_after_admix)} kg/m³"),
        references=[ref("IS10262", "5.3", table="Table 4",
                        note=t("Water content and slump/shape adjustments.", "जल मात्रा तथा स्लंप/आकार समायोजन।"))],
    ))

    # 5. cement content ------------------------------------------------------
    cement_calc = water_after_admix / wc
    cement = max(cement_calc, dur["min_cement"])
    if cement_calc < dur["min_cement"]:
        warnings.append(t(
            f"Calculated cement content ({num(cement_calc)} kg/m³) is below the durability minimum "
            f"({num(dur['min_cement'])} kg/m³) — the minimum governs.",
            f"परिकलित सीमेंट मात्रा ({num(cement_calc)} kg/m³) टिकाऊपन न्यूनतम "
            f"({num(dur['min_cement'])} kg/m³) से कम है — न्यूनतम नियंत्रक है।"))
    steps.append(step(
        5, t("Cement content", "सीमेंट मात्रा"),
        formula="cement = water / (w/c)   ;  adopt the greater of this and the durability minimum",
        substitution=f"= {num(water_after_admix)}/{num(wc,3)} = {num(cement_calc)} kg/m³;  "
                     f"durability min = {num(dur['min_cement'])} kg/m³",
        result=t(f"Cement content = {num(cement)} kg/m³", f"सीमेंट मात्रा = {num(cement)} kg/m³"),
        references=[ref("IS10262", "5.4", note=t("Cement content and durability minimum.", "सीमेंट मात्रा एवं टिकाऊपन न्यूनतम।")),
                    ref("IS456", "Table 5")],
    ))

    # 6. coarse aggregate proportion ----------------------------------------
    p_ca_base = _CA_VOL[msa][zone]
    p_ca = p_ca_base + 0.01 * ((0.5 - wc) / 0.05)
    steps.append(step(
        6, t("Volume of coarse aggregate per unit volume of total aggregate",
             "कुल गिट्टी के प्रति इकाई आयतन मोटी गिट्टी का आयतन"),
        formula="p = Table 5 value (at w/c 0.5) + 0.01 × (0.5 − w/c)/0.05",
        substitution=f"Table 5 ({msa} mm, Zone {zone}) = {num(p_ca_base,2)};  "
                     f"correction = 0.01×({num(0.5,2)}−{num(wc,3)})/0.05 = {num(0.01*(0.5-wc)/0.05,3)}",
        result=t(f"p = {num(p_ca,3)}", f"p = {num(p_ca,3)}"),
        references=[ref("IS10262", "5.5", table="Table 5",
                        note=t("CA proportion by zone and MSA; adjust with w/c.", "ज़ोन एवं MSA अनुसार CA अनुपात; w/c के साथ समायोजित।"))],
    ))

    # 7. absolute-volume aggregate estimation --------------------------------
    v_cement = cement / sg_cement / 1000.0
    v_water = water_after_admix / 1000.0
    v_air = air
    v_agg = 1.0 - (v_cement + v_water + v_air)
    v_ca = v_agg * p_ca
    v_fa = v_agg * (1 - p_ca)
    mass_ca = v_ca * sg_ca * 1000.0
    mass_fa = v_fa * sg_fa * 1000.0
    steps.append(step(
        7, t("Fine and coarse aggregate contents (absolute volume)",
             "बारीक एवं मोटी गिट्टी मात्रा (निरपेक्ष आयतन)"),
        formula="Vagg = 1 − (Vc + Vw + Vair) ;  Vca = Vagg·p ;  Vfa = Vagg·(1−p) ;  mass = V·Sg·1000",
        substitution=f"Vc = {num(cement)}/{num(sg_cement)}/1000 = {num(v_cement,4)} m³;  "
                     f"Vw = {num(v_water,4)} m³;  Vair = {num(v_air,4)} m³;  Vagg = {num(v_agg,4)} m³;  "
                     f"CA = {num(v_ca,4)}×{num(sg_ca)}×1000 = {num(mass_ca,0)} kg;  "
                     f"FA = {num(v_fa,4)}×{num(sg_fa)}×1000 = {num(mass_fa,0)} kg",
        result=t(f"Coarse aggregate = {num(mass_ca,0)} kg/m³, Fine aggregate = {num(mass_fa,0)} kg/m³",
                 f"मोटी गिट्टी = {num(mass_ca,0)} kg/m³, बारीक गिट्टी = {num(mass_fa,0)} kg/m³"),
        references=[ref("IS10262", "5.7", note=t("Absolute-volume method for aggregates.", "गिट्टी हेतु निरपेक्ष-आयतन विधि।"))],
    ))

    # 8. proportions ---------------------------------------------------------
    ratios = f"1 : {num(mass_fa/cement,2)} : {num(mass_ca/cement,2)}  (cement : FA : CA), w/c = {num(wc,2)}"
    steps.append(step(
        8, t("Proportion of ingredients (by mass)", "घटकों का अनुपात (द्रव्यमान अनुसार)"),
        formula="Divide each mass by the cement mass",
        result=t(ratios, ratios),
        references=[ref("IS10262", "5.7"), ref("IS10262", "5.8",
                    note=t("Confirm by trial mixes (±10% w/c).", "परीक्षण मिश्रण (±10% w/c) से पुष्टि करें।"))],
    ))

    mix_table = [
        {"item": t("Cement", "सीमेंट"), "value": num(cement, 0), "unit": "kg/m³"},
        {"item": t("Water", "जल"), "value": num(water_after_admix, 0), "unit": "kg/m³"},
        {"item": t("Fine aggregate", "बारीक गिट्टी"), "value": num(mass_fa, 0), "unit": "kg/m³"},
        {"item": t("Coarse aggregate", "मोटी गिट्टी"), "value": num(mass_ca, 0), "unit": "kg/m³"},
    ]

    summary = {
        "en": (f"M{fck}, {msa} mm aggregate, Zone {zone}, {exposure.replace('_',' ')} exposure. "
               f"Target strength {num(f_target)} N/mm²; w/c {num(wc,2)}; "
               f"cement {num(cement,0)}, water {num(water_after_admix,0)}, "
               f"FA {num(mass_fa,0)}, CA {num(mass_ca,0)} kg/m³."),
        "hi": (f"M{fck}, {msa} मिमी गिट्टी, ज़ोन {zone}, {exposure.replace('_',' ')} अनावरण। "
               f"लक्ष्य सामर्थ्य {num(f_target)} N/mm²; w/c {num(wc,2)}; "
               f"सीमेंट {num(cement,0)}, जल {num(water_after_admix,0)}, "
               f"बारीक गिट्टी {num(mass_fa,0)}, मोटी गिट्टी {num(mass_ca,0)} kg/m³।"),
    }

    return {
        "type": TYPE,
        "title": TITLE,
        "inputs": inputs,
        "steps": steps,
        "mix_table": mix_table,
        "summary": summary,
        "references": collect_references(steps),
        "warnings": warnings,
    }
