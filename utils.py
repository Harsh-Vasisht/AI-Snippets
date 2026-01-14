# File: src/utils.py

import traceback
from utils.logger_setup import setup_logger
import re
import json
from utils.shared_store import SessionStore
# from rich import print
logger = setup_logger('pr_agent_utils')

def get_diff_from_githubV1(repo_url: str, feature_branch: str, base_branch: str, trace = None, next_trace = None) -> str:
    """
    Placeholder function to simulate fetching a git diff.
    
    In a real implementation, you would use a library like GitPython or PyGithub
    to clone the repository, check out the branches, and run a `git diff` command.
    This process requires handling credentials securely.
    
    Args:
        repo_url: The URL of the repository.
        feature_branch: The branch with the new code.
        base_branch: The branch to compare against (e.g., 'main' or 'develop').
        
    Returns:
        A string containing the full git diff.
    """
    logger.info(f"Simulating git diff between {base_branch} and {feature_branch} for {repo_url}")
    return """
diff --git a/src/run.py b/src/run.py
index e69de29..9dae4a7 100644
--- a/src/run.py
+++ b/src/run.py
@@ -0,0 +1,52 @@
+import traceback
+from flask import Flask, jsonify, request
+from flask_cors import cross_origin
+
+from utils.logger_setup import setup_logger
+from .pull_request_agent import NanoBanana
+
+app = Flask(__name__)
+logger = setup_logger("pull_request_agent_run")
+
+PREFIX = "/utility/nano-banana-agent"
+AGENT_NAME = NanoBanana
+
+def prediction(data):
+    try:
+        agent = AGENT_NAME()
+        # This should fetch config from MongoDB
+        config = get_setup_details(data['concierge_id'], data['agent_id'])
+        if config is None:
+            raise ValueError("Could not fetch setup config from MongoDB")
+        
+        agent.setup(config=config, data=data)
+        
+        response, _ = agent.run(**data['agent_arguments'])
+        
+        return response
+
+    except Exception as e:
+        logger.exception(f"Error in prediction: {str(e)} \\n Traceback: {traceback.format_exc()}")
+        raise
+
+@app.route(f'{PREFIX}/prediction', methods=['POST'])
+@cross_origin(supports_credentials=True)
+def predict_api():
+    try:
+        data = request.get_json()
+        logger.info(f"Received prediction request to {AGENT_NAME.__name__} with data: {data}")
+        
+        if 'agent_arguments' not in data or 'github_url' not in data['agent_arguments']:
+            return jsonify({"error": "Missing required fields in agent_arguments"}), 400
+
+        response = prediction(data)
+        return jsonify({"response": response}), 200
+    
+    except Exception as e:
+        logger.exception(f"Error in prediction API: {str(e)} \\n Traceback: {traceback.format_exc()}")
+        return jsonify({"error": str(e)}), 500"""

def get_diff_from_github(diff_json, trace = None, next_trace = None, base_branch = "main", URL = "", feature_branch = "") -> str:
    print(f"++++++++++++++++++++++++++++++++++++++++++\n get_diff_from_github triggered with base_branch: {base_branch}, feature_branch: {feature_branch}, URL: {URL}  diff_json: {diff_json}  ++++++++++++++++++++++++++++++++++++++++++\n")
    holisticInfo = f"#General Info \n - base_branch: {base_branch}\n - target_branch: {feature_branch}\n - URL: {URL}\n # Staged Code Changes\n"
    try:
        diff_json = json.loads(diff_json) if isinstance(diff_json, str) else diff_json
        patch_lines = []
        for file_change in diff_json:
            filename = file_change["file"]
            changes = file_change["changes"]

            patch_lines.append(f"--- a/{filename}")
            patch_lines.append(f"+++ b/{filename}")

            for change in changes:
                ctype = change["type"]
                if ctype == "addition":
                    new = change["new"]
                    patch_lines.append(f"@@ +{new['line']},{new['startCol']} @@")
                    patch_lines.append(f"+{new['content']}")
                elif ctype == "modification":
                    old = change["old"]
                    new = change["new"]
                    patch_lines.append(f"@@ -{old['line']},{old['startCol']} +{new['line']},{new['startCol']} @@")
                    patch_lines.append(f"-{old['content']}")
                    patch_lines.append(f"+{new['content']}")
                elif ctype == "deletion":
                    old = change["old"]
                    patch_lines.append(f"@@ -{old['line']},{old['startCol']} @@")
                    patch_lines.append(f"-{old['content']}")
        
        print("\n [bold green]data fetched from github[/bold green] \n")
        response = holisticInfo + '\n'.join(patch_lines)
        # print("response ---------------------> ", response[:100])
        return response
    except Exception as e:
        traceback.print_exc()
        logger.exception(f"Error in get_diff_from_github: {e}")
        response = holisticInfo + f"\n .Diff JSON from ContentTool: {diff_json} \n."
        return response  


def parse_json_from_string(text: str, key: str = 'json') -> dict:
    """Extract JSON content from between markdown code blocks."""

    pattern = f"```{key}[\\s\\S]*?```"
    matches = re.findall(pattern, text)

    if not matches:
        logger.warning(f"No {key} block found in response")
        return {}

    json_str = matches[0].replace(f"```{key}", "").replace("```", "").strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        return {}
    
def extract_response_from_delimeters(ai_response, extraction_key="response"):
    """
    Extract the response from the response string.
    Parameters: ai_response (str): The response string.
    Returns: response (str): The extracted response content.
    """
    try:
        json_code_start = f"```{extraction_key}"
        json_code_end = "```"
        start_index = ai_response.find(json_code_start) + len(json_code_start)
        end_index = ai_response.find(json_code_end, start_index)
        if start_index != -1 and end_index != -1:
            json_response = ai_response[start_index:end_index].strip()
        # print("AI Response---", json_response)
        return json_response
    except Exception as e:
        traceback.print_exc()
        logger.exception(f"Error in extract_response_from_delimeters: {e}")
        raise e
    
def get_data_api(session_id):
    try:
        store = SessionStore(session_id=session_id)
        blob = store.bucket.blob(f"sessions/metadata/{session_id}.json")
        if not blob.exists():
            print(f"No session data found for session_id: {session_id}")
            return None
        data = blob.download_as_string()
        session_data = json.loads(data)
        # with open(f"/tmp/{session_id}.json", "w") as f:
        #     json.dump(session_data, f, indent=4)
        return session_data
    except Exception as e:
        traceback.print_exc()
        return None
    
