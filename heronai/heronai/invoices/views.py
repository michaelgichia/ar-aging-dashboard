import logging
from collections import defaultdict

from django.views.generic import ListView

from .models import Invoice

logger = logging.getLogger(__name__)

# Aging bucket constants
BUCKET_1 = 1  # 0-30 Days
BUCKET_2 = 2  # 31-60 Days
BUCKET_3 = 3  # 61-90 Days
BUCKET_4 = 4  # 91-120 Days
BUCKET_5 = 5  # Over 120 Days


class InvoiceListView(ListView):
    model = Invoice
    context_object_name = "customer_aging_data"
    template_name = "invoices/invoice_list.html"

    def get_queryset(self):
        """Get invoices grouped by customer and aging bucket."""
        # Get all invoices with customer information
        invoices = Invoice.objects.select_related("customer").filter(
            customer__isnull=False,
            balance_amount__gt=0,  # Only show invoices with outstanding balance
        ).values(
            "customer__name",
            "aging_bucket",
            "balance_amount",
        )

        # Group by customer and aging bucket
        customer_data = defaultdict(lambda: {
            "customer_name": "",
            "bucket_1": 0,
            "bucket_2": 0,
            "bucket_3": 0,
            "bucket_4": 0,
            "bucket_5": 0,
            "total_ar": 0,
        })

        for invoice in invoices:
            customer_name = invoice["customer__name"]
            aging_bucket = invoice["aging_bucket"]
            balance_amount = float(invoice["balance_amount"] or 0)

            if customer_name not in customer_data:
                customer_data[customer_name]["customer_name"] = customer_name

            # Add to appropriate bucket
            if aging_bucket == BUCKET_1:
                customer_data[customer_name]["bucket_1"] += balance_amount
            elif aging_bucket == BUCKET_2:
                customer_data[customer_name]["bucket_2"] += balance_amount
            elif aging_bucket == BUCKET_3:
                customer_data[customer_name]["bucket_3"] += balance_amount
            elif aging_bucket == BUCKET_4:
                customer_data[customer_name]["bucket_4"] += balance_amount
            elif aging_bucket == BUCKET_5:
                customer_data[customer_name]["bucket_5"] += balance_amount

            # Add to total AR
            customer_data[customer_name]["total_ar"] += balance_amount

        return list(customer_data.values())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate totals
        customer_data = context["customer_aging_data"]
        totals = {
            "bucket_1": sum(customer["bucket_1"] for customer in customer_data),
            "bucket_2": sum(customer["bucket_2"] for customer in customer_data),
            "bucket_3": sum(customer["bucket_3"] for customer in customer_data),
            "bucket_4": sum(customer["bucket_4"] for customer in customer_data),
            "bucket_5": sum(customer["bucket_5"] for customer in customer_data),
        }
        totals["grand_total"] = sum(totals.values())

        context["totals"] = totals
        return context


invoice_list_view = InvoiceListView.as_view()
