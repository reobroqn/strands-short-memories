"""
Utility Functions - Portfolio Analysis and Management.

This module contains utility functions for financial analysis and management,
including stock data fetching, portfolio creation, and performance calculation.
All visualization functionality has been removed.
"""

import logging
from typing import Any
import warnings

import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)


def get_stock_data(
    tickers: list[str], start_date: str, end_date: str, cache_file: str | None = None
) -> dict[str, Any]:
    """
    Fetch stock data with optional caching.

    Args:
        tickers: List of stock ticker symbols
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        cache_file: Optional CSV file path for caching

    Returns:
        Dict containing stock data and metadata
    """
    try:
        if cache_file:
            try:
                df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                logger.info(f"Loaded data from cache: {cache_file}")
                return {"data": df, "tickers": tickers}
            except FileNotFoundError:
                pass

        df = yf.download(tickers, start=start_date, end=end_date)["Adj Close"]

        if cache_file:
            df.to_csv(cache_file)
            logger.info(f"Saved data to cache: {cache_file}")

        return {"data": df, "tickers": tickers}

    except Exception as e:
        logger.error(f"Error fetching stock data: {e!s}")
        raise


def get_stock_analysis(
    tickers: list[str], start_date: str, end_date: str, cache_file: str | None = None
) -> dict[str, Any]:
    """
    Fetch stock analysis with summary metrics only (no daily prices).

    Args:
        tickers: List of stock ticker symbols
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        cache_file: Optional CSV file path for caching

    Returns:
        Dict containing summary metrics
    """
    try:
        if cache_file:
            try:
                summary_df = pd.read_csv(cache_file)
                summary = summary_df.set_index("ticker").to_dict("index")
                logger.info(f"Loaded analysis from cache: {cache_file}")
                return {"summary_metrics": summary, "tickers": tickers}
            except FileNotFoundError:
                pass

        df = yf.download(tickers, start=start_date, end=end_date)["Adj Close"]

        # Calculate returns and volatility
        returns = df.pct_change().dropna()
        summary_metrics = {}

        for ticker in tickers:
            if ticker in df.columns:
                prices = df[ticker].dropna()
                if len(prices) > 1:
                    ticker_returns = returns[ticker].dropna()

                    # Annualized return
                    total_return = (prices.iloc[-1] / prices.iloc[0]) - 1
                    annual_return = total_return * (252 / len(prices))

                    # Volatility
                    volatility = ticker_returns.std() * np.sqrt(252)

                    # Sharpe ratio (assuming risk-free rate of 2%)
                    sharpe_ratio = (
                        (annual_return - 0.02) / volatility if volatility > 0 else 0
                    )

                    summary_metrics[ticker] = {
                        "total_return": total_return,
                        "annual_return": annual_return,
                        "volatility": volatility,
                        "sharpe_ratio": sharpe_ratio,
                        "avg_daily_return": ticker_returns.mean(),
                        "max_drawdown": (prices / prices.cummax() - 1).min(),
                    }

        if cache_file:
            summary_df = pd.DataFrame.from_dict(summary_metrics, orient="index")
            summary_df.to_csv(cache_file)
            logger.info(f"Saved analysis to cache: {cache_file}")

        return {"summary_metrics": summary_metrics, "tickers": tickers}

    except Exception as e:
        logger.error(f"Error fetching stock analysis: {e!s}")
        raise


def create_growth_portfolio(
    stock_data: dict[str, Any], allocation_method: str = "performance_weighted"
) -> dict[str, Any]:
    """
    Create a growth-focused portfolio with dynamic allocation.

    Args:
        stock_data: Stock data with summary metrics
        allocation_method: Method for allocation (performance_weighted, risk_adjusted, equal_weight)

    Returns:
        Portfolio allocation dictionary
    """
    try:
        metrics = stock_data["summary_metrics"]

        if allocation_method == "equal_weight":
            num_stocks = len(metrics)
            allocation = dict.fromkeys(metrics.keys(), 100.0 / num_stocks)

        elif allocation_method == "risk_adjusted":
            sharpe_ratios = {}
            for ticker, data in metrics.items():
                ret = data.get("annual_return", data.get("return_pct", 0))
                vol = data.get("volatility", data.get("volatility_pct", 1))
                sharpe_ratios[ticker] = ret / vol if vol > 0 else 0

            total_sharpe = sum(sharpe_ratios.values())
            allocation = {
                ticker: (sharpe / total_sharpe * 100) if total_sharpe > 0 else 0
                for ticker, sharpe in sharpe_ratios.items()
            }

        else:  # performance_weighted (default)
            # Use positive returns only for allocation
            positive_returns = {
                ticker: max(data.get("annual_return", data.get("return_pct", 0)), 0)
                for ticker, data in metrics.items()
            }

            total_return = sum(positive_returns.values())
            allocation = {
                ticker: (ret / total_return * 100) if total_return > 0 else 0
                for ticker, ret in positive_returns.items()
            }

        allocation = {k: round(v, 2) for k, v in allocation.items()}

        expected_return = sum(
            allocation[ticker]
            / 100
            * metrics[ticker].get("annual_return", metrics[ticker].get("return_pct", 0))
            for ticker in allocation
        )

        return {
            "allocation": allocation,
            "strategy": "Growth",
            "method": allocation_method,
            "expected_return": round(expected_return, 2),
            "metrics": metrics,
        }

    except Exception as e:
        logger.error(f"Error creating growth portfolio: {e!s}")
        raise


def create_diversified_portfolio(
    stock_data: dict[str, Any], max_allocation: float = 30.0
) -> dict[str, Any]:
    """
    Create a diversified portfolio with risk-adjusted allocation.

    Args:
        stock_data: Stock data with summary metrics
        max_allocation: Maximum allocation per stock (%)

    Returns:
        Portfolio allocation dictionary
    """
    try:
        metrics = stock_data["summary_metrics"]

        sharpe_ratios = {}
        for ticker, data in metrics.items():
            ret = data.get("annual_return", data.get("return_pct", 0))
            vol = data.get("volatility", data.get("volatility_pct", 1))
            sharpe_ratios[ticker] = ret / vol if vol > 0 else 0

        total_sharpe = sum(sharpe_ratios.values())
        raw_allocation = {
            ticker: (sharpe / total_sharpe * 100) if total_sharpe > 0 else 0
            for ticker, sharpe in sharpe_ratios.items()
        }

        # Apply maximum allocation constraint
        allocation = {}
        for ticker, alloc in raw_allocation.items():
            allocation[ticker] = min(alloc, max_allocation)

        total_alloc = sum(allocation.values())
        allocation = {k: round(v / total_alloc * 100, 2) for k, v in allocation.items()}

        expected_return = sum(
            allocation[ticker]
            / 100
            * metrics[ticker].get("annual_return", metrics[ticker].get("return_pct", 0))
            for ticker in allocation
        )

        avg_volatility = sum(
            allocation[ticker]
            / 100
            * metrics[ticker].get(
                "volatility", metrics[ticker].get("volatility_pct", 0)
            )
            for ticker in allocation
        )

        return {
            "allocation": allocation,
            "strategy": "Diversified",
            "max_allocation": max_allocation,
            "expected_return": round(expected_return, 2),
            "avg_volatility": round(avg_volatility, 2),
            "metrics": metrics,
        }

    except Exception as e:
        logger.error(f"Error creating diversified portfolio: {e!s}")
        raise


def calculate_portfolio_performance(
    portfolio: dict[str, Any],
    stock_data: dict[str, Any],
    investment_amount: float = 1000.0,
) -> dict[str, Any]:
    """
    Calculate portfolio performance with concrete projections.

    Args:
        portfolio: Portfolio allocation dictionary
        stock_data: Stock data with metrics
        investment_amount: Initial investment amount

    Returns:
        Performance metrics and projections
    """
    try:
        allocation = portfolio["allocation"]
        metrics = stock_data["summary_metrics"]

        weighted_return = sum(
            (allocation[ticker] / 100)
            * metrics[ticker].get("annual_return", metrics[ticker].get("return_pct", 0))
            for ticker in allocation
        )

        weighted_volatility = sum(
            (allocation[ticker] / 100)
            * metrics[ticker].get(
                "volatility", metrics[ticker].get("volatility_pct", 0)
            )
            for ticker in allocation
        )

        final_value = investment_amount * (1 + weighted_return / 100)
        profit = final_value - investment_amount

        # Risk metrics
        risk_free_rate = 0.02  # 2% risk-free rate
        sharpe_ratio = (
            (weighted_return - risk_free_rate) / weighted_volatility
            if weighted_volatility > 0
            else 0
        )

        return {
            "initial_investment": investment_amount,
            "expected_return": round(weighted_return, 2),
            "expected_volatility": round(weighted_volatility, 2),
            "final_value": round(final_value, 2),
            "profit": round(profit, 2),
            "sharpe_ratio": round(sharpe_ratio, 3),
            "allocation": allocation,
        }

    except Exception as e:
        logger.error(f"Error calculating portfolio performance: {e!s}")
        raise


def validate_portfolio_performance(
    portfolio: dict[str, Any],
    validation_start: str,
    validation_end: str,
    initial_investment: float = 1000.0,
) -> dict[str, Any]:
    """
    Validate portfolio performance against actual market data.

    Args:
        portfolio: Portfolio allocation
        validation_start: Start date for validation period
        validation_end: End date for validation period
        initial_investment: Initial investment amount

    Returns:
        Validation results with actual performance
    """
    try:
        allocation = portfolio["allocation"]
        tickers = list(allocation.keys())

        df = yf.download(tickers, start=validation_start, end=validation_end)[
            "Adj Close"
        ]

        if df.empty or len(df) < 2:
            return {"success": False, "message": "Insufficient data for validation"}

        # Calculate daily returns
        returns = df.pct_change().dropna()

        # Calculate portfolio returns based on allocation
        portfolio_returns = sum(
            returns[ticker] * allocation[ticker] / 100 for ticker in allocation
        )

        # Cumulative returns
        cumulative_returns = (1 + portfolio_returns).cumprod()
        final_value = initial_investment * cumulative_returns.iloc[-1]
        total_return = (final_value / initial_investment - 1) * 100

        # Annualized metrics
        trading_days = len(returns)
        annual_return = total_return * (252 / trading_days)
        annual_volatility = portfolio_returns.std() * np.sqrt(252)

        return {
            "success": True,
            "validation_period": f"{validation_start} to {validation_end}",
            "initial_investment": initial_investment,
            "final_value": round(final_value, 2),
            "total_return": round(total_return, 2),
            "annual_return": round(annual_return, 2),
            "annual_volatility": round(annual_volatility, 2),
            "trading_days": trading_days,
        }

    except Exception as e:
        logger.error(f"Error validating portfolio: {e!s}")
        return {"success": False, "message": f"Validation error: {e!s}"}
