from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.models import Fee, Payment
from app.schemas.fee import (
    FeeStructureCreate,
    FeeStructureResponse,
    FeePaymentCreate,
    FeePaymentResponse,
    FeeCollectionSummary
)


def _fee_to_dict(fee: Fee) -> dict:
    return {
        "id": fee.id,
        "uuid": fee.uuid,
        "school_id": fee.school_id,
        "student_id": fee.student_id,
        "fee_type": fee.fee_type,
        "title": fee.title,
        "description": fee.description,
        "amount": fee.amount,
        "gst_rate": fee.gst_rate,
        "gst_amount": fee.gst_amount,
        "total_amount": fee.total_amount,
        "discount_amount": fee.discount_amount,
        "final_amount": fee.final_amount,
        "due_date": fee.due_date,
        "issue_date": fee.issue_date,
        "status": fee.status,
        "paid_amount": fee.paid_amount,
        "paid_date": fee.paid_date,
        "payment_method": fee.payment_method,
        "transaction_id": fee.transaction_id,
        "notes": fee.notes,
        "created_at": fee.created_at,
        "updated_at": fee.updated_at,
    }


def _payment_to_dict(payment: Payment) -> dict:
    return {
        "id": payment.id,
        "uuid": payment.uuid,
        "student_id": payment.student_id,
        "fee_id": payment.fee_id,
        "amount": payment.amount,
        "payment_date": payment.payment_date,
        "payment_method": payment.payment_method,
        "transaction_id": payment.transaction_id,
        "status": payment.status,
        "received_by": None,
    }


def get_all_fee_structures(school_id: Optional[int] = None) -> List[FeeStructureResponse]:
    db = SessionLocal()
    try:
        query = db.query(Fee)
        if school_id:
            query = query.filter(Fee.school_id == school_id)
        fees = query.all()
        return [FeeStructureResponse(**_fee_to_dict(f)) for f in fees]
    except Exception:
        return []
    finally:
        db.close()


def get_student_fees(student_id: int) -> List[dict]:
    db = SessionLocal()
    try:
        fees = db.query(Fee).filter(Fee.student_id == student_id).all()
        payments = db.query(Payment).filter(Payment.student_id == student_id).all()
        paid_fee_ids = {p.fee_id for p in payments}

        pending_fees = []
        paid_fees = []
        for fee in fees:
            fee_dict = _fee_to_dict(fee)
            if fee.id not in paid_fee_ids:
                due_date = fee.due_date.date() if isinstance(fee.due_date, datetime) else fee.due_date
                is_overdue = due_date < date.today() if due_date else False
                pending_fees.append({
                    **fee_dict,
                    "student_id": student_id,
                    "paid": False,
                    "is_overdue": is_overdue,
                })
            else:
                payment = next((p for p in payments if p.fee_id == fee.id), None)
                paid_fees.append({
                    **fee_dict,
                    "student_id": student_id,
                    "paid": True,
                    "payment_date": payment.payment_date if payment else None,
                    "payment_method": payment.payment_method if payment else None,
                    "transaction_id": payment.transaction_id if payment else None,
                })

        return {"pending": pending_fees, "paid": paid_fees}
    except Exception:
        return {"pending": [], "paid": []}
    finally:
        db.close()


def create_fee_structure(fee_data: FeeStructureCreate) -> FeeStructureResponse:
    db = SessionLocal()
    try:
        data = fee_data.model_dump()
        due_date_str = data.pop("due_date", None)
        due_date = None
        if due_date_str:
            if isinstance(due_date_str, str):
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            else:
                due_date = due_date_str
        amount = data.get("amount", 0)
        gst_rate = data.get("gst_rate", 0)
        gst_amount = round(amount * gst_rate / 100, 2)
        total_amount = round(amount + gst_amount, 2)
        fee = Fee(
            school_id=data.get("school_id"),
            student_id=data.get("student_id", 1),
            fee_type=data.get("name", data.get("fee_type", "fee")),
            title=data.get("name", data.get("title", "")),
            description=data.get("description"),
            amount=amount,
            gst_rate=gst_rate,
            gst_amount=gst_amount,
            total_amount=total_amount,
            discount_amount=0,
            final_amount=total_amount,
            due_date=due_date,
            status=data.get("status", "pending"),
        )
        db.add(fee)
        db.commit()
        db.refresh(fee)
        return FeeStructureResponse(**_fee_to_dict(fee))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def record_payment(payment_data: FeePaymentCreate) -> FeePaymentResponse:
    db = SessionLocal()
    try:
        data = payment_data.model_dump()
        payment = Payment(
            student_id=data.get("student_id"),
            fee_id=data.get("fee_id"),
            amount=data.get("amount"),
            payment_method=data.get("payment_method"),
            transaction_id=data.get("transaction_id"),
            payment_date=datetime.now().date(),
            status="paid",
        )
        db.add(payment)

        fee = db.query(Fee).filter(Fee.id == data.get("fee_id")).first()
        if fee:
            fee.status = "paid"
            fee.paid_amount = (fee.paid_amount or 0) + data.get("amount", 0)
            fee.paid_date = datetime.now().date()
            fee.payment_method = data.get("payment_method")
            fee.transaction_id = data.get("transaction_id")

        db.commit()
        db.refresh(payment)
        return FeePaymentResponse(**_payment_to_dict(payment))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_collection_summary(start_date: date, end_date: date) -> FeeCollectionSummary:
    db = SessionLocal()
    try:
        payments = db.query(Payment).filter(
            func.date(Payment.payment_date) >= start_date,
            func.date(Payment.payment_date) <= end_date
        ).all()
        total_collected = sum(p.amount for p in payments)
        online_payments = [p for p in payments if p.payment_method == "online"]
        cash_payments = [p for p in payments if p.payment_method == "cash"]

        return FeeCollectionSummary(
            start_date=start_date,
            end_date=end_date,
            total_collected=total_collected,
            total_transactions=len(payments),
            online_transactions=len(online_payments),
            cash_transactions=len(cash_payments),
            online_amount=sum(p.amount for p in online_payments),
            cash_amount=sum(p.amount for p in cash_payments)
        )
    except Exception:
        return FeeCollectionSummary(
            start_date=start_date,
            end_date=end_date,
            total_collected=0,
            total_transactions=0,
            online_transactions=0,
            cash_transactions=0,
            online_amount=0,
            cash_amount=0
        )
    finally:
        db.close()


def get_pending_fees_report(school_id: int) -> List[dict]:
    db = SessionLocal()
    try:
        fees = db.query(Fee).filter(
            Fee.school_id == school_id,
            Fee.status.in_(["pending", "overdue"])
        ).all()
        result = []
        for fee in fees:
            due_date = fee.due_date.date() if isinstance(fee.due_date, datetime) else fee.due_date
            is_overdue = due_date < date.today() if due_date else False
            result.append({
                "fee_name": fee.title,
                "amount": fee.final_amount,
                "due_date": str(due_date) if due_date else None,
                "students_count": 1,
            })
        return result
    except Exception:
        return []
    finally:
        db.close()
