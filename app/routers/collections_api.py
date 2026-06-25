from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.collection import Collection
from app.models.generation import Generation
from app.schemas.collection import (
    CollectionOut,
    CollectionCreate,
    CollectionUpdate,
    CollectionListOut,
    AddToCollectionRequest,
)
from app.schemas.generation import GenerationOut

router = APIRouter(prefix="/api", tags=["collections"])


@router.get("/collections", response_model=CollectionListOut)
async def list_collections(
    db: AsyncSession = Depends(get_db),
):
    """List all collections with generation counts."""
    result = await db.execute(
        select(Collection).order_by(desc(Collection.updated_at))
    )
    collections = result.scalars().all()

    items = []
    for col in collections:
        count_result = await db.execute(
            select(func.count(Generation.id)).where(Generation.collection_id == col.id)
        )
        count = count_result.scalar()

        items.append(
            CollectionOut(
                id=col.id,
                name=col.name,
                description=col.description,
                cover_image=col.cover_image,
                generation_count=count,
                created_at=col.created_at,
                updated_at=col.updated_at,
            )
        )

    return CollectionListOut(items=items, total=len(items))


@router.post("/collections", response_model=CollectionOut, status_code=201)
async def create_collection(
    body: CollectionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new collection."""
    collection = Collection(
        name=body.name,
        description=body.description,
    )
    db.add(collection)
    await db.commit()
    await db.refresh(collection)

    return CollectionOut(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        cover_image=collection.cover_image,
        generation_count=0,
        created_at=collection.created_at,
        updated_at=collection.updated_at,
    )


@router.get("/collections/{collection_id}", response_model=CollectionOut)
async def get_collection(
    collection_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a collection with its generations."""
    collection = await db.get(Collection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="合集未找到")

    # Get generations in this collection
    gen_result = await db.execute(
        select(Generation)
        .where(Generation.collection_id == collection_id, Generation.status == "completed")
        .order_by(desc(Generation.created_at))
    )
    generations = gen_result.scalars().all()

    gen_list = [
        GenerationOut(
            id=g.id,
            prompt=g.prompt,
            model=g.model,
            size=g.size,
            seed=g.seed,
            n_images=g.n_images,
            local_path=g.local_path,
            thumbnail_path=g.thumbnail_path,
            original_url=g.original_url,
            template_id=g.template_id,
            collection_id=g.collection_id,
            status=g.status,
            error_message=g.error_message,
            created_at=g.created_at,
        )
        for g in generations
    ]

    return CollectionOut(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        cover_image=collection.cover_image,
        generations=gen_list,
        generation_count=len(gen_list),
        created_at=collection.created_at,
        updated_at=collection.updated_at,
    )


@router.patch("/collections/{collection_id}", response_model=CollectionOut)
async def update_collection(
    collection_id: int,
    body: CollectionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a collection's name or description."""
    collection = await db.get(Collection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="合集未找到")

    if body.name is not None:
        collection.name = body.name
    if body.description is not None:
        collection.description = body.description

    await db.commit()
    await db.refresh(collection)

    return CollectionOut(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        cover_image=collection.cover_image,
        created_at=collection.created_at,
        updated_at=collection.updated_at,
    )


@router.delete("/collections/{collection_id}", status_code=200)
async def delete_collection(
    collection_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a collection (does not delete the generations in it)."""
    collection = await db.get(Collection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="合集未找到")

    # Unlink generations
    gens = (await db.execute(
        select(Generation).where(Generation.collection_id == collection_id)
    )).scalars().all()

    for gen in gens:
        gen.collection_id = None

    await db.delete(collection)
    await db.commit()

    return {"message": "已删除合集", "id": collection_id}


@router.post("/collections/{collection_id}/add", status_code=200)
async def add_to_collection(
    collection_id: int,
    body: AddToCollectionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Add a generation to a collection."""
    collection = await db.get(Collection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="合集未找到")

    generation = await db.get(Generation, body.generation_id)
    if not generation:
        raise HTTPException(status_code=404, detail="生成记录未找到")

    generation.collection_id = collection_id
    await db.commit()

    return {"message": "已添加到合集", "collection_id": collection_id, "generation_id": body.generation_id}
