from StockBench.controllers.charting.folder.folder_charting_engine import FolderChartingEngine
from StockBench.controllers.charting.multi.multi_charting_engine import MultiChartingEngine
from StockBench.controllers.charting.singular.singular_charting_engine import SingularChartingEngine
from StockBench.controllers.proxies.charting_proxy import ChartingProxy


class ChartingProxyFactory:
    @staticmethod
    def get_charting_proxy_instance() -> ChartingProxy:
        return ChartingProxy(SingularChartingEngine(), MultiChartingEngine(), FolderChartingEngine())
