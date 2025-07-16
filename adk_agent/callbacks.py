import os

from google.adk.agents.llm_agent import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.genai import types


async def artifacts_augmentation_callback(callback_context: CallbackContext, llm_request: LlmRequest):
    invocation_context = (
        callback_context._invocation_context
    )  # pylint: disable=protected-access
    if invocation_context.artifact_service is not None:

        filenames = await invocation_context.artifact_service.list_artifact_keys(
            app_name=invocation_context.app_name,
            user_id=invocation_context.user_id,
            session_id=invocation_context.session.id,
        )

        llm_request.contents[-1].parts.append(
            types.Part.from_text(text=f"Attached images stored as artifacts: {filenames}")
        )
        print(f"Attached artifacts: {filenames}")
    return None
