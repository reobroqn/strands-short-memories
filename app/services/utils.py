"""
Utility Functions - Portfolio Analysis and Management

This module contains utility functions for financial analysis and management,
including stock data fetching, portfolio creation, performance calculation,
and visualization.

These utilities are used by the unified agent service for portfolio orchestration
and financial analysis capabilities.
"""

import logging
import io
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import warnings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


def get_stock_data(
    tickers: List[str],
    start_date: str,
    end_date: str,
    cache_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch comprehensive stock data including daily prices and summary metrics.

    Args:
        tickers: List of stock ticker symbols
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        cache_file: Optional CSV file path for caching

    Returns:
        Dict containing daily prices and summary metrics
    """
    try:
        if cache_file:
            try:
                df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                logger.info(f"Loaded data from cache: {cache_file}")
            except FileNotFoundError:
                df = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
                df.to_csv(cache_file)
                logger.info(f"Fetched and cached data: {cache_file}")
        else:
            df = yf.download(tickers, start=start_date, end=end_date)['Adj Close']

        daily_returns = df.pct_change().dropna()

        summary = {}
        for ticker in tickers:
            annual_return = daily_returns[ticker].mean() * 252
            volatility = daily_returns[ticker].std() * np.sqrt(252)
            summary[ticker] = {
                "annual_return": round(annual_return * 100, 2),
                "volatility": round(volatility * 100, 2)
            }

        return {
            "daily_prices": df.to_dict(),
            "summary_metrics": summary,
            "tickers": tickers
        }

    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        raise


def get_stock_analysis(
    tickers: List[str],
    start_date: str,
    end_date: str,
    cache_file: Optional[str] = None
) -> Dict[str, Any]:
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
                summary = summary_df.set_index('ticker').to_dict('index')
                logger.info(f"Loaded analysis from cache: {cache_file}")
                return {"summary_metrics": summary, "tickers": tickers}
            except FileNotFoundError:
                pass

        df = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
        daily_returns = df.pct_change().dropna()

        summary = {}
        for ticker in tickers:
            return_pct = daily_returns[ticker].mean() * 252 * 100
            volatility_pct = daily_returns[ticker].std() * np.sqrt(252) * 100
            summary[ticker] = {
                "return_pct": round(return_pct, 2),
                "volatility_pct": round(volatility_pct, 2)
            }

        if cache_file:
            summary_df = pd.DataFrame.from_dict(summary, orient='index')
            summary_df.index.name = 'ticker'
            summary_df.to_csv(cache_file)
            logger.info(f"Cached analysis: {cache_file}")

        return {"summary_metrics": summary, "tickers": tickers}

    except Exception as e:
        logger.error(f"Error fetching stock analysis: {str(e)}")
        raise


def create_growth_portfolio(
    stock_data: Dict[str, Any],
    allocation_method: str = "performance_weighted"
) -> Dict[str, Any]:
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
            allocation = {ticker: 100.0 / num_stocks for ticker in metrics.keys()}

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
            returns = {}
            for ticker, data in metrics.items():
                returns[ticker] = data.get("annual_return", data.get("return_pct", 0))

            positive_returns = {t: max(r, 0.1) for t, r in returns.items()}
            total_return = sum(positive_returns.values())
            allocation = {
                ticker: (ret / total_return * 100) if total_return > 0 else 0
                for ticker, ret in positive_returns.items()
            }

        allocation = {k: round(v, 2) for k, v in allocation.items()}

        expected_return = sum(
            allocation[ticker] / 100 * metrics[ticker].get("annual_return", metrics[ticker].get("return_pct", 0))
            for ticker in allocation.keys()
        )

        return {
            "allocation": allocation,
            "strategy": "Growth",
            "allocation_method": allocation_method,
            "expected_return": round(expected_return, 2),
            "risk_level": "High"
        }

    except Exception as e:
        logger.error(f"Error creating growth portfolio: {str(e)}")
        raise


def create_diversified_portfolio(
    stock_data: Dict[str, Any],
    max_allocation: float = 30.0
) -> Dict[str, Any]:
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

        allocation = {}
        for ticker, alloc in raw_allocation.items():
            allocation[ticker] = min(alloc, max_allocation)

        total_alloc = sum(allocation.values())
        allocation = {k: round(v / total_alloc * 100, 2) for k, v in allocation.items()}

        expected_return = sum(
            allocation[ticker] / 100 * metrics[ticker].get("annual_return", metrics[ticker].get("return_pct", 0))
            for ticker in allocation.keys()
        )

        avg_volatility = sum(
            allocation[ticker] / 100 * metrics[ticker].get("volatility", metrics[ticker].get("volatility_pct", 0))
            for ticker in allocation.keys()
        )

        return {
            "allocation": allocation,
            "strategy": "Diversified",
            "expected_return": round(expected_return, 2),
            "avg_volatility": round(avg_volatility, 2),
            "risk_level": "Moderate",
            "sectors": len(allocation)
        }

    except Exception as e:
        logger.error(f"Error creating diversified portfolio: {str(e)}")
        raise


def calculate_portfolio_performance(
    portfolio: Dict[str, Any],
    stock_data: Dict[str, Any],
    investment_amount: float = 1000.0
) -> Dict[str, Any]:
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
            (allocation[ticker] / 100) * metrics[ticker].get("annual_return", metrics[ticker].get("return_pct", 0))
            for ticker in allocation.keys()
        )

        weighted_volatility = sum(
            (allocation[ticker] / 100) * metrics[ticker].get("volatility", metrics[ticker].get("volatility_pct", 0))
            for ticker in allocation.keys()
        )

        final_value = investment_amount * (1 + weighted_return / 100)
        profit = final_value - investment_amount

        return {
            "strategy": portfolio.get("strategy", "Unknown"),
            "initial_investment": investment_amount,
            "final_value": round(final_value, 2),
            "profit": round(profit, 2),
            "return_percent": round(weighted_return, 2),
            "volatility_percent": round(weighted_volatility, 2),
            "risk_level": portfolio.get("risk_level", "Unknown")
        }

    except Exception as e:
        logger.error(f"Error calculating portfolio performance: {str(e)}")
        raise


def visualize_portfolio_allocation(portfolio: Dict[str, Any], title: str = "Portfolio Allocation") -> str:
    """
    Create a pie chart visualization of portfolio allocation.

    Args:
        portfolio: Portfolio with allocation data
        title: Chart title

    Returns:
        Base64 encoded image string
    """
    try:
        allocation = portfolio["allocation"]

        labels = list(allocation.keys())
        values = list(allocation.values())
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3']

        plt.figure(figsize=(10, 6))
        plt.pie(values, labels=labels, autopct='%1.1f%%', colors=colors[:len(values)], startangle=90)
        plt.title(f'📊 {title}', fontsize=14, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close()

        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return img_base64

    except Exception as e:
        logger.error(f"Error creating allocation visualization: {str(e)}")
        raise


def visualize_performance_comparison(
    performance_data: List[Dict[str, Any]],
    title: str = "Performance Comparison"
) -> str:
    """
    Create a bar chart comparing portfolio performance.

    Args:
        performance_data: List of performance dictionaries
        title: Chart title

    Returns:
        Base64 encoded image string
    """
    try:
        strategies = [p["strategy"] for p in performance_data]
        returns = [p["return_percent"] for p in performance_data]

        colors = ['#4ECDC4', '#FF6B6B']

        plt.figure(figsize=(10, 6))
        bars = plt.bar(strategies, returns, color=colors[:len(strategies)])
        plt.title(f'📊 {title}', fontsize=14, fontweight='bold')
        plt.xlabel('Strategy')
        plt.ylabel('Expected Return (%)')
        plt.grid(axis='y', alpha=0.3)

        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom')

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close()

        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return img_base64

    except Exception as e:
        logger.error(f"Error creating performance visualization: {str(e)}")
        raise


def validate_portfolio_performance(
    portfolio: Dict[str, Any],
    validation_start: str,
    validation_end: str,
    initial_investment: float = 1000.0
) -> Dict[str, Any]:
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

        df = yf.download(tickers, start=validation_start, end=validation_end)['Adj Close']

        if df.empty:
            return {
                "success": False,
                "message": "No data available for validation period"
            }

        returns = df.pct_change().dropna()

        portfolio_returns = sum(
            (allocation[ticker] / 100) * returns[ticker]
            for ticker in tickers
        )

        cumulative_return = (1 + portfolio_returns).prod() - 1
        final_value = initial_investment * (1 + cumulative_return)

        actual_volatility = portfolio_returns.std() * np.sqrt(252) * 100

        return {
            "success": True,
            "validation_period": f"{validation_start} to {validation_end}",
            "initial_investment": initial_investment,
            "final_value": round(final_value, 2),
            "actual_return": round(cumulative_return * 100, 2),
            "actual_volatility": round(actual_volatility, 2),
            "profit_loss": round(final_value - initial_investment, 2)
        }

    except Exception as e:
        logger.error(f"Error validating portfolio: {str(e)}")
        return {
            "success": False,
            "message": f"Validation error: {str(e)}"
        }
