from dataclasses import dataclass


@dataclass
class SimulationResult:
    """Represents a bundle of simulation results returned by the simulation QThread for combining numerical simulation
    results and chart filepaths.
    """
    simulation_results: dict
    chart_filepaths: dict
