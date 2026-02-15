from typing import Dict


class EndpointRegistry:
    """
    In-memory trusted endpoint registry.
    Stores endpoint_id → hostname + shared secret.
    """

    def __init__(self):
        self._endpoints: Dict[str, dict] = {}

    def register(self, endpoint_id: str, hostname: str, secret: str):
        self._endpoints[endpoint_id] = {
            "endpoint_id": endpoint_id,
            "hostname": hostname,
            "secret": secret,
        }

    def is_registered(self, endpoint_id: str) -> bool:
        return endpoint_id in self._endpoints

    def get_secret(self, endpoint_id: str) -> str | None:
        endpoint = self._endpoints.get(endpoint_id)
        return endpoint["secret"] if endpoint else None


endpoint_registry = EndpointRegistry()
