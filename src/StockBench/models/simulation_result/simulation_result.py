from dataclasses import dataclass


@dataclass
class SimulationResult:
    status_code: int
    message: str
    simulation_results: dict
    chart_filepaths: dict

    @staticmethod
    def simulation_successful(status_code: int) -> bool:
        if status_code == 200:
            return True
        return False
