from pydantic import BaseModel


class EnergyRecord(BaseModel):
    timestamp: str
    value: float
    unit: str
    label: str


class EnergyReport(BaseModel):
    plant_id: str
    period: str  # "year", "month", "day", "flow"
    date: str
    records: list[EnergyRecord]
    labels: list[str]  # unique labels in this report
