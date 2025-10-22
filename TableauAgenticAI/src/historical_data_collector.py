"""
Historical Data Collector for AI Bubble Analysis

This module collects historical data from the past 30 days to provide
better context for bubble prediction and trend analysis.
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import time
import logging
from dataclasses import dataclass, asdict

try:
    from .config import make_tavily, make_llm
    from .news_tracker import NewsTracker
    from .bubble_analysis import AIBubbleAnalyzer
except ImportError:
    from config import make_tavily, make_llm
    from news_tracker import NewsTracker
    from bubble_analysis import AIBubbleAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class HistoricalDataPoint:
    """Represents a single day's data point"""
    date: str
    timestamp: datetime
    articles: List[Dict[str, Any]]
    bubble_analysis: Dict[str, Any]
    market_metrics: Dict[str, Any]
    sentiment_summary: Dict[str, Any]
    data_quality: str  # "complete", "partial", "incomplete"

class HistoricalDataCollector:
    """Collects and manages historical data for bubble analysis"""
    
    def __init__(self, data_dir: str = "historical_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.tavily = make_tavily()
        self.analyzer = AIBubbleAnalyzer()
        self.tracker = NewsTracker()
        
        # Historical data storage
        self.historical_file = self.data_dir / "historical_data.json"
        self.historical_data: List[HistoricalDataPoint] = []
        self.load_historical_data()
    
    def load_historical_data(self):
        """Load existing historical data from file"""
        if self.historical_file.exists():
            try:
                with open(self.historical_file, 'r') as f:
                    data = json.load(f)
                    self.historical_data = [
                        HistoricalDataPoint(**point) for point in data
                    ]
                logger.info(f"Loaded {len(self.historical_data)} historical data points")
            except Exception as e:
                logger.error(f"Error loading historical data: {e}")
                self.historical_data = []
        else:
            self.historical_data = []
    
    def save_historical_data(self):
        """Save historical data to file"""
        try:
            data = [asdict(point) for point in self.historical_data]
            with open(self.historical_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Saved {len(self.historical_data)} historical data points")
        except Exception as e:
            logger.error(f"Error saving historical data: {e}")
    
    def collect_historical_data(self, days: int = 30, force_recollect: bool = False) -> Dict[str, Any]:
        """
        Collect historical data for the past N days
        
        Args:
            days: Number of days to collect (default 30)
            force_recollect: Whether to recollect existing data
        
        Returns:
            Dictionary with collection results
        """
        logger.info(f"Starting historical data collection for {days} days")
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Check what data we already have
        existing_dates = {point.date for point in self.historical_data}
        
        collected_days = []
        failed_days = []
        
        # Collect data for each day
        for i in range(days):
            target_date = start_date + timedelta(days=i)
            date_str = target_date.strftime("%Y-%m-%d")
            
            # Skip if we already have data and not forcing recollect
            if date_str in existing_dates and not force_recollect:
                logger.info(f"Skipping {date_str} - data already exists")
                continue
            
            try:
                logger.info(f"Collecting data for {date_str}")
                data_point = self._collect_single_day_data(target_date)
                
                if data_point:
                    # Remove existing data for this date if it exists
                    self.historical_data = [p for p in self.historical_data if p.date != date_str]
                    self.historical_data.append(data_point)
                    collected_days.append(date_str)
                    logger.info(f"Successfully collected data for {date_str}")
                else:
                    failed_days.append(date_str)
                    logger.warning(f"Failed to collect data for {date_str}")
                
                # Rate limiting - be respectful to APIs
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error collecting data for {date_str}: {e}")
                failed_days.append(date_str)
        
        # Save the updated data
        self.save_historical_data()
        
        return {
            "collected_days": collected_days,
            "failed_days": failed_days,
            "total_days": days,
            "success_rate": len(collected_days) / days,
            "data_points": len(self.historical_data)
        }
    
    def _collect_single_day_data(self, target_date: datetime.date) -> Optional[HistoricalDataPoint]:
        """Collect data for a single day"""
        try:
            # Create date-specific search queries
            date_str = target_date.strftime("%Y-%m-%d")
            queries = self._get_historical_queries(target_date)
            
            # Search for news articles
            articles = []
            for query in queries:
                try:
                    # Use Tavily search with date filtering
                    results = self.tavily.search(
                        query=query,
                        search_depth="advanced",
                        include_answer=False,
                        max_results=5
                    )
                    
                    for item in results.get("results", []):
                        articles.append({
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "content": item.get("content", ""),
                            "score": item.get("score", 0),
                            "source_query": query,
                            "date": date_str
                        })
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Error searching for query '{query}': {e}")
                    continue
            
            if not articles:
                logger.warning(f"No articles found for {date_str}")
                return None
            
            # Deduplicate articles
            articles = self._deduplicate_articles(articles)
            
            # Analyze articles for bubble indicators
            bubble_analysis = self._analyze_articles_for_bubble(articles)
            
            # Calculate market metrics
            market_metrics = self._calculate_market_metrics(articles, bubble_analysis)
            
            # Calculate sentiment summary
            sentiment_summary = self._calculate_sentiment_summary(articles, bubble_analysis)
            
            # Determine data quality
            data_quality = self._assess_data_quality(articles, bubble_analysis)
            
            return HistoricalDataPoint(
                date=date_str,
                timestamp=datetime.combine(target_date, datetime.min.time()),
                articles=articles,
                bubble_analysis=bubble_analysis,
                market_metrics=market_metrics,
                sentiment_summary=sentiment_summary,
                data_quality=data_quality
            )
            
        except Exception as e:
            logger.error(f"Error collecting data for {target_date}: {e}")
            return None
    
    def _get_historical_queries(self, target_date: datetime.date) -> List[str]:
        """Get optimized search queries - reduced from 10 to 4 per day"""
        date_str = target_date.strftime("%Y-%m-%d")
        weekday = target_date.weekday()
        
        # Smart query selection based on day of week
        if weekday == 0:  # Monday - weekend coverage
            return [
                f"AI weekend news {date_str}",
                f"AI market {date_str}",
                f"AI funding {date_str}"
            ]
        elif weekday < 5:  # Weekday - business focus
            return [
                f"AI news {date_str}",
                f"AI startup funding {date_str}",
                f"AI market bubble {date_str}",
                f"AI regulation {date_str}"
            ]
        else:  # Weekend - research focus
            return [
                f"AI research {date_str}",
                f"AI technology {date_str}",
                f"AI innovation {date_str}"
            ]
    
    def _deduplicate_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles based on URL and title similarity"""
        seen_urls = set()
        seen_titles = set()
        deduplicated = []
        
        # Sort by score to keep highest quality articles
        articles_sorted = sorted(articles, key=lambda x: x.get("score", 0), reverse=True)
        
        for article in articles_sorted:
            url = article.get("url", "")
            title = article.get("title", "").lower().strip()
            
            # Skip if URL already seen
            if url and url in seen_urls:
                continue
                
            # Skip if very similar title already seen
            if title and any(self._titles_similar(title, seen_title) for seen_title in seen_titles):
                continue
            
            # Add to deduplicated list
            if url:
                seen_urls.add(url)
            if title:
                seen_titles.add(title)
            deduplicated.append(article)
        
        return deduplicated
    
    def _titles_similar(self, title1: str, title2: str, threshold: float = 0.8) -> bool:
        """Check if two titles are similar enough to be considered duplicates"""
        if not title1 or not title2:
            return False
        
        # Simple similarity check based on common words
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union)
        return similarity >= threshold
    
    def _analyze_articles_for_bubble(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze articles for bubble indicators"""
        if not articles:
            return {"error": "No articles to analyze"}
        
        try:
            # Analyze each article
            analyses = []
            for article in articles:
                analysis = self.analyzer.analyze_news_article(
                    title=article.get("title", ""),
                    content=article.get("content", ""),
                    url=article.get("url", "")
                )
                analyses.append(analysis)
            
            # Aggregate results
            total_articles = len(analyses)
            avg_bubble_risk = sum(a.overall_bubble_risk for a in analyses) / total_articles
            avg_sentiment = sum(a.sentiment_score for a in analyses) / total_articles
            
            # Count concerning articles
            concerning_articles = sum(1 for a in analyses if a.overall_bubble_risk > 0.3)
            
            # Calculate indicator averages
            indicator_averages = {}
            for indicator in analyses[0].bubble_indicators:
                indicator_name = indicator["name"]
                avg_value = sum(a.bubble_indicators[i]["value"] for a, i in zip(analyses, range(len(analyses)))) / total_articles
                indicator_averages[indicator_name] = avg_value
            
            return {
                "total_articles": total_articles,
                "analyzed_articles": total_articles,
                "average_bubble_risk": avg_bubble_risk,
                "average_sentiment": avg_sentiment,
                "concerning_articles": concerning_articles,
                "indicator_averages": indicator_averages,
                "market_assessment": self._assess_market_condition(avg_bubble_risk, avg_sentiment),
                "analyses": [asdict(a) for a in analyses]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing articles: {e}")
            return {"error": str(e)}
    
    def _calculate_market_metrics(self, articles: List[Dict[str, Any]], bubble_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional market metrics"""
        try:
            # Extract financial numbers from articles
            financial_mentions = []
            for article in articles:
                content = article.get("content", "").lower()
                # Look for financial numbers
                import re
                numbers = re.findall(r'\$[\d,]+(?:\.\d+)?[bmk]?', content)
                financial_mentions.extend(numbers)
            
            # Calculate metrics
            total_financial_mentions = len(financial_mentions)
            avg_financial_mentions = total_financial_mentions / len(articles) if articles else 0
            
            # Calculate article diversity (unique sources)
            unique_sources = len(set(article.get("url", "").split("/")[2] for article in articles if article.get("url")))
            
            return {
                "total_financial_mentions": total_financial_mentions,
                "avg_financial_mentions_per_article": avg_financial_mentions,
                "unique_sources": unique_sources,
                "source_diversity": unique_sources / len(articles) if articles else 0,
                "bubble_risk_level": bubble_analysis.get("average_bubble_risk", 0),
                "sentiment_level": bubble_analysis.get("average_sentiment", 0)
            }
            
        except Exception as e:
            logger.error(f"Error calculating market metrics: {e}")
            return {"error": str(e)}
    
    def _calculate_sentiment_summary(self, articles: List[Dict[str, Any]], bubble_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate sentiment summary"""
        try:
            avg_sentiment = bubble_analysis.get("average_sentiment", 0)
            
            # Categorize sentiment
            if avg_sentiment > 0.3:
                sentiment_category = "Optimistic"
            elif avg_sentiment < -0.3:
                sentiment_category = "Pessimistic"
            else:
                sentiment_category = "Neutral"
            
            # Calculate sentiment volatility (if we have multiple days)
            sentiment_volatility = 0
            if len(self.historical_data) > 1:
                recent_sentiments = [point.sentiment_summary.get("average_sentiment", 0) for point in self.historical_data[-7:]]
                if len(recent_sentiments) > 1:
                    sentiment_volatility = sum(abs(recent_sentiments[i] - recent_sentiments[i-1]) for i in range(1, len(recent_sentiments))) / (len(recent_sentiments) - 1)
            
            return {
                "average_sentiment": avg_sentiment,
                "sentiment_category": sentiment_category,
                "sentiment_volatility": sentiment_volatility,
                "total_articles": len(articles)
            }
            
        except Exception as e:
            logger.error(f"Error calculating sentiment summary: {e}")
            return {"error": str(e)}
    
    def _assess_data_quality(self, articles: List[Dict[str, Any]], bubble_analysis: Dict[str, Any]) -> str:
        """Assess the quality of collected data"""
        try:
            article_count = len(articles)
            analyzed_count = bubble_analysis.get("analyzed_articles", 0)
            
            if article_count >= 10 and analyzed_count >= 8:
                return "complete"
            elif article_count >= 5 and analyzed_count >= 4:
                return "partial"
            else:
                return "incomplete"
                
        except Exception as e:
            logger.error(f"Error assessing data quality: {e}")
            return "incomplete"
    
    def _assess_market_condition(self, avg_bubble_risk: float, avg_sentiment: float) -> str:
        """Assess overall market condition"""
        if avg_bubble_risk > 0.7:
            return "HIGH BUBBLE RISK"
        elif avg_bubble_risk > 0.5:
            return "MODERATE BUBBLE RISK"
        elif avg_sentiment > 0.3 and avg_bubble_risk < 0.3:
            return "OPTIMISTIC MARKET"
        elif avg_sentiment < -0.3:
            return "PESSIMISTIC MARKET"
        else:
            return "NEUTRAL MARKET"
    
    def get_historical_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary of historical data"""
        try:
            # Get recent data points
            recent_data = self.historical_data[-days:] if len(self.historical_data) >= days else self.historical_data
            
            if not recent_data:
                return {"error": "No historical data available"}
            
            # Calculate trends
            bubble_risks = [point.bubble_analysis.get("average_bubble_risk", 0) for point in recent_data]
            sentiments = [point.sentiment_summary.get("average_sentiment", 0) for point in recent_data]
            
            # Calculate trends
            bubble_trend = self._calculate_trend(bubble_risks)
            sentiment_trend = self._calculate_trend(sentiments)
            
            # Calculate averages
            avg_bubble_risk = sum(bubble_risks) / len(bubble_risks)
            avg_sentiment = sum(sentiments) / len(sentiments)
            
            # Count concerning days
            concerning_days = sum(1 for risk in bubble_risks if risk > 0.3)
            
            return {
                "period_days": len(recent_data),
                "date_range": {
                    "start": recent_data[0].date,
                    "end": recent_data[-1].date
                },
                "average_bubble_risk": avg_bubble_risk,
                "average_sentiment": avg_sentiment,
                "bubble_trend": bubble_trend,
                "sentiment_trend": sentiment_trend,
                "concerning_days": concerning_days,
                "data_quality_distribution": self._get_data_quality_distribution(recent_data),
                "market_assessment": self._assess_market_condition(avg_bubble_risk, avg_sentiment)
            }
            
        except Exception as e:
            logger.error(f"Error getting historical summary: {e}")
            return {"error": str(e)}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend calculation
        n = len(values)
        x = list(range(n))
        y = values
        
        # Calculate slope
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
    
    def _get_data_quality_distribution(self, data_points: List[HistoricalDataPoint]) -> Dict[str, int]:
        """Get distribution of data quality"""
        quality_counts = {"complete": 0, "partial": 0, "incomplete": 0}
        
        for point in data_points:
            quality = point.data_quality
            if quality in quality_counts:
                quality_counts[quality] += 1
        
        return quality_counts
    
    def export_historical_data(self, format: str = "csv") -> Dict[str, Any]:
        """Export historical data in various formats"""
        try:
            if format.lower() == "csv":
                return self._export_to_csv()
            elif format.lower() == "json":
                return self._export_to_json()
            else:
                return {"error": f"Unsupported format: {format}"}
                
        except Exception as e:
            logger.error(f"Error exporting historical data: {e}")
            return {"error": str(e)}
    
    def _export_to_csv(self) -> Dict[str, Any]:
        """Export historical data to CSV format"""
        try:
            import pandas as pd
            
            # Prepare data for CSV
            csv_data = []
            for point in self.historical_data:
                csv_data.append({
                    "date": point.date,
                    "timestamp": point.timestamp.isoformat(),
                    "total_articles": len(point.articles),
                    "average_bubble_risk": point.bubble_analysis.get("average_bubble_risk", 0),
                    "average_sentiment": point.sentiment_summary.get("average_sentiment", 0),
                    "concerning_articles": point.bubble_analysis.get("concerning_articles", 0),
                    "market_assessment": point.bubble_analysis.get("market_assessment", "Unknown"),
                    "data_quality": point.data_quality,
                    "unique_sources": point.market_metrics.get("unique_sources", 0),
                    "financial_mentions": point.market_metrics.get("total_financial_mentions", 0)
                })
            
            # Create DataFrame and save
            df = pd.DataFrame(csv_data)
            csv_file = self.data_dir / "historical_data.csv"
            df.to_csv(csv_file, index=False)
            
            return {
                "success": True,
                "file_path": str(csv_file),
                "rows": len(csv_data),
                "columns": list(df.columns)
            }
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return {"error": str(e)}
    
    def _export_to_json(self) -> Dict[str, Any]:
        """Export historical data to JSON format"""
        try:
            json_file = self.data_dir / "historical_data_export.json"
            
            # Convert to serializable format
            export_data = {
                "metadata": {
                    "export_date": datetime.now().isoformat(),
                    "total_data_points": len(self.historical_data),
                    "date_range": {
                        "start": self.historical_data[0].date if self.historical_data else None,
                        "end": self.historical_data[-1].date if self.historical_data else None
                    }
                },
                "data_points": [asdict(point) for point in self.historical_data]
            }
            
            with open(json_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            return {
                "success": True,
                "file_path": str(json_file),
                "data_points": len(self.historical_data)
            }
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return {"error": str(e)}
