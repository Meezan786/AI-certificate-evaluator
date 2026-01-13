from typing import Dict

from pydantic import BaseModel


class EvaluationState(BaseModel):
    criteria: Dict[str, float] = {}
    scores: Dict[str, float] = {}
    final_score: float = 0.0
