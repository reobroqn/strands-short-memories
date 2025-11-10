"""
Budget routes - Budget calculation and financial analysis endpoints.

This module contains endpoints for budget calculations, chart data preparation,
and sample data generation for financial analysis.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from ..models.schemas import (
    BudgetCalculationRequest,
    BudgetCalculationResponse,
    ChartRequest,
    ChartResponse,
    SampleDataResponse,
)
from ..services.agent_service import AgentService

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()

# Global service instance
agent_service = AgentService()


def get_agent_service() -> AgentService:
    """Dependency to get the agent service instance."""
    return agent_service


@router.post(
    "/budget/calculate",
    response_model=BudgetCalculationResponse,
    summary="Calculate Budget",
    description="Calculate 50/30/20 budget breakdown",
    tags=["Budget"],
)
async def calculate_budget(
    request: BudgetCalculationRequest,
    service: AgentService = Depends(get_agent_service),
):
    """Calculate budget breakdown."""
    try:
        result = service.calculate_50_30_20_budget(request.monthly_income)
        return BudgetCalculationResponse(**result)

    except Exception as e:
        logger.error(f"Budget calculation error: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Budget calculation failed: {e!s}",
        ) from e


@router.post(
    "/budget/chart",
    response_model=ChartResponse,
    summary="Prepare Chart Data",
    description="Prepare data for client-side chart visualization",
    tags=["Budget"],
)
async def create_chart(
    request: ChartRequest, service: AgentService = Depends(get_agent_service)
):
    """Prepare chart data for client-side visualization."""
    try:
        result = service.create_chart_data(request.data, request.title)
        return ChartResponse(**result)

    except Exception as e:
        logger.error(f"Chart creation error: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chart creation failed: {e!s}",
        ) from e


@router.get(
    "/budget/sample-data",
    response_model=SampleDataResponse,
    summary="Generate Sample Data",
    description="Generate sample spending data",
    tags=["Budget"],
)
async def generate_sample_data(service: AgentService = Depends(get_agent_service)):
    """Generate sample spending data."""
    try:
        result = service.generate_sample_spending_data()
        return SampleDataResponse(**result)

    except Exception as e:
        logger.error(f"Sample data generation error: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sample data generation failed: {e!s}",
        ) from e
