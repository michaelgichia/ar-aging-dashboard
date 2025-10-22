import dataclasses
from typing import Optional
from enum import Enum


@dataclasses.dataclass
class AccountingInvoiceStatus(str, Enum):
    """
    Invoice statuses
    """

    "DRAFT"
    "VOIDED"
    "AUTHORIZED"
    "PAID"
    "PARTIALLY_PAID"
    "PARTIALLY_REFUNDED"
    "REFUNDED"


@dataclasses.dataclass
class AccountingInvoicePayment_collection_method(str, Enum):
    """
    Invoice payment collection methods
    """

    "send_invoice"
    "charge_automatically"


@dataclasses.dataclass
class AccountingInvoiceType(str, Enum):
    "BILL"

    "INVOICE"
    "CREDITMEMO"


@dataclasses.dataclass
class PropertyAccountingInvoiceCategory_ids:
    id: Optional[str]


@dataclasses.dataclass
class PropertyAccountingInvoiceLineitems:
    id: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    refunded_at: Optional[str]
    total_amount: Optional[int]
    refund_amount: Optional[int]
    discount_amount: Optional[int]
    tax_amount: Optional[int]
    item_id: Optional[str]
    unit_amount: Optional[int]
    """unit_quantity * unit_amount + tax_amount"""
    unit_quantity: Optional[int]
    item_sku: Optional[str]
    item_name: Optional[str]
    item_description: Optional[str]
    notes: Optional[str]
    taxrate_id: Optional[str]
    account_id: Optional[str]
    category_ids: Optional[PropertyAccountingInvoiceCategory_ids]


@dataclasses.dataclass
class PropertyAccountingInvoiceAttachments:
    id: Optional[str]
    download_url: Optional[str]
    name: Optional[str]
    mime_type: Optional[str]


@dataclasses.dataclass
class AccountingInvoice:
    id: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    due_at: Optional[str]
    paid_at: Optional[str]
    refunded_at: Optional[str]
    cancelled_at: Optional[str]
    posted_at: Optional[str]
    total_amount: Optional[int]
    paid_amount: Optional[int]
    refund_amount: Optional[int]
    tax_amount: Optional[int]
    discount_amount: Optional[int]
    balance_amount: Optional[int]
    """External identifier for this invoice"""
    invoice_number: Optional[str]
    contact_id: Optional[str]
    currency: Optional[str]
    notes: Optional[str]
    refund_reason: Optional[str]
    lineitems: Optional[list[PropertyAccountingInvoiceLineitems]]
    status: Optional[AccountingInvoiceStatus]
    """The public URL for the invoice to send to a customer to view or pay."""
    url: Optional[str]
    """When set to charging_automatically, an automated attempt will occur to pay this invoice using the default payment source attached to the contactcustomer. When set to send_invoice, an will email will be sent with this invoice to the contact/customer with payment instructions."""
    payment_collection_method: Optional[AccountingInvoicePayment_collection_method]
    """@deprecated; use posted_at"""
    invoice_at: Optional[str]
    """@deprecated"""
    type: Optional[AccountingInvoiceType]
    attachments: Optional[list[PropertyAccountingInvoiceAttachments]]
    send: Optional[bool]
