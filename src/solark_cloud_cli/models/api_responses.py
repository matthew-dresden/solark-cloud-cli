from pydantic import BaseModel


class Record(BaseModel):
    time: str
    value: str  # API returns numeric values as strings
    updateTime: str | None = None


class Info(BaseModel):
    unit: str
    records: list[Record]
    label: str
    id: str | None = None
    groupCode: str | None = None
    name: str | None = None


class EnergyData(BaseModel):
    infos: list[Info]


class ApiResponse(BaseModel):
    code: int
    msg: str
    data: EnergyData
    success: bool
