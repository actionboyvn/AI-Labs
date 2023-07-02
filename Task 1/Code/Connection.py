from dataclasses import dataclass
@dataclass
class Connection:
    line: str
    departure_time: int
    arrival_time: int
    start_stop: str
    end_stop: str
    start_stop_lat: float
    start_stop_lon: float
    end_stop_lat: float
    end_stop_lon: float

