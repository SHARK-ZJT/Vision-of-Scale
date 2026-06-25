import httpx
from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import templates
from app.dependencies import get_db
from app.models.prompt_template import PromptTemplate
from app.models.generation import Generation
from app.models.collection import Collection

router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
async def page_home(
    request: Request,
    template_id: int | None = Query(None, description="Pre-select this template"),
    db: AsyncSession = Depends(get_db),
):
    """Home page: generator with template sidebar."""
    # Fetch all templates for sidebar
    result = await db.execute(
        select(PromptTemplate)
        .where(PromptTemplate.is_builtin == True)
        .order_by(PromptTemplate.category, PromptTemplate.name)
    )
    all_templates = result.scalars().all()

    # Get categories for filter tabs
    cat_result = await db.execute(
        select(PromptTemplate.category, func.count(PromptTemplate.id))
        .where(PromptTemplate.is_builtin == True)
        .group_by(PromptTemplate.category)
    )
    categories = cat_result.all()

    # Get collections for "add to collection" dropdown
    col_result = await db.execute(
        select(Collection).order_by(desc(Collection.updated_at)).limit(10)
    )
    collections = col_result.scalars().all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "templates": all_templates,
            "categories": categories,
            "collections": collections,
            "selected_template_id": template_id,
            "active_page": "home",
        },
    )


@router.get("/gallery", response_class=HTMLResponse)
async def page_gallery(
    request: Request,
    collection_id: int | None = Query(None),
    template_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db),
):
    """Gallery page: browse generated images."""
    per_page = 20

    # Build query
    query = select(Generation).where(Generation.status == "completed")

    if collection_id:
        query = query.where(Generation.collection_id == collection_id)
    if template_id:
        query = query.where(Generation.template_id == template_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(desc(Generation.created_at)).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    generations = result.scalars().all()

    # Build generation list with template names
    items = []
    for gen in generations:
        items.append({
            "id": gen.id,
            "prompt": gen.prompt,
            "size": gen.size,
            "local_path": gen.local_path,
            "thumbnail_path": gen.thumbnail_path,
            "collection_id": gen.collection_id,
            "template_id": gen.template_id,
            "created_at": gen.created_at,
            "status": gen.status,
        })

    # Fetch collections for filter
    col_result = await db.execute(select(Collection).order_by(desc(Collection.updated_at)))
    all_collections = col_result.scalars().all()

    total_pages = max(1, (total + per_page - 1) // per_page)

    return templates.TemplateResponse(
        "gallery.html",
        {
            "request": request,
            "generations": items,
            "collections": all_collections,
            "total": total,
            "page": page,
            "pages": total_pages,
            "current_collection_id": collection_id,
            "current_template_id": template_id,
            "active_page": "gallery",
        },
    )


@router.get("/templates", response_class=HTMLResponse)
async def page_templates(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Template library page."""
    result = await db.execute(
        select(PromptTemplate)
        .where(PromptTemplate.is_builtin == True)
        .order_by(PromptTemplate.category, PromptTemplate.name)
    )
    all_templates = result.scalars().all()

    # Group by category
    templates_by_category: dict[str, list] = {}
    for t in all_templates:
        templates_by_category.setdefault(t.category, []).append(t)

    # Category display names
    category_names = {
        "megastructure": "Megastructures",
        "contrast": "Contrast / Scale",
        "post_human": "Post-Human",
        "interior": "Interiors",
        "landscape": "Landscapes",
    }

    return templates.TemplateResponse(
        "template_library.html",
        {
            "request": request,
            "templates": all_templates,
            "templates_by_category": templates_by_category,
            "category_names": category_names,
            "active_page": "templates",
        },
    )
