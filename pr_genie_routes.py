
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.pr_genie import PRGenieAnalyzer

router = APIRouter()

class PRRequest(BaseModel):
    language: str
    code: str
    custom_rules: list = []

@router.post("/pr-genie/analyze")
def analyze_pr(request: PRRequest):
    analyzer = PRGenieAnalyzer(language=request.language, custom_rules=request.custom_rules)
    try:
        issues = analyzer.analyze_pr(request.code)
        return {"issues": issues}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
