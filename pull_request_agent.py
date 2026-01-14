# File: src/pull_request_agent.py

import traceback
from pydantic import Field
import json
from typing import Optional, Annotated

from llm_studio_agents.AgentBase import AgentBase, AgentSetupBase, AgentsTraceBase
from llm_studio_agents.utils.utils import process_config, accumulator
from llm_studio_tools.common_orchestrator import CommonOrchestratorCallTool
from utils.logger_setup import setup_logger
from utils.shared_store import SessionStore
from utils.utils_agent_pubsub import send_streaming_response_to_pubsub

from agent_tools.content_tool import ContentTool
from agent_tools.generate_title_desc_tool import GenerateTitleDescTool
from agent_tools.met_requirements_tool import JiraCriteriaCheckTool

from pull_request_agent.src.utils import get_data_api

logger = setup_logger('pull_request_agent')


class PullRequestAgentSetup(AgentSetupBase):
    use_orchestrator_llm: Optional[bool] = Field(
        default=True,
        description="Enable the intelligence layer to decide which tools to call.",
        title="Use Orchestrator LLM",
        toolToggle=CommonOrchestratorCallTool.__name__,
    )
    fallback_response: Optional[str] = Field(
        "There was an issue processing your pull request.",
        description="Default response when no suitable answer can be generated.",
    )


class PullRequestAgentTrace(AgentsTraceBase, PullRequestAgentSetup):
    content_tool_trace: Optional[dict] = None
    generate_title_desc_tool_trace: Optional[dict] = None
    jira_criteria_check_tool_trace: Optional[dict] = None


class PullRequestAgent(AgentBase):
    CONFIG_CLASS = PullRequestAgentSetup

    def setup(self, config: dict, data=None) -> dict:
        logger.info("Setting up Pull Request Agent with config and data")
        self.payload = data
        self.config = config
        self.use_orchestrator_llm = config.get("use_orchestrator_llm", True)
        self.smart_response_adjustment = config.get("smart_response_adjustment", True)

        # Extract branch info from agent_arguments or metadata
        agent_args = data.get("agent_arguments", {})
        metadata = data.get("metadata")
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except Exception:
                metadata = {}

        self.source_branch = (
            metadata.get("sourceBranch") or metadata.get("source_branch") or agent_args.get("source_branch")
        )
        self.target_branch = (
            metadata.get("targetBranch") or metadata.get("target_branch") or agent_args.get("target_branch")
        )

        # Initialize tools config
        content_tool_config = process_config(config["tools"][ContentTool.__name__], sub_level="integrations")
        self.content_tool = ContentTool(config=content_tool_config, data=data)

        self.session_id = data.get("preview_id", "")
        self.sharedStorage = SessionStore(session_id=self.session_id)
        self.question = data.get("question", "")
        self.metadata = metadata or {}

        # Fetch stagedChanges from session store (GCS-backed)
        session_data = get_data_api(self.session_id)
        self.stagedChanges = session_data.get("stagedChanges", []) if session_data else []
        logger.info(f"Fetched stagedChanges: {self.stagedChanges}")

        # Update agent_arguments with stagedChanges and branch data
        if "agent_arguments" not in data:
            data["agent_arguments"] = {}
        data["agent_arguments"]["stagedChanges"] = self.stagedChanges
        data["agent_arguments"]["source_branch"] = self.source_branch
        data["agent_arguments"]["target_branch"] = self.target_branch

        # Store data in session storage
        self.sharedStorage.set_data(
            {
                "question": self.question,
                "metadata": self.metadata,
                "stagedChanges": self.stagedChanges,
                "source_branch": self.source_branch,
                "target_branch": self.target_branch,
            }
        )

        gen_title_tool_config = process_config(config["tools"][GenerateTitleDescTool.__name__], sub_level="integrations")
        self.gen_title_tool = GenerateTitleDescTool(config=gen_title_tool_config, data=data)

        jira_criteria_check_tool_config = process_config(config["tools"][JiraCriteriaCheckTool.__name__], sub_level="integrations")
        self.jira_tool = JiraCriteriaCheckTool(config=jira_criteria_check_tool_config, data=data)

        tools = [ContentTool, GenerateTitleDescTool, JiraCriteriaCheckTool]
        tool_configs = {
            ContentTool.__name__: content_tool_config,
            GenerateTitleDescTool.__name__: gen_title_tool_config,
            JiraCriteriaCheckTool.__name__: jira_criteria_check_tool_config,
        }

        common_orchestrator_llm_config = process_config(
            config=config["tools"][CommonOrchestratorCallTool.__name__], sub_level="integrations"
        )
        self.manager_llm_tool = CommonOrchestratorCallTool()
        self.manager_llm_tool.setup(tools=tools, tools_config=tool_configs, config=common_orchestrator_llm_config, data=data)

        return config

    def run(
        self,
        github_url: Annotated[str, "The URL of the GitHub repository."],
        branch_name: Annotated[str, "The name of the branch for the pull request."],
        stagedChanges: Annotated[str, "The staged changes content in JSON format."] = None,
        agent_arguments: Annotated[dict, "Additional arguments for the agent."] = None,
        user_prompt: Annotated[str, "The user prompt for the pull request."] = None,
        trace=None,
        next_trace=None,
        jira_url: Annotated[str, "The URL of the Jira instance."] = None,
        jira_ticket_details: Annotated[dict, "Details of the Jira ticket."] = None,
    ) -> dict:
        try:
            logger.info("Inside Pull Request Agent run method")
            send_streaming_response_to_pubsub(
                data=self.payload,
                text="Pull Request Agent processing started...",
                is_stream_end=False,
                thinking_break=False,
                header_message=json.dumps({"status": "pending", "agent": "Pull Request Agent"}),
            )

            user_query = user_prompt or (
                f"hey, please help me to generate a pull request title and description for the changes in the branch '{self.source_branch}' "
                f"from the repository '{github_url}'."
            )
            send_streaming_response_to_pubsub(
                data=self.payload,
                text="Running orchestrator to generate PR metadata...",
                is_stream_end=False,
                thinking_break=True,
            )

            response = self.manager_llm_tool.run(query=self.question, trace=trace, next_trace=next_trace)

            logger.info("Process completed in pull request agent")
            send_streaming_response_to_pubsub(
                data=self.payload,
                text="Pull Request Agent completed successfully.",
                is_stream_end=True,
                thinking_break=False,
            )

            return response, {}, not self.smart_response_adjustment

        except Exception as e:
            send_streaming_response_to_pubsub(
                data=self.payload,
                text="An error occurred in Pull Request Agent.",
                is_stream_end=True,
                thinking_break=False,
            )
            logger.exception(f"Error in Pull Request Agent run method: {e}")
            traceback.print_exc()
            return {"error": str(e)}, {}, not self.smart_response_adjustment

    @classmethod
    def get_setup_config(cls) -> dict:
        return accumulator(
            cls.CONFIG_CLASS,
            cls.__name__,
            [
                ContentTool,
                GenerateTitleDescTool,
                JiraCriteriaCheckTool,
                CommonOrchestratorCallTool,
            ],
            "tools",
        )
