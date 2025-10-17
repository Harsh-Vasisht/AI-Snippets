
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.pr_summary import generate_pr_table

router = APIRouter()

class PRSummaryRequest(BaseModel):
    pr_focus: str
    side_effects: str = ""
    status: str
    important_files: List[str]
    pr_url: str

@router.post("/pr-summary/table")
def pr_summary(request: PRSummaryRequest):
    try:
        markdown_table = generate_pr_table(
            pr_focus=request.pr_focus,
            side_effects=request.side_effects,
            status=request.status,
            important_files=request.important_files,
            pr_url=request.pr_url
        )
        return {"markdown_table": markdown_table}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PR table: {str(e)}")
