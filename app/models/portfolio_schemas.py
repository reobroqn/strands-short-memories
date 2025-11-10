"""
Portfolio management schemas.

This module contains Pydantic models for portfolio operations,
orchestration, and performance tracking.
"""

from pydantic import BaseModel, Field

# This file is prepared for future portfolio-specific schemas
# Currently, portfolio functionality uses existing schemas
# but this structure allows for easy extension


class PortfolioOrchestrationRequest(BaseModel):
    """
    Request model for portfolio orchestration.

    Attributes:
        user_request: Natural language request for portfolio operations
    """

    user_request: str = Field(
        ...,
        description="Natural language request for portfolio operations",
        example="Create a diversified portfolio with 70% stocks and 30% bonds",
    )
