from pydantic import BaseModel


class EnergyRecord(BaseModel):
    timestamp: str
    value: float
    unit: str
    label: str


class ValuationRow(BaseModel):
    timestamp: str
    self_consumed_kwh: float
    avoided_cost: float
    export_credit: float
    total_value: float


class EnergyReport(BaseModel):
    plant_id: str
    period: str
    date: str
    records: list[EnergyRecord]
    labels: list[str]
    valuations: list[ValuationRow] | None = None
