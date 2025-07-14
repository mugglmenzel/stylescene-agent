from dotenv import load_dotenv

load_dotenv()

import argparse
import os

import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

from adk_agent.agent import (
    artifact_service_builder,
    root_agent,
    session_service_builder,
)


def _parse_args():
    parser = argparse.ArgumentParser(description="Deploy the StyleScene agent.")
    parser.add_argument(
        "--resource-name",
        type=str,
        default=None,
        help="The resource name of the Reasoning Engine.",
    )
    parser.add_argument(
        "--gcs-dir-name",
        type=str,
        default="adk_agent",
        help="The GCS directory name for the agent.",
    )
    args = parser.parse_args()
    return args

def _extract_session_id(session):
    try:
        session_id = session["id"] if isinstance(session, dict) and "id" in session else session.id
    except:
        session_id = None
    return session_id


def _test_agent(app: AdkApp, agent_resource: str):
    os.environ["GOOGLE_CLOUD_AGENT_ENGINE_ID"] = agent_resource.split("/")[-1]
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"

    user_id = "u_123"
    session = app.create_session(user_id=user_id)
    for event in app.stream_query(
        user_id=user_id,
        session_id=_extract_session_id(session),
        message="Redress a generated Google engineer with a generated barista outfit",
    ):
        print(event)


def main():
    """Initializes and deploys the StyleScene agent."""
    args = _parse_args()

    vertexai.init(staging_bucket="gs://sandbox-michael-menzel-adk-staging-us-central1")

    agent_name = "StyleScene Agent"
    env_vars = {"GOOGLE_GENAI_USE_VERTEXAI": "1", "NUM_WORKERS": "1"}

    app = AdkApp(
        agent=root_agent,
        session_service_builder=session_service_builder,
        artifact_service_builder=artifact_service_builder,
        enable_tracing=True,
        env_vars=env_vars,
    )

    existing_agents = list(agent_engines.list(filter=f'display_name="{agent_name}"'))
    print("Deploying StyleScene Agent...")
    if args.resource_name is None and len(existing_agents) == 0:
        remote_app = agent_engines.create(
            display_name=agent_name,
            agent_engine=app,
            gcs_dir_name=args.gcs_dir_name,
            requirements="deployment/agent-requirements.txt",
            extra_packages=["./adk_agent"],
            env_vars=env_vars,
        )
    else:
        agent_resource = args.resource_name or existing_agents[0].resource_name
        _test_agent(app, agent_resource)
        remote_app = agent_engines.update(
            resource_name=agent_resource,
            display_name=agent_name,
            agent_engine=app,
            gcs_dir_name=args.gcs_dir_name,
            requirements="deployment/agent-requirements.txt",
            extra_packages=["./adk_agent"],
            env_vars=env_vars,
        )
        _test_agent(remote_app, agent_resource)

    print("\n=== Deployment successful! ===")


if __name__ == "__main__":
    main()
