
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/validation/status")
def get_validation_status(feature: str):
    mock_status_map = {
        "User Authentication": "Pass",
        "Payment Gateway": "Fail",
        "Session Timeout": "Incomplete"
    }
    if feature not in mock_status_map:
        raise HTTPException(status_code=404, detail="Feature not found")
    return {"status": mock_status_map[feature]}
