from dataclasses import dataclass


@dataclass
class Credentials:
    """Credentials for broker authentication."""
    api_public_key: str
    api_secret_key: str
