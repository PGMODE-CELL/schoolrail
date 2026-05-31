from datetime import date, datetime, timedelta
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class FeeFrequencyEnum(str):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"


class FeeStructureCreate(BaseModel):
    school_id: int
    name: str
    amount: float
    frequency: str = "yearly"
    description: Optional[str] = None
    due_date: str
    late_fee: float = 0
    status: str = "active"


class FeeStructureResponse(BaseModel):
    id: int
    school_id: int
    name: str
    amount: float
    frequency: str
    description: Optional[str] = None
    due_date: str
    late_fee: float
    status: str = "active"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FeePaymentCreate(BaseModel):
    student_id: int
    fee_id: int
    amount: float
    payment_method: str
    transaction_id: Optional[str] = None
    notes: Optional[str] = None


class FeePaymentResponse(BaseModel):
    id: int
    student_id: int
    fee_id: int
    amount: float
    payment_date: Optional[date] = None
    payment_method: str
    transaction_id: Optional[str] = None
    status: str
    received_by: Optional[int] = None

    class Config:
        from_attributes = True


class FeeCollectionSummary(BaseModel):
    start_date: date
    end_date: date
    total_collected: float
    total_transactions: int
    online_transactions: int
    cash_transactions: int
    online_amount: float
    cash_amount: float


class FeeDefaulterReport(BaseModel):
    student_id: int
    student_name: str
    class_name: str
    fee_name: str
    amount_due: float
    due_date: date
    days_overdue: int
    contact_number: Optional[str] = None


class MonthlyCollectionReport(BaseModel):
    month: str
    year: int
    total_collected: float
    total_transactions: int
    by_fee_type: Dict[str, float]
    growth_percentage: Optional[float] = None


class FeeConcessionRequest(BaseModel):
    student_id: int
    fee_id: int
    concession_type: str
    concession_amount: float
    reason: str
    approved_by: Optional[int] = None


class FeeRefundRequest(BaseModel):
    student_id: int
    payment_id: int
    amount: float
    reason: str
    refund_method: str
    requested_by: int
