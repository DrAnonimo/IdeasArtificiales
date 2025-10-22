"""
Financial Indicators System

Advanced financial indicators for AI bubble analysis including:
- Market momentum indicators
- Volatility risk assessment
- Valuation concerns
- Market correlation analysis
- Sentiment indicators
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FinancialIndicator:
    """Represents a financial indicator with metadata"""
    name: str
    value: float
    weight: float
    threshold: float
    description: str
    is_concerning: bool
    trend: str  # 'increasing', 'decreasing', 'stable'
    confidence: float  # 0-1 confidence in the indicator
    historical_context: Optional[Dict[str, Any]] = None

@dataclass
class MarketRegime:
    """Represents current market regime"""
    regime_type: str  # 'bull', 'bear', 'sideways', 'volatile'
    confidence: float
    characteristics: List[str]
    risk_level: str  # 'low', 'moderate', 'high'

class FinancialIndicatorsSystem:
    """Advanced financial indicators system for bubble analysis"""
    
    def __init__(self):
        self.indicators = {}
        self.historical_data = {}
        self.market_regime = None
        
    def calculate_all_indicators(self, stock_data: Dict[str, Any], 
                                market_indices: Any, 
                                historical_snapshots: List[Dict[str, Any]] = None) -> Dict[str, FinancialIndicator]:
        """Calculate all financial indicators"""
        logger.info("Calculating comprehensive financial indicators...")
        
        indicators = {}
        
        # 1. Market Momentum Indicators
        indicators.update(self._calculate_momentum_indicators(stock_data, market_indices))
        
        # 2. Volatility Risk Indicators
        indicators.update(self._calculate_volatility_indicators(stock_data, market_indices))
        
        # 3. Valuation Indicators
        indicators.update(self._calculate_valuation_indicators(stock_data))
        
        # 4. Market Correlation Indicators
        indicators.update(self._calculate_correlation_indicators(stock_data, market_indices))
        
        # 5. Sentiment Indicators
        indicators.update(self._calculate_sentiment_indicators(stock_data, market_indices))
        
        # 6. Market Regime Indicators
        indicators.update(self._calculate_regime_indicators(stock_data, market_indices))
        
        # 7. Bubble Risk Indicators
        indicators.update(self._calculate_bubble_risk_indicators(stock_data, market_indices, historical_snapshots))
        
        # 8. Liquidity Indicators
        indicators.update(self._calculate_liquidity_indicators(stock_data))
        
        # 9. Market Breadth Indicators
        indicators.update(self._calculate_breadth_indicators(stock_data))
        
        # 10. Risk-Adjusted Performance Indicators
        indicators.update(self._calculate_risk_adjusted_indicators(stock_data, market_indices))
        
        self.indicators = indicators
        return indicators
    
    def _calculate_momentum_indicators(self, stock_data: Dict[str, Any], market_indices: Any) -> Dict[str, FinancialIndicator]:
        """Calculate market momentum indicators"""
        indicators = {}
        
        if not stock_data:
            return indicators
        
        # Calculate average performance metrics
        changes_1d = [stock.change_1d for stock in stock_data.values()]
        changes_7d = [stock.change_7d for stock in stock_data.values()]
        changes_30d = [stock.change_30d for stock in stock_data.values()]
        
        avg_1d = np.mean(changes_1d)
        avg_7d = np.mean(changes_7d)
        avg_30d = np.mean(changes_30d)
        
        # 1. Short-term momentum (1-day)
        momentum_1d = 1 if avg_1d > 2.0 else 0
        indicators['momentum_1d'] = FinancialIndicator(
            name='momentum_1d',
            value=momentum_1d,
            weight=0.05,
            threshold=0.5,
            description='AI stock momentum over 1 day',
            is_concerning=momentum_1d > 0.5,
            trend='increasing' if avg_1d > 0 else 'decreasing',
            confidence=min(abs(avg_1d) / 5.0, 1.0)
        )
        
        # 2. Medium-term momentum (7-day)
        momentum_7d = 1 if avg_7d > 5.0 else 0
        indicators['momentum_7d'] = FinancialIndicator(
            name='momentum_7d',
            value=momentum_7d,
            weight=0.08,
            threshold=0.5,
            description='AI stock momentum over 7 days',
            is_concerning=momentum_7d > 0.5,
            trend='increasing' if avg_7d > 0 else 'decreasing',
            confidence=min(abs(avg_7d) / 10.0, 1.0)
        )
        
        # 3. Long-term momentum (30-day)
        momentum_30d = 1 if avg_30d > 10.0 else 0
        indicators['momentum_30d'] = FinancialIndicator(
            name='momentum_30d',
            value=momentum_30d,
            weight=0.12,
            threshold=0.5,
            description='AI stock momentum over 30 days',
            is_concerning=momentum_30d > 0.5,
            trend='increasing' if avg_30d > 0 else 'decreasing',
            confidence=min(abs(avg_30d) / 20.0, 1.0)
        )
        
        # 4. Momentum acceleration
        momentum_acceleration = (avg_7d - avg_1d) / 6  # Daily acceleration
        indicators['momentum_acceleration'] = FinancialIndicator(
            name='momentum_acceleration',
            value=min(max(momentum_acceleration / 2.0, 0), 1),  # Normalize to 0-1
            weight=0.06,
            threshold=0.6,
            description='Rate of change in momentum',
            is_concerning=momentum_acceleration > 1.0,
            trend='increasing' if momentum_acceleration > 0 else 'decreasing',
            confidence=min(abs(momentum_acceleration) / 2.0, 1.0)
        )
        
        return indicators
    
    def _calculate_volatility_indicators(self, stock_data: Dict[str, Any], market_indices: Any) -> Dict[str, FinancialIndicator]:
        """Calculate volatility risk indicators"""
        indicators = {}
        
        if not stock_data:
            return indicators
        
        # Calculate volatility metrics
        volatilities = [stock.volatility_30d for stock in stock_data.values()]
        avg_volatility = np.mean(volatilities)
        max_volatility = np.max(volatilities)
        volatility_std = np.std(volatilities)
        
        # 1. Average volatility risk
        volatility_risk = 1 if avg_volatility > 3.0 else 0
        indicators['volatility_risk'] = FinancialIndicator(
            name='volatility_risk',
            value=volatility_risk,
            weight=0.10,
            threshold=0.5,
            description='Average volatility risk across AI stocks',
            is_concerning=volatility_risk > 0.5,
            trend='increasing' if avg_volatility > 3.0 else 'decreasing',
            confidence=min(avg_volatility / 5.0, 1.0)
        )
        
        # 2. Volatility dispersion
        volatility_dispersion = volatility_std / avg_volatility if avg_volatility > 0 else 0
        indicators['volatility_dispersion'] = FinancialIndicator(
            name='volatility_dispersion',
            value=min(volatility_dispersion, 1.0),
            weight=0.05,
            threshold=0.7,
            description='Dispersion of volatility across AI stocks',
            is_concerning=volatility_dispersion > 0.7,
            trend='increasing' if volatility_dispersion > 0.5 else 'decreasing',
            confidence=min(volatility_dispersion, 1.0)
        )
        
        # 3. VIX-based volatility
        vix_level = market_indices.vix if market_indices else 20
        vix_risk = 1 if vix_level > 25 else 0
        indicators['vix_risk'] = FinancialIndicator(
            name='vix_risk',
            value=vix_risk,
            weight=0.08,
            threshold=0.5,
            description='Market volatility based on VIX',
            is_concerning=vix_risk > 0.5,
            trend='increasing' if vix_level > 20 else 'decreasing',
            confidence=min((vix_level - 10) / 30, 1.0)
        )
        
        # 4. Volatility spike risk
        volatility_spike = 1 if max_volatility > 5.0 else 0
        indicators['volatility_spike'] = FinancialIndicator(
            name='volatility_spike',
            value=volatility_spike,
            weight=0.07,
            threshold=0.5,
            description='Risk of extreme volatility spikes',
            is_concerning=volatility_spike > 0.5,
            trend='increasing' if max_volatility > 4.0 else 'decreasing',
            confidence=min(max_volatility / 8.0, 1.0)
        )
        
        return indicators
    
    def _calculate_valuation_indicators(self, stock_data: Dict[str, Any]) -> Dict[str, FinancialIndicator]:
        """Calculate valuation concern indicators"""
        indicators = {}
        
        if not stock_data:
            return indicators
        
        # Calculate valuation metrics
        pe_ratios = [stock.pe_ratio for stock in stock_data.values() if stock.pe_ratio]
        market_caps = [stock.market_cap for stock in stock_data.values() if stock.market_cap]
        
        if not pe_ratios:
            return indicators
        
        avg_pe = np.mean(pe_ratios)
        median_pe = np.median(pe_ratios)
        pe_std = np.std(pe_ratios)
        
        # 1. P/E ratio concern
        pe_concern = 1 if avg_pe > 30 else 0
        indicators['pe_concern'] = FinancialIndicator(
            name='pe_concern',
            value=pe_concern,
            weight=0.08,
            threshold=0.5,
            description='P/E ratio valuation concern',
            is_concerning=pe_concern > 0.5,
            trend='increasing' if avg_pe > 25 else 'decreasing',
            confidence=min(avg_pe / 50.0, 1.0)
        )
        
        # 2. P/E dispersion
        pe_dispersion = pe_std / avg_pe if avg_pe > 0 else 0
        indicators['pe_dispersion'] = FinancialIndicator(
            name='pe_dispersion',
            value=min(pe_dispersion, 1.0),
            weight=0.04,
            threshold=0.8,
            description='Dispersion of P/E ratios across stocks',
            is_concerning=pe_dispersion > 0.8,
            trend='increasing' if pe_dispersion > 0.5 else 'decreasing',
            confidence=min(pe_dispersion, 1.0)
        )
        
        # 3. Market cap concentration
        if market_caps:
            total_market_cap = sum(market_caps)
            max_market_cap = max(market_caps)
            concentration = max_market_cap / total_market_cap if total_market_cap > 0 else 0
            
            indicators['market_cap_concentration'] = FinancialIndicator(
                name='market_cap_concentration',
                value=concentration,
                weight=0.05,
                threshold=0.4,
                description='Market cap concentration in largest stock',
                is_concerning=concentration > 0.4,
                trend='increasing' if concentration > 0.3 else 'decreasing',
                confidence=min(concentration * 2, 1.0)
            )
        
        return indicators
    
    def _calculate_correlation_indicators(self, stock_data: Dict[str, Any], market_indices: Any) -> Dict[str, FinancialIndicator]:
        """Calculate market correlation indicators"""
        indicators = {}
        
        if not stock_data or not market_indices:
            return indicators
        
        # Calculate correlation metrics
        changes_30d = [stock.change_30d for stock in stock_data.values()]
        avg_ai_performance = np.mean(changes_30d)
        
        # 1. Market correlation
        # Simplified correlation calculation
        if market_indices.sp500 > 0:
            market_correlation = 0.7 if (avg_ai_performance > 0 and market_indices.sp500 > 0) or (avg_ai_performance < 0 and market_indices.sp500 < 0) else 0.3
        else:
            market_correlation = 0.5
        
        indicators['market_correlation'] = FinancialIndicator(
            name='market_correlation',
            value=market_correlation,
            weight=0.06,
            threshold=0.7,
            description='Correlation between AI stocks and market',
            is_concerning=market_correlation > 0.7,
            trend='increasing' if market_correlation > 0.6 else 'decreasing',
            confidence=0.8
        )
        
        # 2. Sector correlation
        # AI stocks correlation with each other
        if len(changes_30d) > 1:
            # Simplified correlation calculation
            sector_correlation = 0.6  # Placeholder for actual calculation
        else:
            sector_correlation = 0.5
        
        indicators['sector_correlation'] = FinancialIndicator(
            name='sector_correlation',
            value=sector_correlation,
            weight=0.04,
            threshold=0.8,
            description='Correlation within AI sector',
            is_concerning=sector_correlation > 0.8,
            trend='stable',
            confidence=0.6
        )
        
        return indicators
    
    def _calculate_sentiment_indicators(self, stock_data: Dict[str, Any], market_indices: Any) -> Dict[str, FinancialIndicator]:
        """Calculate market sentiment indicators"""
        indicators = {}
        
        if not stock_data:
            return indicators
        
        # Calculate sentiment metrics
        changes_1d = [stock.change_1d for stock in stock_data.values()]
        changes_7d = [stock.change_7d for stock in stock_data.values()]
        
        positive_1d = sum(1 for change in changes_1d if change > 0)
        positive_7d = sum(1 for change in changes_7d if change > 0)
        
        # 1. Daily sentiment
        daily_sentiment = positive_1d / len(changes_1d) if changes_1d else 0.5
        indicators['daily_sentiment'] = FinancialIndicator(
            name='daily_sentiment',
            value=daily_sentiment,
            weight=0.05,
            threshold=0.8,
            description='Percentage of stocks with positive daily performance',
            is_concerning=daily_sentiment > 0.8,
            trend='increasing' if daily_sentiment > 0.6 else 'decreasing',
            confidence=min(len(changes_1d) / 10.0, 1.0)
        )
        
        # 2. Weekly sentiment
        weekly_sentiment = positive_7d / len(changes_7d) if changes_7d else 0.5
        indicators['weekly_sentiment'] = FinancialIndicator(
            name='weekly_sentiment',
            value=weekly_sentiment,
            weight=0.07,
            threshold=0.8,
            description='Percentage of stocks with positive weekly performance',
            is_concerning=weekly_sentiment > 0.8,
            trend='increasing' if weekly_sentiment > 0.6 else 'decreasing',
            confidence=min(len(changes_7d) / 10.0, 1.0)
        )
        
        # 3. Sentiment momentum
        sentiment_momentum = weekly_sentiment - daily_sentiment
        indicators['sentiment_momentum'] = FinancialIndicator(
            name='sentiment_momentum',
            value=min(max(sentiment_momentum + 0.5, 0), 1),
            weight=0.04,
            threshold=0.7,
            description='Momentum in market sentiment',
            is_concerning=sentiment_momentum > 0.2,
            trend='increasing' if sentiment_momentum > 0 else 'decreasing',
            confidence=min(abs(sentiment_momentum) * 2, 1.0)
        )
        
        return indicators
    
    def _calculate_regime_indicators(self, stock_data: Dict[str, Any], market_indices: Any) -> Dict[str, FinancialIndicator]:
        """Calculate market regime indicators"""
        indicators = {}
        
        if not stock_data or not market_indices:
            return indicators
        
        # Calculate regime metrics
        changes_30d = [stock.change_30d for stock in stock_data.values()]
        avg_performance = np.mean(changes_30d)
        volatility = np.std(changes_30d)
        vix_level = market_indices.vix if market_indices else 20
        
        # 1. Bull market indicator
        bull_market = 1 if avg_performance > 5.0 and vix_level < 20 else 0
        indicators['bull_market'] = FinancialIndicator(
            name='bull_market',
            value=bull_market,
            weight=0.08,
            threshold=0.5,
            description='Bull market regime indicator',
            is_concerning=bull_market > 0.5,
            trend='increasing' if avg_performance > 3.0 else 'decreasing',
            confidence=min(avg_performance / 10.0, 1.0)
        )
        
        # 2. Volatile market indicator
        volatile_market = 1 if volatility > 4.0 or vix_level > 25 else 0
        indicators['volatile_market'] = FinancialIndicator(
            name='volatile_market',
            value=volatile_market,
            weight=0.06,
            threshold=0.5,
            description='High volatility market regime',
            is_concerning=volatile_market > 0.5,
            trend='increasing' if volatility > 3.0 else 'decreasing',
            confidence=min(volatility / 6.0, 1.0)
        )
        
        # 3. Sideways market indicator
        sideways_market = 1 if abs(avg_performance) < 2.0 and volatility < 3.0 else 0
        indicators['sideways_market'] = FinancialIndicator(
            name='sideways_market',
            value=sideways_market,
            weight=0.04,
            threshold=0.5,
            description='Sideways market regime',
            is_concerning=False,  # Sideways is not concerning
            trend='stable',
            confidence=min((2.0 - abs(avg_performance)) / 2.0, 1.0)
        )
        
        return indicators
    
    def _calculate_bubble_risk_indicators(self, stock_data: Dict[str, Any], 
                                        market_indices: Any, 
                                        historical_snapshots: List[Dict[str, Any]] = None) -> Dict[str, FinancialIndicator]:
        """Calculate specific bubble risk indicators"""
        indicators = {}
        
        if not stock_data:
            return indicators
        
        # Calculate bubble risk metrics
        changes_30d = [stock.change_30d for stock in stock_data.values()]
        avg_performance = np.mean(changes_30d)
        volatility = np.std(changes_30d)
        
        # 1. Performance acceleration
        if historical_snapshots and len(historical_snapshots) > 1:
            # Calculate performance acceleration over time
            recent_performance = avg_performance
            historical_performance = np.mean([s.get('average_bubble_risk', 0) for s in historical_snapshots[-5:]])
            acceleration = recent_performance - historical_performance
        else:
            acceleration = 0
        
        performance_acceleration = min(max(acceleration / 10.0, 0), 1)
        indicators['performance_acceleration'] = FinancialIndicator(
            name='performance_acceleration',
            value=performance_acceleration,
            weight=0.10,
            threshold=0.7,
            description='Acceleration in performance over time',
            is_concerning=performance_acceleration > 0.7,
            trend='increasing' if acceleration > 0 else 'decreasing',
            confidence=min(abs(acceleration) / 15.0, 1.0)
        )
        
        # 2. Volatility expansion
        volatility_expansion = 1 if volatility > 5.0 else 0
        indicators['volatility_expansion'] = FinancialIndicator(
            name='volatility_expansion',
            value=volatility_expansion,
            weight=0.08,
            threshold=0.5,
            description='Expansion in volatility indicating stress',
            is_concerning=volatility_expansion > 0.5,
            trend='increasing' if volatility > 4.0 else 'decreasing',
            confidence=min(volatility / 8.0, 1.0)
        )
        
        # 3. Euphoria indicator
        euphoria = 1 if avg_performance > 15.0 and volatility > 3.0 else 0
        indicators['euphoria'] = FinancialIndicator(
            name='euphoria',
            value=euphoria,
            weight=0.12,
            threshold=0.5,
            description='Market euphoria indicator',
            is_concerning=euphoria > 0.5,
            trend='increasing' if avg_performance > 10.0 else 'decreasing',
            confidence=min(avg_performance / 25.0, 1.0)
        )
        
        return indicators
    
    def _calculate_liquidity_indicators(self, stock_data: Dict[str, Any]) -> Dict[str, FinancialIndicator]:
        """Calculate liquidity indicators"""
        indicators = {}
        
        if not stock_data:
            return indicators
        
        # Calculate liquidity metrics
        volumes = [stock.volume for stock in stock_data.values()]
        avg_volume = np.mean(volumes)
        volume_std = np.std(volumes)
        
        # 1. Volume surge
        volume_surge = 1 if avg_volume > np.percentile(volumes, 80) else 0
        indicators['volume_surge'] = FinancialIndicator(
            name='volume_surge',
            value=volume_surge,
            weight=0.05,
            threshold=0.5,
            description='Unusual volume surge in AI stocks',
            is_concerning=volume_surge > 0.5,
            trend='increasing' if avg_volume > np.percentile(volumes, 60) else 'decreasing',
            confidence=min(avg_volume / np.percentile(volumes, 90), 1.0)
        )
        
        # 2. Volume dispersion
        volume_dispersion = volume_std / avg_volume if avg_volume > 0 else 0
        indicators['volume_dispersion'] = FinancialIndicator(
            name='volume_dispersion',
            value=min(volume_dispersion, 1.0),
            weight=0.03,
            threshold=0.8,
            description='Dispersion in trading volumes',
            is_concerning=volume_dispersion > 0.8,
            trend='increasing' if volume_dispersion > 0.6 else 'decreasing',
            confidence=min(volume_dispersion, 1.0)
        )
        
        return indicators
    
    def _calculate_breadth_indicators(self, stock_data: Dict[str, Any]) -> Dict[str, FinancialIndicator]:
        """Calculate market breadth indicators"""
        indicators = {}
        
        if not stock_data:
            return indicators
        
        # Calculate breadth metrics
        changes_1d = [stock.change_1d for stock in stock_data.values()]
        changes_7d = [stock.change_7d for stock in stock_data.values()]
        
        positive_1d = sum(1 for change in changes_1d if change > 0)
        positive_7d = sum(1 for change in changes_7d if change > 0)
        
        # 1. Market breadth
        breadth_1d = positive_1d / len(changes_1d) if changes_1d else 0.5
        indicators['market_breadth_1d'] = FinancialIndicator(
            name='market_breadth_1d',
            value=breadth_1d,
            weight=0.04,
            threshold=0.8,
            description='Market breadth over 1 day',
            is_concerning=breadth_1d > 0.8,
            trend='increasing' if breadth_1d > 0.6 else 'decreasing',
            confidence=min(len(changes_1d) / 10.0, 1.0)
        )
        
        breadth_7d = positive_7d / len(changes_7d) if changes_7d else 0.5
        indicators['market_breadth_7d'] = FinancialIndicator(
            name='market_breadth_7d',
            value=breadth_7d,
            weight=0.06,
            threshold=0.8,
            description='Market breadth over 7 days',
            is_concerning=breadth_7d > 0.8,
            trend='increasing' if breadth_7d > 0.6 else 'decreasing',
            confidence=min(len(changes_7d) / 10.0, 1.0)
        )
        
        return indicators
    
    def _calculate_risk_adjusted_indicators(self, stock_data: Dict[str, Any], market_indices: Any) -> Dict[str, FinancialIndicator]:
        """Calculate risk-adjusted performance indicators"""
        indicators = {}
        
        if not stock_data:
            return indicators
        
        # Calculate risk-adjusted metrics
        changes_30d = [stock.change_30d for stock in stock_data.values()]
        volatilities = [stock.volatility_30d for stock in stock_data.values()]
        
        avg_performance = np.mean(changes_30d)
        avg_volatility = np.mean(volatilities)
        
        # 1. Sharpe ratio (simplified)
        risk_free_rate = market_indices.treasury_10y if market_indices else 3.0
        sharpe_ratio = (avg_performance - risk_free_rate) / avg_volatility if avg_volatility > 0 else 0
        sharpe_normalized = min(max((sharpe_ratio + 1) / 2, 0), 1)  # Normalize to 0-1
        
        indicators['sharpe_ratio'] = FinancialIndicator(
            name='sharpe_ratio',
            value=sharpe_normalized,
            weight=0.08,
            threshold=0.7,
            description='Risk-adjusted performance (Sharpe ratio)',
            is_concerning=sharpe_normalized < 0.3,
            trend='increasing' if sharpe_ratio > 0 else 'decreasing',
            confidence=min(abs(sharpe_ratio) / 2.0, 1.0)
        )
        
        # 2. Risk-adjusted return
        risk_adjusted_return = avg_performance / avg_volatility if avg_volatility > 0 else 0
        risk_adjusted_normalized = min(max(risk_adjusted_return / 5.0, 0), 1)
        
        indicators['risk_adjusted_return'] = FinancialIndicator(
            name='risk_adjusted_return',
            value=risk_adjusted_normalized,
            weight=0.06,
            threshold=0.6,
            description='Risk-adjusted return metric',
            is_concerning=risk_adjusted_normalized < 0.4,
            trend='increasing' if risk_adjusted_return > 0 else 'decreasing',
            confidence=min(abs(risk_adjusted_return) / 8.0, 1.0)
        )
        
        return indicators
    
    def get_combined_risk_score(self) -> float:
        """Calculate combined risk score from all indicators"""
        if not self.indicators:
            return 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for indicator in self.indicators.values():
            total_weighted_score += indicator.value * indicator.weight * indicator.confidence
            total_weight += indicator.weight * indicator.confidence
        
        return total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    def get_concerning_indicators(self) -> List[FinancialIndicator]:
        """Get all concerning indicators"""
        return [indicator for indicator in self.indicators.values() if indicator.is_concerning]
    
    def get_top_indicators(self, n: int = 5) -> List[FinancialIndicator]:
        """Get top N indicators by weighted importance"""
        sorted_indicators = sorted(
            self.indicators.values(),
            key=lambda x: x.weight * x.value * x.confidence,
            reverse=True
        )
        return sorted_indicators[:n]
    
    def get_indicator_summary(self) -> Dict[str, Any]:
        """Get summary of all indicators"""
        if not self.indicators:
            return {"error": "No indicators calculated"}
        
        concerning_count = len(self.get_concerning_indicators())
        total_count = len(self.indicators)
        
        return {
            "total_indicators": total_count,
            "concerning_indicators": concerning_count,
            "concerning_percentage": concerning_count / total_count * 100,
            "combined_risk_score": self.get_combined_risk_score(),
            "top_indicators": [
                {
                    "name": ind.name,
                    "value": ind.value,
                    "weight": ind.weight,
                    "is_concerning": ind.is_concerning,
                    "description": ind.description
                }
                for ind in self.get_top_indicators(5)
            ],
            "concerning_indicators": [
                {
                    "name": ind.name,
                    "value": ind.value,
                    "description": ind.description,
                    "trend": ind.trend
                }
                for ind in self.get_concerning_indicators()
            ]
        }

# Example usage
if __name__ == "__main__":
    # This would be used with actual stock data
    print("Financial Indicators System initialized")
    print("Use with FinancialDataCollector to get comprehensive indicators")
