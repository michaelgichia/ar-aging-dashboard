# invoices/admin.py
from django.contrib import admin
from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "customer_id",
        "total_amount",
        "status",
        "due_at",
        "created_at",
    )
    search_fields = ("invoice_number", "customer_id")
    list_filter = ("status", "type", "currency")
    date_hierarchy = "created_at"
