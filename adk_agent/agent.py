from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import Agent
from google.adk.artifacts import GcsArtifactService
from google.adk.sessions import VertexAiSessionService
from google.adk.runners import Runner

from .callbacks import artifacts_augmentation_callback
from .tools import (
    generate_clothing,
    generate_person,
    generate_redress,
    store_user_content_artifacts,
)

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
    output_key="output",
    before_model_callback=artifacts_augmentation_callback,
)


artifact_service_builder = lambda: GcsArtifactService(
    bucket_name="sandbox-michael-menzel-adk-staging-us-central1"
)
session_service_builder = lambda: VertexAiSessionService()
