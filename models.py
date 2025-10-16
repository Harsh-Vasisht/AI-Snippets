from pydantic import BaseModel
from typing import Union

class PRInfo(BaseModel):
    github_url: str
    branch_name: str
    user_id: str
    session_id: str

class PRUpdate(BaseModel):
    session_id: str
    key: str
    value: Union[str, dict]
