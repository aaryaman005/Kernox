import hashlib
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.endpoint import Endpoint


class EndpointRegistry:
    """
    Durable endpoint registry backed by DB.
    Compatible with test expectations.
    """

    def _hash_secret(self, secret: str) -> str:
        return hashlib.sha256(secret.encode()).hexdigest()

    def register(
        self,
        endpoint_id: str,
        hostname: str,
        secret: str,
    ) -> Endpoint:
        db: Session = SessionLocal()

        try:
            existing = db.query(Endpoint).filter_by(endpoint_id=endpoint_id).first()

            if existing:
                return existing

            secret_hash = self._hash_secret(secret)

            endpoint = Endpoint(
                endpoint_id=endpoint_id,
                hostname=hostname,
                secret_hash=secret_hash,
            )

            db.add(endpoint)
            db.commit()
            db.refresh(endpoint)

            return endpoint
        finally:
            db.close()

    def is_registered(self, endpoint_id: str) -> bool:
        db: Session = SessionLocal()
        try:
            return (
                db.query(Endpoint).filter_by(endpoint_id=endpoint_id).first()
                is not None
            )
        finally:
            db.close()

    def get_secret_hash(self, endpoint_id: str) -> str | None:
        db: Session = SessionLocal()
        try:
            endpoint = db.query(Endpoint).filter_by(endpoint_id=endpoint_id).first()
            return endpoint.secret_hash if endpoint else None
        finally:
            db.close()


endpoint_registry = EndpointRegistry()
