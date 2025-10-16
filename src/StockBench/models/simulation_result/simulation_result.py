from dataclasses import dataclass


@dataclass
class SimulationResult:
    status_code: int
    message: str
    simulation_results: dict
    chart_filepaths: dict
