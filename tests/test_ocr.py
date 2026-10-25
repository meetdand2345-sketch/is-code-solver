"""Tests for OCR-based extraction from images.

These are skipped automatically if the OCR engine isn't installed, so the rest
of the suite still runs on a minimal environment.
"""

import io
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest.importorskip("rapidocr_onnxruntime")
pytest.importorskip("PIL")

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from app.ocr import extract  # noqa: E402

_FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def _font(size=28):
    for p in _FONT_PATHS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    pytest.skip("No TrueType font available to render a test image")


def _img(lines, size=28):
    font = _font(size)
    img = Image.new("RGB", (820, 60 * len(lines) + 40), "white")
    d = ImageDraw.Draw(img)
    y = 20
    for ln in lines:
        d.text((20, y), ln, fill="black", font=font)
        y += 60
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_ocr_reads_beam_question():
    data = _img([
        "Design a simply supported beam",
        "b = 300 mm   D = 500 mm",
        "M25 concrete, Fe500 steel",
        "Mu = 120 kNm",
    ])
    r = extract.parse_image(data)
    assert r["status"] == "parsed"
    assert r["problem_type"] == "beam_flexure"
    assert r["params"].get("b") == 300
    assert r["params"].get("fck") == 25
    assert r["params"].get("fy") == 500


def test_ocr_reads_mix_design():
    data = _img([
        "Concrete mix design M25",
        "20 mm aggregate, zone II",
        "moderate exposure",
    ])
    r = extract.parse_image(data)
    assert r["problem_type"] == "mix_design"
    assert r["params"].get("grade") == "M25"
    assert r["params"].get("msa") == 20


def test_ocr_endpoint():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    data = _img(["Shear design of a beam", "b = 250 mm  d = 450 mm", "Vu = 90 kN"])
    resp = client.post("/api/ask-image", files={"file": ("q.png", data, "image/png")})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in ("parsed", "no_text")
    assert "text" in body


def test_ocr_endpoint_rejects_empty():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    resp = client.post("/api/ask-image", files={"file": ("q.png", b"", "image/png")})
    assert resp.status_code == 400


def test_ocr_health_flag():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    assert client.get("/api/health").json()["ocr"] is True
