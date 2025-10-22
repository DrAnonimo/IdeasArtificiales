from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
try:
    from .bubble_analysis import NewsAnalysis, AIBubbleAnalyzer
except ImportError:
    from bubble_analysis import NewsAnalysis, AIBubbleAnalyzer


@dataclass
class TrackedNews:
    """Represents a tracked news article with analysis"""
    title: str
    url: str
    content: str
    source_query: str
    score: float
    added_date: datetime
    analysis: Optional[NewsAnalysis] = None
    is_analyzed: bool = False


class NewsTracker:
    """Manages tracking of top 10 most relevant AI news articles"""
    
    def __init__(self, data_file: str = "tracked_news.json"):
        self.data_file = Path(data_file)
        self.tracked_news: List[TrackedNews] = []
        self.analyzer = AIBubbleAnalyzer()
        self.max_articles = 10
        self.load_data()

    def add_news_articles(self, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add new articles from search results, maintaining top 10 most relevant"""
        new_articles = []
        
        for result in search_results:
            article = TrackedNews(
                title=result.get("title", ""),
                url=result.get("url", ""),
                content=result.get("content", ""),
                source_query=result.get("source_query", ""),
                score=result.get("score", 0.0),
                added_date=datetime.now()
            )
            new_articles.append(article)
        
        # Merge with existing articles, removing duplicates by URL
        self._merge_articles(new_articles)
        
        # Keep only top 10 by score
        self.tracked_news = sorted(
            self.tracked_news, 
            key=lambda x: x.score, 
            reverse=True
        )[:self.max_articles]
        
        # Save updated data
        self.save_data()
        
        return {
            "added_articles": len(new_articles),
            "total_tracked": len(self.tracked_news),
            "articles": [self._article_to_dict(article) for article in self.tracked_news]
        }

    def analyze_news(self, force_reanalyze: bool = False) -> Dict[str, Any]:
        """Analyze all tracked news articles for bubble indicators"""
        analyses = []
        analyzed_count = 0
        
        for article in self.tracked_news:
            # Skip if already analyzed and not forcing reanalysis
            if article.is_analyzed and not force_reanalyze:
                if article.analysis:
                    analyses.append(article.analysis)
                continue
            
            try:
                # Perform analysis
                analysis = self.analyzer.analyze_news_article(
                    article.title, 
                    article.content, 
                    article.url
                )
                
                # Update article with analysis
                article.analysis = analysis
                article.is_analyzed = True
                analyses.append(analysis)
                analyzed_count += 1
                
            except Exception as e:
                print(f"Error analyzing article '{article.title}': {str(e)}")
                continue
        
        # Save updated data
        self.save_data()
        
        return {
            "analyzed_count": analyzed_count,
            "total_analyses": len(analyses),
            "analyses": analyses
        }

    def get_bubble_report(self) -> Dict[str, Any]:
        """Get comprehensive bubble analysis report"""
        analyses = [article.analysis for article in self.tracked_news if article.analysis]
        
        if not analyses:
            return {"error": "No analyzed articles available"}
        
        return self.analyzer.generate_bubble_report(analyses)

    def export_tableau_data(self) -> List[Dict[str, Any]]:
        """Export data in Tableau-compatible format"""
        analyses = [article.analysis for article in self.tracked_news if article.analysis]
        
        if not analyses:
            return []
        
        return self.analyzer.export_for_tableau(analyses)

    def get_article_summary(self) -> List[Dict[str, Any]]:
        """Get summary of tracked articles"""
        return [self._article_to_dict(article) for article in self.tracked_news]

    def remove_old_articles(self, days_old: int = 7) -> int:
        """Remove articles older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        initial_count = len(self.tracked_news)
        
        self.tracked_news = [
            article for article in self.tracked_news 
            if article.added_date > cutoff_date
        ]
        
        removed_count = initial_count - len(self.tracked_news)
        
        if removed_count > 0:
            self.save_data()
        
        return removed_count

    def _merge_articles(self, new_articles: List[TrackedNews]) -> None:
        """Merge new articles with existing ones, avoiding duplicates"""
        existing_urls = {article.url for article in self.tracked_news}
        
        for new_article in new_articles:
            if new_article.url not in existing_urls:
                self.tracked_news.append(new_article)
            else:
                # Update existing article if new one has higher score
                for i, existing in enumerate(self.tracked_news):
                    if existing.url == new_article.url and new_article.score > existing.score:
                        self.tracked_news[i] = new_article
                        break

    def _article_to_dict(self, article: TrackedNews) -> Dict[str, Any]:
        """Convert article to dictionary for serialization"""
        result = {
            "title": article.title,
            "url": article.url,
            "source_query": article.source_query,
            "score": article.score,
            "added_date": article.added_date.isoformat(),
            "is_analyzed": article.is_analyzed
        }
        
        if article.analysis:
            result.update({
                "sentiment_score": article.analysis.sentiment_score,
                "bubble_risk": article.analysis.overall_bubble_risk,
                "market_impact": article.analysis.market_impact,
                "key_phrases": article.analysis.key_phrases[:5]
            })
        
        return result

    def load_data(self) -> None:
        """Load tracked news from file"""
        if not self.data_file.exists():
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.tracked_news = []
            for item in data.get('articles', []):
                article = TrackedNews(
                    title=item['title'],
                    url=item['url'],
                    content=item.get('content', ''),
                    source_query=item.get('source_query', ''),
                    score=item.get('score', 0.0),
                    added_date=datetime.fromisoformat(item['added_date']),
                    is_analyzed=item.get('is_analyzed', False)
                )
                
                # Reconstruct analysis if available
                if item.get('analysis'):
                    analysis_data = item['analysis']
                    from .bubble_analysis import BubbleIndicator
                    
                    # Reconstruct bubble indicators
                    indicators = []
                    for ind_data in analysis_data.get('bubble_indicators', []):
                        indicator = BubbleIndicator(
                            name=ind_data['name'],
                            value=ind_data['value'],
                            weight=ind_data['weight'],
                            trend=ind_data['trend'],
                            description=ind_data['description'],
                            threshold=ind_data['threshold'],
                            is_concerning=ind_data['is_concerning']
                        )
                        indicators.append(indicator)
                    
                    # Reconstruct analysis
                    analysis = NewsAnalysis(
                        title=analysis_data['title'],
                        url=analysis_data['url'],
                        sentiment_score=analysis_data['sentiment_score'],
                        bubble_indicators=indicators,
                        overall_bubble_risk=analysis_data['overall_bubble_risk'],
                        key_phrases=analysis_data['key_phrases'],
                        market_impact=analysis_data['market_impact'],
                        analysis_date=datetime.fromisoformat(analysis_data['analysis_date'])
                    )
                    article.analysis = analysis
                
                self.tracked_news.append(article)
                
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            self.tracked_news = []

    def save_data(self) -> None:
        """Save tracked news to file"""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'articles': []
            }
            
            for article in self.tracked_news:
                article_dict = {
                    'title': article.title,
                    'url': article.url,
                    'content': article.content,
                    'source_query': article.source_query,
                    'score': article.score,
                    'added_date': article.added_date.isoformat(),
                    'is_analyzed': article.is_analyzed
                }
                
                if article.analysis:
                    article_dict['analysis'] = {
                        'title': article.analysis.title,
                        'url': article.analysis.url,
                        'sentiment_score': article.analysis.sentiment_score,
                        'bubble_indicators': [
                            {
                                'name': ind.name,
                                'value': ind.value,
                                'weight': ind.weight,
                                'trend': ind.trend,
                                'description': ind.description,
                                'threshold': ind.threshold,
                                'is_concerning': ind.is_concerning
                            }
                            for ind in article.analysis.bubble_indicators
                        ],
                        'overall_bubble_risk': article.analysis.overall_bubble_risk,
                        'key_phrases': article.analysis.key_phrases,
                        'market_impact': article.analysis.market_impact,
                        'analysis_date': article.analysis.analysis_date.isoformat()
                    }
                
                data['articles'].append(article_dict)
            
            # Ensure directory exists
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving data: {str(e)}")

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the news tracker"""
        analyzed_count = sum(1 for article in self.tracked_news if article.is_analyzed)
        
        return {
            "total_articles": len(self.tracked_news),
            "analyzed_articles": analyzed_count,
            "pending_analysis": len(self.tracked_news) - analyzed_count,
            "data_file": str(self.data_file),
            "last_updated": datetime.now().isoformat()
        }
