import uuid

from django.db import models
from django.db.models import Sum


class InvoiceStatus(models.TextChoices):
    AUTHORIZED = "AUTHORIZED", "Authorized"
    PENDING = "PENDING", "Pending"
    PAID = "PAID", "Paid in Full"
    CANCELLED = "CANCELLED", "Cancelled"
    DRAFT = "DRAFT", "Draft"
    VOIDED = "VOIDED", "Voided"
    PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED", "Partially Refunded"
    REFUNDED = "REFUNDED", "Refunded"


class InvoiceType(models.TextChoices):
    BILL = "BILL", "Bill"
    INVOICE = "INVOICE", "Invoice"
    CREDIT_MEMO = "CREDITMEMO", "Credit Memo"


class Invoice(models.Model):
    invoice_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="invoices",
        db_column="customer_id",
        null=True,
        blank=True,
    )
    invoice_number = models.CharField(max_length=100)
    currency = models.CharField(max_length=3, null=True, blank=True)  # noqa: DJ001

    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    paid_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    balance_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_at = models.DateTimeField()
    days_overdue = models.IntegerField(default=0)
    aging_bucket = models.IntegerField(default=0)
    invoice_at = models.DateTimeField()
    posted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        verbose_name="Invoice Status",
    )
    type = models.CharField(
        max_length=50,
        choices=InvoiceType.choices,
        default=InvoiceType.INVOICE,
        verbose_name="Invoice Type",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "invoices"
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self):
        return f"Invoice {self.invoice_number} ({self.invoice_id})"

    def get_aging_bucket_display(self):
        """Return the display name for the aging bucket."""
        aging_buckets = {
            1: "0-30 Days",
            2: "31-60 Days",
            3: "61-90 Days",
            4: "91-120 Days",
            5: "Over 120 Days"
        }
        return aging_buckets.get(self.aging_bucket, "Unknown")

    def get_aging_bucket_class(self):
        """Return CSS class for aging bucket styling."""
        if self.aging_bucket <= 2:
            return "text-success"  # Green for current/30-60 days
        elif self.aging_bucket <= 3:
            return "text-warning"  # Orange for 61-90 days
        else:
            return "text-danger"  # Red for over 90 days

    def get_queryset(self):
        return (
            Invoice.objects.select_related("customer")
            .values("customer__name", "aging_bucket")
            .annotate(total_ar=Sum("balance_amount"))
            .order_by("customer__name", "aging_bucket")
        )
