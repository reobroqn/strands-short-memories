"""
Budget and financial analysis schemas.

This module contains Pydantic models for budget calculations,
financial analysis, and chart visualization.
"""

from typing import Any

from pydantic import BaseModel, Field


class BudgetCalculationRequest(BaseModel):
    """Request model for budget calculation."""

    monthly_income: float = Field(
        ..., description="Monthly income amount", gt=0, example=5000.0
    )


class BudgetCalculationResponse(BaseModel):
    """Response model for budget calculation."""

    monthly_income: float = Field(..., description="Monthly income")
    needs: dict[str, Any] = Field(..., description="50% for needs")
    wants: dict[str, Any] = Field(..., description="30% for wants")
    savings: dict[str, Any] = Field(..., description="20% for savings")
    total: float = Field(..., description="Total income")


class ChartRequest(BaseModel):
    """Request model for creating financial charts."""

    data: dict[str, float] = Field(
        ...,
        description="Data to visualize",
        example={"Category A": 100, "Category B": 200},
    )
    title: str = Field(
        ..., description="Chart title", example="Monthly Spending Breakdown"
    )


class ChartResponse(BaseModel):
    """Response model for chart data."""

    title: str = Field(..., description="Chart title")
    data: dict[str, float] = Field(..., description="Data for visualization")
    chart_type: str = Field(default="pie", description="Recommended chart type")
    labels: list[str] = Field(..., description="Labels for chart data")
    values: list[float] = Field(..., description="Values for chart data")


class SampleDataResponse(BaseModel):
    """Response for sample data generation."""

    categories: dict[str, float] = Field(..., description="Spending by category")
    total: float = Field(..., description="Total monthly spending")
    month: str = Field(..., description="Month and year")
    description: str = Field(..., description="Data description")
