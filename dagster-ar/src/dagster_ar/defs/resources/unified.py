from common.types.customers import AccountingContact
from common.types.invoice import AccountingInvoice
from common.types.payments import PaymentPayment
import dagster as dg
import requests
from urllib.parse import urljoin, urlencode
from typing import Any


class UnifiedAccountingResource(dg.ConfigurableResource):
    """
    A resource for connecting to the Unified Accounting API endpoint, managing
    the base URL, connection ID, and authentication key.
    """

    base_url: str
    conn_id: str
    api_key: str

    def _request(
        self,
        resource_url: str,
        endpoint_path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """
        Internal method to build the full URL, execute the GET request, and handle errors.
        """
        accounting_base = urljoin(self.base_url, f"{resource_url}/{self.conn_id}/")

        url = urljoin(accounting_base, endpoint_path)

        if params:
            query_string = urlencode(params)
            url = f"{url}?{query_string}"

        headers = {"Authorization": f"Bearer {self.api_key}"}

        resp = requests.get(url, headers=headers)
        resp.raise_for_status()

        return resp.json()

    def get_invoices(
        self, params: dict[str, Any] | None = None
    ) -> list[AccountingInvoice]:
        """
        Fetches invoice data from the Unified Accounting API.

        Args:
            params: A dictionary of query parameters
                (e.g limit=10).

        Returns:
            A list of invoice dictionaries.
        """
        return self._request("accounting", "invoice", params)

    def get_customers(
        self, params: dict[str, Any] | None = None
    ) -> list[AccountingContact]:
        """
        Fetches customer data from the Unified Accounting API.

        Args:
            params: A dictionary of query parameters
                (e.g limit=10).

        Returns:
            A list of customer dictionaries.
        """
        return self._request("accounting", "contact", params)

    def get_payments(
        self, params: dict[str, Any] | None = None
    ) -> list[PaymentPayment]:
        """
        Fetches payment data from the Unified Accounting API.

        Args:
            params: A dictionary of query parameters
                (e.g limit=10).

        Returns:
            A list of payment dictionaries.
        """
        return self._request("payment", "payment", params)
