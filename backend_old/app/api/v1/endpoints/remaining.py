"""
SchoolRail - Fees Endpoints
============================
Direct CRUD endpoints for fees, matching frontend API expectations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from sqlalchemy import desc

from app.core.database import get_db
from app.core.security import get_current_user, TokenData, require_role
from app.models.models import Fee
from app.schemas.schemas import (
    FeeCreate, FeeResponse, FeePaymentCreate, SuccessResponse
)

# =============================================================================
# FEES
# =============================================================================

fees_router = APIRouter(prefix="/fees", tags=["Fees"])


@fees_router.get("")
async def get_fees(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    student_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get all fees."""
    query = db.query(Fee)

    if student_id:
        query = query.filter(Fee.student_id == student_id)
    if status:
        query = query.filter(Fee.status == status)

    total = query.count()
    fees = query.order_by(desc(Fee.due_date)).offset((page - 1) * limit).limit(limit).all()
    return {"items": fees, "total": total, "page": page, "limit": limit}


@fees_router.get("/{fee_id}")
async def get_fee(fee_id: int, db: Session = Depends(get_db)):
    """Get fee by ID."""
    fee = db.query(Fee).filter(Fee.id == fee_id).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Fee not found")
    return fee


@fees_router.post("", response_model=FeeResponse, status_code=status.HTTP_201_CREATED)
async def create_fee(
    fee_data: FeeCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_role(["admin", "school_admin"]))
):
    """Create a new fee."""
    gst_amount = fee_data.amount * (fee_data.gst_rate / 100)
    total_amount = fee_data.amount + gst_amount

    fee = Fee(
        **fee_data.dict(),
        gst_amount=gst_amount,
        total_amount=total_amount,
        final_amount=total_amount
    )
    db.add(fee)
    db.commit()
    db.refresh(fee)
    return fee


@fees_router.post("/{fee_id}/pay")
async def pay_fee(
    fee_id: int,
    payment_data: FeePaymentCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Pay a fee."""
    fee = db.query(Fee).filter(Fee.id == fee_id).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Fee not found")

    if fee.status == "paid":
        raise HTTPException(status_code=400, detail="Fee already paid")

    fee.paid_amount += payment_data.amount
    fee.payment_method = payment_data.payment_method
    fee.transaction_id = payment_data.transaction_id
    fee.paid_date = datetime.utcnow()

    if fee.paid_amount >= fee.final_amount:
        fee.status = "paid"
    else:
        fee.status = "partial"

    from app.models.models import Payment
    payment = Payment(
        fee_id=fee_id,
        student_id=fee.student_id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method,
        transaction_id=payment_data.transaction_id,
        payment_date=datetime.utcnow(),
        status="success"
    )
    db.add(payment)
    db.commit()

    return SuccessResponse(message=f"Payment of ₹{payment_data.amount} recorded")