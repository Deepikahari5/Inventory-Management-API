from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Product, Supplier
from app.schemas import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])

DUPLICATE_SKU = "A product with this SKU already exists"
NON_NULLABLE_FIELDS = {
    "name",
    "sku",
    "price",
    "quantity",
    "reorder_level",
    "category_id",
}


def get_product_or_404(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return product


def sku_taken(db: Session, sku: str, exclude_id: int | None = None) -> bool:
    query = select(Product.id).where(Product.sku == sku)
    if exclude_id is not None:
        query = query.where(Product.id != exclude_id)
    return db.scalar(query) is not None


def ensure_category_exists(db: Session, category_id: int) -> None:
    if db.get(Category, category_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")


def ensure_supplier_exists(db: Session, supplier_id: int) -> None:
    if db.get(Supplier, supplier_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Supplier not found")


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    if sku_taken(db, payload.sku):
        raise HTTPException(status.HTTP_409_CONFLICT, DUPLICATE_SKU)
    ensure_category_exists(db, payload.category_id)
    if payload.supplier_id is not None:
        ensure_supplier_exists(db, payload.supplier_id)
    product = Product(**payload.model_dump())
    db.add(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, DUPLICATE_SKU)
    db.refresh(product)
    return product


@router.get("", response_model=List[ProductOut])
def list_products(
    search: Optional[str] = Query(default=None, min_length=1),
    category_id: Optional[int] = Query(default=None, gt=0),
    supplier_id: Optional[int] = Query(default=None, gt=0),
    needs_restock: Optional[bool] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = select(Product)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(Product.name.like(pattern) | Product.sku.like(pattern))
    if category_id is not None:
        query = query.where(Product.category_id == category_id)
    if supplier_id is not None:
        query = query.where(Product.supplier_id == supplier_id)
    if needs_restock is True:
        query = query.where(Product.quantity <= Product.reorder_level)
    elif needs_restock is False:
        query = query.where(Product.quantity > Product.reorder_level)
    return db.scalars(query.order_by(Product.id).offset(skip).limit(limit)).all()


@router.get("/restock", response_model=List[ProductOut])
def products_needing_restock(db: Session = Depends(get_db)):
    query = (
        select(Product)
        .where(Product.quantity <= Product.reorder_level)
        .order_by(Product.quantity, Product.id)
    )
    return db.scalars(query).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return get_product_or_404(db, product_id)


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)
):
    product = get_product_or_404(db, product_id)
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No fields provided to update")
    null_fields = [f for f in NON_NULLABLE_FIELDS if f in data and data[f] is None]
    if null_fields:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"These fields cannot be null: {', '.join(sorted(null_fields))}",
        )
    if "sku" in data and sku_taken(db, data["sku"], exclude_id=product_id):
        raise HTTPException(status.HTTP_409_CONFLICT, DUPLICATE_SKU)
    if "category_id" in data:
        ensure_category_exists(db, data["category_id"])
    if data.get("supplier_id") is not None:
        ensure_supplier_exists(db, data["supplier_id"])
    for field, value in data.items():
        setattr(product, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, DUPLICATE_SKU)
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_or_404(db, product_id)
    db.delete(product)
    db.commit()
