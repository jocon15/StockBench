import os

from StockBench.controllers.broker.configuration import BrokerConfiguration
from StockBench.gui.configuration import AppConfiguration


class ClientConfigurationFactory:
    """Encapsulates a factory for creating client configurations."""

    @staticmethod
    def create_broker_config() -> BrokerConfiguration:
        """Create a broker client configuration."""
        return BrokerConfiguration(
            os.environ.get('ALPACA_API_KEY'),
            os.environ.get('ALPACA_SECRET_KEY'))


class ApplicationConfigurationFactory:
    """Encapsulates a factory for creating application configurations."""

    @staticmethod
    def create_app_config() -> AppConfiguration:
        """Create an application configuration."""
        filepath = os.path.join('resources', 'version.txt')
        if os.path.isfile(filepath):
            with open(filepath, 'r') as file:
                version = file.readline()
            try:
                version_number = version.split(':')[1].strip()
                return AppConfiguration(version_number)
            except:  # noqa
                # if there are any issues with the version parsing, just pass and mark unversioned
                pass

        return AppConfiguration('Unversioned')
