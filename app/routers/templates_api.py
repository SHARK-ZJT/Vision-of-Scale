from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.prompt_template import PromptTemplate
from app.schemas.template import TemplateOut

router = APIRouter(prefix="/api", tags=["templates"])


@router.get("/templates")
async def list_templates(
    category: str | None = Query(None, description="Filter by category"),
    language: str | None = Query(None, description="Filter by language"),
    builtin: bool | None = Query(None, description="Filter built-in vs user-created"),
    db: AsyncSession = Depends(get_db),
) -> list[TemplateOut]:
    """List all prompt templates with optional filters."""
    query = select(PromptTemplate)

    if category:
        query = query.where(PromptTemplate.category == category)
    if language:
        query = query.where(PromptTemplate.language == language)
    if builtin is not None:
        query = query.where(PromptTemplate.is_builtin == builtin)

    query = query.order_by(PromptTemplate.category, PromptTemplate.name)
    result = await db.execute(query)
    templates = result.scalars().all()

    return [TemplateOut.model_validate(t) for t in templates]


@router.get("/templates/{template_id}", response_model=TemplateOut)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single template by ID."""
    template = await db.get(PromptTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板未找到")

    return TemplateOut.model_validate(template)
