from dataclasses import dataclass


@dataclass
class SimulationResult:
    status_code: int
    simulation_results: dict
    chart_filepaths: dict
