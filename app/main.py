"""
IS Code Solver — FastAPI application.

Answers structural / RCC engineering questions using deterministic,
rule-based solvers, and returns the exact Indian Standard (IS) clause
references for every step, with links to open the codes.

Endpoints
---------
GET  /                     -> the single-page web app
GET  /api/health           -> liveness probe
GET  /api/codes            -> the IS code library
GET  /api/codes/{code_id}  -> one code, with its clause index
GET  /api/problem-types    -> catalogue + form fields for the UI
POST /api/solve            -> run a solver on structured inputs
POST /api/ask              -> parse a free-text question and answer it
"""

import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .codes import library
from .solvers import registry
from .solvers.common import t

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(
    title="IS Code Solver",
    description="Solve structural / RCC engineering problems with IS code references.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------
class SolveRequest(BaseModel):
    type: str = Field(..., description="Problem type id, e.g. 'beam_flexure'")
    inputs: dict = Field(default_factory=dict)
    lang: str = Field(default="en")


class AskRequest(BaseModel):
    question: str
    lang: str = Field(default="en")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _clean_inputs(raw: dict) -> dict:
    """Drop empty strings; coerce numeric-looking values."""
    out = {}
    for k, v in raw.items():
        if v is None or v == "":
            continue
        if isinstance(v, str):
            s = v.strip()
            if s == "":
                continue
            try:
                out[k] = float(s)
            except ValueError:
                out[k] = s
        else:
            out[k] = v
    return out


def _references_with_links(refs):
    """Attach code titles and open-links to a list of references."""
    out = []
    for r in refs:
        code = library.get_code(r["code"])
        item = dict(r)
        if code:
            item["code_number"] = code["number"]
            item["code_title"] = code["title"]
            item["links"] = code["links"]
        out.append(item)
    return out


def _enrich(solution):
    solution["references"] = _references_with_links(solution.get("references", []))
    return solution


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"status": "ok", "codes": len(library.list_codes()),
            "problem_types": len(registry.list_problem_types())}


@app.get("/api/codes")
def get_codes():
    return {"codes": library.list_codes()}


@app.get("/api/codes/{code_id}")
def get_code(code_id: str):
    code = library.get_code(code_id)
    if not code:
        raise HTTPException(status_code=404, detail=f"Code '{code_id}' not found")
    return code


@app.get("/api/problem-types")
def get_problem_types():
    return {"problem_types": registry.list_problem_types()}


@app.post("/api/solve")
def post_solve(req: SolveRequest):
    if req.type not in registry.SOLVERS:
        raise HTTPException(status_code=400, detail=f"Unknown problem type: {req.type}")
    params = _clean_inputs(req.inputs)
    try:
        solution = registry.solve(req.type, params)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except ZeroDivisionError:
        raise HTTPException(status_code=422, detail="A value of zero is not valid for this input.")
    return _enrich(solution)


@app.post("/api/ask")
def post_ask(req: AskRequest):
    question = (req.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Empty question")

    ptype = registry.detect_type(question)
    if not ptype:
        return {
            "status": "no_match",
            "message": t(
                "I couldn't match this to one of the supported problem types. "
                "Try mentioning a beam, slab, shear, development length, column or load combination.",
                "यह प्रश्न समर्थित समस्या प्रकारों में से किसी से मेल नहीं खाता। "
                "बीम, स्लैब, अपरूपण, विकास लंबाई, स्तंभ या भार संयोजन का उल्लेख करें।",
            ),
            "problem_types": [{"id": p["id"], "title": p["title"]} for p in registry.list_problem_types()],
            "references": _references_with_links(
                [{"code": c["id"], "clause": None, "table": None} for c in library.list_codes()]
            ),
        }

    params = registry.extract_params(question)
    missing = registry.missing_fields(ptype, params)

    if missing:
        pt = registry.PROBLEM_TYPES[ptype]
        return {
            "status": "need_inputs",
            "problem_type": ptype,
            "title": pt["title"],
            "detected_inputs": params,
            "missing_fields": missing,
            "message": t(
                f"This looks like: {pt['title']['en']}. I need the highlighted values to solve it.",
                f"यह प्रतीत होता है: {pt['title']['hi']}। हल करने हेतु चिह्नित मान आवश्यक हैं।",
            ),
        }

    try:
        solution = registry.solve(ptype, params)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    solution["parsed_from"] = question
    return _enrich(solution)


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


# Friendly 404 for unknown API paths
@app.exception_handler(404)
async def not_found(request, exc):
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
