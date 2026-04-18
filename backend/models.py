# models.py
# These are the "shapes" of data our API sends and receives.
# Pydantic makes sure the data is always the right type.

from pydantic import BaseModel

class QuestionRequest(BaseModel):
    """What the frontend sends us: just a question string."""
    question: str
    session_id: str  # so we know which uploaded PDF to use

class NCTSResult(BaseModel):
    """The trust score breakdown."""
    grounding_score: float      # G: are numbers found in source?
    math_score: float           # M: is the math correct?
    trust_score: float          # T = 0.6*G + 0.4*M
    confidence_label: str       # HIGH / MEDIUM / LOW
    flagged_numbers: list       # which numbers were checked

class AnswerResponse(BaseModel):
    """Everything we send back to the frontend."""
    answer: str
    ncts: NCTSResult
    source_chunks: list         # the passages we retrieved
    session_id: str