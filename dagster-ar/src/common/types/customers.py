import dataclasses
from enum import Enum
from typing import Optional


@dataclasses.dataclass
class AccountingContactTax_exemption(str, Enum):
    "FEDERAL_GOV"

    "REGION_GOV"
    "LOCAL_GOV"
    "TRIBAL_GOV"
    "CHARITABLE_ORG"
    "RELIGIOUS_ORG"
    "EDUCATIONAL_ORG"
    "MEDICAL_ORG"
    "RESALE"
    "FOREIGN"
    "OTHER"


@dataclasses.dataclass
class AccountingContactEmailsType(str, Enum):
    "WORK"

    "HOME"
    "OTHER"


@dataclasses.dataclass
class PropertyAccountingContactEmails:
    email: Optional[str]
    type: Optional[AccountingContactEmailsType]


@dataclasses.dataclass
class AccountingContactTelephonesType(str, Enum):
    "WORK"

    "HOME"
    "OTHER"
    "FAX"
    "MOBILE"


@dataclasses.dataclass
class PropertyAccountingContactTelephones:
    telephone: Optional[str]
    type: Optional[AccountingContactTelephonesType]


@dataclasses.dataclass
class PropertyAccountingContactBilling_address:
    address1: Optional[str]
    address2: Optional[str]
    city: Optional[str]
    """Regional area of the employee's address.  For example, in the U.S., the region is the employee's state; in Canada, the region is the employee’s province."""
    region: Optional[str]
    """Short form for the regional area of the employee's address.   For example, in the U.S., the region code is the two-letter abbreviation for the employee’s state; in Canada, the region is the two-letter abbreviation for the employee's province."""
    region_code: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    """Country code for the country, in ISO 3166 A-2 format"""
    country_code: Optional[str]


@dataclasses.dataclass
class PropertyAccountingContactShipping_address:
    address1: Optional[str]
    address2: Optional[str]
    city: Optional[str]
    """Regional area of the employee's address.  For example, in the U.S., the region is the employee's state; in Canada, the region is the employee’s province."""
    region: Optional[str]
    """Short form for the regional area of the employee's address.   For example, in the U.S., the region code is the two-letter abbreviation for the employee’s state; in Canada, the region is the two-letter abbreviation for the employee's province."""
    region_code: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    """Country code for the country, in ISO 3166 A-2 format"""
    country_code: Optional[str]


@dataclasses.dataclass
class AccountingContactPayment_methodsType(str, Enum):
    "ACH"

    "ALIPAY"
    "CARD"
    "GIROPAY"
    "IDEAL"
    "OTHER"
    "PAYPAL"
    "WIRE"
    "CHECK"


@dataclasses.dataclass
class PropertyAccountingContactPayment_methods:
    id: Optional[str]
    type: Optional[AccountingContactPayment_methodsType]
    name: Optional[str]
    default: Optional[bool]


@dataclasses.dataclass
class PropertyAccountingContactAssociated_contacts:
    id: Optional[str]
    name: Optional[str]
    emails: Optional[PropertyAccountingContactEmails]


@dataclasses.dataclass
class AccountingContact:
    id: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    name: Optional[str]
    emails: Optional[list[PropertyAccountingContactEmails]]
    telephones: Optional[list[PropertyAccountingContactTelephones]]
    currency: Optional[str]
    billing_address: Optional[PropertyAccountingContactBilling_address]
    shipping_address: Optional[PropertyAccountingContactShipping_address]
    is_active: Optional[bool]
    tax_exemption: Optional[AccountingContactTax_exemption]
    """The ID/number of the customer's tax number.  This is also known as the ABN (Australia), GST Number (New Zealand), VAT Number (UK) or Tax ID Number (US and global)."""
    tax_number: Optional[str]
    is_customer: Optional[bool]
    is_supplier: Optional[bool]
    """URL for the contact’s portal"""
    portal_url: Optional[str]
    payment_methods: Optional[list[PropertyAccountingContactPayment_methods]]
    company_name: Optional[str]
    """contact account numbers such as registration, A membership or identification reference to help to identify and search customers"""
    identification: Optional[str]
    associated_contacts: Optional[list[PropertyAccountingContactAssociated_contacts]]
