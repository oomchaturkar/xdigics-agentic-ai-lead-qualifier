from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .models import LeadRequest, QualificationResponse
from .research import research_company
from .scoring import score_lead
import csv, io, json

app = FastAPI(title="Xdigics B2B Lead Qualifier", version="1.0.0",
              description="Evidence-backed lead research and explainable ICP scoring prototype.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
_last_results = []

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "xdigics-lead-qualifier", "live_research": "DDGS search; subject to provider availability"}

@app.get("/api/scoring-method")
def scoring_method():
    return {"maximum": 100, "weights": {"industry_match": 25, "service_need_signals": 30, "geography_match": 15, "company_size": 15, "evidence_coverage": 15},
            "tiers": {"high_fit": "70-100 with at least 2 sources", "potential_fit": "40-69 with at least 2 sources", "low_fit": "0-39 with at least 2 sources", "needs_research": "fewer than 2 sources or no evidence"},
            "note": "Heuristic prioritization only. Not proof of purchase intent. Human review required."}

@app.post("/api/qualify", response_model=QualificationResponse)
def qualify(request: LeadRequest):
    global _last_results
    companies = [c.strip() for c in request.companies if c and c.strip()]
    if not companies:
        raise HTTPException(status_code=422, detail="Enter at least one non-empty company name.")
    if len(companies) > 25:
        raise HTTPException(status_code=422, detail="Maximum 25 companies per run.")
    results, warnings = [], []
    for company in companies:
        if request.research_live:
            evidence, search_warnings = research_company(company)
            warnings.extend(search_warnings)
        else:
            evidence = []
            warnings.append(f"Live research disabled for {company}; result is marked as needing research.")
        results.append(score_lead(company, evidence, request.icp))
    results.sort(key=lambda x: x.score, reverse=True)
    _last_results = [r.model_dump(mode="json") for r in results]
    return QualificationResponse(results=results, scoring_method={
        "maximum": 100,
        "weights": {"industry_match": 25, "service_need_signals": 30, "geography_match": 15, "company_size": 15, "evidence_coverage": 15},
        "tiers": {"High fit": "70-100 and >=2 sources", "Potential fit": "40-69 and >=2 sources", "Low fit": "0-39 and >=2 sources", "Needs research": "<2 sources"},
        "caveat": "Scores support human review; they do not prove a company is ready to buy."
    }, research_mode="live public web search" if request.research_live else "research disabled", warnings=warnings[:40])

@app.get("/api/export/json")
def export_json():
    if not _last_results:
        raise HTTPException(status_code=404, detail="Run a qualification first.")
    return Response(content=json.dumps(_last_results, indent=2), media_type="application/json",
                     headers={"Content-Disposition": "attachment; filename=qualified_leads.json"})

@app.get("/api/export/csv")
def export_csv():
    if not _last_results:
        raise HTTPException(status_code=404, detail="Run a qualification first.")
    stream = io.StringIO()
    fields = ["company", "score", "tier", "industry", "geography", "estimated_size", "confidence", "signals", "missing_information", "rationale", "evidence_urls"]
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    for lead in _last_results:
        row = {k: lead.get(k, "") for k in fields}
        for k in ("signals", "missing_information", "rationale"):
            row[k] = " | ".join(row[k]) if isinstance(row[k], list) else row[k]
        row["evidence_urls"] = " | ".join(e.get("url", "") for e in lead.get("evidence", []))
        writer.writerow(row)
    return Response(content=stream.getvalue(), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=qualified_leads.csv"})
