"""
schemas.py — Pydantic models for structured LLM output.

Using Pydantic + with_structured_output() means the model returns a typed object,
not a free-text blob that we have to regex-parse. If the model hallucinates a
non-integer score, Pydantic raises immediately — the error is clear and early.
"""

from pydantic import BaseModel, Field


class Discrepancy(BaseModel):
    """A single visual difference between the target and the rendered attempt."""
    region: str = Field(
        default="UI element",
        description="UI region, e.g. 'header', 'primary button', 'pricing card'"
    )
    issue: str = Field(
        default="Visual difference compared to target",
        description="What is wrong compared to the target image"
    )
    severity: int = Field(
        default=3,
        description="1-5, where 5 = most visually significant difference",
        ge=1,
        le=5,
    )
    fix: str = Field(
        default="Adjust spacing, sizing, or colors to match target",
        description="Concrete CSS/Tailwind instruction, e.g. 'increase padding to p-6'"
    )


class Critique(BaseModel):
    """Structured critique of one rendered attempt against the target."""
    score: int = Field(
        default=50,
        description="Visual fidelity score 0-100. 85+ means a designer would accept it.",
        ge=0,
        le=100,
    )
    discrepancies: list[Discrepancy] = Field(
        default_factory=list,
        description="At most 6 discrepancies, sorted by severity descending",
        max_length=6,
    )
    summary: str = Field(
        default="Ongoing visual refinements needed.",
        description="One sentence summarising the biggest remaining gap"
    )
