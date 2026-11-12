from typing import Literal
from pydantic import BaseModel, Field

class EngineStats(BaseModel):
    max_thrust_kn: float
    isp_vac: float
    isp_asl: float
    propellants: dict[str, float]

class Part(BaseModel):
    name: str
    title: str
    mod: str
    category: str | None = None
    size: str | None = None
    mass_t: float
    cost: float = 0
    tech_required: str | None = None
    description: str | None = None
    roles: list[str] = Field(default_factory=list)
    resources: dict[str, float] = Field(default_factory=dict)
    engine: EngineStats | None = None

class PartRef(BaseModel):
    name: str
    qty: int = Field(default=1, ge=1)
    placement: Literal["stack", "radial"] = "stack"

class Stage(BaseModel):
    label: str
    parts: list[PartRef]
    fires_with_next: bool = False
    twr_body: str | None = None

class Build(BaseModel):
    name: str
    mission: str
    body: str = "Kerbin"
    stages: list[Stage]
    payload: list[PartRef] = Field(default_factory=list)
    notes: str = ""

class StageResult(BaseModel):
    label: str
    wet_mass_t: float
    end_mass_t: float
    dv_vac: float
    dv_asl: float
    twr_start: float
    burn_time_s: float

class BuildReport(BaseModel):
    stages: list[StageResult]
    total_dv_vac: float
    launch_twr: float
    warnings: list[str] = Field(default_factory=list)