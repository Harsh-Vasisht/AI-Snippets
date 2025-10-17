
from typing import List, Dict

def generate_pr_table(pr_focus: str, side_effects: str, status: str, important_files: List[str], pr_url: str) -> str:
    """
    Generate a markdown table summarizing a pull request.
    - pr_focus: concise summary of PR objective
    - side_effects: potential unintended consequences
    - status: PR status
    - important_files: list of critical file paths
    - pr_url: base URL to link files in the PR
    Returns: markdown string
    """
    if not pr_focus or not status or important_files is None:
        return "PR summary could not be generated."
    
    # Limit to top 5 files
    top_files = important_files[:5]
    files_md = [f"[{f}]({pr_url}/blob/main/{f})" for f in top_files]
    if len(important_files) > 5:
        files_md.append(f"...and {len(important_files)-5} more")
    
    side_effects_md = side_effects if side_effects else "None identified"
    
    table_md = f"""
| PR Focus | Side Effects | Status | Important Files |
|----------|-------------|--------|----------------|
| {pr_focus} | {side_effects_md} | {status} | {', '.join(files_md)} |
"""
    return table_md
