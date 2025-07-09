from google.adk.agents import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from .tools import (generate_clothing, generate_person, generate_redress,
                    store_user_content_artifacts)

root_agent = Agent(
    name="stylescene_agent",
    model="gemini-2.5-flash",
    description=(
        "An agent allowing to redress persons, modify the scene, and animate as video."
    ),
    instruction=(
        "You are a helpful agent who can generate, modify, and animate scenes as images and videos."
    ),
    tools=[
        store_user_content_artifacts,
        generate_person,
        generate_clothing,
        generate_redress,
    ],
)

artifact_service = InMemoryArtifactService()
session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name="stylescene_agent_app",
    session_service=session_service,
    artifact_service=artifact_service,
)
