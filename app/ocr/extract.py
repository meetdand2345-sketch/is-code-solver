"""
OCR-based extraction from images of RCC questions.

Reads text from an uploaded image (a photo or scan of a question, or a labelled
figure), then re-uses the same question parser the text endpoint uses, so an
image and typed text go through identical logic.

This module NEVER auto-solves. Engineering drawings are easy to misread, so it
returns *candidate* values for the user to confirm in the Design Tools form.
"""

import io
import re
import time

import numpy as np
from PIL import Image

_ENGINE = None
MAX_SIDE = 1600          # upscale small images; cap very large ones
MIN_SIDE = 1000
OCR_TRIES = 3            # ONNX Runtime occasionally fails a call; retry it


def _build_engine():
    """Build the OCR engine.

    A single-threaded session with the angle classifier off is markedly more
    stable across repeated calls in this environment (the multi-session default
    fails intermittently).
    """
    from rapidocr_onnxruntime import RapidOCR
    try:
        return RapidOCR(use_angle_cls=False, intra_op_num_threads=1)
    except Exception:  # noqa: BLE001 - older builds may not accept the kwargs
        return RapidOCR()


def _get_engine():
    """Lazily build the OCR engine (model load is slow, so cache it)."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = _build_engine()
    return _ENGINE


def _run_ocr(arr):
    """Run OCR with retries; rebuild the engine once if it keeps failing."""
    global _ENGINE
    last = None
    for _ in range(OCR_TRIES):
        try:
            return _get_engine()(arr)
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(0.2)
    try:
        _ENGINE = _build_engine()
        return _ENGINE(arr)
    except Exception as exc:  # noqa: BLE001
        last = exc
    raise last


def _prepare(data: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(data))
    img = img.convert("RGB")
    w, h = img.size
    if w < 20 or h < 20:
        raise ValueError("Image is too small to read.")
    longest = max(w, h)
    if longest < MIN_SIDE:
        s = MIN_SIDE / float(longest)
        img = img.resize((int(w * s), int(h * s)))
    elif longest > MAX_SIDE:
        s = MAX_SIDE / float(longest)
        img = img.resize((int(w * s), int(h * s)))
    return np.array(img)


def _reading_order(results):
    """Sort OCR boxes top-to-bottom, left-to-right, grouping rows."""
    items = []
    for entry in results:
        box, text, conf = entry[0], entry[1], entry[2]
        ys = [p[1] for p in box]
        xs = [p[0] for p in box]
        items.append((sum(ys) / 4.0, sum(xs) / 4.0, str(text), float(conf)))
    items.sort(key=lambda t: (round(t[0] / 18.0), t[1]))
    return items


def _normalize(text: str) -> str:
    """Insert spaces at letter/digit boundaries to help the token parser.

    'M25concrete,Fe500' -> 'M 25 concrete,Fe 500'  ;  'b=300mm' -> 'b=300 mm'
    """
    text = re.sub(r"([A-Za-z])(\d)", r"\1 \2", text)
    text = re.sub(r"(\d)([A-Za-z])", r"\1 \2", text)
    return text


def read_image(data: bytes):
    """Run OCR and return the raw text, tokens and a normalized text string."""
    arr = _prepare(data)
    result, _ = _run_ocr(arr)
    if not result:
        return {"text": "", "normalized": "", "tokens": []}
    items = _reading_order(result)
    tokens = [{"text": t, "conf": round(c, 2)} for _, _, t, c in items]
    text = " ".join(t for _, _, t, _ in items)
    return {"text": text, "normalized": _normalize(text), "tokens": tokens}


def _harvest_numbers(tokens):
    """All numeric tokens found — useful when a figure has unlabelled dimensions."""
    out = []
    for tk in tokens:
        nums = re.findall(r"\d+(?:\.\d+)?", tk["text"])
        for n in nums:
            out.append({"text": n, "from": tk["text"]})
    return out


def parse_image(data: bytes):
    """OCR an image and return candidate problem type + parameters.

    Returns a dict mirroring the /api/ask 'need_inputs' shape so the front-end
    can render it the same way and offer to load it into the Design Tools form.
    """
    from ..solvers import registry
    from ..solvers.common import t

    try:
        out = read_image(data)
    except Exception as exc:  # noqa: BLE001 - surface a clean message to the user
        return {
            "status": "error",
            "message": t(f"Could not read the image: {exc}",
                         f"छवि पढ़ी नहीं जा सकी: {exc}"),
            "text": "",
            "tokens": [],
            "params": {},
            "numbers": [],
            "problem_type": None,
            "missing_fields": [],
        }

    text = out["normalized"]
    tokens = out["tokens"]
    numbers = _harvest_numbers(tokens)

    if not text.strip():
        return {
            "status": "no_text",
            "message": t("No readable text found in the image. Try a clearer photo, or type the question.",
                         "छवि में पठनीय पाठ नहीं मिला। स्पष्ट फ़ोटो लें या प्रश्न टाइप करें।"),
            "text": "",
            "tokens": [],
            "params": {},
            "numbers": [],
            "problem_type": None,
            "missing_fields": [],
        }

    ptype = registry.detect_type(text)
    params = registry.extract_params(text)
    missing = registry.missing_fields(ptype, params) if ptype else []

    notes = [
        t("Values are read from the image and may be wrong — check each one before solving.",
          "मान छवि से पढ़े गए हैं और गलत हो सकते हैं — हल करने से पूर्व प्रत्येक की जाँच करें।"),
    ]
    if ptype is None:
        notes.append(t("Couldn't identify the problem type. Pick one in Design Tools and enter the values.",
                       "समस्या प्रकार पहचाना नहीं गया। अभिकल्प उपकरण में प्रकार चुनें और मान भरें।"))
    elif not params:
        notes.append(t("No labelled values were recognised — the figure may have unlabelled dimensions. "
                       "Map the numbers below to b, D, d, etc. in the form.",
                       "कोई लेबलित मान नहीं पहचाना गया — आकृति में बिना लेबल के आयाम हो सकते हैं। "
                       "नीचे दिए अंकों को फॉर्म में b, D, d आदि से मिलाएँ।"))

    return {
        "status": "parsed",
        "text": out["text"],
        "tokens": tokens,
        "problem_type": ptype,
        "title": registry.PROBLEM_TYPES[ptype]["title"] if ptype else None,
        "params": params,
        "numbers": numbers,
        "missing_fields": missing,
        "message": t("Text read from the image. Confirm the values, then solve.",
                     "छवि से पाठ पढ़ा गया। मान जाँचें, फिर हल करें।"),
        "notes": notes,
    }
