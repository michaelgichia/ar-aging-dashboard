from django.urls import path

from .views import invoice_list_view

app_name = "invoices"

urlpatterns = [
    path("", view=invoice_list_view, name="list"),
]
