"""
IS Code library.

A small, curated store of Indian Standard codes relevant to structural
analysis / RCC design. Each code carries:
  - metadata (number, title, revision, committee, scope) in English + Hindi
  - links to open/read the code (public reference copy, official BIS source,
    and a clause browser)
  - an index of the clauses this application actually cites, each with a
    short bilingual summary.

Links point to publicly available reference copies and to the official BIS
sources. The authoritative text is always the one published by the Bureau of
Indian Standards (BIS); the public copies are provided for convenience.
"""

# ---------------------------------------------------------------------------
# Link targets (reused across codes)
# ---------------------------------------------------------------------------
BIS_HOME = "https://www.services.bis.gov.in/"
BIS_ESEARCH = "https://standardsbis.bsbedge.com/BIS_SearchStandard.aspx?Standard_Number={num}&id=0"
LAW_456 = "https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf"
LAW_1786 = "https://law.resource.org/pub/in/bis/S03/is.1786.2008.pdf"
LAW_CED37 = "https://law.resource.org/pub/in/bis/manifest.ced.37.html"
INFRALENS_456 = "https://infralens.in/code/IS-456-2000/clauses"
ARCHIVE_10262 = "https://archive.org/details/gov.in.is.10262.2019"
BIS_10262 = "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/knowyourstandards/Indian_standards/isdetails/MTA4Mw=="
INFRALENS_10262 = "https://infralens.in/code/IS-10262-2019"


def _links(bis_num, public=None, clause_browser=None):
    links = []
    if public:
        links.append(
            {
                "kind": "public",
                "label": {"en": "Open public reference copy (PDF)", "hi": "सार्वजनिक संदर्भ प्रति खोलें (PDF)"},
                "url": public,
            }
        )
    links.append(
        {
            "kind": "official",
            "label": {"en": "Official BIS source (buy / authentic)", "hi": "आधिकारिक BIS स्रोत (क्रय / प्रामाणिक)"},
            "url": BIS_ESEARCH.format(num=bis_num),
        }
    )
    if clause_browser:
        links.append(
            {
                "kind": "clauses",
                "label": {"en": "Browse clause by clause", "hi": "खंड-दर-खंड देखें"},
                "url": clause_browser,
            }
        )
    return links


# ---------------------------------------------------------------------------
# Codes
# ---------------------------------------------------------------------------
CODES = {
    "IS456": {
        "id": "IS456",
        "number": "IS 456:2000",
        "title": {
            "en": "Plain and Reinforced Concrete — Code of Practice",
            "hi": "सादा एवं प्रबलित कंक्रीट — कार्य संहिता",
        },
        "revision": "Fourth Revision (incorporating Amendments 1 & 2)",
        "committee": "CED 2 — Cement and Concrete",
        "scope": {
            "en": "The core design code for reinforced-concrete structures in India. "
            "Covers materials, durability, analysis, and design by the limit state method "
            "(flexure, compression, shear, torsion, deflection, cracking).",
            "hi": "भारत में प्रबलित कंक्रीट संरचनाओं की मुख्य डिज़ाइन संहिता। सामग्री, टिकाऊपन, "
            "विश्लेषण तथा सीमा-अवस्था विधि द्वारा डिज़ाइन (बंकन, संपीडन, अपरूपण, ऐंठन, विक्षेप, "
            "दरार) को समाहित करती है।",
        },
        "links": _links("is456", public=LAW_456, clause_browser=INFRALENS_456),
        "clauses": [
            {
                "number": "22.2",
                "title": {"en": "Effective span", "hi": "प्रभावी विस्तृति"},
                "summary": {
                    "en": "Effective span of a simply supported beam/slab = clear span + effective depth, or centre-to-centre of supports, whichever is less.",
                    "hi": "शुद्धालंबित बीम/स्लैब की प्रभावी विस्तृति = स्पष्ट विस्तृति + प्रभावी गहराई, या आलंबों के केंद्र-से-केंद्र दूरी, इनमें जो कम हो।",
                },
            },
            {
                "number": "23.2.1",
                "title": {"en": "Span/effective-depth ratios (deflection control)", "hi": "विस्तृति/प्रभावी-गहराई अनुपात (विक्षेप नियंत्रण)"},
                "summary": {
                    "en": "Basic span/depth ratios: cantilever 7, simply supported 20, continuous 26 (modified by steel-area factor of Fig. 4).",
                    "hi": "मूल विस्तृति/गहराई अनुपात: कैंटिलीवर 7, शुद्धालंबित 20, सतत 26 (चित्र 4 के स्टील-क्षेत्रफल गुणक से संशोधित)।",
                },
            },
            {
                "number": "24.1",
                "title": {"en": "Solid slabs — general", "hi": "ठोस स्लैब — सामान्य"},
                "summary": {
                    "en": "Beam provisions apply to slabs; for two-way slabs the shorter span governs the span/depth ratio.",
                    "hi": "बीम के प्रावधान स्लैब पर भी लागू; द्वि-दिशीय स्लैब में छोटी विस्तृति विस्तृति/गहराई अनुपात निर्धारित करती है।",
                },
            },
            {
                "number": "26.2.1",
                "title": {"en": "Development length of bars", "hi": "सरियों की विकास लंबाई"},
                "summary": {
                    "en": "Development length Ld = φ σs / (4 τbd). Bond stress τbd taken from Cl. 26.2.1.1.",
                    "hi": "विकास लंबाई Ld = φ σs / (4 τbd)। बंध प्रतिबल τbd खंड 26.2.1.1 से लिया जाता है।",
                },
            },
            {
                "number": "26.2.1.1",
                "title": {"en": "Design bond stress", "hi": "अभिकल्प बंध प्रतिबल"},
                "summary": {
                    "en": "Design bond stress for plain bars in tension: M20 1.2, M25 1.4, M30 1.5, M35 1.7, M40+ 1.9 N/mm². Increase by 60% for deformed bars, and by 25% for bars in compression.",
                    "hi": "तनाव में सादी सरियों के लिए अभिकल्प बंध प्रतिबल: M20 1.2, M25 1.4, M30 1.5, M35 1.7, M40+ 1.9 N/mm²। विकृत (deformed) सरियों के लिए 60% तथा संपीडन में 25% की वृद्धि।",
                },
            },
            {
                "number": "26.3.3",
                "title": {"en": "Spacing / clear distance between bars", "hi": "सरियों के बीच अंतराल / स्पष्ट दूरी"},
                "summary": {
                    "en": "Minimum clear distance between bars depends on bar diameter (Table 15); spacing limits for slabs are 3d or 300 mm (main) and 5d or 450 mm (distribution).",
                    "hi": "सरियों के बीच न्यूनतम स्पष्ट दूरी सरिया व्यास पर निर्भर (तालिका 15); स्लैब में अधिकतम अंतराल 3d या 300 मिमी (मुख्य) तथा 5d या 450 मिमी (वितरण)।",
                },
            },
            {
                "number": "26.4.2",
                "title": {"en": "Nominal cover to meet durability (Table 16)", "hi": "टिकाऊपन हेतु नाममात्र कवर (तालिका 16)"},
                "summary": {
                    "en": "Nominal cover: mild 20, moderate 30, severe 45, very severe 50, extreme 75 mm. Footings: minimum 50 mm.",
                    "hi": "नाममात्र कवर: सौम्य 20, मध्यम 30, कठोर 45, अति कठोर 50, अति तीव्र 75 मिमी। फुटिंग: न्यूनतम 50 मिमी।",
                },
            },
            {
                "number": "26.5.1.1",
                "title": {"en": "Tension reinforcement in beams (min/max)", "hi": "बीम में तनन प्रबलन (न्यूनतम/अधिकतम)"},
                "summary": {
                    "en": "Minimum tension steel As = 0.85 b d / fy. Maximum tension steel = 0.04 b D.",
                    "hi": "न्यूनतम तनन स्टील As = 0.85 b d / fy। अधिकतम तनन स्टील = 0.04 b D।",
                },
            },
            {
                "number": "26.5.1.5",
                "title": {"en": "Maximum spacing of shear reinforcement", "hi": "अपरूपण प्रबलन का अधिकतम अंतराल"},
                "summary": {
                    "en": "Spacing of vertical stirrups shall not exceed 0.75 d and shall in no case exceed 300 mm.",
                    "hi": "ऊर्ध्वाधर रकाबों का अंतराल 0.75 d से अधिक नहीं, और किसी भी स्थिति में 300 मिमी से अधिक नहीं।",
                },
            },
            {
                "number": "26.5.1.6",
                "title": {"en": "Minimum shear reinforcement", "hi": "न्यूनतम अपरूपण प्रबलन"},
                "summary": {
                    "en": "Minimum stirrups: Asv / (b·sv) ≥ 0.4 / (0.87 fy).",
                    "hi": "न्यूनतम रकाब: Asv / (b·sv) ≥ 0.4 / (0.87 fy)।",
                },
            },
            {
                "number": "26.5.2.1",
                "title": {"en": "Minimum reinforcement in slabs", "hi": "स्लैब में न्यूनतम प्रबलन"},
                "summary": {
                    "en": "Minimum steel in either direction = 0.15% of gross area (0.12% when high-strength deformed bars or welded wire fabric are used).",
                    "hi": "किसी भी दिशा में न्यूनतम स्टील = सकल क्षेत्रफल का 0.15% (उच्च-सामर्थ्य विकृत सरियों या वेल्डेड जाल के लिए 0.12%)।",
                },
            },
            {
                "number": "36.4.1",
                "title": {"en": "Partial safety factor for loads (Table 18)", "hi": "भार हेतु आंशिक सुरक्षा गुणक (तालिका 18)"},
                "summary": {
                    "en": "Limit state of collapse: DL+LL → 1.5(DL+LL); DL+WL/EL → 1.2(DL+WL/EL) or 0.9DL+1.5(WL/EL); DL+LL+WL → 1.2(DL+LL+WL).",
                    "hi": "संक्षिप्त अवस्था: DL+LL → 1.5(DL+LL); DL+WL/EL → 1.2(DL+WL/EL) या 0.9DL+1.5(WL/EL); DL+LL+WL → 1.2(DL+LL+WL)।",
                },
            },
            {
                "number": "38.1",
                "title": {"en": "Assumptions for limit state of collapse: flexure", "hi": "संक्षिप्त अवस्था: बंकन की अवधारणाएँ"},
                "summary": {
                    "en": "Plane sections remain plane; max concrete strain 0.0035; concrete design stress 0.67 fck (γm 1.5); steel γm 1.15; limiting neutral axis xu,max/d = 0.53 (Fe250), 0.48 (Fe415), 0.46 (Fe500).",
                    "hi": "समतल परिच्छेद समतल रहते हैं; कंक्रीट का अधिकतम विकृति 0.0035; कंक्रीट अभिकल्प प्रतिबल 0.67 fck (γm 1.5); स्टील γm 1.15; सीमांत उदासीन अक्ष xu,max/d = 0.53 (Fe250), 0.48 (Fe415), 0.46 (Fe500)।",
                },
            },
            {
                "number": "39.3",
                "title": {"en": "Short axially loaded members in compression", "hi": "संपीडन में लघु अक्षीय भारित सदस्य"},
                "summary": {
                    "en": "Pu = 0.4 fck Ac + 0.67 fy Asc.",
                    "hi": "Pu = 0.4 fck Ac + 0.67 fy Asc।",
                },
            },
            {
                "number": "40.1",
                "title": {"en": "Nominal shear stress", "hi": "नाममात्र अपरूपण प्रतिबल"},
                "summary": {
                    "en": "τv = Vu / (b·d).",
                    "hi": "τv = Vu / (b·d)।",
                },
            },
            {
                "number": "40.2.1",
                "title": {"en": "Design shear strength of concrete (Table 19)", "hi": "कंक्रीट की अभिकल्प अपरूपण सामर्थ्य (तालिका 19)"},
                "summary": {
                    "en": "τc from Table 19 as a function of 100 As/(b d) and concrete grade.",
                    "hi": "τc तालिका 19 से 100 As/(b d) तथा कंक्रीट ग्रेड के फलन के रूप में।",
                },
            },
            {
                "number": "40.2.3",
                "title": {"en": "Maximum shear stress (Table 20)", "hi": "अधिकतम अपरूपण प्रतिबल (तालिका 20)"},
                "summary": {
                    "en": "τc,max: M15 2.5, M20 2.8, M25 3.1, M30 3.5, M35 3.7, M40+ 4.0 N/mm². Nominal shear stress shall not exceed this even with shear reinforcement.",
                    "hi": "τc,max: M15 2.5, M20 2.8, M25 3.1, M30 3.5, M35 3.7, M40+ 4.0 N/mm²। अपरूपण प्रबलन के साथ भी नाममात्र अपरूपण प्रतिबल इससे अधिक नहीं होगा।",
                },
            },
            {
                "number": "40.4",
                "title": {"en": "Design of shear reinforcement", "hi": "अपरूपण प्रबलन का अभिकल्प"},
                "summary": {
                    "en": "Vertical stirrups: Vus = 0.87 fy Asv d / sv, carrying the shear in excess of τc·b·d.",
                    "hi": "ऊर्ध्वाधर रकाब: Vus = 0.87 fy Asv d / sv, जो τc·b·d से अधिक अपरूपण वहन करते हैं।",
                },
            },
            {
                "number": "Annex G-1.1",
                "title": {"en": "Moment of resistance — rectangular sections", "hi": "प्रतिरोध आघूर्ण — आयताकार परिच्छेद"},
                "summary": {
                    "en": "Mu = 0.87 fy Ast d (1 − Ast fy /(b d fck)); limiting Mu,lim = 0.36 (xu,max/d)(1 − 0.42 xu,max/d) fck b d².",
                    "hi": "Mu = 0.87 fy Ast d (1 − Ast fy /(b d fck)); सीमांत Mu,lim = 0.36 (xu,max/d)(1 − 0.42 xu,max/d) fck b d²।",
                },
            },
        ],
    },
    "IS1786": {
        "id": "IS1786",
        "number": "IS 1786:2008",
        "title": {
            "en": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement — Specification",
            "hi": "कंक्रीट प्रबलन हेतु उच्च-सामर्थ्य विकृत स्टील सरियाँ एवं तार — विशिष्टि",
        },
        "revision": "Fourth Revision (incorporating Amendments 1–4)",
        "committee": "CED 54 — Concrete Reinforcement",
        "scope": {
            "en": "Specifies strength grades (Fe415, Fe500, Fe550, Fe600 and their D/S variants), chemical composition, mechanical properties, rib geometry and bond requirements for reinforcement bars.",
            "hi": "प्रबलन सरियों के सामर्थ्य ग्रेड (Fe415, Fe500, Fe550, Fe600 तथा उनके D/S प्रकार), रासायनिक संघटन, यांत्रिक गुण, रिब ज्यामिति एवं बंध आवश्यकताएँ निर्दिष्ट करती है।",
        },
        "links": _links("is1786", public=LAW_1786),
        "clauses": [
            {
                "number": "1.1",
                "title": {"en": "Strength grades covered", "hi": "समाहित सामर्थ्य ग्रेड"},
                "summary": {
                    "en": "Grades: Fe415, Fe415D, Fe415S; Fe500, Fe500D, Fe500S; Fe550, Fe550D; Fe600 (and Fe650, Fe700 per Amendment 3). The number after 'Fe' is the minimum 0.2% proof/yield stress in N/mm².",
                    "hi": "ग्रेड: Fe415, Fe415D, Fe415S; Fe500, Fe500D, Fe500S; Fe550, Fe550D; Fe600 (संशोधन 3 के अनुसार Fe650, Fe700)। 'Fe' के बाद की संख्या न्यूनतम 0.2% प्रमाण/पराभव प्रतिबल N/mm² में है।",
                },
            },
            {
                "number": "Table 3",
                "title": {"en": "Mechanical properties (Cl. 8.1)", "hi": "यांत्रिक गुण (खंड 8.1)"},
                "summary": {
                    "en": "Fe415: YS ≥ 415, TS ≥ 485, elongation ≥ 14.5%. Fe500: YS ≥ 500, TS ≥ 545, elongation ≥ 12.0%. Fe550: YS ≥ 550, TS ≥ 585. Fe600: YS ≥ 600, TS ≥ 660.",
                    "hi": "Fe415: YS ≥ 415, TS ≥ 485, दीर्घीकरण ≥ 14.5%। Fe500: YS ≥ 500, TS ≥ 545, दीर्घीकरण ≥ 12.0%। Fe550: YS ≥ 550, TS ≥ 585। Fe600: YS ≥ 600, TS ≥ 660।",
                },
            },
            {
                "number": "5.3",
                "title": {"en": "Rib geometry and bond", "hi": "रिब ज्यामिति एवं बंध"},
                "summary": {
                    "en": "Rib dimensions govern the bond (pull-out) performance of deformed bars; effective cross-sectional area is based on mass per unit length.",
                    "hi": "रिब आयाम विकृत सरियों के बंध (पुल-आउट) प्रदर्शन को निर्धारित करते हैं; प्रभावी अनुप्रस्थ काट क्षेत्रफल प्रति इकाई लंबाई द्रव्यमान पर आधारित।",
                },
            },
        ],
    },
    "IS875P1": {
        "id": "IS875P1",
        "number": "IS 875 (Part 1):1987",
        "title": {
            "en": "Design Loads (Other than Earthquake) for Buildings and Structures — Part 1: Dead Loads — Unit Weights of Building Materials and Stored Materials",
            "hi": "भवनों एवं संरचनाओं हेतु अभिकल्प भार (भूकंप से भिन्न) — भाग 1: स्थायी भार — निर्माण सामग्री एवं भंडारित सामग्री के एकक भार",
        },
        "revision": "Second Revision",
        "committee": "CED 37 — Structural Safety",
        "scope": {
            "en": "Unit weights of building materials and stored materials used to compute dead loads. Reinforced concrete is commonly taken as 25 kN/m³.",
            "hi": "स्थायी भार की गणना हेतु निर्माण एवं भंडारित सामग्री के एकक भार। प्रबलित कंक्रीट सामान्यतः 25 kN/m³ लिया जाता है।",
        },
        "links": _links("is875", public=LAW_CED37),
        "clauses": [
            {
                "number": "Cl. 2 / Table 1",
                "title": {"en": "Unit weight of materials", "hi": "सामग्री का एकक भार"},
                "summary": {
                    "en": "Unit weights for common materials (e.g. RCC 25 kN/m³, brick masonry 19–20 kN/m³, floor finish as specified) used to build the dead load.",
                    "hi": "सामान्य सामग्री के एकक भार (जैसे RCC 25 kN/m³, ईंट चिनाई 19–20 kN/m³, फर्श परिसज्जा यथा निर्दिष्ट) जिनसे स्थायी भार बनता है।",
                },
            }
        ],
    },
    "IS875P2": {
        "id": "IS875P2",
        "number": "IS 875 (Part 2):1987",
        "title": {
            "en": "Design Loads (Other than Earthquake) for Buildings and Structures — Part 2: Imposed Loads",
            "hi": "भवनों एवं संरचनाओं हेतु अभिकल्प भार (भूकंप से भिन्न) — भाग 2: आरोपित भार",
        },
        "revision": "Second Revision",
        "committee": "CED 37 — Structural Safety",
        "scope": {
            "en": "Imposed (live) loads for floors, roofs and staircases by occupancy: residential 2.0 kN/m² (with 3.0 kN/m² for some cases), corridors/stairs 3.0–5.0 kN/m², etc.",
            "hi": "उपभोग के अनुसार फर्श, छत एवं सीढ़ियों के आरोपित (चल) भार: आवासीय 2.0 kN/m² (कुछ स्थितियों में 3.0 kN/m²), गलियारा/सीढ़ी 3.0–5.0 kN/m² इत्यादि।",
        },
        "links": _links("is875", public=LAW_CED37),
        "clauses": [
            {
                "number": "Table 1",
                "title": {"en": "Imposed floor loads", "hi": "आरोपित फर्श भार"},
                "summary": {
                    "en": "Imposed load values by type of occupancy and floor use; used as the characteristic live load LL.",
                    "hi": "उपभोग एवं उपयोग के अनुसार आरोपित भार मान; अभिलाक्षणिक चल भार LL के रूप में प्रयुक्त।",
                },
            }
        ],
    },
    "IS875P3": {
        "id": "IS875P3",
        "number": "IS 875 (Part 3):2015",
        "title": {
            "en": "Design Loads (Other than Earthquake) for Buildings and Structures — Part 3: Wind Loads",
            "hi": "भवनों एवं संरचनाओं हेतु अभिकल्प भार (भूकंप से भिन्न) — भाग 3: पवन भार",
        },
        "revision": "Third Revision",
        "committee": "CED 37 — Structural Safety",
        "scope": {
            "en": "Wind pressure/force on structures: basic wind speed by zone, design wind speed with risk, terrain and topography factors, pressure and force coefficients.",
            "hi": "संरचनाओं पर पवन दाब/बल: क्षेत्र अनुसार मूल पवन वेग, जोखिम, भू-आकृति एवं स्थलाकृति गुणकों सहित अभिकल्प पवन वेग, दाब एवं बल गुणक।",
        },
        "links": _links("is875", public=LAW_CED37),
        "clauses": [
            {
                "number": "Cl. 6–7",
                "title": {"en": "Design wind speed and pressure", "hi": "अभिकल्प पवन वेग एवं दाब"},
                "summary": {
                    "en": "Vz = Vb·k1·k2·k3·k4 and pz = 0.6 Vz²; gives the wind load WL used in load combinations.",
                    "hi": "Vz = Vb·k1·k2·k3·k4 तथा pz = 0.6 Vz²; भार संयोजनों में प्रयुक्त पवन भार WL देता है।",
                },
            }
        ],
    },
    "IS875P4": {
        "id": "IS875P4",
        "number": "IS 875 (Part 4):1987 (rev. 2021)",
        "title": {
            "en": "Design Loads (Other than Earthquake) for Buildings and Structures — Part 4: Snow Loads",
            "hi": "भवनों एवं संरचनाओं हेतु अभिकल्प भार (भूकंप से भिन्न) — भाग 4: हिम भार",
        },
        "revision": "Second Revision (Third Revision 2021)",
        "committee": "CED 37 — Structural Safety",
        "scope": {
            "en": "Snow load on roofs: ground snow load by zone, roof shape and slope coefficients, and the effect of rain-on-snow.",
            "hi": "छतों पर हिम भार: क्षेत्र अनुसार भूमि हिम भार, छत आकार एवं ढाल गुणक, तथा हिम पर वर्षा का प्रभाव।",
        },
        "links": _links("is875", public=LAW_CED37),
        "clauses": [
            {
                "number": "Cl. 6–7",
                "title": {"en": "Design snow load", "hi": "अभिकल्प हिम भार"},
                "summary": {
                    "en": "Roof snow load = ground snow load × exposure × thermal × shape factors.",
                    "hi": "छत हिम भार = भूमि हिम भार × अनावरण × तापीय × आकार गुणक।",
                },
            }
        ],
    },
    "IS875P5": {
        "id": "IS875P5",
        "number": "IS 875 (Part 5):1987",
        "title": {
            "en": "Design Loads (Other than Earthquake) for Buildings and Structures — Part 5: Special Loads and Load Combinations",
            "hi": "भवनों एवं संरचनाओं हेतु अभिकल्प भार (भूकंप से भिन्न) — भाग 5: विशेष भार एवं भार संयोजन",
        },
        "revision": "Second Revision",
        "committee": "CED 37 — Structural Safety",
        "scope": {
            "en": "Special loads (temperature, settlement, erection, etc.) and guidance on combining loads; complements the partial safety factors of IS 456 Table 18.",
            "hi": "विशेष भार (तापमान, निपटान, निर्माण आदि) तथा भारों के संयोजन हेतु मार्गदर्शन; IS 456 तालिका 18 के आंशिक सुरक्षा गुणकों का पूरक।",
        },
        "links": _links("is875", public=LAW_CED37),
        "clauses": [
            {
                "number": "Cl. 3",
                "title": {"en": "Combination of loads", "hi": "भारों का संयोजन"},
                "summary": {
                    "en": "Rules for combining dead, imposed, wind and other loads, including the reduced probability of simultaneous maxima.",
                    "hi": "स्थायी, आरोपित, पवन एवं अन्य भारों के संयोजन के नियम, जिनमें एक साथ अधिकतम होने की घटी प्रायिकता सम्मिलित है।",
                },
            }
        ],
    },
    "IS10262": {
        "id": "IS10262",
        "number": "IS 10262:2019",
        "title": {
            "en": "Concrete Mix Proportioning — Guidelines",
            "hi": "कंक्रीट मिश्रण अनुपातन — दिशानिर्देश",
        },
        "revision": "Second Revision",
        "committee": "CED 02 — Cement and Concrete",
        "scope": {
            "en": "Step-by-step guidelines for proportioning concrete mixes (ordinary, standard and high-strength grades) to meet strength, workability and durability requirements. Provides the target-strength formula, water-cement ratio, water and cement content, and aggregate proportions, aligned with IS 456:2000.",
            "hi": "सामर्थ्य, कार्यशीलता एवं टिकाऊपन की आवश्यकताओं की पूर्ति हेतु कंक्रीट मिश्रण के अनुपातन हेतु चरण-दर-चरण दिशानिर्देश (साधारण, मानक एवं उच्च-सामर्थ्य ग्रेड)। लक्ष्य-सामर्थ्य सूत्र, जल-सीमेंट अनुपात, जल एवं सीमेंट मात्रा तथा गिट्टी अनुपात देता है, जो IS 456:2000 के अनुरूप है।",
        },
        "links": _links("is10262", public=ARCHIVE_10262, clause_browser=INFRALENS_10262),
        "clauses": [
            {
                "number": "1.2",
                "title": {"en": "Applicability", "hi": "प्रयोज्यता"},
                "summary": {
                    "en": "Applies to ordinary, standard and high-strength concrete grades; also covers self-compacting and mass concrete.",
                    "hi": "साधारण, मानक एवं उच्च-सामर्थ्य कंक्रीट ग्रेड पर लागू; स्व-संपीडक एवं द्रव्यमान कंक्रीट भी समाहित।",
                },
            },
            {
                "number": "4.1",
                "title": {"en": "Data required for mix proportioning", "hi": "मिश्रण अनुपातन हेतु आवश्यक आँकड़े"},
                "summary": {
                    "en": "Grade designation, type of cement, nominal maximum size of aggregate, exposure/durability limits, workability, degree of site control, and aggregate types.",
                    "hi": "ग्रेड नाम, सीमेंट प्रकार, गिट्टी का नाममात्र अधिकतम आकार, अनावरण/टिकाऊपन सीमाएँ, कार्यशीलता, साइट नियंत्रण की कोटि तथा गिट्टी प्रकार।",
                },
            },
            {
                "number": "4.2",
                "title": {"en": "Target mean strength (Tables 1 & 2)", "hi": "लक्ष्य माध्य सामर्थ्य (तालिका 1 एवं 2)"},
                "summary": {
                    "en": "f'ck = fck + 1.65 S or fck + X, whichever is higher. X (Table 1): M10–M15 5.0, M20–M25 5.5, M30–M60 6.5, M65+ 8.0. Assumed S (Table 2): M10–M15 3.5, M20–M25 4.0, M30–M60 5.0, M65+ 6.0 N/mm².",
                    "hi": "f'ck = fck + 1.65 S या fck + X, इनमें जो अधिक हो। X (तालिका 1): M10–M15 5.0, M20–M25 5.5, M30–M60 6.5, M65+ 8.0। अनुमानित S (तालिका 2): M10–M15 3.5, M20–M25 4.0, M30–M60 5.0, M65+ 6.0 N/mm²।",
                },
            },
            {
                "number": "5.1",
                "title": {"en": "Selection of water-cement ratio", "hi": "जल-सीमेंट अनुपात का चयन"},
                "summary": {
                    "en": "Preliminary free w/c from the strength relationship (Fig. 1); the lower of this and the durability limit (IS 456 Table 5) is adopted.",
                    "hi": "सामर्थ्य संबंध (चित्र 1) से प्रारंभिक मुक्त w/c; इस तथा टिकाऊपन सीमा (IS 456 तालिका 5) में से जो कम हो वह अपनाया जाता है।",
                },
            },
            {
                "number": "5.2",
                "title": {"en": "Estimation of air content (Table 3)", "hi": "वायु-अंश का अनुमान (तालिका 3)"},
                "summary": {
                    "en": "Entrapped air (non-air-entrained): 10 mm 1.5%, 20 mm 1.0%, 40 mm 0.8% of concrete volume.",
                    "hi": "फँसी वायु (वायु-संवाहित रहित): 10 मिमी 1.5%, 20 मिमी 1.0%, 40 मिमी 0.8% (कंक्रीट आयतन का)।",
                },
            },
            {
                "number": "5.3",
                "title": {"en": "Selection of water content (Table 4)", "hi": "जल मात्रा का चयन (तालिका 4)"},
                "summary": {
                    "en": "Water content for angular aggregate at 50 mm slump: 10 mm 208, 20 mm 186, 40 mm 165 kg/m³. Adjust −10/−15/−20 kg for sub-angular/gravel/rounded; ±3% per 25 mm change in slump.",
                    "hi": "कोणीय गिट्टी हेतु 50 मिमी स्लंप पर जल मात्रा: 10 मिमी 208, 20 मिमी 186, 40 मिमी 165 kg/m³। उप-कोणीय/बजरी/गोल हेतु −10/−15/−20 किग्रा; स्लंप में प्रति 25 मिमी परिवर्तन पर ±3%।",
                },
            },
            {
                "number": "5.4",
                "title": {"en": "Calculation of cement/cementitious content", "hi": "सीमेंट/सीमेंटीशियस मात्रा की गणना"},
                "summary": {
                    "en": "Cement content = water content / w-c ratio; adopt the greater of this and the durability minimum (IS 456 Table 5).",
                    "hi": "सीमेंट मात्रा = जल मात्रा / w-c अनुपात; इस तथा टिकाऊपन न्यूनतम (IS 456 तालिका 5) में से जो अधिक हो वह अपनाएँ।",
                },
            },
            {
                "number": "5.5",
                "title": {"en": "Estimation of coarse aggregate proportion (Table 5)", "hi": "मोटी गिट्टी अनुपात का अनुमान (तालिका 5)"},
                "summary": {
                    "en": "Volume of coarse aggregate per unit volume of total aggregate at w/c = 0.5 (e.g. 20 mm: Zone IV 0.66, III 0.64, II 0.62, I 0.60). Increase 0.01 for every 0.05 decrease in w/c, decrease 0.01 for every 0.05 increase.",
                    "hi": "w/c = 0.5 पर कुल गिट्टी के प्रति इकाई आयतन मोटी गिट्टी का आयतन (जैसे 20 मिमी: ज़ोन IV 0.66, III 0.64, II 0.62, I 0.60)। w/c में प्रत्येक 0.05 कमी पर 0.01 बढ़ाएँ, प्रत्येक 0.05 वृद्धि पर 0.01 घटाएँ।",
                },
            },
            {
                "number": "5.7",
                "title": {"en": "Estimation of fine and coarse aggregate contents", "hi": "बारीक एवं मोटी गिट्टी मात्रा का अनुमान"},
                "summary": {
                    "en": "Absolute-volume method: subtract the absolute volumes of cement, water and air from unit volume; split the remainder between coarse and fine aggregate by the proportion from 5.5.",
                    "hi": "निरपेक्ष-आयतन विधि: इकाई आयतन से सीमेंट, जल एवं वायु के निरपेक्ष आयतन घटाएँ; शेष को 5.5 के अनुपात से मोटी एवं बारीक गिट्टी में बाँटें।",
                },
            },
            {
                "number": "5.8",
                "title": {"en": "Trial mixes", "hi": "परीक्षण मिश्रण"},
                "summary": {
                    "en": "Calculated proportions shall be checked by trial batches; adjust water/admixture, then vary w/c by ±10% for confirmation mixes.",
                    "hi": "परिकलित अनुपात परीक्षण बैचों से जाँचे जाएँ; जल/मिश्रण समायोजित करें, फिर पुष्टि हेतु w/c में ±10% परिवर्तन करें।",
                },
            },
        ],
    },
}


def list_codes():
    """Return the full code library as a list (order preserved)."""
    return list(CODES.values())


def get_code(code_id):
    return CODES.get(code_id)


def find_clause(code_id, clause_number):
    code = CODES.get(code_id)
    if not code:
        return None
    for cl in code["clauses"]:
        if cl["number"] == clause_number:
            return cl
    return None
