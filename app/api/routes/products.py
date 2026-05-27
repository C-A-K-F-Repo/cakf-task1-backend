from fastapi import APIRouter, status, HTTPException, Depends, Request
from sqlalchemy import select
import uuid

from app.dependencies.db import SessionDep
from app.dependencies.user import allow_admin, get_current_user
from app.core.audit import audit_event
from app.models.product import Product
from app.models.product_type import ProductType
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductOut

import aiofiles
from pathlib import Path
from fastapi import UploadFile, File

router = APIRouter()


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(allow_admin)])
async def create_product(product_in: ProductCreate, db: SessionDep, request: Request, current_user = Depends(get_current_user)):
    # Verify product type exists
    product = await ProductRepository(db).create(product_in)
    audit_event("product.create", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), target_type="product", target_id=product.id, request=request)
    return product


@router.get("/", response_model=list[ProductOut])
async def get_products(db: SessionDep, request: Request, skip: int = 0, limit: int = 100):
    stmt = select(Product).offset(skip).limit(limit)
    result = await db.execute(stmt)
    products = result.scalars().all()
    audit_event("product.list", "success", metadata={"skip": skip, "limit": limit, "result_count": len(products)}, request=request)
    return products


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: uuid.UUID, db: SessionDep, request: Request):
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        audit_event("product.read", "failure", target_type="product", target_id=product_id, metadata={"reason": "not_found"}, request=request)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    audit_event("product.read", "success", target_type="product", target_id=product_id, request=request)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(allow_admin)])
async def delete_product(product_id: uuid.UUID, db: SessionDep, request: Request, current_user = Depends(get_current_user)):
    await ProductRepository(db).delete(product_id)
    audit_event("product.delete", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), target_type="product", target_id=product_id, request=request)
STATIC_DIR = Path("static")
STATIC_DIR.mkdir(exist_ok=True)

@router.post("/{product_id}/image", response_model=ProductOut, dependencies=[Depends(allow_admin)])
async def upload_product_image(product_id: uuid.UUID, db: SessionDep, request: Request, file: UploadFile = File(...), current_user = Depends(get_current_user)):
    ext = Path(file.filename).suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        audit_event("product.image_upload", "failure", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), target_type="product", target_id=product_id, metadata={"reason": "unsupported_file_type", "extension": ext}, request=request)
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        audit_event("product.image_upload", "failure", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), target_type="product", target_id=product_id, metadata={"reason": "file_too_large", "file_size": len(content)}, request=request)
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()
    if not product:
        audit_event("product.image_upload", "failure", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), target_type="product", target_id=product_id, metadata={"reason": "product_not_found"}, request=request)
        raise HTTPException(status_code=404, detail="Product not found")

    if product.image_url:
        old_path = Path(product.image_url.lstrip("/"))
        if old_path.exists():
            old_path.unlink()

    filename = f"{uuid.uuid4()}{ext}"
    file_path = STATIC_DIR / filename

    async with aiofiles.open(file_path, "wb") as buffer:
        await buffer.write(content)

    product.image_url = f"/static/{filename}"
    await db.commit()
    await db.refresh(product)
    audit_event("product.image_upload", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), target_type="product", target_id=product_id, metadata={"extension": ext, "file_size": len(content)}, request=request)
    return product
