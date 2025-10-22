from dagster import ConfigurableResource
from pydantic import Field
import requests
from urllib.parse import urljoin, urlencode
from typing import Any


class APIClientResource(ConfigurableResource):
    """A configurable resource for connecting to an external API."""

    base_url: str = Field(
        description="The base URL of the accounting API (e.g., https://api.example.com/v1)"
    )
    api_key: str = Field(description="The necessary API key for authentication.")

    def _get_headers(self) -> dict:
        """Helper to manage authentication headers."""
        return {"Authorization": f"Bearer {self.api_key}"}

    def fetch_data(
        self, endpoint_path: str, params: dict[str, Any] | None = None
    ) -> dict:
        """
        Constructs the full URL, fetches data, and returns the parsed JSON.

        Args:
            endpoint_path: The specific path (e.g., "invoice").
            params: A dictionary of query parameters (e.g., {"env": "Sandbox", "limit": 10}).

        Returns:
            The JSON response as a Python dictionary.
        """

        url = urljoin(self.base_url, endpoint_path)

        if params:
            # urlencode converts the dict into a query string like "?env=Sandbox&limit=10"
            # TODO: Apply env conditional before deploying to production.
            query_string = urlencode(params)
            url = f"{url}?{query_string}"

        response = requests.get(url, headers=self._get_headers())

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        return response.json()
