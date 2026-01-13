from typing import Dict

from pydantic import BaseModel


class CertificateState(BaseModel):
    raw_text: str = ""
    extracted_fields: Dict[str, str] = {}
    confidence: Dict[str, float] = {}
