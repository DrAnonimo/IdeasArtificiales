from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import re
import json
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
try:
    from .config import make_llm
except ImportError:
    from config import make_llm


@dataclass
class BubbleIndicator:
    """Represents a key performance indicator for AI bubble detection"""
    name: str
    value: float
    weight: float  # Importance weight (0-1)
    trend: str  # "increasing", "decreasing", "stable"
    description: str
    threshold: float  # Threshold for concern
    is_concerning: bool


@dataclass
class NewsAnalysis:
    """Analysis result for a single news article"""
    title: str
    url: str
    sentiment_score: float  # -1 to 1
    bubble_indicators: List[BubbleIndicator]
    overall_bubble_risk: float  # 0 to 1
    key_phrases: List[str]
    market_impact: str
    analysis_date: datetime


class AIBubbleAnalyzer:
    """Analyzes AI news for potential bubble indicators"""
    
    def __init__(self):
        self.llm = make_llm()
        self.bubble_keywords = {
            'hype': ['revolutionary', 'breakthrough', 'game-changer', 'disruptive', 'transformative', 
                    'unprecedented', 'explosive growth', 'skyrocketing', 'soaring', 'surge'],
            'investment': ['funding', 'investment', 'valuation', 'IPO', 'acquisition', 'merger', 
                          'venture capital', 'private equity', 'billion', 'million', 'unicorn'],
            'market_speculation': ['bubble', 'overvalued', 'overheated', 'speculation', 'frenzy', 
                                 'mania', 'euphoria', 'irrational exuberance', 'tulip mania'],
            'competition': ['race', 'competition', 'battle', 'war', 'arms race', 'gold rush', 
                           'land grab', 'market share', 'dominance'],
            'regulatory': ['regulation', 'oversight', 'compliance', 'policy', 'government', 
                          'legislation', 'ban', 'restriction', 'ethics', 'safety']
        }
        
        self.bubble_indicators = {
            'hype_level': {'weight': 0.25, 'threshold': 0.7},
            'investment_frenzy': {'weight': 0.20, 'threshold': 0.6},
            'market_speculation': {'weight': 0.20, 'threshold': 0.5},
            'competitive_intensity': {'weight': 0.15, 'threshold': 0.6},
            'regulatory_concern': {'weight': 0.20, 'threshold': 0.4}
        }

    def analyze_news_article(self, title: str, content: str, url: str) -> NewsAnalysis:
        """Analyze a single news article for bubble indicators"""
        
        # Extract key phrases and sentiment
        key_phrases = self._extract_key_phrases(content)
        sentiment_score = self._analyze_sentiment(title, content)
        
        # Calculate bubble indicators
        bubble_indicators = self._calculate_bubble_indicators(title, content, key_phrases)
        
        # Calculate overall bubble risk
        overall_risk = self._calculate_overall_bubble_risk(bubble_indicators)
        
        # Determine market impact
        market_impact = self._assess_market_impact(bubble_indicators, sentiment_score)
        
        return NewsAnalysis(
            title=title,
            url=url,
            sentiment_score=sentiment_score,
            bubble_indicators=bubble_indicators,
            overall_bubble_risk=overall_risk,
            key_phrases=key_phrases,
            market_impact=market_impact,
            analysis_date=datetime.now()
        )

    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases related to AI bubble indicators"""
        content_lower = content.lower()
        phrases = []
        
        for category, keywords in self.bubble_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    # Find the context around the keyword
                    pattern = rf'.{{0,50}}{re.escape(keyword)}.{{0,50}}'
                    matches = re.findall(pattern, content_lower, re.IGNORECASE)
                    phrases.extend(matches[:2])  # Limit to 2 matches per keyword
        
        return list(set(phrases))[:10]  # Return unique phrases, max 10

    def _analyze_sentiment(self, title: str, content: str) -> float:
        """Analyze sentiment of the article using LLM"""
        sentiment_prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze the sentiment of this AI news article. Consider:
            - Overall tone (positive, negative, neutral)
            - Market optimism vs pessimism
            - Speculation level
            - Hype vs realistic assessment
            
            Return a sentiment score from -1 (very negative/pessimistic) to 1 (very positive/optimistic).
            Consider that extreme optimism might indicate bubble risk.
            
            Format: Just return the score as a number between -1 and 1."""),
            ("human", "Title: {title}\n\nContent: {content}")
        ])
        
        chain = sentiment_prompt | self.llm | StrOutputParser()
        result = chain.invoke({"title": title, "content": content[:2000]})
        
        # Extract number from response
        try:
            score = float(re.findall(r'-?\d+\.?\d*', result)[0])
            return max(-1, min(1, score))  # Clamp between -1 and 1
        except (ValueError, IndexError):
            return 0.0

    def _calculate_bubble_indicators(self, title: str, content: str, key_phrases: List[str]) -> List[BubbleIndicator]:
        """Calculate specific bubble indicators"""
        content_lower = content.lower()
        indicators = []
        
        for indicator_name, config in self.bubble_indicators.items():
            value = self._calculate_indicator_value(indicator_name, title, content_lower, key_phrases)
            trend = self._determine_trend(value, config['threshold'])
            is_concerning = value > config['threshold']
            
            indicators.append(BubbleIndicator(
                name=indicator_name,
                value=value,
                weight=config['weight'],
                trend=trend,
                description=self._get_indicator_description(indicator_name),
                threshold=config['threshold'],
                is_concerning=is_concerning
            ))
        
        return indicators

    def _calculate_indicator_value(self, indicator_name: str, title: str, content: str, key_phrases: List[str]) -> float:
        """Calculate the value for a specific bubble indicator"""
        if indicator_name == 'hype_level':
            return self._calculate_hype_level(title, content)
        elif indicator_name == 'investment_frenzy':
            return self._calculate_investment_frenzy(content)
        elif indicator_name == 'market_speculation':
            return self._calculate_market_speculation(content)
        elif indicator_name == 'competitive_intensity':
            return self._calculate_competitive_intensity(content)
        elif indicator_name == 'regulatory_concern':
            return self._calculate_regulatory_concern(content)
        else:
            return 0.0

    def _calculate_hype_level(self, title: str, content: str) -> float:
        """Calculate hype level based on superlative language"""
        hype_words = self.bubble_keywords['hype']
        title_lower = title.lower()
        content_lower = content.lower()
        
        title_hype = sum(1 for word in hype_words if word in title_lower)
        content_hype = sum(1 for word in hype_words if word in content_lower)
        
        # Weight title more heavily
        total_hype = (title_hype * 3) + content_hype
        return min(1.0, total_hype / 10.0)  # Normalize to 0-1

    def _calculate_investment_frenzy(self, content: str) -> float:
        """Calculate investment frenzy level"""
        investment_words = self.bubble_keywords['investment']
        market_words = ['market', 'valuation', 'price', 'stock', 'trading']
        
        investment_count = sum(1 for word in investment_words if word in content)
        market_count = sum(1 for word in market_words if word in content)
        
        # Look for large numbers (billion, million)
        large_numbers = len(re.findall(r'\b\d+\.?\d*\s*(billion|million)\b', content, re.IGNORECASE))
        
        total_score = investment_count + market_count + (large_numbers * 2)
        return min(1.0, total_score / 15.0)

    def _calculate_market_speculation(self, content: str) -> float:
        """Calculate market speculation level"""
        speculation_words = self.bubble_keywords['market_speculation']
        speculation_count = sum(1 for word in speculation_words if word in content)
        
        # Look for future predictions and projections
        future_words = ['will', 'expected', 'projected', 'forecast', 'prediction', 'anticipate']
        future_count = sum(1 for word in future_words if word in content)
        
        total_score = speculation_count + (future_count * 0.5)
        return min(1.0, total_score / 8.0)

    def _calculate_competitive_intensity(self, content: str) -> float:
        """Calculate competitive intensity level"""
        competition_words = self.bubble_keywords['competition']
        competition_count = sum(1 for word in competition_words if word in content)
        
        # Look for company names (capitalized words)
        company_names = len(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content))
        
        total_score = competition_count + min(company_names * 0.1, 3.0)
        return min(1.0, total_score / 10.0)

    def _calculate_regulatory_concern(self, content: str) -> float:
        """Calculate regulatory concern level"""
        regulatory_words = self.bubble_keywords['regulatory']
        regulatory_count = sum(1 for word in regulatory_words if word in content)
        
        # Look for concern/risk words
        concern_words = ['concern', 'risk', 'threat', 'challenge', 'problem', 'issue']
        concern_count = sum(1 for word in concern_words if word in content)
        
        total_score = regulatory_count + (concern_count * 0.5)
        return min(1.0, total_score / 8.0)

    def _determine_trend(self, value: float, threshold: float) -> str:
        """Determine trend based on value relative to threshold"""
        if value > threshold * 1.2:
            return "increasing"
        elif value < threshold * 0.8:
            return "decreasing"
        else:
            return "stable"

    def _get_indicator_description(self, indicator_name: str) -> str:
        """Get description for an indicator"""
        descriptions = {
            'hype_level': 'Level of hype and superlative language in the article',
            'investment_frenzy': 'Intensity of investment and funding discussions',
            'market_speculation': 'Level of market speculation and future predictions',
            'competitive_intensity': 'Intensity of competitive dynamics mentioned',
            'regulatory_concern': 'Level of regulatory concerns and risks mentioned'
        }
        return descriptions.get(indicator_name, 'Unknown indicator')

    def _calculate_overall_bubble_risk(self, indicators: List[BubbleIndicator]) -> float:
        """Calculate overall bubble risk score"""
        weighted_sum = sum(indicator.value * indicator.weight for indicator in indicators)
        concerning_count = sum(1 for indicator in indicators if indicator.is_concerning)
        
        # Add penalty for multiple concerning indicators
        penalty = concerning_count * 0.1
        return min(1.0, weighted_sum + penalty)

    def _assess_market_impact(self, indicators: List[BubbleIndicator], sentiment_score: float) -> str:
        """Assess overall market impact based on indicators"""
        concerning_indicators = [i for i in indicators if i.is_concerning]
        risk_level = len(concerning_indicators)
        
        if risk_level >= 4:
            return "High Risk - Multiple bubble indicators present"
        elif risk_level >= 2:
            return "Moderate Risk - Some concerning indicators"
        elif sentiment_score > 0.7:
            return "Optimistic - High sentiment but few concerning indicators"
        elif sentiment_score < -0.3:
            return "Pessimistic - Low sentiment and market concerns"
        else:
            return "Neutral - Balanced market sentiment"

    def generate_bubble_report(self, analyses: List[NewsAnalysis]) -> Dict[str, Any]:
        """Generate a comprehensive bubble analysis report"""
        if not analyses:
            return {"error": "No analyses provided"}
        
        # Calculate aggregate metrics
        avg_sentiment = sum(a.sentiment_score for a in analyses) / len(analyses)
        avg_bubble_risk = sum(a.overall_bubble_risk for a in analyses) / len(analyses)
        
        # Count concerning indicators
        concerning_articles = sum(1 for a in analyses if a.overall_bubble_risk > 0.6)
        
        # Aggregate indicator scores
        indicator_totals = {}
        for analysis in analyses:
            for indicator in analysis.bubble_indicators:
                if indicator.name not in indicator_totals:
                    indicator_totals[indicator.name] = []
                indicator_totals[indicator.name].append(indicator.value)
        
        # Calculate average indicator scores
        avg_indicators = {
            name: sum(values) / len(values) 
            for name, values in indicator_totals.items()
        }
        
        # Determine overall market assessment
        if avg_bubble_risk > 0.7:
            market_assessment = "HIGH BUBBLE RISK"
        elif avg_bubble_risk > 0.5:
            market_assessment = "MODERATE BUBBLE RISK"
        elif avg_sentiment > 0.5:
            market_assessment = "OPTIMISTIC MARKET"
        else:
            market_assessment = "NEUTRAL MARKET"
        
        return {
            "analysis_date": datetime.now().isoformat(),
            "total_articles": len(analyses),
            "average_sentiment": round(avg_sentiment, 3),
            "average_bubble_risk": round(avg_bubble_risk, 3),
            "concerning_articles": concerning_articles,
            "market_assessment": market_assessment,
            "indicator_averages": avg_indicators,
            "individual_analyses": [
                {
                    "title": a.title,
                    "url": a.url,
                    "sentiment_score": a.sentiment_score,
                    "bubble_risk": a.overall_bubble_risk,
                    "market_impact": a.market_impact,
                    "key_phrases": a.key_phrases[:5]  # Top 5 phrases
                }
                for a in analyses
            ]
        }

    def export_for_tableau(self, analyses: List[NewsAnalysis]) -> List[Dict[str, Any]]:
        """Export data in format suitable for Tableau dashboard"""
        tableau_data = []
        
        for analysis in analyses:
            # Main article record
            base_record = {
                "article_id": hash(analysis.url) % 1000000,  # Simple ID generation
                "title": analysis.title,
                "url": analysis.url,
                "analysis_date": analysis.analysis_date.isoformat(),
                "sentiment_score": analysis.sentiment_score,
                "overall_bubble_risk": analysis.overall_bubble_risk,
                "market_impact": analysis.market_impact,
                "key_phrases_count": len(analysis.key_phrases)
            }
            
            # Add individual indicator records
            for indicator in analysis.bubble_indicators:
                record = base_record.copy()
                record.update({
                    "indicator_name": indicator.name,
                    "indicator_value": indicator.value,
                    "indicator_weight": indicator.weight,
                    "indicator_trend": indicator.trend,
                    "indicator_threshold": indicator.threshold,
                    "is_concerning": indicator.is_concerning,
                    "indicator_description": indicator.description
                })
                tableau_data.append(record)
        
        return tableau_data
