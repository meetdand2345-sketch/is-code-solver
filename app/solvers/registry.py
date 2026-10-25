"""Problem-type registry, dispatcher, and free-text question parser.

The registry is the single source of truth for:
  - which problem types exist
  - the form fields the UI should show for each
  - how a natural-language question is mapped to a type and its parameters
"""

import re

from . import column, development, flexure, loads, mix_design, shear, slab
from .common import t

# ---------------------------------------------------------------------------
# Solvers
# ---------------------------------------------------------------------------
SOLVERS = {
    flexure.TYPE: flexure.solve,
    slab.TYPE: slab.solve,
    shear.TYPE: shear.solve,
    development.TYPE: development.solve,
    loads.TYPE: loads.solve,
    column.TYPE: column.solve,
    mix_design.TYPE: mix_design.solve,
}


def _f(name, en, hi, unit="", required=True, ftype="number", options=None):
    d = {"name": name, "label": t(en, hi), "unit": unit, "required": required, "type": ftype}
    if options:
        d["options"] = options
    return d


def _opt(val, en, hi):
    return {"value": val, "label": t(en, hi)}


GRADE_OPTS = [_opt(v, f"M{v}", f"M{v}") for v in [15, 20, 25, 30, 35, 40]]
STEEL_OPTS = [_opt(v, f"Fe{v}", f"Fe{v}") for v in [250, 415, 500, 550]]

# ---------------------------------------------------------------------------
# Problem-type catalogue (drives both the API and the UI forms)
# ---------------------------------------------------------------------------
PROBLEM_TYPES = {
    flexure.TYPE: {
        "id": flexure.TYPE,
        "title": t("Beam — Flexural (bending) design", "बीम — बंकन अभिकल्प"),
        "summary": t("Singly reinforced rectangular beam; Mu vs Mu,lim; area of tension steel.",
                     "एकल-प्रबलित आयताकार बीम; Mu बनाम Mu,lim; तनन स्टील क्षेत्रफल।"),
        "fields": [
            _f("b", "Width b", "चौड़ाई b", "mm"),
            _f("D", "Overall depth D", "कुल गहराई D", "mm"),
            _f("d", "Effective depth d", "प्रभावी गहराई d", "mm", required=False),
            _f("fck", "Concrete grade fck", "कंक्रीट ग्रेड fck", "N/mm²", ftype="select", options=GRADE_OPTS),
            _f("fy", "Steel grade fy", "स्टील ग्रेड fy", "N/mm²", ftype="select", options=STEEL_OPTS),
            _f("Mu", "Factored moment Mu", "गुणित आघूर्ण Mu", "kN·m", required=False),
            _f("w", "or: load w", "या: भार w", "kN/m", required=False),
            _f("L", "or: span L", "या: विस्तृति L", "m", required=False),
            _f("support", "Support", "आलंबन", "", required=False, ftype="select",
               options=[_opt("simply_supported", "Simply supported", "शुद्धालंबित"),
                        _opt("continuous", "Continuous", "सतत"),
                        _opt("cantilever", "Cantilever", "कैंटिलीवर")]),
        ],
    },
    slab.TYPE: {
        "id": slab.TYPE,
        "title": t("One-way slab design", "एक-दिशीय स्लैब अभिकल्प"),
        "summary": t("Depth from span/depth, loads, Mu, main and distribution steel.",
                     "विस्तृति/गहराई से गहराई, भार, Mu, मुख्य एवं वितरण स्टील।"),
        "fields": [
            _f("L", "Effective span L", "प्रभावी विस्तृति L", "m"),
            _f("LL", "Imposed (live) load", "आरोपित (चल) भार", "kN/m²"),
            _f("ff", "Floor finish + services", "फर्श परिसज्जा + सेवाएँ", "kN/m²", required=False),
            _f("fck", "Concrete grade fck", "कंक्रीट ग्रेड fck", "N/mm²", ftype="select", options=GRADE_OPTS),
            _f("fy", "Steel grade fy", "स्टील ग्रेड fy", "N/mm²", ftype="select", options=STEEL_OPTS),
            _f("support", "Support", "आलंबन", "", required=False, ftype="select",
               options=[_opt("simply_supported", "Simply supported", "शुद्धालंबित"),
                        _opt("continuous", "Continuous", "सतत")]),
        ],
    },
    shear.TYPE: {
        "id": shear.TYPE,
        "title": t("Beam — Shear design", "बीम — अपरूपण अभिकल्प"),
        "summary": t("τv vs τc (Table 19) and τc,max (Table 20); stirrup spacing.",
                     "τv बनाम τc (तालिका 19) एवं τc,max (तालिका 20); रकाब अंतराल।"),
        "fields": [
            _f("b", "Width b", "चौड़ाई b", "mm"),
            _f("d", "Effective depth d", "प्रभावी गहराई d", "mm"),
            _f("Vu", "Factored shear Vu", "गुणित अपरूपण Vu", "kN"),
            _f("Ast", "Tension steel Ast", "तनन स्टील Ast", "mm²"),
            _f("fck", "Concrete grade fck", "कंक्रीट ग्रेड fck", "N/mm²", ftype="select", options=GRADE_OPTS),
            _f("fy", "Stirrup steel fy", "रकाब स्टील fy", "N/mm²", ftype="select", options=STEEL_OPTS),
            _f("stirrup_dia", "Stirrup dia", "रकाब व्यास", "mm", required=False),
            _f("legs", "Legs", "भुजाएँ", "", required=False),
        ],
    },
    development.TYPE: {
        "id": development.TYPE,
        "title": t("Development & lap length", "विकास एवं लैप लंबाई"),
        "summary": t("Ld = φσs/(4τbd); lap length for tension / compression.",
                     "Ld = φσs/(4τbd); तनाव / संपीडन हेतु लैप लंबाई।"),
        "fields": [
            _f("phi", "Bar diameter φ", "सरिया व्यास φ", "mm"),
            _f("fck", "Concrete grade fck", "कंक्रीट ग्रेड fck", "N/mm²", ftype="select", options=GRADE_OPTS),
            _f("fy", "Steel grade fy", "स्टील ग्रेड fy", "N/mm²", ftype="select", options=STEEL_OPTS),
            _f("bar_type", "Bar type", "सरिया प्रकार", "", required=False, ftype="select",
               options=[_opt("deformed", "Deformed (HYSD)", "विकृत (HYSD)"),
                        _opt("plain", "Plain (mild)", "सादा (माइल्ड)")]),
            _f("condition", "Condition", "स्थिति", "", required=False, ftype="select",
               options=[_opt("tension", "Tension", "तनाव"),
                        _opt("compression", "Compression", "संपीडन")]),
        ],
    },
    loads.TYPE: {
        "id": loads.TYPE,
        "title": t("Factored load / combinations", "गुणित भार / संयोजन"),
        "summary": t("γf from IS 456 Table 18; factored design load combinations.",
                     "IS 456 तालिका 18 से γf; गुणित अभिकल्प भार संयोजन।"),
        "fields": [
            _f("dl", "Dead load DL", "स्थायी भार DL", "kN/m or kN/m²"),
            _f("ll", "Imposed / live load LL", "आरोपित / चल भार LL", "kN/m or kN/m²"),
            _f("wl", "Wind / seismic WL/EL", "पवन / भूकंप WL/EL", "kN/m or kN/m²", required=False),
        ],
    },
    column.TYPE: {
        "id": column.TYPE,
        "title": t("Short axially loaded column", "लघु अक्षीय भारित स्तंभ"),
        "summary": t("Pu = 0.4 fck Ac + 0.67 fy Asc; required longitudinal steel.",
                     "Pu = 0.4 fck Ac + 0.67 fy Asc; आवश्यक अनुदैर्ध्य स्टील।"),
        "fields": [
            _f("b", "Width b", "चौड़ाई b", "mm"),
            _f("D", "Depth D", "गहराई D", "mm"),
            _f("fck", "Concrete grade fck", "कंक्रीट ग्रेड fck", "N/mm²", ftype="select", options=GRADE_OPTS),
            _f("fy", "Steel grade fy", "स्टील ग्रेड fy", "N/mm²", ftype="select", options=STEEL_OPTS),
            _f("Pu", "Factored axial load Pu", "गुणित अक्षीय भार Pu", "kN"),
            _f("Asc", "Provided steel Asc (optional)", "प्रदत्त स्टील Asc (वैकल्पिक)", "mm²", required=False),
        ],
    },
    mix_design.TYPE: {
        "id": mix_design.TYPE,
        "title": t("Concrete mix proportioning (IS 10262)", "कंक्रीट मिश्रण अनुपातन (IS 10262)"),
        "summary": t("Target strength, w/c, water, cement and aggregate contents per IS 10262:2019.",
                     "IS 10262:2019 अनुसार लक्ष्य सामर्थ्य, w/c, जल, सीमेंट एवं गिट्टी मात्रा।"),
        "fields": [
            _f("grade", "Grade of concrete", "कंक्रीट ग्रेड", "", ftype="select",
               options=[_opt(f"M{v}", f"M{v}", f"M{v}") for v in [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]]),
            _f("msa", "Nominal max. size of aggregate", "गिट्टी का नाममात्र अधिकतम आकार", "mm", ftype="select",
               options=[_opt(v, f"{v} mm", f"{v} मिमी") for v in [10, 20, 40]]),
            _f("slump", "Slump (workability)", "स्लंप (कार्यशीलता)", "mm", required=False),
            _f("zone", "Fine aggregate grading zone", "बारीक गिट्टी ग्रेडिंग ज़ोन", "", ftype="select",
               options=[_opt(z, f"Zone {z}", f"ज़ोन {z}") for z in ["I", "II", "III", "IV"]]),
            _f("exposure", "Exposure condition", "अनावरण स्थिति", "", ftype="select",
               options=[_opt("mild", "Mild", "सौम्य"), _opt("moderate", "Moderate", "मध्यम"),
                        _opt("severe", "Severe", "कठोर"), _opt("very_severe", "Very severe", "अति कठोर"),
                        _opt("extreme", "Extreme", "अति तीव्र")]),
            _f("agg_shape", "Coarse aggregate shape", "मोटी गिट्टी आकार", "", required=False, ftype="select",
               options=[_opt("angular", "Angular (crushed)", "कोणीय (कुचली)"),
                        _opt("sub_angular", "Sub-angular", "उप-कोणीय"),
                        _opt("gravel", "Gravel + crushed", "बजरी + कुचली"),
                        _opt("rounded", "Rounded gravel", "गोल बजरी")]),
            _f("wc", "Preliminary free w/c (from Fig. 1)", "प्रारंभिक मुक्त w/c (चित्र 1 से)", "", required=False),
            _f("admix", "Admixture water reduction", "मिश्रण जल कमी", "%", required=False),
        ],
    },
}


def list_problem_types():
    return list(PROBLEM_TYPES.values())


def solve(problem_type, params):
    fn = SOLVERS.get(problem_type)
    if not fn:
        raise KeyError(f"Unknown problem type: {problem_type}")
    return fn(params)


# ---------------------------------------------------------------------------
# Free-text question handling
# ---------------------------------------------------------------------------
# keyword -> weight (higher weight = more specific / stronger signal)
KEYWORDS = {
    flexure.TYPE: {"beam": 1, "flexure": 3, "bending": 2, "bending moment": 3,
                   "singly reinforced": 3, "ast": 2, "बीम": 1, "बंकन": 3, "आघूर्ण": 2},
    slab.TYPE: {"slab": 2, "one-way": 3, "one way": 3, "स्लैब": 2, "एक-दिशीय": 3},
    shear.TYPE: {"shear": 3, "stirrup": 3, "stirrups": 3, "nominal shear": 3,
                 "अपरूपण": 3, "रकाब": 3},
    development.TYPE: {"development length": 4, "lap length": 4, "lap": 3,
                       "anchorage": 3, "ld": 2, "विकास लंबाई": 4, "लैप": 3, "लंगर": 3},
    loads.TYPE: {"factored load": 4, "load combination": 4, "partial safety": 4,
                 "dead load": 1, "live load": 1, "गुणित भार": 4, "भार संयोजन": 4,
                 "स्थायी भार": 1, "चल भार": 1},
    column.TYPE: {"column": 2, "axial": 3, "स्तंभ": 2, "कॉलम": 2, "अक्षीय": 3},
    mix_design.TYPE: {"mix design": 4, "mix proportion": 4, "concrete mix": 4, "proportioning": 3,
                      "target strength": 3, "मिश्रण अनुपात": 4, "कंक्रीट मिश्रण": 4},
}

# parameter aliases -> canonical name (case-sensitive where it matters: d vs D)
ALIASES = {
    "b": "b", "B": "b", "breadth": "b", "width": "b", "Width": "b",
    "d": "d", "D": "D", "depth": "D", "Depth": "D", "overall": "D",
    "fck": "fck", "Fck": "fck", "ck": "fck", "m": "fck", "M": "fck",
    "fy": "fy", "Fy": "fy", "fe": "fy", "Fe": "fy",
    "Mu": "Mu", "mu": "Mu", "moment": "Mu", "Moment": "Mu",
    "L": "L", "l": "L", "span": "L", "Span": "L", "length": "L",
    "LL": "LL", "ll": "LL",
    "DL": "dl", "dl": "dl", "dead": "dl", "Dead": "dl",
    "WL": "wl", "wl": "wl", "wind": "wl", "Wind": "wl",
    "Vu": "Vu", "vu": "Vu", "shear": "Vu", "Shear": "Vu", "V": "Vu",
    "Ast": "Ast", "ast": "Ast", "As": "Ast", "as": "Ast",
    "phi": "phi", "Phi": "phi", "dia": "phi", "Dia": "phi",
    "diameter": "phi", "bar": "phi", "Bar": "phi",
    "Pu": "Pu", "pu": "Pu",
    "Asc": "Asc", "asc": "Asc",
    "w": "w", "W": "w",
    "ff": "ff", "finish": "ff",
}

_NUM = r"(\d+(?:\.\d+)?)"

# multi-word phrases normalised before token parsing
_PHRASES = [
    (r"development\s+length", "development length"),
    (r"lap\s+length", "lap length"),
    (r"live\s+load", "ll"),
    (r"dead\s+load", "dl"),
    (r"wind\s+load", "wl"),
    (r"imposed\s+load", "ll"),
    (r"floor\s+finish", "ff"),
    (r"effective\s+depth", "d"),
    (r"overall\s+depth", "D"),
]


def detect_type(question):
    """Return the best-matching problem type id, or None."""
    q = question.lower()
    best = None
    best_score = 0
    for ptype, words in KEYWORDS.items():
        score = sum(w for kw, w in words.items() if kw in q)
        if score > best_score:
            best_score = score
            best = ptype
    return best


def extract_params(question):
    """Extract named numeric parameters from a free-text question.

    Recognises patterns like: b=300, D 500 mm, Mu = 120 kNm, fck 25 N/mm2,
    6 mm dia, span 4 m, live load 3 kN/m2.  Returns canonical name -> value.
    """
    q = question
    params = {}

    # normalise multi-word phrases so the token parser sees a single key
    for pat, rep in _PHRASES:
        q = re.sub(pat, rep, q, flags=re.IGNORECASE)

    # pattern: <name> [=:] <number> [unit]
    # negative lookbehind avoids matching single letters inside units (kN/m2)
    pat = re.compile(
        r"(?<![A-Za-z0-9/])([A-Za-z_]{1,6})\s*[=:]?\s*" + _NUM +
        r"\s*(mm|m|kNm|kN·m|kN/m2|kN/m²|kN/m|kN|N/mm2|N/mm²|MPa|%|nos?\.?)?"
    )
    for m in pat.finditer(q):
        name = m.group(1)
        canon = ALIASES.get(name)
        if canon is None:
            canon = ALIASES.get(name.lower())
        if canon is None:
            continue
        val = float(m.group(2))
        if canon not in params:
            params[canon] = val

    # explicit "6 mm dia" style for bar diameter
    m2 = re.search(r"(\d+(?:\.\d+)?)\s*mm\s*(?:dia|diameter|bar|φ)", q, re.IGNORECASE)
    if m2 and "phi" not in params:
        params["phi"] = float(m2.group(1))

    # mix-design specific tokens
    mg = re.search(r"\bM\s?(\d{2,3})\b", q)
    if mg:
        params.setdefault("grade", f"M{int(mg.group(1))}")
    msa = re.search(r"(\d+(?:\.\d+)?)\s*mm\s+(?:nominal\s+)?(?:max\w*\s+)?(?:size\s+)?(?:of\s+)?(?:coarse\s+)?aggregate",
                    q, re.IGNORECASE)
    if msa:
        params.setdefault("msa", float(msa.group(1)))
    mz = re.search(r"zone[\s\-:]*([IVX]+)", q, re.IGNORECASE)
    if mz:
        params.setdefault("zone", mz.group(1).upper())
    me = re.search(r"\b(very\s*severe|severe|moderate|mild|extreme)\b", q, re.IGNORECASE)
    if me:
        params.setdefault("exposure", re.sub(r"\s+", "_", me.group(1).lower()))

    # bar_type / condition / support hints
    if re.search(r"plain|mild", q, re.IGNORECASE):
        params.setdefault("bar_type", "plain")
    if re.search(r"deformed|hysd|tor|tmt", q, re.IGNORECASE):
        params.setdefault("bar_type", "deformed")
    if re.search(r"compression", q, re.IGNORECASE):
        params.setdefault("condition", "compression")
    if re.search(r"cantilever", q, re.IGNORECASE):
        params.setdefault("support", "cantilever")
    elif re.search(r"continuous", q, re.IGNORECASE):
        params.setdefault("support", "continuous")
    elif re.search(r"simply\s*supported", q, re.IGNORECASE):
        params.setdefault("support", "simply_supported")

    return params


def required_fields(problem_type):
    pt = PROBLEM_TYPES.get(problem_type)
    if not pt:
        return []
    return [f for f in pt["fields"] if f.get("required")]


def missing_fields(problem_type, params):
    """Fields that are required but absent (handles the flexure OR-condition)."""
    missing = []
    for f in required_fields(problem_type):
        name = f["name"]
        if name in ("Mu", "w", "L"):
            continue
        if params.get(name) in (None, ""):
            missing.append(f)
    if problem_type == flexure.TYPE:
        has_mu = params.get("Mu") not in (None, "")
        has_wl = params.get("w") not in (None, "") and params.get("L") not in (None, "")
        if not (has_mu or has_wl):
            missing.append(PROBLEM_TYPES[flexure.TYPE]["fields"][5])  # Mu field
    return missing
