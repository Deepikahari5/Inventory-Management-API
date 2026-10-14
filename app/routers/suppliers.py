from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Supplier
from app.schemas import SupplierCreate, SupplierOut, SupplierUpdate

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

DUPLICATE_EMAIL = "A supplier with this email already exists"


def get_supplier_or_404(db: Session, supplier_id: int) -> Supplier:
    supplier = db.get(Supplier, supplier_id)
    if supplier is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Supplier not found")
    return supplier


def email_taken(db: Session, email: str, exclude_id: int | None = None) -> bool:
    query = select(Supplier.id).where(Supplier.email == email)
    if exclude_id is not None:
        query = query.where(Supplier.id != exclude_id)
    return db.scalar(query) is not None


@router.post("", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db)):
    if payload.email and email_taken(db, payload.email):
        raise HTTPException(status.HTTP_409_CONFLICT, DUPLICATE_EMAIL)
    supplier = Supplier(**payload.model_dump())
    db.add(supplier)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, DUPLICATE_EMAIL)
    db.refresh(supplier)
    return supplier


@router.get("", response_model=List[SupplierOut])
def list_suppliers(
    is_active: Optional[bool] = Query(default=None),
    active_only: bool = Query(default=False),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = select(Supplier)
    if active_only:
        query = query.where(Supplier.is_active.is_(True))
    elif is_active is not None:
        query = query.where(Supplier.is_active.is_(is_active))
    return db.scalars(query.order_by(Supplier.id).offset(skip).limit(limit)).all()


@router.get("/active", response_model=List[SupplierOut])
def list_active_suppliers(db: Session = Depends(get_db)):
    query = select(Supplier).where(Supplier.is_active.is_(True)).order_by(Supplier.id)
    return db.scalars(query).all()


@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    return get_supplier_or_404(db, supplier_id)


@router.put("/{supplier_id}", response_model=SupplierOut)
def update_supplier(
    supplier_id: int, payload: SupplierUpdate, db: Session = Depends(get_db)
):
    supplier = get_supplier_or_404(db, supplier_id)
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "name cannot be null")
    if "is_active" in data and data["is_active"] is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "is_active cannot be null")
    if data.get("email") and email_taken(db, data["email"], exclude_id=supplier_id):
        raise HTTPException(status.HTTP_409_CONFLICT, DUPLICATE_EMAIL)
    for field, value in data.items():
        setattr(supplier, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, DUPLICATE_EMAIL)
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = get_supplier_or_404(db, supplier_id)
    db.delete(supplier)
    db.commit()
