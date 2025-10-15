from dataclasses import dataclass


@dataclass
class BrokerConfiguration:
    public_key: str
    private_key: str
