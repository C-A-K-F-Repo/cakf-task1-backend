from fastapi import APIRouter, status, HTTPException, Depends, Request
from sqlalchemy import select
import uuid

from app.dependencies.db import SessionDep
from app.dependencies.user import allow_admin, get_current_user
from app.core.audit import audit_event
from app.models.product_type import ProductType
from app.repositories.product_type import ProductTypeRepository
from app.schemas.product_type import ProductTypeCreate, ProductTypeOut

router = APIRouter()


@router.post("/", response_model=ProductTypeOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(allow_admin)])
async def create_product_type(product_type_in: ProductTypeCreate, db: SessionDep, request: Request, current_user = Depends(get_current_user)):
    product_type = await ProductTypeRepository(db).create(product_type_in)
    audit_event("product_type.create", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), target_type="product_type", target_id=product_type.id, request=request)
    return product_type


@router.get("/", response_model=list[ProductTypeOut])
async def get_product_types(db: SessionDep, request: Request, skip: int = 0, limit: int = 100):
    product_types = await ProductTypeRepository(db).get(skip, limit)
    audit_event("product_type.list", "success", metadata={"skip": skip, "limit": limit, "result_count": len(product_types)}, request=request)
    return product_types


@router.get("/{product_type_id}", response_model=ProductTypeOut)
async def get_product_type(product_type_id: uuid.UUID, db: SessionDep, request: Request):
    product_type = await ProductTypeRepository(db).get_by_id(product_type_id)
    audit_event("product_type.read", "success", target_type="product_type", target_id=product_type_id, request=request)
    return product_type


@router.delete("/{product_type_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(allow_admin)])
async def delete_product_type(product_type_id: uuid.UUID, db: SessionDep, request: Request, current_user = Depends(get_current_user)):
    await ProductTypeRepository(db).delete(product_type_id)
    audit_event("product_type.delete", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), target_type="product_type", target_id=product_type_id, request=request)
