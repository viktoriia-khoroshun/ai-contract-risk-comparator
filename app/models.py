from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    unknown = "unknown"


class ClauseRisk(BaseModel):
    clause: str
    risk_level: RiskLevel = RiskLevel.unknown
    risk_score: int = Field(0, ge=0, le=10)
    description: str = ""


class ContractAnalysisResponse(BaseModel):
    filename: str
    total_clauses: int
    analyzed_clauses: int
    risks: list[ClauseRisk]


class ContractComparison(BaseModel):
    contract_a: ContractAnalysisResponse
    contract_b: ContractAnalysisResponse
    avg_score_a: float
    avg_score_b: float
    riskier_contract: str
    summary: str
