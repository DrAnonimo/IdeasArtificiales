"""
Financial Data Collector

Collects stock market data for AI bubble analysis without requiring API calls.
Uses yfinance library which scrapes data directly from Yahoo Finance.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StockData:
    """Represents stock market data for a single stock"""
    ticker: str
    name: str
    current_price: float
    change_1d: float
    change_7d: float
    change_30d: float
    volume: int
    volatility_30d: float
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None

@dataclass
class MarketIndices:
    """Represents market indices data"""
    sp500: float
    nasdaq: float
    vix: float
    treasury_10y: float
    dollar_index: float

class FinancialDataCollector:
    """Collects financial data for AI bubble analysis"""
    
    def __init__(self):
        # AI-related stocks to track
        self.ai_stocks = {
            'NVDA': 'NVIDIA',
            'MSFT': 'Microsoft',
            'GOOGL': 'Google',
            'META': 'Meta',
            'TSLA': 'Tesla',
            'AMD': 'AMD',
            'INTC': 'Intel',
            'ORCL': 'Oracle',
            'CRM': 'Salesforce',
            'ADBE': 'Adobe'
        }
        
        # Market indices to track
        self.market_indices = {
            '^GSPC': 'S&P 500',
            '^IXIC': 'NASDAQ',
            '^VIX': 'VIX (Volatility)',
            '^TNX': '10-Year Treasury',
            'DX-Y.NYB': 'US Dollar Index'
        }
    
    def collect_stock_data(self, days: int = 30) -> Dict[str, StockData]:
        """Collect stock data for AI-related companies"""
        logger.info(f"Collecting stock data for {len(self.ai_stocks)} AI stocks")
        
        stock_data = {}
        
        for ticker, name in self.ai_stocks.items():
            try:
                logger.info(f"Fetching data for {ticker} ({name})")
                
                # Get stock data - NO API CALLS, just web scraping
                stock = yf.Ticker(ticker)
                hist = stock.history(period=f"{days}d")
                
                if hist.empty:
                    logger.warning(f"No data available for {ticker}")
                    continue
                
                # Calculate metrics
                current_price = hist['Close'].iloc[-1]
                change_1d = hist['Close'].pct_change().iloc[-1] * 100
                change_7d = hist['Close'].pct_change(7).iloc[-1] * 100
                change_30d = hist['Close'].pct_change(30).iloc[-1] * 100
                volume = hist['Volume'].iloc[-1]
                volatility_30d = hist['Close'].pct_change().std() * 100
                
                # Get additional info if available
                info = stock.info
                market_cap = info.get('marketCap')
                pe_ratio = info.get('trailingPE')
                
                stock_data[ticker] = StockData(
                    ticker=ticker,
                    name=name,
                    current_price=current_price,
                    change_1d=change_1d,
                    change_7d=change_7d,
                    change_30d=change_30d,
                    volume=volume,
                    volatility_30d=volatility_30d,
                    market_cap=market_cap,
                    pe_ratio=pe_ratio
                )
                
                logger.info(f"✅ {ticker}: ${current_price:.2f} ({change_1d:+.2f}%)")
                
            except Exception as e:
                logger.error(f"Error fetching data for {ticker}: {e}")
                continue
        
        logger.info(f"Successfully collected data for {len(stock_data)} stocks")
        return stock_data
    
    def collect_market_indices(self) -> MarketIndices:
        """Collect market indices data"""
        logger.info("Collecting market indices data")
        
        indices_data = {}
        
        for ticker, name in self.market_indices.items():
            try:
                logger.info(f"Fetching {name} ({ticker})")
                
                # Get index data - NO API CALLS
                index = yf.Ticker(ticker)
                hist = index.history(period="2d")
                
                if hist.empty:
                    logger.warning(f"No data available for {ticker}")
                    continue
                
                current_value = hist['Close'].iloc[-1]
                indices_data[ticker] = current_value
                
                logger.info(f"✅ {name}: {current_value:.2f}")
                
            except Exception as e:
                logger.error(f"Error fetching {ticker}: {e}")
                continue
        
        return MarketIndices(
            sp500=indices_data.get('^GSPC', 0),
            nasdaq=indices_data.get('^IXIC', 0),
            vix=indices_data.get('^VIX', 0),
            treasury_10y=indices_data.get('^TNX', 0),
            dollar_index=indices_data.get('DX-Y.NYB', 0)
        )
    
    def calculate_financial_indicators(self, stock_data: Dict[str, StockData], market_indices: MarketIndices) -> Dict[str, Any]:
        """Calculate financial bubble indicators"""
        if not stock_data:
            return {"error": "No stock data available"}
        
        try:
            # Calculate average AI stock performance
            changes_1d = [stock.change_1d for stock in stock_data.values()]
            changes_7d = [stock.change_7d for stock in stock_data.values()]
            changes_30d = [stock.change_30d for stock in stock_data.values()]
            volatilities = [stock.volatility_30d for stock in stock_data.values()]
            
            avg_performance_1d = np.mean(changes_1d)
            avg_performance_7d = np.mean(changes_7d)
            avg_performance_30d = np.mean(changes_30d)
            avg_volatility = np.mean(volatilities)
            
            # Calculate market momentum indicators
            momentum_1d = 1 if avg_performance_1d > 2.0 else 0  # >2% in 1 day
            momentum_7d = 1 if avg_performance_7d > 5.0 else 0  # >5% in 7 days
            momentum_30d = 1 if avg_performance_30d > 10.0 else 0  # >10% in 30 days
            
            # Calculate volatility risk
            volatility_risk = 1 if avg_volatility > 3.0 else 0  # >3% daily volatility
            
            # Calculate market correlation
            market_correlation = self._calculate_market_correlation(stock_data, market_indices)
            
            # Calculate bubble risk indicators
            bubble_indicators = {
                'ai_stock_performance_1d': avg_performance_1d,
                'ai_stock_performance_7d': avg_performance_7d,
                'ai_stock_performance_30d': avg_performance_30d,
                'ai_stock_volatility': avg_volatility,
                'momentum_1d': momentum_1d,
                'momentum_7d': momentum_7d,
                'momentum_30d': momentum_30d,
                'volatility_risk': volatility_risk,
                'market_correlation': market_correlation,
                'vix_level': market_indices.vix,
                'treasury_yield': market_indices.treasury_10y,
                'dollar_strength': market_indices.dollar_index
            }
            
            # Calculate overall financial bubble risk
            financial_bubble_risk = self._calculate_financial_bubble_risk(bubble_indicators)
            bubble_indicators['financial_bubble_risk'] = financial_bubble_risk
            
            return bubble_indicators
            
        except Exception as e:
            logger.error(f"Error calculating financial indicators: {e}")
            return {"error": str(e)}
    
    def _calculate_market_correlation(self, stock_data: Dict[str, StockData], market_indices: MarketIndices) -> float:
        """Calculate correlation between AI stocks and market indices"""
        try:
            # This is a simplified correlation calculation
            # In a real implementation, you'd calculate actual correlation coefficients
            ai_performance = np.mean([stock.change_30d for stock in stock_data.values()])
            market_performance = 0  # Would need historical data for proper calculation
            
            # Simplified correlation based on performance direction
            if ai_performance > 0 and market_indices.sp500 > 0:
                return 0.7  # Positive correlation
            elif ai_performance < 0 and market_indices.sp500 < 0:
                return 0.7  # Positive correlation
            else:
                return 0.3  # Lower correlation
            
        except Exception as e:
            logger.error(f"Error calculating market correlation: {e}")
            return 0.5  # Default neutral correlation
    
    def _calculate_financial_bubble_risk(self, indicators: Dict[str, Any]) -> float:
        """Calculate overall financial bubble risk score"""
        try:
            # Weighted scoring system
            weights = {
                'momentum_30d': 0.3,
                'volatility_risk': 0.25,
                'ai_stock_performance_30d': 0.2,
                'vix_level': 0.15,
                'market_correlation': 0.1
            }
            
            # Normalize indicators to 0-1 scale
            normalized_indicators = {}
            
            # Momentum indicators (already 0 or 1)
            normalized_indicators['momentum_30d'] = indicators.get('momentum_30d', 0)
            normalized_indicators['volatility_risk'] = indicators.get('volatility_risk', 0)
            
            # Performance indicator (normalize to 0-1)
            perf_30d = indicators.get('ai_stock_performance_30d', 0)
            normalized_indicators['ai_stock_performance_30d'] = min(max(perf_30d / 20.0, 0), 1)  # 20% = 1.0
            
            # VIX level (normalize to 0-1)
            vix = indicators.get('vix_level', 20)
            normalized_indicators['vix_level'] = min(max((vix - 10) / 30, 0), 1)  # 10-40 range
            
            # Market correlation (already 0-1)
            normalized_indicators['market_correlation'] = indicators.get('market_correlation', 0.5)
            
            # Calculate weighted average
            total_score = 0
            total_weight = 0
            
            for indicator, weight in weights.items():
                if indicator in normalized_indicators:
                    total_score += normalized_indicators[indicator] * weight
                    total_weight += weight
            
            return total_score / total_weight if total_weight > 0 else 0
            
        except Exception as e:
            logger.error(f"Error calculating financial bubble risk: {e}")
            return 0
    
    def get_financial_summary(self, stock_data: Dict[str, StockData], market_indices: MarketIndices) -> Dict[str, Any]:
        """Get a summary of financial data"""
        if not stock_data:
            return {"error": "No financial data available"}
        
        try:
            # Calculate summary statistics
            total_market_cap = sum(stock.market_cap for stock in stock_data.values() if stock.market_cap)
            avg_pe_ratio = np.mean([stock.pe_ratio for stock in stock_data.values() if stock.pe_ratio])
            
            # Find top performers
            top_performers = sorted(stock_data.values(), key=lambda x: x.change_30d, reverse=True)[:3]
            worst_performers = sorted(stock_data.values(), key=lambda x: x.change_30d)[:3]
            
            return {
                "total_stocks": len(stock_data),
                "total_market_cap": total_market_cap,
                "average_pe_ratio": avg_pe_ratio,
                "top_performers": [
                    {"ticker": stock.ticker, "name": stock.name, "change_30d": stock.change_30d}
                    for stock in top_performers
                ],
                "worst_performers": [
                    {"ticker": stock.ticker, "name": stock.name, "change_30d": stock.change_30d}
                    for stock in worst_performers
                ],
                "market_indices": {
                    "sp500": market_indices.sp500,
                    "nasdaq": market_indices.nasdaq,
                    "vix": market_indices.vix,
                    "treasury_10y": market_indices.treasury_10y,
                    "dollar_index": market_indices.dollar_index
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating financial summary: {e}")
            return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    collector = FinancialDataCollector()
    
    # Collect stock data (NO API CALLS)
    stock_data = collector.collect_stock_data(days=30)
    
    # Collect market indices (NO API CALLS)
    market_indices = collector.collect_market_indices()
    
    # Calculate financial indicators
    indicators = collector.calculate_financial_indicators(stock_data, market_indices)
    
    # Get summary
    summary = collector.get_financial_summary(stock_data, market_indices)
    
    print("Financial Data Collection Complete!")
    print(f"Stocks collected: {len(stock_data)}")
    print(f"Financial bubble risk: {indicators.get('financial_bubble_risk', 0):.3f}")
