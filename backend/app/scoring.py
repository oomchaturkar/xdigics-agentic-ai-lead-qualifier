from urllib.parse import urlparse
from .models import ICP, Evidence, LeadResult

INDUSTRY_TERMS = {
    "SaaS": ["saas", "software as a service", "software platform", "cloud software"],
    "Financial Services": ["financial services", "bank", "fintech", "insurance", "payments"],
    "Healthcare": ["healthcare", "health tech", "hospital", "clinical", "medical"],
    "Manufacturing": ["manufacturing", "industrial", "factory", "supply chain"],
    "Retail": ["retail", "e-commerce", "ecommerce", "consumer goods"],
    "Technology": ["technology", "IT services", "information technology", "AI company"]
}
GEO_TERMS = ["united states", "usa", "us", "united kingdom", "uk", "india", "canada", "australia"]
SERVICE_TERMS = {
    "cloud": ["cloud", "aws", "azure", "google cloud", "cloud migration"],
    "data analytics": ["analytics", "data platform", "business intelligence", "data engineering", "machine learning"],
    "AI automation": ["artificial intelligence", "generative ai", "automation", "agentic ai", "machine learning", "llm"]
}

def score_lead(company: str, evidence: list[Evidence], icp: ICP) -> LeadResult:
    """Transparent heuristic scoring; evidence snippets, not model guesses, drive signals."""
    corpus = " ".join([company] + [f"{e.title} {e.snippet} {e.source_domain}" for e in evidence]).lower()
    rationale, signals, missing = [], [], []
    points = 0

    industry_matches = []
    for industry in icp.target_industries:
        terms = INDUSTRY_TERMS.get(industry, [industry.lower()])
        if any(term in corpus for term in terms):
            industry_matches.append(industry)
    if industry_matches:
        points += 25
        industry = industry_matches[0]
        rationale.append(f"+25: evidence contains terms matching target industry ({', '.join(industry_matches)}).")
        signals.append("Target-industry language found in research snippets.")
    else:
        industry = "Unknown"
        missing.append("Industry not verified from available search evidence.")
        rationale.append("+0: no reliable target-industry signal found.")

    service_matches = []
    requested_services = icp.services or list(SERVICE_TERMS.keys())
    for service in requested_services:
        terms = SERVICE_TERMS.get(service.lower(), [service.lower()])
        if any(term in corpus for term in terms):
            service_matches.append(service)
    service_points = min(30, 15 * len(service_matches))
    points += service_points
    if service_matches:
        rationale.append(f"+{service_points}: service/technology signals found for {', '.join(service_matches)}.")
        signals.extend([f"Potential need signal: {s}." for s in service_matches])
    else:
        rationale.append("+0: no matching cloud, analytics, or AI-automation need signal found.")
        missing.append("Potential business need for the consulting services is not verified.")

    geo_matches = [g for g in icp.target_geographies if g.lower() in corpus or (g.lower() == "united states" and any(x in corpus for x in [" usa ", " united states", " us-based"]))]
    if geo_matches:
        points += 15
        geography = geo_matches[0]
        rationale.append(f"+15: target-geography signal found ({', '.join(geo_matches)}).")
        signals.append("Target-geography language found in research snippets.")
    else:
        geography = "Unknown"
        rationale.append("+0: target geography not verified.")
        missing.append("Company location/geography needs verification.")

    # Search results rarely contain a dependable employee count. Only award size points for explicit numeric evidence.
    size_points = 0
    size_text = "Unknown"
    import re
    for e in evidence:
        text = f"{e.title} {e.snippet}"
        match = re.search(r"\b(\d[\d,]*)\s*\+?\s*(?:employees|staff|team members)\b", text, re.I)
        if match:
            count = int(match.group(1).replace(",", ""))
            size_text = f"~{count:,} employees (source snippet; verify)"
            if count >= icp.min_employee_count:
                size_points = 15 if count >= icp.ideal_employee_count else 10
            break
    points += size_points
    if size_points:
        rationale.append(f"+{size_points}: explicit employee-count signal ({size_text}).")
        signals.append("An employee-count estimate appeared in a search snippet; verify against a primary source.")
    else:
        rationale.append("+0: employee count not verified; no size points awarded.")
        missing.append("Employee count/scale not verified.")

    # Evidence quality: source diversity and non-empty citations; capped at 15.
    domains = {urlparse(e.url).netloc.lower().removeprefix("www.") for e in evidence if e.url.startswith("http")}
    quality_points = min(15, len(domains) * 5) if evidence else 0
    points += quality_points
    if quality_points:
        rationale.append(f"+{quality_points}: evidence coverage bonus from {len(domains)} distinct source domain(s), capped at 15.")
    else:
        rationale.append("+0: no usable source citations available.")
        missing.append("No source evidence available; treat all company claims as unverified.")

    score = min(100, points)
    if not evidence or len(evidence) < 2:
        tier = "Needs research"
    elif score >= 70:
        tier = "High fit"
    elif score >= 40:
        tier = "Potential fit"
    else:
        tier = "Low fit"
    confidence = "High" if len(evidence) >= 4 and len(domains) >= 3 and not missing else "Medium" if len(evidence) >= 2 else "Low"
    if not evidence:
        missing.append("Search returned no results; retry later or add a verified company URL.")
    return LeadResult(company=company, score=score, tier=tier, rationale=rationale, industry=industry,
                      geography=geography, estimated_size=size_text, signals=signals,
                      missing_information=missing, confidence=confidence, human_review_required=True, evidence=evidence)
