"""Domain models shared by the parser, tools, agent and UI."""
from typing import Literal

from pydantic import BaseModel, Field


class EngineStats(BaseModel):
    max_thrust_kn: float  # KSP 1.x maxThrust is vacuum thrust
    isp_vac: float
    isp_asl: float
    propellants: dict[str, float] = Field(default_factory=dict)  # resource -> ratio


class Part(BaseModel):
    name: str  # internal name, e.g. "liquidEngine2"
    title: str = ""
    mod: str = "unknown"  # top-level GameData folder
    category: str | None = None
    size: str | None = None  # first bulkheadProfiles entry, e.g. "size1"
    mass_t: float = 0.0  # dry mass in tonnes
    cost: float = 0.0
    tech_required: str | None = None
    description: str = ""
    roles: list[str] = Field(default_factory=list)
    resources: dict[str, float] = Field(default_factory=dict)  # name -> maxAmount
    engine: EngineStats | None = None


class PartRef(BaseModel):
    name: str
    qty: int = Field(1, ge=1)
    placement: Literal["stack", "radial"] = "stack"


class Stage(BaseModel):
    label: str
    parts: list[PartRef]  # dropped when this stage separates; stack parts listed top to bottom
    fires_with_next: bool = False  # side boosters burning alongside the next stage
    twr_body: str | None = None  # body used for this stage's TWR, e.g. "Mun"


class Build(BaseModel):
    name: str
    mission: str
    body: str = "Kerbin"
    stages: list[Stage]  # firing order: index 0 fires first
    payload: list[PartRef] = Field(default_factory=list)  # never dropped (pod, chute...)
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
