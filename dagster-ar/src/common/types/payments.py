import dataclasses
from typing import Optional


@dataclasses.dataclass
class PaymentPayment:
    id: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    total_amount: Optional[int]
    contact_id: Optional[str]
    payment_method: Optional[str]
    currency: Optional[str]
    notes: Optional[str]
    invoice_id: Optional[str]
    account_id: Optional[str]
    reference: Optional[str]
