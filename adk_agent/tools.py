import base64
import uuid

from google import genai
from google.adk.tools import ToolContext
from google.cloud import aiplatform
from google.cloud import aiplatform_v1 as aip
from google.genai import types

genai_client = genai.Client()
gcp_project_id = genai_client._api_client.project
gcp_location = genai_client._api_client.location
aiplatform.init()


async def _generated_image_to_part(image: types.GeneratedImage) -> types.Part:
    return types.Part.from_bytes(
        data=image.image.image_bytes, mime_type=image.image.mime_type
    )


async def store_user_content_artifacts(tool_context: ToolContext) -> dict:
    """
    Stores uploaded content from a user as artifacts for later use with tools.
    """
    artifacts = []
    for part in tool_context.user_content.parts:
        if part.inline_data:
            artifact_id = f"artifact_{uuid.uuid4()}"
            await tool_context.save_artifact(artifact_id, part)
            artifacts.append(artifact_id)
    return {"artifacts": artifacts}


async def generate_person(person_description: str, tool_context: ToolContext) -> dict:
    print("tool_context", vars(tool_context))
    response = genai_client.models.generate_images(
        model="imagen-4.0-fast-generate-preview-06-06",
        prompt=f"Generate a photorealistic, full-body image of a person on a plain white background, suitable for use in a virtual try-on application. The person should be the main focus. Person description: {person_description}",
        config=types.GenerateImagesConfig(number_of_images=1),
    )
    person_image = response.generated_images[0]
    person_image_part = await _generated_image_to_part(person_image)
    await tool_context.save_artifact("person.image", person_image_part)
    return {
        "status": "success",
        "message": "Image 'person.image' successfully generated.",
        "artifact_name": "person.image",
    }


async def generate_clothing(
    clothing_description: str, tool_context: ToolContext
) -> dict:
    response = genai_client.models.generate_images(
        model="imagen-4.0-fast-generate-preview-06-06",
        prompt=f"Generate a photorealistic image of this clothing item on a plain white background, suitable for a product catalog. The item should be the main focus. {clothing_description}",
        config=types.GenerateImagesConfig(number_of_images=1),
    )
    clothing_image = response.generated_images[0]
    clothing_image_part = await _generated_image_to_part(clothing_image)
    await tool_context.save_artifact("clothing.image", clothing_image_part)
    return {
        "status": "success",
        "message": "Image 'clothing.image' successfully generated.",
        "artifact_name": "clothing.image",
    }


async def generate_redress(
    person_image_artifact: str, clothing_image_artifact: str, tool_context: ToolContext
) -> dict:
    print("tool_context", vars(tool_context))
    person_image: types.Part = await tool_context.load_artifact(person_image_artifact)
    clothing_image: types.Part = await tool_context.load_artifact(
        clothing_image_artifact
    )

    aip_client = aip.PredictionServiceClient()
    request = aip.PredictRequest()
    request.endpoint = f"projects/{gcp_project_id}/locations/{gcp_location}/publishers/google/models/virtual-try-on-exp-05-31"
    request.instances.append(
        {
            "personImage": {
                "image": {
                    "bytesBase64Encoded": base64.b64encode(
                        person_image.inline_data.data
                    ).decode("utf-8"),
                    "mimeType": person_image.inline_data.mime_type,
                }
            },
            "productImages": [
                {
                    "image": {
                        "bytesBase64Encoded": base64.b64encode(
                            clothing_image.inline_data.data
                        ).decode("utf-8"),
                        "mimeType": clothing_image.inline_data.mime_type,
                    }
                }
            ],
        },
    )
    request.parameters = {"sampleCount": 1}
    response = aip_client.predict(request=request)
    response_bytes = base64.b64decode(response.predictions[0]["bytesBase64Encoded"])
    redress_image_part = types.Part.from_bytes(
        data=response_bytes, mime_type="image/png"
    )
    await tool_context.save_artifact("redress.image", redress_image_part)
    return {
        "status": "success",
        "message": "Image 'redress.image' successfully generated.",
        "artifact_name": "redress.image",
    }


async def generate_scene_background(
    person_image_artifact: str, scene_description: str, tool_context: ToolContext
) -> dict:
    person_image: types.Part = await tool_context.load_artifact(person_image_artifact)

    reference_image = types.RawReferenceImage(
        referenceId=0,
        referenceImage=types.Image(
            imageBytes=person_image.inline_data.data,
            mime_type=person_image.inline_data.mime_type,
        ),
    )
    mask_image = types.MaskReferenceImage(
        reference_id=1,
        config=types.MaskReferenceConfig(
            mask_mode=types.MaskReferenceMode.MASK_MODE_BACKGROUND
        ),
    )

    response = genai_client.models.edit_image(
        model="imagen-3.0-capability-001",
        prompt=f"Generate a photorealistic image of the person [0] from the reference image in this scene: {scene_description}. The final image should be a coherent and high-quality photograph.",
        reference_images=[reference_image, mask_image],
        config=types.EditImageConfig(
            aspect_ratio="16:9",
            number_of_images=1,
            edit_mode=types.EditMode.EDIT_MODE_BGSWAP,
        ),
    )

    scene_image = response.generated_images[0]
    scene_image_part = await _generated_image_to_part(scene_image)
    await tool_context.save_artifact("scene.image", scene_image_part)

    return {
        "status": "success",
        "message": "Image 'scene.image' successfully generated.",
        "artifact_name": "scene.image",
    }
