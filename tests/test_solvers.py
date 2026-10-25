"""Tests for the IS Code Solver solvers and API."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.solvers import registry  # noqa: E402


def test_loads_governing_combination():
    res = registry.solve("loads", {"dl": 6, "ll": 3})
    # 1.5*(6+3) = 13.5
    assert "13.5" in res["summary"]["en"]
    refs = {(r["code"], r["clause"]) for r in res["references"]}
    assert ("IS456", "36.4.1") in refs


def test_flexure_area_of_steel():
    res = registry.solve("beam_flexure", {"b": 300, "D": 500, "d": 450, "fck": 25, "fy": 500, "Mu": 120})
    # expected Ast ~ 682 mm2
    ast_step = [s for s in res["steps"] if s["n"] == 4][0]
    assert "68" in ast_step["result"]["en"]
    assert "kN·m" in res["summary"]["en"]
    codes = {r["code"] for r in res["references"]}
    assert "IS456" in codes


def test_flexure_flags_over_limit():
    res = registry.solve("beam_flexure", {"b": 230, "D": 400, "d": 350, "fck": 20, "fy": 415, "Mu": 200})
    assert res["warnings"], "expected a warning for Mu > Mu,lim"


def test_shear_stirrup_spacing():
    res = registry.solve("shear", {"b": 250, "d": 450, "Vu": 90, "Ast": 942, "fck": 20, "fy": 415})
    spacing_step = [s for s in res["steps"] if s["n"] == 5][0]
    assert "mm c/c" in spacing_step["result"]["en"]
    refs = {(r["code"], r["clause"]) for r in res["references"]}
    assert ("IS456", "40.4") in refs
    assert ("IS456", "40.2.1") in refs


def test_shear_inadequate_section():
    res = registry.solve("shear", {"b": 150, "d": 200, "Vu": 300, "Ast": 300, "fck": 20, "fy": 415})
    assert res["warnings"]


def test_slab_design():
    res = registry.solve("slab_oneway", {"L": 4, "LL": 3, "fck": 25, "fy": 500})
    ast_step = [s for s in res["steps"] if s["n"] == 5][0]
    assert "33" in ast_step["result"]["en"]  # ~339 mm2
    refs = {(r["code"], r["clause"]) for r in res["references"]}
    assert ("IS456", "26.5.2.1") in refs


def test_development_length():
    res = registry.solve("development", {"phi": 16, "fck": 25, "fy": 500})
    ld_step = [s for s in res["steps"] if s["n"] == 2][0]
    assert "77" in ld_step["result"]["en"]  # ~777 mm
    refs = {(r["code"], r["clause"]) for r in res["references"]}
    assert ("IS456", "26.2.1.1") in refs


def test_development_compression_plain():
    res = registry.solve("development", {"phi": 20, "fck": 20, "fy": 415,
                                          "bar_type": "plain", "condition": "compression"})
    # tbd = 1.2 * 1.25 = 1.5
    assert "1.5" in res["summary"]["en"]


def test_column_required_steel():
    res = registry.solve("column_axial", {"b": 300, "D": 300, "fck": 20, "fy": 415, "Pu": 1000})
    asc_step = [s for s in res["steps"] if s["n"] == 2][0]
    assert "1037" in asc_step["result"]["en"]


def test_column_capacity_check():
    res = registry.solve("column_axial", {"b": 300, "D": 300, "fck": 20, "fy": 415,
                                           "Pu": 1000, "Asc": 1200})
    assert "SAFE" in res["steps"][1]["result"]["en"]


def test_bilingual_output():
    res = registry.solve("loads", {"dl": 6, "ll": 3})
    assert res["summary"]["hi"]
    assert res["steps"][0]["title"]["hi"]


# --- question parsing -------------------------------------------------------
def test_detect_type():
    assert registry.detect_type("Design a slab spanning 4 m") == "slab_oneway"
    assert registry.detect_type("shear design of a beam") == "shear"
    assert registry.detect_type("development length of a bar") == "development"


def test_extract_params():
    p = registry.extract_params("b=300, D=500, fck=25, fy=500, Mu=120 kNm")
    assert p["b"] == 300 and p["D"] == 500 and p["fck"] == 25 and p["fy"] == 500 and p["Mu"] == 120


def test_missing_fields():
    p = registry.extract_params("design a beam b=300 D=500")
    missing = registry.missing_fields("beam_flexure", p)
    names = {m["name"] for m in missing}
    assert "fck" in names or "Mu" in names


# --- API --------------------------------------------------------------------
def test_api_health():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_api_codes():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    r = client.get("/api/codes")
    assert r.status_code == 200
    ids = {c["id"] for c in r.json()["codes"]}
    assert {"IS456", "IS1786", "IS875P1", "IS875P2", "IS875P3", "IS875P4", "IS875P5"} <= ids


def test_api_solve_enriches_links():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    r = client.post("/api/solve", json={"type": "beam_flexure",
                                        "inputs": {"b": 300, "D": 500, "d": 450,
                                                   "fck": 25, "fy": 500, "Mu": 120}})
    assert r.status_code == 200
    data = r.json()
    assert data["references"][0]["links"]


def test_api_ask_full_solution():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    r = client.post("/api/ask", json={
        "question": "Design a slab, span 4 m, live load 3 kN/m2, fck 25, fy 500"})
    assert r.status_code == 200
    assert r.json().get("type") == "slab_oneway"


def test_api_ask_needs_inputs():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    r = client.post("/api/ask", json={"question": "How do I design a beam?"})
    assert r.status_code == 200
    assert r.json()["status"] == "need_inputs"
