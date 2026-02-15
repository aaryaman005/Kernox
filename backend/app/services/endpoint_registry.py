from typing import Dict


class EndpointRegistry:
    """
    In-memory trusted endpoint registry.
    Will be replaced by DB in Phase 2.
    """

    def __init__(self):
        self._endpoints: Dict[str, dict] = {}

    def register(self, endpoint_id: str, hostname: str):
        self._endpoints[endpoint_id] = {
            "endpoint_id": endpoint_id,
            "hostname": hostname,
        }

    def is_registered(self, endpoint_id: str) -> bool:
        return endpoint_id in self._endpoints


# Global registry instance
endpoint_registry = EndpointRegistry()
