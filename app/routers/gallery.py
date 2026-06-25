import math
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import templates
from app.dependencies import get_db
from app.models.generation import Generation
from app.models.collection import Collection
from app.models.prompt_template import PromptTemplate
from app.schemas.generation import GenerationOut, GenerationListOut, GenerationUpdate
from app.services.image_storage import delete_image_files

router = APIRouter(tags=["gallery"])


@router.get("/api/generations", response_model=GenerationListOut)
async def list_generations(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    collection_id: int | None = Query(None),
    template_id: int | None = Query(None),
    sort: str = Query("newest"),
    db: AsyncSession = Depends(get_db),
):
    """List generations with pagination and filtering."""
    query = select(Generation)

    if status:
        query = query.where(Generation.status == status)
    else:
        query = query.where(Generation.status == "completed")

    if collection_id:
        query = query.where(Generation.collection_id == collection_id)
    if template_id:
        query = query.where(Generation.template_id == template_id)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Sort
    if sort == "oldest":
        query = query.order_by(Generation.created_at)
    else:
        query = query.order_by(desc(Generation.created_at))

    # Paginate
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    generations = result.scalars().all()

    # Build output with template names
    items = []
    for gen in generations:
        template_name = None
        if gen.template_id:
            tpl = await db.get(PromptTemplate, gen.template_id)
            if tpl:
                template_name = tpl.name

        collection_name = None
        if gen.collection_id:
            col = await db.get(Collection, gen.collection_id)
            if col:
                collection_name = col.name

        items.append(
            GenerationOut(
                id=gen.id,
                prompt=gen.prompt,
                model=gen.model,
                size=gen.size,
                seed=gen.seed,
                n_images=gen.n_images,
                local_path=gen.local_path,
                thumbnail_path=gen.thumbnail_path,
                original_url=gen.original_url,
                template_id=gen.template_id,
                template_name=template_name,
                collection_id=gen.collection_id,
                collection_name=collection_name,
                status=gen.status,
                error_message=gen.error_message,
                created_at=gen.created_at,
            )
        )

    total_pages = max(1, math.ceil(total / per_page))

    return GenerationListOut(
        items=items,
        total=total,
        page=page,
        pages=total_pages,
    )


@router.get("/api/generations/{generation_id}", response_model=GenerationOut)
async def get_generation(
    generation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single generation by ID."""
    gen = await db.get(Generation, generation_id)
    if not gen:
        raise HTTPException(status_code=404, detail="生成记录未找到")

    template_name = None
    if gen.template_id:
        tpl = await db.get(PromptTemplate, gen.template_id)
        if tpl:
            template_name = tpl.name

    return GenerationOut(
        id=gen.id,
        prompt=gen.prompt,
        model=gen.model,
        size=gen.size,
        seed=gen.seed,
        n_images=gen.n_images,
        local_path=gen.local_path,
        thumbnail_path=gen.thumbnail_path,
        original_url=gen.original_url,
        template_id=gen.template_id,
        template_name=template_name,
        collection_id=gen.collection_id,
        status=gen.status,
        error_message=gen.error_message,
        created_at=gen.created_at,
    )


@router.delete("/api/generations/{generation_id}", status_code=200)
async def delete_generation(
    generation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a generation record and its image files."""
    gen = await db.get(Generation, generation_id)
    if not gen:
        raise HTTPException(status_code=404, detail="生成记录未找到")

    # Delete image files from disk
    if gen.local_path:
        delete_image_files(gen.local_path, gen.thumbnail_path or "")

    await db.delete(gen)
    await db.commit()

    return {"message": "已删除", "id": generation_id}


@router.patch("/api/generations/{generation_id}", response_model=GenerationOut)
async def update_generation(
    generation_id: int,
    body: GenerationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a generation (e.g., move to a different collection)."""
    gen = await db.get(Generation, generation_id)
    if not gen:
        raise HTTPException(status_code=404, detail="生成记录未找到")

    if body.collection_id is not None:
        gen.collection_id = body.collection_id

    await db.commit()
    await db.refresh(gen)

    template_name = None
    if gen.template_id:
        tpl = await db.get(PromptTemplate, gen.template_id)
        if tpl:
            template_name = tpl.name

    return GenerationOut(
        id=gen.id,
        prompt=gen.prompt,
        model=gen.model,
        size=gen.size,
        seed=gen.seed,
        n_images=gen.n_images,
        local_path=gen.local_path,
        thumbnail_path=gen.thumbnail_path,
        original_url=gen.original_url,
        template_id=gen.template_id,
        template_name=template_name,
        collection_id=gen.collection_id,
        status=gen.status,
        error_message=gen.error_message,
        created_at=gen.created_at,
    )


# HTMX partial routes
@router.get("/htmx/gallery-grid", response_class=HTMLResponse)
async def htmx_gallery_grid(
    request: Request,
    page: int = Query(1, ge=1),
    collection_id: int | None = Query(None),
    template_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Return gallery grid HTML partial for infinite scroll."""
    per_page = 20

    query = select(Generation).where(Generation.status == "completed")

    if collection_id:
        query = query.where(Generation.collection_id == collection_id)
    if template_id:
        query = query.where(Generation.template_id == template_id)

    query = query.order_by(desc(Generation.created_at)).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    generations = result.scalars().all()

    items = []
    for gen in generations:
        items.append({
            "id": gen.id,
            "prompt": gen.prompt,
            "size": gen.size,
            "local_path": gen.local_path,
            "thumbnail_path": gen.thumbnail_path,
            "created_at": gen.created_at,
        })

    return templates.TemplateResponse(
        "partials/gallery_grid.html",
        {
            "request": request,
            "generations": items,
            "page": page,
            "has_more": len(items) == per_page,
            "current_collection_id": collection_id,
            "current_template_id": template_id,
        },
    )
