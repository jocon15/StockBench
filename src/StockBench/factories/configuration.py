import os

from StockBench.broker.configuration import BrokerConfiguration


class ClientConfigurationFactory:
    """Encapsulates a factory for creating client configurations."""

    @staticmethod
    def create_broker_config() -> BrokerConfiguration:
        """Create a broker client configuration."""
        return BrokerConfiguration(
            os.environ.get('ALPACA_API_KEY'),
            os.environ.get('ALPACA_SECRET_KEY'))
