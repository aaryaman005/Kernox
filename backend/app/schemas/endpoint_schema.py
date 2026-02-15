from pydantic import BaseModel, Field


class EndpointRegistration(BaseModel):
    endpoint_id: str = Field(..., min_length=3, max_length=128)
    hostname: str = Field(..., min_length=1, max_length=255)

    model_config = {"extra": "forbid"}
