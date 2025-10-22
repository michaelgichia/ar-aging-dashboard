import dataclasses
from typing import Optional
from enum import Enum


@dataclasses.dataclass
class AccountingAccountType(str, Enum):
    """
    Account types
    """

    "ACCOUNTS_RECEIVABLE"
    "ACCOUNTS_PAYABLE"
    "BANK"
    "CREDIT_CARD"
    "FIXED_ASSET"
    "LIABILITY"
    "EQUITY"
    "EXPENSE"
    "REVENUE"
    "OTHER"


@dataclasses.dataclass
class AccountingAccountStatus(str, Enum):
    """
    Account statuses
    """

    "ACTIVE"
    "ARCHIVED"


@dataclasses.dataclass
class AccountingAccount:
    """Identifier used by the SaaS application to uniquely identify the Account"""

    id: Optional[str]
    """Date and time when the Account was created, in ISO 8601 format and UTC"""
    created_at: Optional[str]
    """Date and time when the Account was last updated, in ISO 8601 format and UTC"""
    updated_at: Optional[str]
    """Account name"""
    name: Optional[str]
    """Account description"""
    description: Optional[str]
    """Account type, such as BANK. EQUITY, ASSET, ..."""
    type: Optional[AccountingAccountType]
    """Account status, such as ACTIVE or ARCHIVED"""
    status: Optional[AccountingAccountStatus]
    """Balance of the account."""
    balance: Optional[int]
    """Account’s currency, in ISO 4217 format (e.g. U.S. dollars is USD)"""
    currency: Optional[str]
    """Identifier for tracking and categorizing accounts for reporting or analysis purposes that is defined by the end-customer"""
    customer_defined_code: Optional[str]
    """True if the account is an “accounts payable” account"""
    is_payable: Optional[bool]
    """@deprecated; use parent_id instead"""
    parent_account_id: Optional[str]
    section: Optional[str]
    subsection: Optional[str]
    group: Optional[str]
    subgroup: Optional[str]
    """The parent account ID for this account"""
    parent_id: Optional[str]
