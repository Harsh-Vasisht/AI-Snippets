# File: src/run.py

import time
import traceback
from flask import Flask, jsonify, request
from flask_cors import cross_origin

from llm_studio_tools.utils.utils import get_setup_details, process_config
from utils.logger_setup import setup_logger
from utils.shared_store import SessionStore
from pull_request_agent.src.pull_request_agent import PullRequestAgent
from utils.utils_agent_pubsub import send_streaming_response_to_pubsub
import json

app = Flask(__name__)
logger = setup_logger("pull_request_agent_run")

PREFIX = "/utility/pull-request-agent"
AGENT_NAME = PullRequestAgent


def prediction(data, trace):
    trace = {}
    next_trace = {}
    try:
        agent = AGENT_NAME()
        db = None
        if data.get('preview_id'):
            db = SessionStore(session_id=data['preview_id'])
        data['db'] = db

        # Extract source_branch and target_branch preferably from metadata
        metadata = data.get("metadata")
        source_branch = None
        target_branch = None
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except Exception:
                metadata = {}
        if metadata:
            source_branch = metadata.get("sourceBranch") or metadata.get("source_branch")
            target_branch = metadata.get("targetBranch") or metadata.get("target_branch")
        # Fallback from agent_arguments if not present
        if not source_branch:
            source_branch = data["agent_arguments"].get("source_branch")
        if not target_branch:
            target_branch = data["agent_arguments"].get("target_branch")

        # Add source_branch and target_branch to agent_arguments for downstream use
        if 'agent_arguments' not in data:
            data['agent_arguments'] = {}
        data['agent_arguments']['source_branch'] = source_branch
        data['agent_arguments']['target_branch'] = target_branch

        # Initial waiting room message
        meta_start = json.dumps({"status": "pending", "agent": "Pull Request Agent"})
        header_message_start = f'Welcome to Pull request agent [[meta: {meta_start}]]'
        send_streaming_response_to_pubsub(
            data=data,
            text="Processing your request...",
            is_stream_end=False,
            thinking_break=False,
            header_message=header_message_start,
        )

        # Fetch the real configuration from MongoDB
        config = get_setup_details(data['concierge_id'], data['agent_id'])
        if config is None:
            raise ValueError("Could not fetch setup config from MongoDB")

        send_streaming_response_to_pubsub(
            data=data,
            text="Configuration fetched. Running agent...",
            is_stream_end=False,
            thinking_break=True,
        )

        agent_config = process_config(config=config, sub_level="tools")
        agent.setup(config=agent_config, data=data)

        # Run agent with required fields, ensuring stagedChanges are loaded inside the agent from SessionStore
        response, _, bypass_orchestrator_response = agent.run(
            trace=trace,
            next_trace=next_trace,
            github_url=data['agent_arguments']['github_url'],
            branch_name=source_branch if source_branch else data['agent_arguments']['branch_name'],
            stagedChanges=None,  # The agent loads this internally from SessionStore
            agent_arguments=data['agent_arguments'],
            jira_url=data['agent_arguments'].get('jira_url'),
            jira_ticket_details=data['agent_arguments'].get('jira_ticket_details')
        )

        send_streaming_response_to_pubsub(
            data=data,
            text="Pull Request Agent execution completed successfully.",
            is_stream_end=True,
            thinking_break=False,
        )
        shared_storage = SessionStore(session_id=data.get('preview_id'))
        response_data = {}
        shared_storage_data = shared_storage.get_data()
        if "business_logic_output" in shared_storage_data:
            response_data["business_logic_output"] = shared_storage_data["business_logic_output"]
        if "criteria_validation_json" in shared_storage_data:
            response_data["met_requirements_output"] = shared_storage_data["criteria_validation_json"]
        if "requirements_data" in shared_storage_data:
            response_data["requirements_data"] = shared_storage_data["requirements_data"]

        return response, response_data, trace, bypass_orchestrator_response

    except Exception:
        send_streaming_response_to_pubsub(
            data=data,
            text="An error occurred while running the Pull Request Agent.",
            is_stream_end=True,
            thinking_break=False,
        )
        traceback.print_exc()
        raise


@app.route(f'{PREFIX}/prediction', methods=['POST'])
@cross_origin(supports_credentials=True)
def predict_api():
    trace = {}
    try:
        data = request.get_json()
        logger.info(f"Received prediction request to {AGENT_NAME.__name__} with data: {data}")

        # Basic validation
        required_agent_args = ['github_url']
        if 'agent_arguments' not in data or not all(k in data['agent_arguments'] for k in required_agent_args):
            return jsonify({"error": f"Missing required fields in agent_arguments: {required_agent_args}"}), 400

        required_top_level = ['concierge_id', 'agent_id', 'preview_id', 'agent_arguments']
        if not all(k in data for k in required_top_level):
            return jsonify({"error": f"Missing required top-level fields: {required_top_level}"}), 400

        response, response_data, trace, bypass_orchestrator_response = prediction(data, trace)

        return jsonify({
            "response": response,
            "response_json": response_data,
            "trace": trace,
            "trace_root": trace.pop('root', None),
            "bypass_orchestrator_response": bypass_orchestrator_response
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e), "trace": trace, "trace_root": trace.pop('root', None)}), 500


@app.route(f'{PREFIX}/save_data', methods=['POST'])
@cross_origin(supports_credentials=True)
def save_data_api():
    try:
        data = request.get_json()
        session_id = data.get("session_id")
        session_data = data.get("data")

        if not session_id or not isinstance(session_data, dict):
            return jsonify({"error": "Missing session_id or data"}), 400

        timestamp = int(time.time())
        store = SessionStore(session_id=session_id)

        blob = store.bucket.blob(f"sessions/metadata/{session_id}.json")
        blob.upload_from_string(json.dumps(session_data))

        return jsonify({
            "success": True,
            "message": "Session data stored in GCS",
            "path": f"pr-agent/sessions/{session_id}_{timestamp}.json"
        }), 200

    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
        return jsonify({"error": "Failed to save data"}), 400


@app.route(f'{PREFIX}/get_config', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_config_api():
    try:
        response = AGENT_NAME.get_setup_config()
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error in get_config_api: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route(f'{PREFIX}/get_llm_config', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_llm_config_api():
    try:
        response = AGENT_NAME().get_llm_config()
        if response:
            return jsonify(response), 200
        else:
            return jsonify({"message": "No LLM configuration found"}), 204
    except Exception as e:
        logger.info(f"Error in get_llm_config_api: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route(f"{PREFIX}/get_session_data", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_current_session_data():
    try:
        db = None
        session_id = request.args.get("session_id", "")
        key = request.args.get("key", "")
        session_data = {}
        if session_id:
            db = SessionStore(session_id=session_id)
            session_data = db.get_data()
        else:
            return jsonify({"error": "Missing session_id parameter"}), 400

        if session_data is not None:
            status_info = {
                "total_keys": len(session_data.keys()),
                "key_names": list(session_data.keys()),
            }

            if key:
                if key in session_data:
                    return jsonify({
                        "status": status_info,
                        "data": {key: session_data[key]},
                        "filtered_key": key
                    }), 200
                else:
                    return jsonify({
                        "status": status_info,
                        "message": f"Key '{key}' not found in session data",
                        "available_keys": list(session_data.keys())
                    }), 404
            else:
                return jsonify({
                    "status": status_info,
                    "data": session_data
                }), 200
        else:
            return jsonify({"message": "No data found for this session"}), 204

    except Exception as e:
        logger.error(f"Error in get_current_session_data: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route(f'{PREFIX}/')
def home():
    return f"{AGENT_NAME.__name__} is running!", 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002)
