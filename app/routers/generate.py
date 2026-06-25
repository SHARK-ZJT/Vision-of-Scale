import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.dependencies import get_db
from app.schemas.generation import GenerateRequest, GenerationOut, ImageResult
from app.models.generation import Generation
from app.models.prompt_template import PromptTemplate
from app.services.image_api import generate_images, ImageAPIError
from app.services.image_storage import download_and_save, ImageStorageError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["generate"])


@router.post("/generate", response_model=GenerationOut, status_code=201)
async def api_generate(
    body: GenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate images from a text prompt using 火山引擎 即梦AI (Seedream 4.0)."""
    # Create a generation record (pending)
    generation = Generation(
        prompt=body.prompt,
        model="doubao-seedream-4-0-250828",
        size=body.size,
        seed=body.seed,
        n_images=body.n,
        template_id=body.template_id,
        collection_id=body.collection_id,
        status="generating",
    )
    db.add(generation)
    await db.commit()
    await db.refresh(generation)

    try:
        # Call the 火山引擎 image generation API
        api_response = await generate_images(
            prompt=body.prompt,
            size=body.size,
            n=body.n,
            seed=body.seed,
        )

        # Parse response and download images
        data = api_response.get("data", [])
        images: list[ImageResult] = []
        local_path = None
        thumbnail_path = None
        original_url = None

        async with httpx.AsyncClient(timeout=120.0) as http_client:
            for idx, item in enumerate(data):
                url = item.get("url", "")

                if url:
                    # Download and save locally
                    try:
                        local, thumb = await download_and_save(
                            url, client=http_client, filename_prefix=f"gen{generation.id}_"
                        )
                        img_result = ImageResult(
                            local_path=local,
                            thumbnail_path=thumb,
                            original_url=url,
                        )
                        images.append(img_result)

                        # Store first image paths on the generation record
                        if idx == 0:
                            local_path = local
                            thumbnail_path = thumb
                            original_url = url
                    except ImageStorageError as e:
                        logger.error(f"Failed to download image {idx}: {e.message}")
                        img_result = ImageResult(original_url=url)
                        images.append(img_result)

        # Update the generation record
        generation.status = "completed"
        generation.local_path = local_path
        generation.thumbnail_path = thumbnail_path
        generation.original_url = original_url
        generation.api_response = json.dumps(api_response)
        await db.commit()
        await db.refresh(generation)

        # Increment template usage count
        if body.template_id:
            await db.execute(
                update(PromptTemplate)
                .where(PromptTemplate.id == body.template_id)
                .values(usage_count=PromptTemplate.usage_count + 1)
            )
            await db.commit()

        # Build response
        template_name = None
        if generation.template_id:
            tpl = await db.get(PromptTemplate, generation.template_id)
            if tpl:
                template_name = tpl.name

        return GenerationOut(
            id=generation.id,
            prompt=generation.prompt,
            model=generation.model,
            size=generation.size,
            seed=generation.seed,
            n_images=generation.n_images,
            images=images,
            local_path=local_path,
            thumbnail_path=thumbnail_path,
            original_url=original_url,
            template_id=generation.template_id,
            template_name=template_name,
            collection_id=generation.collection_id,
            status="completed",
            error_message=None,
            created_at=generation.created_at,
        )

    except ImageAPIError as e:
        generation.status = "failed"
        generation.error_message = e.message
        await db.commit()
        raise HTTPException(status_code=e.status_code or 500, detail=e.message)

    except Exception as e:
        generation.status = "failed"
        generation.error_message = str(e)
        await db.commit()
        logger.exception("Unexpected error during generation")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")
