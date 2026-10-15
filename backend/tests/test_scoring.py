from app.models import ICP, Evidence
from app.scoring import score_lead

def ev(title, snippet, url):
    from urllib.parse import urlparse
    return Evidence(title=title, snippet=snippet, url=url, source_domain=urlparse(url).netloc)

def test_no_evidence_is_conservative():
    result = score_lead("Unknown Co", [], ICP())
    assert result.score == 0
    assert result.tier == "Needs research"
    assert result.confidence == "Low"
    assert result.human_review_required is True

def test_evidence_generates_explainable_score():
    evidence = [
        ev("Acme SaaS AI platform", "US-based SaaS company offering cloud analytics and AI automation", "https://acme.example/about"),
        ev("Acme company profile", "Technology platform; team of 600 employees", "https://directory.example/acme"),
    ]
    result = score_lead("Acme", evidence, ICP())
    assert 0 <= result.score <= 100
    assert result.evidence == evidence
    assert result.rationale
    assert result.human_review_required

def test_unknown_data_is_marked_missing():
    result = score_lead("Plain Name", [ev("Company", "A company profile", "https://example.com")], ICP())
    assert result.missing_information
